from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sentence_transformers import SentenceTransformer

from src.database.models import Issue


DATABASE_URL = (
    "postgresql://recommender:"
    "recommender_password@localhost:5433/"
    "issue_recommender"
)

engine = create_engine(DATABASE_URL)

model = SentenceTransformer("all-MiniLM-L6-v2")


def create_issue_text(issue):
    """
    Combine issue title and body into one text string.
    """

    title = issue.title or ""
    body = issue.body or ""

    return f"{title}\n{body}"


with Session(engine) as session:

    issues = session.query(Issue).all()

    print(f"Found {len(issues)} issues")

    issue_texts = [
        create_issue_text(issue)
        for issue in issues
    ]

    embeddings = model.encode(issue_texts)

    print("\nEmbedding generation complete")

    print(f"Number of embeddings: {len(embeddings)}")

    if len(embeddings) > 0:
        print(
            f"Embedding dimensions: "
            f"{len(embeddings[0])}"
        )

        print("\nFirst issue:")
        print(issue_texts[0][:500])

        print("\nFirst embedding:")
        print(embeddings[0])