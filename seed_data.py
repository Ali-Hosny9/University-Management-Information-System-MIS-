# seed_data.py
from database import SessionLocal
from models import Faculty, Department, User
from sqlalchemy.exc import IntegrityError


def create_initial_data():
    db = SessionLocal()

    try:
        # === Faculties and their departments/majors ===
        faculty_structure = {
            "Faculty of Computers & Information": [
                "Computer Science",
                "Information Systems",
                "Information Technology",
                "Software Engineering",
                "Artificial Intelligence",
            ],
            "Faculty of Engineering": [
                "Civil Engineering",
                "Electrical Engineering",
                "Mechanical Engineering",
                "Architecture",
            ],
            "Faculty of Commerce": [
                "Accounting",
                "Business Administration",
                "Marketing",
                "Finance"
            ],
            "Faculty of Science": [
                "Mathematics",
                "Physics",
                "Chemistry",
                "Biology",
            ],
        }

        # Create faculties and departments if not exist
        for faculty_name, dept_list in faculty_structure.items():
            faculty = db.query(Faculty).filter_by(name=faculty_name).first()
            if not faculty:
                faculty = Faculty(name=faculty_name)
                db.add(faculty)
                db.flush()  # get faculty.id

            for dept_name in dept_list:
                exists = (
                    db.query(Department)
                    .filter_by(name=dept_name, faculty_id=faculty.id)
                    .first()
                )
                if not exists:
                    db.add(Department(name=dept_name, faculty_id=faculty.id))

        # Ensure an admin user exists
        admin = db.query(User).filter_by(username="admin").first()
        if not admin:
            admin_user = User(
                username="admin",
                password_hash="admin",  
                role="admin",
            )
            db.add(admin_user)

        db.commit()
        print("Initial data (faculties, departments, admin user) inserted/updated successfully.")

    except IntegrityError:
        db.rollback()
        print("Error while inserting data (IntegrityError).")
    finally:
        db.close()


if __name__ == "__main__":
    create_initial_data()
