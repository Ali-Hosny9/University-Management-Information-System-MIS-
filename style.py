# style.py

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
    background-color: #0b1b3b;              /* navy */
    border-right: 1px solid #12264d;
}

QPushButton#sidebarButton {
    background-color: transparent;
    color: #ffffff;
    border: none;
    padding: 10px 16px;
    text-align: left;
}

QPushButton#sidebarButton:hover {
    background-color: #12264d;              /* slightly lighter navy */
}

QPushButton#sidebarButton:checked {
    background-color: #ffffff;
    color: #0b1b3b;
    font-weight: bold;
}

/* ---------- Form controls ---------- */
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

/* ---------- Buttons ---------- */
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

/* ---------- Table ---------- */
QTableWidget {
    background-color: #ffffff;
    gridline-color: #d0d4df;
    border: 1px solid #d0d4df;
}

QHeaderView::section {
    background-color: #0b1b3b;
    color: #ffffff;
    padding: 4px;
    border: none;
}

QTableWidget::item:selected {
    background-color: #e1e6f5;
    color: #0b1b3b;
}
"""
