# pages/courses_page.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView,
    QFileDialog
)

from sqlalchemy.exc import IntegrityError
import csv

from database import SessionLocal
from models import Course, Department


class CoursesPage(QWidget):
    def __init__(self):
        super().__init__()

        self.db = SessionLocal()
        self.selected_course_id = None

        main_layout = QHBoxLayout(self)

        # ================= LEFT: ADD / EDIT FORM =================
        form_layout = QVBoxLayout()

        title = QLabel("Add / Edit Course")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        form_layout.addWidget(title)

        # Course code
        self.input_code = QLineEdit()
        self.input_code.setPlaceholderText("Course Code (e.g. CS101)")
        form_layout.addWidget(self.input_code)

        # Course name
        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("Course Name")
        form_layout.addWidget(self.input_name)

        # Department
        self.input_dept = QComboBox()
        self.load_departments()
        form_layout.addWidget(self.input_dept)

        # Credits
        self.input_credits = QLineEdit()
        self.input_credits.setPlaceholderText("Credits / Hours (e.g. 3)")
        form_layout.addWidget(self.input_credits)

        # Semester
        self.input_semester = QComboBox()
        self.input_semester.addItems(["1", "2"])
        form_layout.addWidget(self.input_semester)

        # Buttons row
        buttons_row = QHBoxLayout()

        btn_add = QPushButton("Add")
        btn_add.clicked.connect(self.add_course)
        buttons_row.addWidget(btn_add)

        btn_update = QPushButton("Update Selected")
        btn_update.clicked.connect(self.update_course)
        buttons_row.addWidget(btn_update)

        btn_delete = QPushButton("Delete Selected")
        btn_delete.clicked.connect(self.delete_course)
        buttons_row.addWidget(btn_delete)

        form_layout.addLayout(buttons_row)

        btn_clear = QPushButton("Clear Form")
        btn_clear.clicked.connect(self.clear_form)
        form_layout.addWidget(btn_clear)

        form_layout.addStretch()

        # ================= RIGHT: SEARCH + TABLE + EXPORT =================
        right_layout = QVBoxLayout()

        # Search row
        search_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by code or name...")
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
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Code", "Name", "Dept", "Credits", "Semester"]
        )
        self.table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.Stretch
        )  # stretch Name column
        self.table.setSelectionBehavior(self.table.SelectRows)
        self.table.setEditTriggers(self.table.NoEditTriggers)
        self.table.cellClicked.connect(self.on_row_clicked)

        right_layout.addWidget(self.table)

        # Export row
        export_row = QHBoxLayout()
        export_row.addStretch()
        btn_export = QPushButton("Export to CSV (Excel)")
        btn_export.clicked.connect(self.export_to_csv)
        export_row.addWidget(btn_export)

        right_layout.addLayout(export_row)

        # Load data
        self.load_courses()

        # Add to main layout
        main_layout.addLayout(form_layout, 1)
        main_layout.addLayout(right_layout, 3)

    # ---------- Helpers ----------

    def load_departments(self):
        self.input_dept.clear()
        departments = self.db.query(Department).all()
        for dept in departments:
            faculty_name = dept.faculty.name if dept.faculty else "Unknown Faculty"
            display_name = f"{faculty_name} - {dept.name}"
            self.input_dept.addItem(display_name, dept.id)


    def load_courses(self, search_text: str = ""):
        query = self.db.query(Course)

        if search_text:
            like = f"%{search_text}%"
            query = query.filter(
                (Course.code.ilike(like)) |
                (Course.name.ilike(like))
            )

        courses = query.all()
        self.table.setRowCount(len(courses))

        for row, c in enumerate(courses):
            self.table.setItem(row, 0, QTableWidgetItem(str(c.id)))
            self.table.setItem(row, 1, QTableWidgetItem(c.code))
            self.table.setItem(row, 2, QTableWidgetItem(c.name))
            self.table.setItem(row, 3, QTableWidgetItem(c.department.name if c.department else ""))
            self.table.setItem(row, 4, QTableWidgetItem(str(c.credits) if c.credits is not None else ""))
            self.table.setItem(row, 5, QTableWidgetItem(str(c.semester) if c.semester is not None else ""))

        self.selected_course_id = None

    # ---------- CRUD ----------

    def add_course(self):
        code = self.input_code.text().strip()
        name = self.input_name.text().strip()
        dept_id = self.input_dept.currentData()
        credits_text = self.input_credits.text().strip()
        semester = int(self.input_semester.currentText())

        if not code or not name:
            QMessageBox.warning(self, "Error", "Course code and name are required.")
            return

        try:
            credits = int(credits_text) if credits_text else None
        except ValueError:
            QMessageBox.warning(self, "Error", "Credits must be a number.")
            return

        new_course = Course(
            code=code,
            name=name,
            department_id=dept_id,
            credits=credits,
            semester=semester
        )

        try:
            self.db.add(new_course)
            self.db.commit()
            QMessageBox.information(self, "Success", "Course added successfully.")
            self.clear_form()
            self.load_courses()
        except IntegrityError:
            self.db.rollback()
            QMessageBox.warning(self, "Error", "Course code already exists.")

    def on_row_clicked(self, row, column):
        id_item = self.table.item(row, 0)
        if not id_item:
            return

        course_id = int(id_item.text())
        self.selected_course_id = course_id

        course = self.db.query(Course).get(course_id)
        if not course:
            return

        self.input_code.setText(course.code)
        self.input_name.setText(course.name)
        self.input_credits.setText(str(course.credits) if course.credits is not None else "")

        if course.department_id:
            idx = self.input_dept.findData(course.department_id)
            if idx >= 0:
                self.input_dept.setCurrentIndex(idx)

        if course.semester:
            idx = self.input_semester.findText(str(course.semester))
            if idx >= 0:
                self.input_semester.setCurrentIndex(idx)

    def update_course(self):
        if not self.selected_course_id:
            QMessageBox.warning(self, "Error", "Please select a course to update.")
            return

        course = self.db.query(Course).get(self.selected_course_id)
        if not course:
            QMessageBox.warning(self, "Error", "Course not found.")
            return

        code = self.input_code.text().strip()
        name = self.input_name.text().strip()
        dept_id = self.input_dept.currentData()
        credits_text = self.input_credits.text().strip()
        semester = int(self.input_semester.currentText())

        if not code or not name:
            QMessageBox.warning(self, "Error", "Course code and name are required.")
            return

        try:
            credits = int(credits_text) if credits_text else None
        except ValueError:
            QMessageBox.warning(self, "Error", "Credits must be a number.")
            return

        course.code = code
        course.name = name
        course.department_id = dept_id
        course.credits = credits
        course.semester = semester

        try:
            self.db.commit()
            QMessageBox.information(self, "Success", "Course updated successfully.")
            self.load_courses()
        except IntegrityError:
            self.db.rollback()
            QMessageBox.warning(self, "Error", "Course code already exists.")

    def delete_course(self):
        if not self.selected_course_id:
            QMessageBox.warning(self, "Error", "Please select a course to delete.")
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this course?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.No:
            return

        course = self.db.query(Course).get(self.selected_course_id)
        if not course:
            QMessageBox.warning(self, "Error", "Course not found.")
            return

        self.db.delete(course)
        self.db.commit()

        QMessageBox.information(self, "Success", "Course deleted.")
        self.clear_form()
        self.load_courses()

    def clear_form(self):
        self.input_code.clear()
        self.input_name.clear()
        self.input_credits.clear()
        self.selected_course_id = None
        if self.input_dept.count() > 0:
            self.input_dept.setCurrentIndex(0)
        self.input_semester.setCurrentIndex(0)

    # ---------- Search & Export ----------

    def on_search(self):
        text = self.search_input.text().strip()
        self.load_courses(text)

    def on_reset_search(self):
        self.search_input.clear()
        self.load_courses()

    def export_to_csv(self):
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Courses Data",
            "courses_export.csv",
            "CSV Files (*.csv)"
        )

        if not path:
            return

        row_count = self.table.rowCount()
        col_count = self.table.columnCount()

        headers = [self.table.horizontalHeaderItem(c).text() for c in range(col_count)]

        try:
            with open(path, mode="w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(headers)

                for r in range(row_count):
                    row_data = []
                    for c in range(col_count):
                        item = self.table.item(r, c)
                        row_data.append(item.text() if item else "")
                    writer.writerow(row_data)

            QMessageBox.information(
                self,
                "Export Successful",
                f"Courses exported successfully to:\n{path}\n\nYou can open it with Excel."
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Failed",
                f"An error occurred while exporting:\n{e}"
            )
