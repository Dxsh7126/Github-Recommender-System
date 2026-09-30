import os

from dotenv import load_dotenv
from github import Github

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.database.models import Repository, Issue, Base


load_dotenv()

github = Github(os.getenv("GITHUB_TOKEN"))

DATABASE_URL = (
    "postgresql://recommender:"
    "recommender_password@localhost:5433/"
    "issue_recommender"
)

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)


with Session(engine) as session:

    # Get repositories already stored in PostgreSQL
    repositories = session.query(Repository).all()

    print(f"Found {len(repositories)} repositories")

    for db_repo in repositories:

        print(f"\nRepository: {db_repo.full_name}")


        if db_repo.issues_collected:

            print("Issues already collected -> SKIPPING")
            continue


        print("Issues not collected -> Fetching...")

        repo = github.get_repo(db_repo.full_name)

        issues = repo.get_issues(state="open")

        count = 0

        for issue in issues:

            if issue.pull_request is not None:
                continue

            db_issue = Issue(
                github_id=issue.id,
                repository_id=db_repo.id,
                title=issue.title,
                body=issue.body,
                labels=[
                    label.name
                    for label in issue.labels
                ],
                comments=issue.comments,
                created_at=issue.created_at,
                updated_at=issue.updated_at
            )

            session.add(db_issue)

            count += 1

            if count == 10:
                break


        db_repo.issues_collected = True

        session.commit()

        print(
            f"Saved {count} issues for "
            f"{db_repo.full_name}"
        )

print("\nIssue collection completed!")
