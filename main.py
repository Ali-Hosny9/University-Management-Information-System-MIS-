import sys
import os

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QDialog,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QFrame,
    QStackedWidget,
)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt

from database import SessionLocal
from models import User
from pages.students_page import StudentsPage
from pages.courses_page import CoursesPage
from pages.instructors_page import InstructorsPage
from pages.dashboard_page import DashboardPage
from pages.enrollments_page import EnrollmentsPage

# --------------------------------------------------------------------
#  Absolute path to the logo 
# --------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(BASE_DIR, "assets", "sadatacademy_logo.jpeg")

# --------------------------------------------------------------------
#  GLOBAL NAVY & WHITE THEME
# --------------------------------------------------------------------
APP_STYLESHEET = """
QMainWindow {
    background-color: #f5f7fb;
}

QWidget {
    font-family: "Segoe UI";
    font-size: 10pt;
}

/* ---------- Sidebar ---------- */
QWidget#Sidebar {
    background-color: #0b1b3b;
    border-right: 1px solid #12264d;
}

QPushButton#sidebarButton {
    background-color: transparent;
    color: #ffffff;
    border: none;
    padding: 10px 16px;
    text-align: left;
    font-size: 11pt;
}

QPushButton#sidebarButton:hover {
    background-color: #12264d;
}

QPushButton#sidebarButton:checked {
    background-color: #ffffff;
    color: #0b1b3b;
    font-weight: bold;
}

QLabel {
    color: #0b1b3b;
}

QLineEdit, QComboBox {
    background-color: #ffffff;
    border: 1px solid #c3c8d4;
    border-radius: 4px;
    padding: 4px;
}

QLineEdit:focus, QComboBox:focus {
    border: 1px solid #0b1b3b;
}

QPushButton {
    background-color: #0b1b3b;
    color: #ffffff;
    border-radius: 4px;
    padding: 6px 12px;
}

QPushButton:hover {
    background-color: #12264d;
}

QPushButton:disabled {
    background-color: #d0d4df;
    color: #777777;
}

QTableWidget {
    background-color: #ffffff;
    gridline-color: #d0d4df;
    border: 1px solid #d0d4df;
}

QHeaderView::section {
    background-color: #0b1b3b;
    color: #ffffff;
    padding: 4px;
}

QTableWidget::item:selected {
    background-color: #e1e6f5;
    color: #0b1b3b;
}
"""

# --------------------------------------------------------------------
#  LOGIN DIALOG
# --------------------------------------------------------------------
class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.logged_in_username = None
        self.setWindowTitle("Sadat Academy for Management Science - MIS System")
        self.setFixedSize(460, 360)   # a bit wider & taller

        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        # ---- Logo ----
        logo_label = QLabel()
        pix = QPixmap(LOGO_PATH)
        if not pix.isNull():
            pix = pix.scaled(90, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(pix)
        logo_label.setAlignment(Qt.AlignCenter)

        # ---- Academy name ----
        title_label = QLabel("Sadat Academy for Management Science")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-weight: bold; font-size: 12pt; color: #0b1b3b;")
        title_label.setWordWrap(True)   # allow multi-line so it doesn't crop

        subtitle_label = QLabel("Management Information System")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("color: #555555; font-size: 9pt;")

        layout.addWidget(logo_label)
        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)

        # username
        user_layout = QHBoxLayout()
        user_label = QLabel("Username:")
        self.user_input = QLineEdit()
        user_layout.addWidget(user_label)
        user_layout.addWidget(self.user_input)

        # password
        pass_layout = QHBoxLayout()
        pass_label = QLabel("Password:")
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.Password)
        pass_layout.addWidget(pass_label)
        pass_layout.addWidget(self.pass_input)

        # login button
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.handle_login)

        layout.addLayout(user_layout)
        layout.addLayout(pass_layout)
        layout.addSpacing(8)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    def handle_login(self):
        username = self.user_input.text().strip()
        password = self.pass_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter username and password.")
            return

        db = SessionLocal()
        try:
            user = db.query(User).filter_by(username=username, password_hash=password).first()
        finally:
            db.close()

        if user:
            self.logged_in_username = user.username
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Invalid username or password.")


# --------------------------------------------------------------------
#  ABOUT DIALOG
# --------------------------------------------------------------------
class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("About - Sadat Academy MIS")
        self.setFixedSize(420, 280)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        logo_label = QLabel()
        pix = QPixmap(LOGO_PATH)
        if not pix.isNull():
            pix = pix.scaled(72, 72, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(pix)
        logo_label.setAlignment(Qt.AlignCenter)

        title_label = QLabel("Sadat Academy for Management Science")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-weight: bold; font-size: 12pt; color: #0b1b3b;")
        title_label.setWordWrap(True)  # wrap long text

        subtitle_label = QLabel("Management Information System (MIS)")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("color: #555555; font-size: 9pt;")
        subtitle_label.setWordWrap(True)

        version_label = QLabel("Version 1.0.0")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("color: #777777; font-size: 9pt;")

        footer_label = QLabel("© Sadat Academy for Management Science")
        footer_label.setAlignment(Qt.AlignCenter)
        footer_label.setStyleSheet("color: #999999; font-size: 8pt;")
        footer_label.setWordWrap(True)

        layout.addWidget(logo_label)
        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)
        layout.addWidget(version_label)
        layout.addStretch()
        layout.addWidget(footer_label)

        self.setLayout(layout)


