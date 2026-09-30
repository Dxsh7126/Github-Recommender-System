import os

from dotenv import load_dotenv
from github import Github

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.database.models import Base, Repository, Issue


load_dotenv()

github = Github(os.getenv("GITHUB_TOKEN"))


DATABASE_URL = (
    "postgresql://recommender:"
    "recommender_password@localhost:5433/"
    "issue_recommender"
)

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)

languages = ["Python","JavaScript","TypeScript","Java","Go"]

repos_per_lang = 10

for language in languages:

    print(f"\nSearching for {language} repos")

    repos = github.search_repositories(
        query=f"language:{language} stars:>100",
        sort="updated",
        order="desc"
    )

    for repo in repos[:repos_per_lang]:
        print(
            f"{repo.full_name} | "
            f"{repo.language} |"
            f"{repo.stargazers_count} stars"
            )

        with Session(engine) as session:

            existing_repo = session.query(Repository).filter_by(github_id=repo.id).first()
            if existing_repo:
                db_repo = existing_repo
                print(f"Already exists: {repo.full_name}")
            else:
                db_repo=Repository(
                    github_id=repo.id,
                    name=repo.name,
                    full_name=repo.full_name,
                    description=repo.description,
                    url=repo.html_url,
                    language=repo.language,
                    stars=repo.stargazers_count,
                    forks=repo.forks_count,
                    topics=repo.get_topics(),
                    created_at=repo.created_at,
                    updated_at=repo.updated_at,
                    issues_collected=False
                )

                session.add(db_repo)
                session.flush()

                print(f"Saved repository: {repo.full_name}")

            session.commit()

