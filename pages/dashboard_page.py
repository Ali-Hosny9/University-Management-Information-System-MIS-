# pages/dashboard_page.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QPushButton, QHeaderView
)

from database import SessionLocal
from models import Student, Course, Instructor, Faculty


class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()

        self.db = SessionLocal()

        main_layout = QVBoxLayout(self)

        # -------- Top summary counters --------
        counters_layout = QHBoxLayout()

        self.lbl_students = QLabel()
        self.lbl_courses = QLabel()
        self.lbl_instructors = QLabel()

        for lbl in (self.lbl_students, self.lbl_courses, self.lbl_instructors):
            lbl.setStyleSheet("font-size: 18px; font-weight: bold;")

        counters_layout.addWidget(self.lbl_students)
        counters_layout.addWidget(self.lbl_courses)
        counters_layout.addWidget(self.lbl_instructors)
        counters_layout.addStretch()

        btn_refresh = QPushButton("Refresh")
        btn_refresh.clicked.connect(self.load_stats)
        counters_layout.addWidget(btn_refresh)

        main_layout.addLayout(counters_layout)

        # -------- Faculty summary table --------
        title = QLabel("Faculty Summary")
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin-top: 10px;")
        main_layout.addWidget(title)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Faculty",
            "Departments",
            "Students",
            "Courses",
            "Instructors",
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)

        main_layout.addWidget(self.table)

        # Initial load
        self.load_stats()

    def load_stats(self):
        # Top counters
        total_students = self.db.query(Student).count()
        total_courses = self.db.query(Course).count()
        total_instructors = self.db.query(Instructor).count()

        self.lbl_students.setText(f"👥 Students: {total_students}")
        self.lbl_courses.setText(f"📚 Courses: {total_courses}")
        self.lbl_instructors.setText(f"👨‍🏫 Instructors: {total_instructors}")

        # Faculty table
        faculties = self.db.query(Faculty).all()
        self.table.setRowCount(len(faculties))

        for row, fac in enumerate(faculties):
            dept_count = len(fac.departments)
            student_count = sum(len(d.students) for d in fac.departments)
            course_count = sum(len(d.courses) for d in fac.departments)
            instructor_count = sum(len(d.instructors) for d in fac.departments)

            self.table.setItem(row, 0, QTableWidgetItem(fac.name))
            self.table.setItem(row, 1, QTableWidgetItem(str(dept_count)))
            self.table.setItem(row, 2, QTableWidgetItem(str(student_count)))
            self.table.setItem(row, 3, QTableWidgetItem(str(course_count)))
            self.table.setItem(row, 4, QTableWidgetItem(str(instructor_count)))
