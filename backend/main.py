import os
import fitz

from datetime import datetime

from dotenv import load_dotenv

from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    UploadFile,
    File
)

from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy import text
from sqlalchemy.orm import Session

from pydantic import BaseModel, EmailStr

from backend.database import (
    engine,
    Base,
    SessionLocal
)

from backend.models import (
    Student,
    StudyMaterial,
    QuestionHistory
)

from backend.subject_detector import detect_subject

from backend.performance import calculate_performance

from backend.weak_topic import detect_weak_topics

from backend.recommendation import generate_recommendations

from backend.concept_analysis import detect_weak_concepts

from rag.ai_quiz_generator import generate_ai_mcqs

from rag.rag_pipeline import (
    build_knowledge_base,
    ask_question
)


# ============================================================
# Environment
# ============================================================

load_dotenv()


# ============================================================
# FastAPI Application
# ============================================================

app = FastAPI(
    title="Agentic AI-Powered Personalized Student Assistant"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# Database
# ============================================================

Base.metadata.create_all(
    bind=engine
)


def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# ============================================================
# Student Request Model
# ============================================================

class StudentCreate(BaseModel):

    name: str

    email: EmailStr

    course: str

    semester: int

    academic_goal: str | None = None


# ============================================================
# Quiz Result Model
# ============================================================

class QuizResult(BaseModel):

    topic: str

    question: str | None = None

    correct: bool


# ============================================================
# Home
# ============================================================

@app.get("/")
def home():

    return {
        "message":
        "Agentic AI Student Assistant API is running!"
    }


# ============================================================
# Test Database
# ============================================================

@app.get("/test-db")
def test_database():

    try:

        with engine.connect() as connection:

            connection.execute(
                text("SELECT 1")
            )

        return {
            "status": "success",
            "message":
            "PostgreSQL database connected successfully!"
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }


# ============================================================
# Create Student
# ============================================================

@app.post("/students")
def create_student(
    student: StudentCreate,
    db: Session = Depends(get_db)
):

    existing_student = (
        db.query(Student)
        .filter(
            Student.email == student.email
        )
        .first()
    )

    if existing_student:

        raise HTTPException(
            status_code=400,
            detail=
            "A student with this email already exists."
        )

    new_student = Student(
        name=student.name,
        email=student.email,
        course=student.course,
        semester=student.semester,
        academic_goal=student.academic_goal
    )

    db.add(new_student)

    db.commit()

    db.refresh(new_student)

    return {
        "status": "success",
        "message":
        "Student onboarded successfully!",

        "student": {
            "id": new_student.id,
            "name": new_student.name,
            "email": new_student.email,
            "course": new_student.course,
            "semester": new_student.semester,
            "academic_goal":
            new_student.academic_goal
        }
    }


# ============================================================
# Get All Students
# ============================================================

@app.get("/students")
def get_students(
    db: Session = Depends(get_db)
):

    students = db.query(Student).all()

    return {
        "count": len(students),
        "students": students
    }


# ============================================================
# Upload Study Material
# ============================================================

@app.post("/upload-material")
async def upload_material(
    file: UploadFile = File(...)
):

    # --------------------------------------------------------
    # Check file type
    # --------------------------------------------------------

    if not file.filename.lower().endswith(".pdf"):

        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    # --------------------------------------------------------
    # Create uploads folder
    # --------------------------------------------------------

    os.makedirs(
        "uploads",
        exist_ok=True
    )

    # --------------------------------------------------------
    # Save uploaded PDF
    # --------------------------------------------------------

    file_path = os.path.join(
        "uploads",
        file.filename
    )

    file_content = await file.read()

    with open(
        file_path,
        "wb"
    ) as buffer:

        buffer.write(file_content)

    # --------------------------------------------------------
    # Extract text from PDF
    # --------------------------------------------------------

    document = fitz.open(
        file_path
    )

    extracted_text = ""

    for page in document:

        extracted_text += (
            page.get_text()
            + "\n"
        )

    pages = len(document)

    document.close()

    # --------------------------------------------------------
    # Check readable text
    # --------------------------------------------------------

    if not extracted_text.strip():

        raise HTTPException(
            status_code=400,
            detail=
            "The uploaded PDF contains no readable text."
        )

    # --------------------------------------------------------
    # Detect subject using AI
    # --------------------------------------------------------

    subject = detect_subject(
        extracted_text
    )

    # --------------------------------------------------------
    # Connect to PostgreSQL
    # --------------------------------------------------------

    db = SessionLocal()

    try:

        # ----------------------------------------------------
        # Check duplicate material
        # ----------------------------------------------------

        existing_material = (
            db.query(StudyMaterial)
            .filter(
                StudyMaterial.filename
                == file.filename
            )
            .first()
        )

        # ----------------------------------------------------
        # Update existing material
        # ----------------------------------------------------

        if existing_material:

            existing_material.subject = subject

            existing_material.path = file_path

            existing_material.pages = pages

            db.commit()

            db.refresh(
                existing_material
            )

            return {
                "status": "success",

                "message":
                "Study material already exists. "
                "Existing record updated.",

                "filename":
                existing_material.filename,

                "subject":
                existing_material.subject,

                "pages":
                existing_material.pages,

                "text_length":
                len(extracted_text),

                "text_preview":
                extracted_text[:500]
            }

        # ----------------------------------------------------
        # Create new material
        # ----------------------------------------------------

        new_material = StudyMaterial(
            filename=file.filename,
            subject=subject,
            path=file_path,
            pages=pages
        )

        db.add(
            new_material
        )

        db.commit()

        db.refresh(
            new_material
        )

        return {
            "status": "success",

            "message":
            "Study material uploaded successfully!",

            "filename":
            new_material.filename,

            "subject":
            new_material.subject,

            "pages":
            new_material.pages,

            "text_length":
            len(extracted_text),

            "text_preview":
            extracted_text[:500]
        }

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:

        db.close()


# ============================================================
# Get Study Materials
# ============================================================

@app.get("/study-materials")
def get_study_materials(
    db: Session = Depends(get_db)
):

    materials = (
        db.query(StudyMaterial)
        .all()
    )

    return {
        "status": "success",

        "materials": [

            {
                "id": material.id,

                "filename":
                material.filename,

                "subject":
                material.subject,

                "path":
                material.path,

                "pages":
                material.pages
            }

            for material in materials
        ]
    }


# ============================================================
# Ask AI using RAG
# ============================================================

@app.post("/ask-ai")
def ask_ai(
    question: str,
    material: str,
    db: Session = Depends(get_db)
):

    try:

        # ----------------------------------------------------
        # Build RAG knowledge base
        # ----------------------------------------------------

        store = build_knowledge_base(
            material
        )

        # ----------------------------------------------------
        # Ask question
        # ----------------------------------------------------

        result = ask_question(
            store,
            question
        )

        answer = result["answer"]

        # ----------------------------------------------------
        # SAVE QUESTION HISTORY
        # ----------------------------------------------------

        history = QuestionHistory(

            question=question,

            answer=answer,

            material=material,

            created_at=
            datetime.now().isoformat()
        )

        db.add(
            history
        )

        db.commit()

        db.refresh(
            history
        )

        # ----------------------------------------------------
        # Return response
        # ----------------------------------------------------

        return {

            "status": "success",

            "material": material,

            "question":
            result["question"],

            "answer":
            answer,

            "sources":
            result["sources"],

            "history_id":
            history.id
        }

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================================
# Get Previous Question History
# ============================================================

@app.get("/question-history")
def get_question_history(
    db: Session = Depends(get_db)
):

    history = (
        db.query(QuestionHistory)
        .order_by(
            QuestionHistory.id.desc()
        )
        .all()
    )

    return {

        "status": "success",

        "history": [

            {
                "id":
                item.id,

                "question":
                item.question,

                "answer":
                item.answer,

                "material":
                item.material,

                "created_at":
                item.created_at
            }

            for item in history
        ]
    }


# ============================================================
# Generate AI Quiz
# ============================================================

@app.post("/generate-quiz")
def generate_quiz(
    material: str,
    db: Session = Depends(get_db)
):

    try:

        # ----------------------------------------------------
        # Find selected material
        # ----------------------------------------------------

        selected_material = (
            db.query(StudyMaterial)
            .filter(
                StudyMaterial.filename
                == material
            )
            .first()
        )

        if selected_material is None:

            raise HTTPException(
                status_code=404,
                detail=
                "Selected study material was not found."
            )

        # ----------------------------------------------------
        # Get PDF path
        # ----------------------------------------------------

        file_path = (
            selected_material.path
        )

        # ----------------------------------------------------
        # Check PDF
        # ----------------------------------------------------

        if not os.path.exists(
            file_path
        ):

            raise HTTPException(
                status_code=404,
                detail=
                "Selected study material PDF not found."
            )

        # ----------------------------------------------------
        # Extract text
        # ----------------------------------------------------

        document = fitz.open(
            file_path
        )

        all_text = ""

        for page in document:

            all_text += (
                page.get_text()
                + "\n"
            )

        document.close()

        if not all_text.strip():

            raise HTTPException(
                status_code=400,
                detail=
                "Selected PDF contains no readable text."
            )

        # ----------------------------------------------------
        # Generate AI questions
        # ----------------------------------------------------

        questions = generate_ai_mcqs(
            all_text,
            number_of_questions=5
        )

        # ----------------------------------------------------
        # Get subject
        # ----------------------------------------------------

        subject = (
            selected_material.subject
        )

        # ----------------------------------------------------
        # Add subject to questions
        # ----------------------------------------------------

        for question in questions:

            question["topic"] = subject

        return {

            "status": "success",

            "material": material,

            "subject": subject,

            "questions": questions
        }

    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================================
# Analyze Quiz Performance
# ============================================================

@app.post("/analyze-performance")
def analyze_performance(
    results: list[QuizResult]
):

    # --------------------------------------------------------
    # Convert Pydantic objects
    # --------------------------------------------------------

    result_data = [

        {
            "topic":
            result.topic,

            "question":
            result.question,

            "correct":
            result.correct
        }

        for result in results
    ]

    # --------------------------------------------------------
    # Calculate performance
    # --------------------------------------------------------

    performance = calculate_performance(
        result_data
    )

    # --------------------------------------------------------
    # Detect weak topics
    # --------------------------------------------------------

    weak_topics = detect_weak_topics(
        performance[
            "topic_performance"
        ]
    )

    # --------------------------------------------------------
    # Generate recommendations
    # --------------------------------------------------------

    recommendations = (
        generate_recommendations(
            weak_topics
        )
    )

    # --------------------------------------------------------
    # Detect weak concepts
    # --------------------------------------------------------

    weak_concepts = (
        detect_weak_concepts(
            result_data
        )
    )

    print(
        "WEAK CONCEPTS:",
        weak_concepts
    )

    return {

        "status": "success",

        "performance":
        performance,

        "weak_topics":
        weak_topics,

        "recommendations":
        recommendations,

        "weak_concepts":
        weak_concepts
    }