# Finance Manager

#### Description:

The **Finance Manager** is a web application designed to help users organize and monitor their personal finances.
It was developed as a final project for **CS50’s Introduction to Computer Science** and combines Python (Flask), SQLite, HTML, CSS, and JavaScript to deliver a full-stack solution.

The main goal of this system is to provide a simple yet effective way for users to **track their income, expenses, financial goals, and monthly reports** through an intuitive interface.

---

## Features

- **User authentication**: registration and login system with session management.
- **Add transactions**: record both income and expenses with description, category, and amount.
- **Dashboard**: quick overview of total incomes, expenses, and current balance.
- **Reports**:
  - Monthly income vs expenses chart.
  - Accumulated balance chart.
  - Pie chart of expenses by category.
- **Goals**: define and monitor financial goals.
- **Responsive interface**: built with Bootstrap for usability across devices.

---

## Files and Structure

### 1. `app.py`
The main Flask application file.
Defines the routes, business logic, and database interactions.
Examples:
- `/` → Dashboard with summary.
- `/transactions` → List of transactions.
- `/add_transaction` → Form to add income or expense.
- `/reports` → Financial reports with charts.
- `/goals` → Manage financial goals.

### 2. `helpers.py`
Contains helper functions:
- `login_required`: decorator to restrict routes to logged-in users.
- Error handling and reusable utilities.

### 3. Templates (in `/templates/`)
- **`layout.html`**: base layout with navbar and shared structure.
- **`index.html`**: dashboard overview.
- **`login.html` / `register.html`**: authentication forms.
- **`transactions.html`**: table with user transactions.
- **`add_transaction.html`**: form to create new entries.
- **`reports.html`**: page with interactive financial charts.
- **`goals.html`**: create and track goals.
- **`settings.html`**: placeholder for future customization (currency, language, preferences).

### 4. Database (`finance.db`)
Built with SQLite and managed via CS50’s `SQL` library.
Tables include:
- `users` → user accounts.
- `transactions` → incomes and expenses linked to a user.
- `goals` → financial goals.

### 5. Frontend libraries
- **Bootstrap** → responsive design.
- **Chart.js** → interactive charts for reports.

---

## Design Decisions

1. **Database choice (SQLite)**
   Selected for simplicity and native integration with CS50’s environment.
   It provides relational structure without requiring external configuration.

2. **Transaction model**
   Transactions include a `type` column (`income` or `expense`) to simplify queries.
   This enabled easy calculation of balances and categorization.

3. **Reports with accumulated balance**
   SQL queries were written to calculate month-to-month balance by subtracting expenses from incomes, giving users a clear view of their financial health over time.

4. **Charts with Chart.js**
   Chosen for its easy integration with Flask templates and ability to display combined bar and line charts (incomes, expenses, accumulated balance).

5. **Separation of concerns**
   - Logic in `app.py`.
   - Helper functions in `helpers.py`.
   - Presentation in Jinja templates.
   - Database persistence in `finance.db`.

---

## How to Run

1. Clone the repository.
2. Create a Python virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
3. Install dependencies:
   pip install -r requirements.txt
4. Inicialize the database (if needed, run schema.sql).
5. Start the Flask server:
   flask run
6. Open in browser:
   http://127.0.0.1:5000/

---

### Future Improvements

- **Export reports as PDF or Excel.**
- **Add notifications when goals are reached or expenses exceed a limit.**
- **Allow users to create custom categories.**
- **Internationalization (multi-language support).**
- **Implement Settings page (currency, language, privacy).**

---

### Conclusion

The **Finance Manager** is more than a course assignment: it is a working application that can be used for real financial management.

Through this project I applied knowledge of **Python, Flask, SQL, HTML, CSS, and JavaScript**, while also practicing design thinking, usability, and project organization.

Every design choice—from database schema to report generation—was made to keep the system simple, user-friendly, and scalable.

This project reflects not only the technical skills acquired in CS50, but also the importance of **documentation, maintainability, and user experience** in building complete software solutions.
