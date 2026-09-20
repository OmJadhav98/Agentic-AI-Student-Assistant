from sqlalchemy import Column, Integer, String, Text

from backend.database import Base


# -----------------------------
# Student Model
# -----------------------------
class Student(Base):
    __tablename__ = "students"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(100),
        nullable=False
    )

    email = Column(
        String(150),
        unique=True,
        nullable=False,
        index=True
    )

    course = Column(
        String(100),
        nullable=False
    )

    semester = Column(
        Integer,
        nullable=False
    )

    academic_goal = Column(
        Text,
        nullable=True
    )


# -----------------------------
# Study Material Model
# -----------------------------
class StudyMaterial(Base):
    __tablename__ = "study_materials"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    filename = Column(
        String(255),
        nullable=False
    )

    subject = Column(
        String(150),
        nullable=False
    )

    path = Column(
        String(500),
        nullable=False
    )

    pages = Column(
        Integer,
        nullable=False
    )

# -----------------------------
# Question History Model
# -----------------------------
class QuestionHistory(Base):
    __tablename__ = "question_history"

    id = Column(Integer, primary_key=True, index=True)

    question = Column(Text, nullable=False)

    answer = Column(Text, nullable=False)

    material = Column(String, nullable=True)

    created_at = Column(
        String,
        nullable=False
    )