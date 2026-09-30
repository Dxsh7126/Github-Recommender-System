from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    Boolean,
    String,
    Text,
    DateTime,
    ForeignKey,
    JSON
)

from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


class Developer(Base):
    __tablename__ = "developers"

    id = Column(Integer, primary_key=True)
    github_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String(255), unique=True, nullable=False)
    name = Column(String(255))
    bio = Column(Text)
    created_at = Column(DateTime)

    repositories = relationship(
        "Repository",
        back_populates="developer"
    )


class Repository(Base):
    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True)
    github_id = Column(BigInteger, unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    full_name = Column(String(255), unique=True, nullable=False)
    description = Column(Text)
    url = Column(String(500))
    issues_collected = Column(Boolean,default=False,nullable=False)
    language = Column(String(100))
    stars = Column(Integer, default=0)
    forks = Column(Integer, default=0)
    topics = Column(JSON)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    developer_id = Column(
        Integer,
        ForeignKey("developers.id")
    )

    developer = relationship(
        "Developer",
        back_populates="repositories"
    )

    issues = relationship(
        "Issue",
        back_populates="repository"
    )


class Issue(Base):
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True)
    github_id = Column(BigInteger, unique=True, nullable=False)

    repository_id = Column(
        Integer,
        ForeignKey("repositories.id"),
        nullable=False
    )

    title = Column(String(500), nullable=False)
    body = Column(Text)
    labels = Column(JSON)
    comments = Column(Integer, default=0)

    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    repository = relationship(
        "Repository",
        back_populates="issues"
    )