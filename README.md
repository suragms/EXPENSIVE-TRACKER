# 💸 Expense Tracker Web Application

The **Expense Tracker Web Application** is a robust and user-friendly tool built with **Python** and **Django** to empower users to manage their personal finances effectively. It enables tracking of income, expenses, budgets, and shared event-based expenses, providing a centralized platform for financial oversight.

---

## 🚀 Features

- **User Authentication & Profiles**: Secure login, registration, and profile management.  
- **Transaction Management**: Add, edit, and delete income and expense records.  
- **Categorization**: Organize transactions with customizable or predefined categories.  
- **Bill Storage**: Upload and manage digital bill images.  
- **Recurring Transactions**: Track one-time and recurring financial activities.  
- **Financial Insights**: Generate reports and summaries for informed decision-making.  
- **Budget Tracking**: Set and monitor category-based budgets with alerts.  
- **Event Expenses**: Manage shared expenses and contributions for events.  
- **Admin Panel**: Comprehensive user and system management for administrators.

---

## 🛠 Tech Stack

| Layer        | Technology                         |
|--------------|------------------------------------|
| Frontend     | HTML5, CSS3, JavaScript            |
| Backend      | Python, Django                     |
| Database     | MySQL (SQLite3 for development)    |
| File Storage | Django ImageKit for media handling |
| Admin Panel  | Django Admin                       |
| Hosting      | Render / Localhost                 |

---

## ⚙️ Installation & Setup

### 🧱 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- MySQL (or SQLite3 for development)
- Git (for cloning the repository)
- Virtual environment (recommended)

### 🪜 Steps

1. **Clone the Repository**

   ```bash
   git clone https://github.com/suragsunil/expense-tracker-app.git
   cd expense-tracker-app
   ```

2. **Set Up a Virtual Environment**

   ```bash
   # Create virtual environment
   python -m venv myvenv

   # Activate virtual environment
   # On Unix/macOS
   source myvenv/bin/activate
   # On Windows
   myvenv\Scripts\activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the Database**

   Ensure MySQL is installed and running, or use SQLite3 for development. Update database settings in `expense_tracker/settings.py` if using MySQL.

5. **Apply Database Migrations**

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create a Superuser (for Admin Panel)**

   ```bash
   python manage.py createsuperuser
   ```

7. **Run the Development Server**

   ```bash
   python manage.py runserver
   ```

8. **Access the Application**

   - Web Interface: `http://127.0.0.1:8000/`  
   - Admin Panel: `http://127.0.0.1:8000/admin/`

---

## 📂 Project Structure

```
expense-tracker/
├── .gitignore
├── .vscode/
├── Expensiveapp/
│   ├── migrations/
│   ├── static/
│   ├── templates/
│   │   └── [...multiple HTML files...]
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   ├── __init__.py
│   └── __pycache__/
├── Expensive_tracker/
├── media/
├── myvenv/
├── db.sqlite3
├── manage.py
├── requirements.txt
└── README.md
```

---

## 🔮 Future Enhancements

- **Mobile Optimization**: Implement a responsive UI using Bootstrap or React.  
- **Advanced Visualizations**: Integrate Chart.js or D3.js for enhanced reporting.  
- **Multi-language Support**: Add internationalization for global accessibility.  
- **Security Enhancements**: Introduce two-factor authentication.  
- **Notifications**: Enable email alerts and periodic financial summaries.  
- **Multi-currency Support**: Add currency conversion and multi-currency tracking.

---

## 👤 Author

**Surag**  
🎓 MCA Student | 🖥️ Python Django Developer  
🔗 [GitHub](http://github.com/suragms) | [LinkedIn](https://linkedin.com/in/suragsunil) | [Instagram](https://instagram.com/surag_sunil)

---

## 📄 License

This project is licensed under the **MIT License**. You are free to use, modify, and distribute it as needed.

---

## 🙏 Acknowledgments

- Django Documentation and Community  
- Open Source Contributors  
- Mentors and Peers

---

📬 *For feedback or collaboration, please contact me via GitHub or LinkedIn.*
