from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView,
    QFileDialog
)
from PyQt5.QtCore import Qt

from sqlalchemy.exc import IntegrityError

import csv

from database import SessionLocal
from models import Student, Department, Faculty


class StudentsPage(QWidget):
    def __init__(self):
        super().__init__()

        self.db = SessionLocal()
        self.selected_student_id = None  # will store ID of selected row

        # === MAIN LAYOUT ===
        main_layout = QHBoxLayout(self)

        # ----------------------------------------
        # LEFT SIDE: Add / Edit Student Form
        # ----------------------------------------
        form_layout = QVBoxLayout()

        title = QLabel("Add / Edit Student")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        form_layout.addWidget(title)

        # University ID
        self.input_univid = QLineEdit()
        self.input_univid.setPlaceholderText("University ID (e.g. 2025-1234)")
        form_layout.addWidget(self.input_univid)

        # Full Name
        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("Full Name")
        form_layout.addWidget(self.input_name)

        # Faculty
        self.input_faculty = QComboBox()
        self.input_faculty.currentIndexChanged.connect(self.on_faculty_changed)
        form_layout.addWidget(self.input_faculty)

        # Department (depends on faculty)
        self.input_dept = QComboBox()
        form_layout.addWidget(self.input_dept)

        # Level
        self.input_level = QComboBox()
        self.input_level.addItems(["1", "2", "3", "4"])
        form_layout.addWidget(self.input_level)

        # Phone
        self.input_phone = QLineEdit()
        self.input_phone.setPlaceholderText("Phone number")
        form_layout.addWidget(self.input_phone)

        # Email
        self.input_email = QLineEdit()
        self.input_email.setPlaceholderText("Email")
        form_layout.addWidget(self.input_email)

        # Buttons: Add / Update / Delete
        buttons_row = QHBoxLayout()

        btn_add = QPushButton("Add")
        btn_add.clicked.connect(self.add_student)
        buttons_row.addWidget(btn_add)

        btn_update = QPushButton("Update Selected")
        btn_update.clicked.connect(self.update_student)
        buttons_row.addWidget(btn_update)

        btn_delete = QPushButton("Delete Selected")
        btn_delete.clicked.connect(self.delete_student)
        buttons_row.addWidget(btn_delete)

        form_layout.addLayout(buttons_row)

        btn_clear = QPushButton("Clear Form")
        btn_clear.clicked.connect(self.clear_form)
        form_layout.addWidget(btn_clear)

        form_layout.addStretch()

        # ----------------------------------------
        # RIGHT SIDE: Search + Students Table + Export
        # ----------------------------------------
        right_layout = QVBoxLayout()

        # Search row
        search_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name or University ID...")
        btn_search = QPushButton("Search")
        btn_search.clicked.connect(self.on_search)
        btn_reset = QPushButton("Reset")
        btn_reset.clicked.connect(self.on_reset_search)

        search_row.addWidget(self.search_input)
        search_row.addWidget(btn_search)
        search_row.addWidget(btn_reset)

        right_layout.addLayout(search_row)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            ["ID", "University ID", "Name", "Faculty", "Dept", "Level", "Phone"]
        )
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.setSelectionBehavior(self.table.SelectRows)
        self.table.setEditTriggers(self.table.NoEditTriggers)
        self.table.cellClicked.connect(self.on_row_clicked)

        right_layout.addWidget(self.table)

        # Export buttons row
        export_row = QHBoxLayout()
        export_row.addStretch()
        btn_export_csv = QPushButton("Export to CSV (Excel)")
        btn_export_csv.clicked.connect(self.export_to_csv)
        export_row.addWidget(btn_export_csv)

        right_layout.addLayout(export_row)

        # Fill combos + table
        self.load_faculties()
        self.load_students()

        # Add to main layout
        main_layout.addLayout(form_layout, 1)
        main_layout.addLayout(right_layout, 3)

    # ========= FACULTIES & DEPARTMENTS ==========

    def load_faculties(self):
        """Fill faculty combo and trigger loading departments for first faculty."""
        self.input_faculty.clear()
        faculties = self.db.query(Faculty).order_by(Faculty.name).all()
        for fac in faculties:
            self.input_faculty.addItem(fac.name, fac.id)

        # trigger dept loading for first faculty
        if self.input_faculty.count() > 0:
            self.on_faculty_changed(0)
        else:
            self.input_dept.clear()

    def on_faculty_changed(self, index):
        faculty_id = self.input_faculty.currentData()
        self.load_departments(faculty_id)

    def load_departments(self, faculty_id: int):
        """Fill department combo for a faculty + 'Not specified yet' option."""
        self.input_dept.clear()

        # Default "please choose"
        self.input_dept.addItem("-- Select Department --", None)

        # Special option: Not specified yet (value = 0)
        self.input_dept.addItem("Not specified yet", 0)

        if faculty_id is None:
            return

        # Actual departments from DB
        departments = (
            self.db.query(Department)
            .filter(Department.faculty_id == faculty_id)
            .order_by(Department.name)
            .all()
        )
        for dep in departments:
            self.input_dept.addItem(dep.name, dep.id)

    # ========= LOAD STUDENTS TABLE ==========

    def load_students(self, search_text: str = ""):
        query = self.db.query(Student)

        if search_text:
            like = f"%{search_text}%"
            query = query.filter(
                (Student.full_name.ilike(like)) |
                (Student.university_id.ilike(like))
            )

        students = query.all()
        self.table.setRowCount(len(students))

        for row, s in enumerate(students):
            faculty_name = s.department.faculty.name if s.department and s.department.faculty else ""
            # Show "Not specified yet" if no department
            dept_name = s.department.name if s.department else "Not specified yet"

            self.table.setItem(row, 0, QTableWidgetItem(str(s.id)))
            self.table.setItem(row, 1, QTableWidgetItem(s.university_id))
            self.table.setItem(row, 2, QTableWidgetItem(s.full_name))
            self.table.setItem(row, 3, QTableWidgetItem(faculty_name))
            self.table.setItem(row, 4, QTableWidgetItem(dept_name))
            self.table.setItem(row, 5, QTableWidgetItem(str(s.level) if s.level is not None else ""))
            self.table.setItem(row, 6, QTableWidgetItem(s.phone or ""))

        self.selected_student_id = None

    # ========= ADD NEW STUDENT ==========

    def add_student(self):
        univid = self.input_univid.text().strip()
        name = self.input_name.text().strip()
        dept_data = self.input_dept.currentData()
        level = int(self.input_level.currentText())
        phone = self.input_phone.text().strip()
        email = self.input_email.text().strip()

        if not univid or not name:
            QMessageBox.warning(self, "Error", "University ID and Name are required.")
            return

        # Require at least some choice: actual dept or "Not specified yet"
        if dept_data is None:
            QMessageBox.warning(self, "Error", "Please select a department (or 'Not specified yet').")
            return

        # If "Not specified yet" chosen → store NULL in DB
        dept_id = None if dept_data == 0 else dept_data

        new_student = Student(
            university_id=univid,
            full_name=name,
            department_id=dept_id,
            level=level,
            phone=phone,
            email=email
        )

        try:
            self.db.add(new_student)
            self.db.commit()
            QMessageBox.information(self, "Success", "Student added successfully.")
            self.clear_form()
            self.load_students()
        except IntegrityError:
            self.db.rollback()
            QMessageBox.warning(self, "Error", "University ID already exists.")

    # ========= WHEN TABLE ROW CLICKED ==========

    def on_row_clicked(self, row, column):
        id_item = self.table.item(row, 0)
        if not id_item:
            return

        student_id = int(id_item.text())
        self.selected_student_id = student_id

        student = self.db.query(Student).get(student_id)
        if not student:
            return

        # Fill form with selected student data
        self.input_univid.setText(student.university_id)
        self.input_name.setText(student.full_name)
        self.input_phone.setText(student.phone or "")
        self.input_email.setText(student.email or "")

        # Faculty & Department combos
        if student.department and student.department.faculty:
            fac = student.department.faculty
            dept = student.department

            idx_fac = self.input_faculty.findData(fac.id)
            if idx_fac >= 0:
                self.input_faculty.setCurrentIndex(idx_fac)  # this reloads departments

            idx_dept = self.input_dept.findData(dept.id)
            if idx_dept >= 0:
                self.input_dept.setCurrentIndex(idx_dept)
        else:
            # No department → set faculty to first & department to "Not specified yet"
            if self.input_faculty.count() > 0:
                self.input_faculty.setCurrentIndex(0)

            idx_not_spec = self.input_dept.findData(0)
            if idx_not_spec >= 0:
                self.input_dept.setCurrentIndex(idx_not_spec)

        # Level
        if student.level:
            idx = self.input_level.findText(str(student.level))
            if idx >= 0:
                self.input_level.setCurrentIndex(idx)

    # ========= UPDATE SELECTED STUDENT ==========

    def update_student(self):
        if not self.selected_student_id:
            QMessageBox.warning(self, "Error", "Please select a student from the table.")
            return

        student = self.db.query(Student).get(self.selected_student_id)
        if not student:
            QMessageBox.warning(self, "Error", "Student not found.")
            return

        univid = self.input_univid.text().strip()
        name = self.input_name.text().strip()
        dept_data = self.input_dept.currentData()
        level = int(self.input_level.currentText())
        phone = self.input_phone.text().strip()
        email = self.input_email.text().strip()

        if not univid or not name:
            QMessageBox.warning(self, "Error", "University ID and Name are required.")
            return

        if dept_data is None:
            QMessageBox.warning(self, "Error", "Please select a department (or 'Not specified yet').")
            return

        dept_id = None if dept_data == 0 else dept_data

        student.university_id = univid
        student.full_name = name
        student.department_id = dept_id
        student.level = level
        student.phone = phone
        student.email = email

        try:
            self.db.commit()
            QMessageBox.information(self, "Success", "Student updated successfully.")
            self.load_students()
        except IntegrityError:
            self.db.rollback()
            QMessageBox.warning(self, "Error", "University ID already exists.")

    # ========= DELETE SELECTED STUDENT ==========

    def delete_student(self):
        if not self.selected_student_id:
            QMessageBox.warning(self, "Error", "Please select a student to delete.")
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this student?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.No:
            return

        student = self.db.query(Student).get(self.selected_student_id)
        if not student:
            QMessageBox.warning(self, "Error", "Student not found.")
            return

        self.db.delete(student)
        self.db.commit()

        QMessageBox.information(self, "Success", "Student deleted.")
        self.clear_form()
        self.load_students()

    # ========= CLEAR FORM ==========

    def clear_form(self):
        self.input_univid.clear()
        self.input_name.clear()
        self.input_phone.clear()
        self.input_email.clear()
        self.selected_student_id = None

        if self.input_faculty.count() > 0:
            self.input_faculty.setCurrentIndex(0)
        if self.input_dept.count() > 0:
            self.input_dept.setCurrentIndex(0)
        self.input_level.setCurrentIndex(0)

    # ========= SEARCH ==========

    def on_search(self):
        text = self.search_input.text().strip()
        self.load_students(text)

    def on_reset_search(self):
        self.search_input.clear()
        self.load_students()

    # ========= EXPORT TO CSV (Excel) ==========

    def export_to_csv(self):
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Students Data",
            "students_export.csv",
            "CSV Files (*.csv)"
        )

        if not path:
            return

        row_count = self.table.rowCount()
        column_count = self.table.columnCount()

        headers = [
            self.table.horizontalHeaderItem(c).text()
            for c in range(column_count)
        ]

        try:
            with open(path, mode="w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(headers)

                for row in range(row_count):
                    row_data = []
                    for col in range(column_count):
                        item = self.table.item(row, col)
                        row_data.append(item.text() if item else "")
                    writer.writerow(row_data)

            QMessageBox.information(
                self,
                "Export Successful",
                f"Students exported successfully to:\n{path}\n\nYou can open it with Excel."
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Failed",
                f"An error occurred while exporting:\n{e}"
            )
