# pages/instructors_page.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView,
    QFileDialog
)

from sqlalchemy.exc import IntegrityError
import csv

from database import SessionLocal
from models import Instructor, Department


class InstructorsPage(QWidget):
    def __init__(self):
        super().__init__()

        self.db = SessionLocal()
        self.selected_instructor_id = None

        main_layout = QHBoxLayout(self)

        # ================= LEFT: ADD / EDIT FORM =================
        form_layout = QVBoxLayout()

        title = QLabel("Add / Edit Instructor")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        form_layout.addWidget(title)

        # Full name
        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("Full Name")
        form_layout.addWidget(self.input_name)

        # Department
        self.input_dept = QComboBox()
        self.load_departments()
        form_layout.addWidget(self.input_dept)

        # Rank
        self.input_rank = QLineEdit()
        self.input_rank.setPlaceholderText("Rank (Assistant, Lecturer, Professor...)")
        form_layout.addWidget(self.input_rank)

        # Email
        self.input_email = QLineEdit()
        self.input_email.setPlaceholderText("Email")
        form_layout.addWidget(self.input_email)

        # Phone
        self.input_phone = QLineEdit()
        self.input_phone.setPlaceholderText("Phone number")
        form_layout.addWidget(self.input_phone)

        # Buttons row
        buttons_row = QHBoxLayout()

        btn_add = QPushButton("Add")
        btn_add.clicked.connect(self.add_instructor)
        buttons_row.addWidget(btn_add)

        btn_update = QPushButton("Update Selected")
        btn_update.clicked.connect(self.update_instructor)
        buttons_row.addWidget(btn_update)

        btn_delete = QPushButton("Delete Selected")
        btn_delete.clicked.connect(self.delete_instructor)
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
        self.search_input.setPlaceholderText("Search by name or email...")
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
            ["ID", "Name", "Dept", "Rank", "Email", "Phone"]
        )
        self.table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.Stretch  # stretch Name column
        )
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
        self.load_instructors()

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


    def load_instructors(self, search_text: str = ""):
        query = self.db.query(Instructor)

        if search_text:
            like = f"%{search_text}%"
            query = query.filter(
                (Instructor.full_name.ilike(like)) |
                (Instructor.email.ilike(like))
            )

        instructors = query.all()
        self.table.setRowCount(len(instructors))

        for row, ins in enumerate(instructors):
            self.table.setItem(row, 0, QTableWidgetItem(str(ins.id)))
            self.table.setItem(row, 1, QTableWidgetItem(ins.full_name))
            self.table.setItem(row, 2, QTableWidgetItem(ins.department.name if ins.department else ""))
            self.table.setItem(row, 3, QTableWidgetItem(ins.rank or ""))
            self.table.setItem(row, 4, QTableWidgetItem(ins.email or ""))
            self.table.setItem(row, 5, QTableWidgetItem(ins.phone or ""))

        self.selected_instructor_id = None

    # ---------- CRUD ----------

    def add_instructor(self):
        name = self.input_name.text().strip()
        dept_id = self.input_dept.currentData()
        rank = self.input_rank.text().strip()
        email = self.input_email.text().strip()
        phone = self.input_phone.text().strip()

        if not name:
            QMessageBox.warning(self, "Error", "Name is required.")
            return

        new_ins = Instructor(
            full_name=name,
            department_id=dept_id,
            rank=rank,
            email=email,
            phone=phone
        )

        try:
            self.db.add(new_ins)
            self.db.commit()
            QMessageBox.information(self, "Success", "Instructor added successfully.")
            self.clear_form()
            self.load_instructors()
        except IntegrityError:
            self.db.rollback()
            QMessageBox.warning(self, "Error", "Could not add instructor (integrity error).")

    def on_row_clicked(self, row, column):
        id_item = self.table.item(row, 0)
        if not id_item:
            return

        ins_id = int(id_item.text())
        self.selected_instructor_id = ins_id

        ins = self.db.query(Instructor).get(ins_id)
        if not ins:
            return

        self.input_name.setText(ins.full_name)
        self.input_rank.setText(ins.rank or "")
        self.input_email.setText(ins.email or "")
        self.input_phone.setText(ins.phone or "")

        if ins.department_id:
            idx = self.input_dept.findData(ins.department_id)
            if idx >= 0:
                self.input_dept.setCurrentIndex(idx)

    def update_instructor(self):
        if not self.selected_instructor_id:
            QMessageBox.warning(self, "Error", "Please select an instructor to update.")
            return

        ins = self.db.query(Instructor).get(self.selected_instructor_id)
        if not ins:
            QMessageBox.warning(self, "Error", "Instructor not found.")
            return

        name = self.input_name.text().strip()
        dept_id = self.input_dept.currentData()
        rank = self.input_rank.text().strip()
        email = self.input_email.text().strip()
        phone = self.input_phone.text().strip()

        if not name:
            QMessageBox.warning(self, "Error", "Name is required.")
            return

        ins.full_name = name
        ins.department_id = dept_id
        ins.rank = rank
        ins.email = email
        ins.phone = phone

        try:
            self.db.commit()
            QMessageBox.information(self, "Success", "Instructor updated successfully.")
            self.load_instructors()
        except IntegrityError:
            self.db.rollback()
            QMessageBox.warning(self, "Error", "Could not update instructor (integrity error).")

    def delete_instructor(self):
        if not self.selected_instructor_id:
            QMessageBox.warning(self, "Error", "Please select an instructor to delete.")
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this instructor?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.No:
            return

        ins = self.db.query(Instructor).get(self.selected_instructor_id)
        if not ins:
            QMessageBox.warning(self, "Error", "Instructor not found.")
            return

        self.db.delete(ins)
        self.db.commit()

        QMessageBox.information(self, "Success", "Instructor deleted.")
        self.clear_form()
        self.load_instructors()

    def clear_form(self):
        self.input_name.clear()
        self.input_rank.clear()
        self.input_email.clear()
        self.input_phone.clear()
        self.selected_instructor_id = None
        if self.input_dept.count() > 0:
            self.input_dept.setCurrentIndex(0)

    # ---------- Search & Export ----------

    def on_search(self):
        text = self.search_input.text().strip()
        self.load_instructors(text)

    def on_reset_search(self):
        self.search_input.clear()
        self.load_instructors()

    def export_to_csv(self):
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Instructors Data",
            "instructors_export.csv",
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
                f"Instructors exported successfully to:\n{path}\n\nYou can open it with Excel."
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Failed",
                f"An error occurred while exporting:\n{e}"
            )
