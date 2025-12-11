# models.py
from datetime import date

from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    ForeignKey
)
from sqlalchemy.orm import relationship

from database import Base, engine


# ---------- USER (for login) ----------

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)  # later we'll hash passwords
    role = Column(String, nullable=False, default="staff")  # admin / staff / readonly


# ---------- FACULTY ----------

class Faculty(Base):
    __tablename__ = "faculties"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    # one faculty has many departments
    departments = relationship("Department", back_populates="faculty")


# ---------- DEPARTMENT (major inside a faculty) ----------

class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    faculty_id = Column(Integer, ForeignKey("faculties.id"), nullable=False)
    faculty = relationship("Faculty", back_populates="departments")

    # relationships
    students = relationship("Student", back_populates="department")
    courses = relationship("Course", back_populates="department")
    instructors = relationship("Instructor", back_populates="department")


# ---------- STUDENT ----------

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    university_id = Column(String, unique=True, nullable=False)   # e.g. 2025-12345
    full_name = Column(String, nullable=False)
    gender = Column(String)
    date_of_birth = Column(Date, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    level = Column(Integer, nullable=True)      # 1, 2, 3, 4
    status = Column(String, default="active")   # active / graduated / suspended

    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)

    # relationships
    department = relationship("Department", back_populates="students")
    enrollments = relationship("Enrollment", back_populates="student")


# ---------- INSTRUCTOR ----------

class Instructor(Base):
    __tablename__ = "instructors"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    rank = Column(String, nullable=True)        # Assistant, Lecturer, etc.

    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    department = relationship("Department", back_populates="instructors")


# ---------- COURSE ----------

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, nullable=False)   # e.g. CS101
    name = Column(String, nullable=False)
    credits = Column(Integer, nullable=True)
    semester = Column(Integer, nullable=True)            # 1 or 2

    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    instructor_id = Column(Integer, ForeignKey("instructors.id"), nullable=True)

    # relationships
    department = relationship("Department", back_populates="courses")
    enrollments = relationship("Enrollment", back_populates="course")
    # instructor simple link (no back_populates for now)


# ---------- ENROLLMENT (Student-Course registration) ----------

class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    academic_year = Column(String, nullable=True)   # e.g. "2024/2025"
    semester = Column(Integer, nullable=True)       # 1 or 2
    status = Column(String, default="Enrolled")     # Enrolled / Withdrawn / Completed

    # relationships
    student = relationship("Student", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")


# ---------- CREATE TABLES IN DB WHEN RUN DIRECTLY ----------

if __name__ == "__main__":
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Done.")