# --------------------------------------------------------------------
#  MAIN WINDOW
# --------------------------------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self, username):
        super().__init__()

        self.username = username

        self.setWindowTitle("Sadat Academy for Management Science - MIS System")
        self.resize(1280, 720)

        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)

        # ---------------- SIDEBAR ----------------
        self.sidebar = QWidget()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(260)

        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(16, 16, 16, 16)
        sidebar_layout.setSpacing(10)

        # Sidebar header (logo + text)
        header = QWidget()
        hlayout = QHBoxLayout(header)
        hlayout.setContentsMargins(0, 0, 0, 0)

        logo = QLabel()
        pix = QPixmap(LOGO_PATH)
        if not pix.isNull():
            pix = pix.scaled(42, 42, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo.setPixmap(pix)

        title = QLabel("Sadat Academy\nMIS System")
        title.setStyleSheet("color: white; font-weight: bold; font-size: 11pt;")

        hlayout.addWidget(logo)
        hlayout.addWidget(title)
        hlayout.addStretch()

        sidebar_layout.addWidget(header)

        # Divider
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #30416d;")
        sidebar_layout.addWidget(line)

        # Sidebar button builder
        def make_btn(text):
            b = QPushButton(text)
            b.setObjectName("sidebarButton")
            b.setCheckable(True)
            b.setAutoExclusive(True)
            return b

        # Buttons
        self.btn_dashboard = make_btn("Dashboard")
        self.btn_students = make_btn("Students")
        self.btn_courses = make_btn("Courses")
        self.btn_enrollments = make_btn("Enrollments")
        self.btn_instructors = make_btn("Instructors")
        self.btn_about = make_btn("About")
        self.btn_about.setCheckable(False)
        self.btn_exit = make_btn("Exit")
        self.btn_exit.setCheckable(False)

        sidebar_layout.addWidget(self.btn_dashboard)
        sidebar_layout.addWidget(self.btn_students)
        sidebar_layout.addWidget(self.btn_courses)
        sidebar_layout.addWidget(self.btn_enrollments)
        sidebar_layout.addWidget(self.btn_instructors)
        sidebar_layout.addSpacing(20)

        sidebar_layout.addWidget(self.btn_about)
        sidebar_layout.addWidget(self.btn_exit)
        sidebar_layout.addStretch()

        # ---------------- CONTENT PAGES ----------------
        self.pages = QStackedWidget()
        self.pages.addWidget(DashboardPage())     # 0
        self.pages.addWidget(StudentsPage())      # 1
        self.pages.addWidget(CoursesPage())       # 2
        self.pages.addWidget(EnrollmentsPage())   # 3
        self.pages.addWidget(InstructorsPage())   # 4

        # Page switching
        self.btn_dashboard.clicked.connect(lambda: self.switch_page(0, self.btn_dashboard))
        self.btn_students.clicked.connect(lambda: self.switch_page(1, self.btn_students))
        self.btn_courses.clicked.connect(lambda: self.switch_page(2, self.btn_courses))
        self.btn_enrollments.clicked.connect(lambda: self.switch_page(3, self.btn_enrollments))
        self.btn_instructors.clicked.connect(lambda: self.switch_page(4, self.btn_instructors))

        self.btn_about.clicked.connect(self.show_about_dialog)
        self.btn_exit.clicked.connect(self.close)

        # Default
        self.btn_dashboard.setChecked(True)

        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.pages)

        self.setCentralWidget(central_widget)

        # ---------- STATUS BAR ----------
        self.statusBar().showMessage(f"Logged in as: {self.username}")

    def switch_page(self, index, button):
        self.pages.setCurrentIndex(index)
        button.setChecked(True)

    def show_about_dialog(self):
        dlg = AboutDialog(self)
        dlg.exec_()

# --------------------------------------------------------------------
#  APP ENTRY
# --------------------------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(APP_STYLESHEET)
    app.setWindowIcon(QIcon(LOGO_PATH))

    login = LoginDialog()
    if login.exec_() == QDialog.Accepted:
        username = login.logged_in_username or "admin"
        window = MainWindow(username)
        window.showMaximized()
        sys.exit(app.exec_())
    else:
        sys.exit(0)
