import os

from dotenv import load_dotenv
from github import Github

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.database.models import Developer, Base


load_dotenv()

github = Github(os.getenv("GITHUB_TOKEN"))

DATABASE_URL = (
    "postgresql://recommender:"
    "recommender_password@localhost:5433/"
    "issue_recommender"
)

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)

developers = ["Dxsh7126","torvalds","karpathy","gvanrossum","ad1tyq"]

for username in developers:
    print(f"\nFetching developer: {username}")

    user=github.get_user(username)

    with Session(engine) as session:

        existing = session.query(Developer).filter_by(github_id=user.id).first()

        if existing:
            db_developer = existing
            print(f"Already exists: {username}")

        else:
            db_developer = Developer(
                github_id=user.id,
                username=user.login,
                name=user.name,
                bio=user.bio,
                created_at=user.created_at,
                language=[]
            )

            session.add(db_developer)
            session.flush()

            print(f"Saved eveloper: {user.login}")

        print("Fetching repositories...")
        repos = user.get_repos()

        languages=set()
        for repo in repos:
            print(repo.full_name,repo.language)

            if repo.language:
                languages.add(repo.language)

        db_developer.language=sorted(languages)

        commits = github.search_commits(query=f"Author: {username}")
        recent_commits = []

        for i,commit in enumerate(commits):

            if i>=10:
                break

            recent_commits.append({
                "repository":commit.repository.full_name,
                "message":commit.commit.message,
                "date":(
                    commit.commit.author.date.isoformat()
                    if commit.commit.author.date
                    else None
                )
            })

        db_developer.recent_commits = recent_commits
        session.commit()

        print(f"Languages: {db_developer.language}")