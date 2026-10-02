import os
from dotenv import load_dotenv
from github import Github
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sentence_transformers import SentenceTransformer

from src.database.models import Issue, Developer, Repository

load_dotenv()
github = Github(os.getenv("GITHUB_TOKEN"))


DATABASE_URL = (
    "postgresql://recommender:"
    "recommender_password@localhost:5433/"
    "issue_recommender"
)

engine = create_engine(DATABASE_URL)

model = SentenceTransformer("all-MiniLM-L6-v2")

def create_developer_text(dev):
    """
    Combine developer details and their repo details into one text string
    """

    developer_name = dev.username
    dev_languages = dev.language

    developer_text = (
        f"Developer: {developer_name}\n"
        f"Languages: {dev_languages}\n"
    )

    github_user = github.get_user(developer_name)

    repositories = github_user.get_repos(
        type="owner",
        sort="updated"
    )

    for repository in list(repositories)[:5]:
        dev_repo=repository.name
        dev_repo_desc=repository.description
        dev_repo_languages=repository.language
        dev_topics=repository.get_topics()

        repo_text = (
            f"Repository: {dev_repo}\n"
            f"Description: {dev_repo_desc or ''}\n"
            f"Language: {dev_repo_languages}\n"
            f"Topics: {dev_topics}\n"
        )
        try:
            readme = repository.get_readme()

            readme_text = (
                readme.decoded_content
                .decode("utf-8")
            )

            readme_text = readme_text[:5000]

            repo_text += f"\nREADME:\n{readme_text}"

        except Exception as e:
            print(
                f"Could not get README for "
                f"{repository.full_name}: {e}"
            ) 
        developer_text += f"\n\n{repo_text}"
    return developer_text

with Session(engine) as session:

    developers = session.query(Developer).all()

    print(f"Found {len(developers)} developers")

    developer_texts = [create_developer_text(dev) for dev in developers]

    embeddings = model.encode(developer_texts)
    print("\nEmbedding generation complete")
    print(f"Number of embeddings: {len(embeddings)}")

    if len(embeddings) > 0:
        print(f"Embedding dimenstions: {(len(embeddings[0]))}")

        print("\nFirst developer:")
        print(developer_texts[0][:500])

        print("\nFirst embedding:")
        print(embeddings[0])

    # for dev in developers:

    #     print("\n"+"="*60)
    #     print(f"Developer: {dev.username}")

    #     developer_text = create_developer_text(dev)

    #     print(
    #         f"Profile text length: "
    #         f"{len(developer_text)} characters"
    #     )

    #     print("\nPreview:")
    #     print(developer_text[:2000])