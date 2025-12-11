# pages/enrollments_page.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView,
    QFileDialog
)
from PyQt5.QtCore import Qt
from sqlalchemy.exc import IntegrityError
import csv

from database import SessionLocal
from models import Enrollment, Student, Course, Faculty, Department


class EnrollmentsPage(QWidget):
    def __init__(self):
        super().__init__()

        self.db = SessionLocal()
        self.selected_enrollment_id = None
        self.current_student_id = None

        main_layout = QHBoxLayout(self)

        # ====================================
        # LEFT SIDE (FORM)
        # ====================================
        form_layout = QVBoxLayout()

        title = QLabel("Enroll Student in Course")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        form_layout.addWidget(title)

        # -------- 1) STUDENT CODE AT THE TOP --------
        student_search_row = QHBoxLayout()
        self.input_student_code = QLineEdit()
        self.input_student_code.setPlaceholderText("Enter Student ID / Code")
        student_search_row.addWidget(self.input_student_code)

        self.btn_search_student = QPushButton("Find Student")
        self.btn_search_student.clicked.connect(self.search_student_by_code)
        student_search_row.addWidget(self.btn_search_student)

        form_layout.addLayout(student_search_row)

        self.label_student_info = QLabel("Student: (not selected)")
        self.label_student_info.setStyleSheet("color: #555;")
        form_layout.addWidget(self.label_student_info)

        # -------- CONTAINER FOR THE REST (INITIALLY DISABLED) --------
        self.details_container = QWidget()
        details_layout = QVBoxLayout(self.details_container)

        # Faculty
        faculty_row = QHBoxLayout()
        faculty_row.addWidget(QLabel("Faculty:"))
        self.input_faculty = QComboBox()
        self.input_faculty.currentIndexChanged.connect(self.on_faculty_changed)
        faculty_row.addWidget(self.input_faculty)
        details_layout.addLayout(faculty_row)

        # Department
        dept_row = QHBoxLayout()
        dept_row.addWidget(QLabel("Department:"))
        self.input_department = QComboBox()
        self.input_department.currentIndexChanged.connect(self.on_department_changed)
        dept_row.addWidget(self.input_department)
        details_layout.addLayout(dept_row)

        # Course
        course_row = QHBoxLayout()
        course_row.addWidget(QLabel("Course:"))
        self.input_course = QComboBox()
        course_row.addWidget(self.input_course)
        details_layout.addLayout(course_row)

        # Academic year
        year_row = QHBoxLayout()
        year_row.addWidget(QLabel("Academic Year:"))
        self.input_academic_year = QLineEdit()
        self.input_academic_year.setPlaceholderText("e.g. 2025/2026")
        year_row.addWidget(self.input_academic_year)
        details_layout.addLayout(year_row)

        # Level / term (example: 1,2,3,4)
        level_row = QHBoxLayout()
        level_row.addWidget(QLabel("Level:"))
        self.input_level = QLineEdit()
        self.input_level.setPlaceholderText("e.g. 1")
        level_row.addWidget(self.input_level)
        details_layout.addLayout(level_row)

        # Status (Completed / In Progress / etc.)
        status_row = QHBoxLayout()
        status_row.addWidget(QLabel("Status:"))
        self.input_status = QComboBox()
        self.input_status.addItems(["", "Completed", "In Progress", "Failed"])
        status_row.addWidget(self.input_status)
        details_layout.addLayout(status_row)

        # Buttons: Add / Update / Delete
        buttons_row = QHBoxLayout()
        self.btn_add = QPushButton("Add")
        self.btn_add.clicked.connect(self.create_enrollment)
        buttons_row.addWidget(self.btn_add)

        self.btn_update = QPushButton("Update Selected")
        self.btn_update.clicked.connect(self.update_enrollment)
        buttons_row.addWidget(self.btn_update)

        self.btn_delete = QPushButton("Delete Selected")
        self.btn_delete.clicked.connect(self.delete_enrollment)
        buttons_row.addWidget(self.btn_delete)

        details_layout.addLayout(buttons_row)

        # Clear + Export
        bottom_buttons_row = QHBoxLayout()
        self.btn_clear = QPushButton("Clear Form")
        self.btn_clear.clicked.connect(self.clear_form)
        bottom_buttons_row.addWidget(self.btn_clear)

        self.btn_export = QPushButton("Export to CSV")
        self.btn_export.clicked.connect(self.export_csv)
        bottom_buttons_row.addWidget(self.btn_export)

        details_layout.addLayout(bottom_buttons_row)

        form_layout.addWidget(self.details_container)
        form_layout.addStretch()
        main_layout.addLayout(form_layout, 2)

        # ====================================
        # RIGHT SIDE (TABLE)
        # ====================================
        right_layout = QVBoxLayout()

        table_title = QLabel("Student Enrollments")
        table_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        right_layout.addWidget(table_title)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Course", "Faculty", "Department",
            "Academic Year", "Level", "Status"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.cellClicked.connect(self.on_table_row_clicked)

        right_layout.addWidget(self.table)
        main_layout.addLayout(right_layout, 3)

        # ===== INITIAL STATE =====
        self.load_faculties()
        self.set_details_enabled(False)   # 🔒 lock all combos/buttons/table at start

    # ---------------------------------------------------------
    # Helpers to enable/disable the lower part
    # ---------------------------------------------------------
    def set_details_enabled(self, enabled: bool):
        """Enable/disable all widgets except student code + Find button."""
        self.details_container.setEnabled(enabled)
        self.table.setEnabled(enabled)

    # ---------------------------------------------------------
    # Load / cascade combos
    # ---------------------------------------------------------
    def load_faculties(self):
        self.input_faculty.clear()
        self.input_faculty.addItem("-- Select Faculty --", None)
        faculties = self.db.query(Faculty).order_by(Faculty.name).all()
        for fac in faculties:
            self.input_faculty.addItem(fac.name, fac.id)

        self.input_department.clear()
        self.input_department.addItem("-- Select Department --", None)
        self.input_course.clear()
        self.input_course.addItem("-- Select Course --", None)

    def on_faculty_changed(self, index: int):
        faculty_id = self.input_faculty.itemData(index)
        self.input_department.clear()
        self.input_department.addItem("-- Select Department --", None)
        self.input_course.clear()
        self.input_course.addItem("-- Select Course --", None)

        if not faculty_id:
            return

        departments = (
            self.db.query(Department)
            .filter(Department.faculty_id == faculty_id)
            .order_by(Department.name)
            .all()
        )
        for dep in departments:
            self.input_department.addItem(dep.name, dep.id)

    def on_department_changed(self, index: int):
        dep_id = self.input_department.itemData(index)
        self.input_course.clear()
        self.input_course.addItem("-- Select Course --", None)

        if not dep_id:
            return

        courses = (
            self.db.query(Course)
            .filter(Course.department_id == dep_id)
            .order_by(Course.name)
            .all()
        )
        for c in courses:
            self.input_course.addItem(c.name, c.id)

    # ---------------------------------------------------------
    # Student search
    # ---------------------------------------------------------
    def search_student_by_code(self):
        code = self.input_student_code.text().strip()
        if not code:
            QMessageBox.warning(self, "Error", "Please enter a student ID/code.")
            return

        try:
            # 🔧 Use correct field name: university_id (NOT Student.code)
            student = (
                self.db.query(Student)
                .filter(Student.university_id == code)
                .first()
            )
        except Exception as e:
            # If something really weird happens, show it instead of crashing
            QMessageBox.critical(self, "Error", f"Failed to search student:\n{e}")
            self.current_student_id = None
            self.set_details_enabled(False)
            self.clear_table()
            return

        if not student:
            self.current_student_id = None
            self.label_student_info.setText("Student: not found")
            self.set_details_enabled(False)
            self.clear_table()
            QMessageBox.warning(self, "Not found", "No student with this ID/code.")
            return

        self.current_student_id = student.id
        name = getattr(student, "full_name", None) or getattr(student, "name", "")
        info_text = f"Student: {name} (ID: {student.id})"

        # ------------------------------------------
        # Handle department / faculty if specified
        # ------------------------------------------
        dept = getattr(student, "department", None)
        fac = getattr(dept, "faculty", None) if dept else None

        if dept and fac:
            # Pre-select faculty and department
            idx_fac = self.input_faculty.findData(fac.id)
            if idx_fac >= 0:
                self.input_faculty.setCurrentIndex(idx_fac)

            idx_dep = self.input_department.findData(dept.id)
            if idx_dep >= 0:
                self.input_department.setCurrentIndex(idx_dep)
        else:
            # Student has no department ("Not specified yet" in StudentsPage logic)
            # Reset combos to default and add note in label
            if self.input_faculty.count() > 0:
                self.input_faculty.setCurrentIndex(0)
            if self.input_department.count() > 0:
                self.input_department.setCurrentIndex(0)

            info_text += " - Department not specified yet"

        self.label_student_info.setText(info_text)

        # ✅ Unlock rest of form & load his enrollments
        self.set_details_enabled(True)
        self.load_enrollments_for_student(student.id)

    # ---------------------------------------------------------
    # Table loading
    # ---------------------------------------------------------
    def clear_table(self):
        self.table.setRowCount(0)

    def load_enrollments_for_student(self, student_id: int):
        self.clear_table()
        enrollments = (
            self.db.query(Enrollment)
            .filter(Enrollment.student_id == student_id)
            .all()
        )

        for row, enr in enumerate(enrollments):
            self.table.insertRow(row)

            course = getattr(enr, "course", None)
            department = getattr(course, "department", None) if course else None
            faculty = getattr(department, "faculty", None) if department else None

            course_name = getattr(course, "name", "") if course else ""
            dep_name = getattr(department, "name", "") if department else ""
            fac_name = getattr(faculty, "name", "") if faculty else ""

            academic_year = getattr(enr, "academic_year", "")
            level = getattr(enr, "level", "")
            status = getattr(enr, "status", "")

            self.table.setItem(row, 0, QTableWidgetItem(str(enr.id)))
            self.table.setItem(row, 1, QTableWidgetItem(course_name))
            self.table.setItem(row, 2, QTableWidgetItem(fac_name))
            self.table.setItem(row, 3, QTableWidgetItem(dep_name))
            self.table.setItem(row, 4, QTableWidgetItem(str(academic_year)))
            self.table.setItem(row, 5, QTableWidgetItem(str(level)))
            self.table.setItem(row, 6, QTableWidgetItem(str(status)))

    # ---------------------------------------------------------
    # CRUD operations
    # ---------------------------------------------------------
    def create_enrollment(self):
        if self.current_student_id is None:
            QMessageBox.warning(self, "Error", "First select a student.")
            return

        course_id = self.input_course.currentData()
        if course_id is None:
            QMessageBox.warning(self, "Error", "Please select a course.")
            return

        academic_year = self.input_academic_year.text().strip()
        level = self.input_level.text().strip()
        status = self.input_status.currentText().strip()

        try:
            enr = Enrollment(
                student_id=self.current_student_id,
                course_id=course_id
            )
            if hasattr(Enrollment, "academic_year"):
                enr.academic_year = academic_year
            if hasattr(Enrollment, "level"):
                enr.level = level
            if hasattr(Enrollment, "status"):
                enr.status = status

            self.db.add(enr)
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            QMessageBox.warning(self, "Error", "This enrollment already exists.")
            return
        except Exception as e:
            self.db.rollback()
            QMessageBox.critical(self, "Error", str(e))
            return

        self.load_enrollments_for_student(self.current_student_id)
        QMessageBox.information(self, "Done", "Enrollment added.")

    def update_enrollment(self):
        if self.selected_enrollment_id is None:
            QMessageBox.warning(self, "Error", "Select a row from the table first.")
            return

        course_id = self.input_course.currentData()
        if course_id is None:
            QMessageBox.warning(self, "Error", "Please select a course.")
            return

        academic_year = self.input_academic_year.text().strip()
        level = self.input_level.text().strip()
        status = self.input_status.currentText().strip()

        enr = (
            self.db.query(Enrollment)
            .filter(Enrollment.id == self.selected_enrollment_id)
            .first()
        )
        if not enr:
            QMessageBox.warning(self, "Error", "Enrollment not found.")
            return

        enr.course_id = course_id
        if hasattr(enr, "academic_year"):
            enr.academic_year = academic_year
        if hasattr(enr, "level"):
            enr.level = level
        if hasattr(enr, "status"):
            enr.status = status

        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            QMessageBox.warning(self, "Error", "Duplicate enrollment.")
            return
        except Exception as e:
            self.db.rollback()
            QMessageBox.critical(self, "Error", str(e))
            return

        self.load_enrollments_for_student(self.current_student_id)
        QMessageBox.information(self, "Done", "Enrollment updated.")

    def delete_enrollment(self):
        if self.selected_enrollment_id is None:
            QMessageBox.warning(self, "Error", "Select a row from the table first.")
            return

        confirm = QMessageBox.question(
            self, "Confirm", "Delete selected enrollment?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm != QMessageBox.Yes:
            return

        enr = (
            self.db.query(Enrollment)
            .filter(Enrollment.id == self.selected_enrollment_id)
            .first()
        )
        if not enr:
            QMessageBox.warning(self, "Error", "Enrollment not found.")
            return

        self.db.delete(enr)
        self.db.commit()

        self.selected_enrollment_id = None
        if self.current_student_id:
            self.load_enrollments_for_student(self.current_student_id)
        QMessageBox.information(self, "Done", "Enrollment deleted.")

    # ---------------------------------------------------------
    # Other helpers
    # ---------------------------------------------------------
    def on_table_row_clicked(self, row, col):
        """Fill form when a row is clicked."""
        enr_id_item = self.table.item(row, 0)
        if not enr_id_item:
            return

        self.selected_enrollment_id = int(enr_id_item.text())
        enr = (
            self.db.query(Enrollment)
            .filter(Enrollment.id == self.selected_enrollment_id)
            .first()
        )
        if not enr:
            return

        # Select course / faculty / department in combos
        course = getattr(enr, "course", None)
        dep = getattr(course, "department", None) if course else None
        fac = getattr(dep, "faculty", None) if dep else None

        if fac:
            idx = self.input_faculty.findData(fac.id)
            if idx >= 0:
                self.input_faculty.setCurrentIndex(idx)
        if dep:
            idx = self.input_department.findData(dep.id)
            if idx >= 0:
                self.input_department.setCurrentIndex(idx)
        if course:
            idx = self.input_course.findData(course.id)
            if idx >= 0:
                self.input_course.setCurrentIndex(idx)

        if hasattr(enr, "academic_year"):
            self.input_academic_year.setText(str(getattr(enr, "academic_year", "")))
        if hasattr(enr, "level"):
            self.input_level.setText(str(getattr(enr, "level", "")))
        if hasattr(enr, "status"):
            status = getattr(enr, "status", "")
            idx = self.input_status.findText(status)
            if idx >= 0:
                self.input_status.setCurrentIndex(idx)

    def clear_form(self):
        self.selected_enrollment_id = None
        self.input_academic_year.clear()
        self.input_level.clear()
        self.input_status.setCurrentIndex(0)
        # We don't clear student code so the form stays unlocked

    def export_csv(self):
        if self.table.rowCount() == 0:
            QMessageBox.information(self, "Info", "No enrollments to export.")
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "Save CSV", "enrollments.csv", "CSV Files (*.csv)"
        )
        if not path:
            return

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            headers = [self.table.horizontalHeaderItem(i).text()
                       for i in range(self.table.columnCount())]
            writer.writerow(headers)

            for row in range(self.table.rowCount()):
                row_data = []
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    row_data.append(item.text() if item else "")
                writer.writerow(row_data)

        QMessageBox.information(self, "Done", "CSV exported successfully.")
