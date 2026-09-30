from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import Base, Repository, Developer, Issue
import os
from dotenv import load_dotenv
from github import Github

load_dotenv()

github=Github(os.getenv("GITHUB_TOKEN"))

repos = github.search_repositories(query="language:Python stars:>100")

DATABASE_URL = (
    "postgresql://recommender:"
    "recommender_password@localhost:5433/"
    "issue_recommender"
)

engine = create_engine(DATABASE_URL)

Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
print("Tables recreated successfully")

print("Getting repo...")
repo = github.get_repo("NousResearch/hermes-agent")
print("Repo fetched: ",repo.full_name)

db_repo = Repository(
    github_id = repo.id,
    name=repo.name,
    full_name=repo.full_name,
    description=repo.description,
    url=repo.html_url,
    language=repo.language,
    stars=repo.stargazers_count,
    forks=repo.forks_count,
    topics=repo.get_topics(),
    created_at=repo.created_at,
    updated_at=repo.updated_at
)

with Session(engine) as session:
    session.add(db_repo)
    session.flush()

    print("Repo inserted with db ID: ",db_repo.id)
    session.commit()

    print("fetching open issues...")

    issues = repo.get_issues(state="open")[:20]
    print("issue object recieved")

    count = 0

    for issue in issues:
        if issue.pull_request is not None:
            continue

        db_issue = Issue(
            github_id=issue.id,
            repository_id=db_repo.id,
            title=issue.title,
            body=issue.body,
            labels=[label.name for label in issue.labels],
            comments=issue.comments,
            created_at=issue.created_at,
            updated_at=issue.updated_at
        )

        session.add(db_issue)
        count+=1

    print("issues added to session ",count)
    session.commit()

print("REPO and ISSUE data inserted successfully!")
