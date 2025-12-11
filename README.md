# University Management Information System (MIS)

A desktop-based **University Management Information System (MIS)** built using **Python**, **PyQt5**, and **SQLAlchemy**.  
The system provides a complete workflow to manage **students**, **courses**, **departments**, **faculties**, **instructors**, and **enrollments**, with a clean and user-friendly GUI connected to an SQLite database.

---

## 🚀 Features

### 🎓 Student Management
- Add, edit, delete students  
- Assign students to departments and faculties  
- Search students by name or university ID  
- Export student records to CSV  

### 📘 Course Management
- Add, update, delete courses  
- Assign courses to departments and instructors  
- Search and filter courses  
- Export to CSV  

### 👨‍🏫 Instructor Management
- Manage instructor details (name, email, phone, rank)  
- Link instructors to departments  
- Search and filter instructors  
- Export to CSV  

### 🏫 Enrollment Management
- Enroll students into courses  
- Select faculty → department → student → course  
- Manage academic year, semester, and enrollment status  
- Export enrollment table to CSV  

### 📊 Dashboard
- Displays faculty-level statistics:
  - Number of departments  
  - Total students  
  - Total courses  
  - Total instructors  

### 🔐 Authentication
- Simple login system using preset admin credentials  
- Roles supported in the database (admin, staff, read-only)

---

## 🛠️ Technologies Used

- **Python 3**
- **PyQt5** – GUI Framework  
- **SQLAlchemy ORM** – Database modeling  
- **SQLite** – Local lightweight database  
- **QStackedWidget** – For page navigation  
- **Custom QSS Stylesheet** – For UI styling  

---

## 📁 Project Structure
university_mis/

│── assets/

│ └── sadatacademy_logo.jpeg

│
│── pages/

│ ├── students_page.py

│ ├── instructors_page.py

│ ├── courses_page.py

│ ├── enrollments_page.py

│ └── dashboard_page.py

│
│── database.py

│── models.py

│── seed_data.py

│── style.py

│── main.py

│── .gitignore



---



## ▶️ How to Run the Project

1. Install required packages:
   ```bash
   pip install PyQt5 SQLAlchemy
2. Initialize the database with seed data:
   ```bash
   python seed_data.py
3. Lanch the application:
   ```bash
   python main.py


## 📌 Notes

- This project is a prototype for educational purposes.

- Passwords are stored in plain text for simplicity (can be upgraded later).

- The system is designed to be modular and extendable.


## 👤 Author

Ali Hosny
- GitHub: https://github.com/Ali-Hosny9

- Project Repository: https://github.com/Ali-Hosny9/University-Management-Information-System-MIS-
