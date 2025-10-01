import os
import io
import sqlite3
import csv
import pandas as pd
from flask import send_file
from flask import Response
from cs50 import SQL
from flask import Flask, render_template, request, redirect, session, flash
from flask_session import Session
from jinja2 import Environment
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required

# Flask application config
app = Flask(__name__)

# Session config
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Db connection
db = SQL("sqlite:///finance.db")

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

def format_currency(value):
    return f"$ {value:,.2f}"
app.jinja_env.filters['currency'] = format_currency

# Initial Page
@app.route("/")
@login_required
def index():
    incomes = db.execute("""
        SELECT COALESCE(SUM(amount), 0) AS total FROM transactions WHERE user_id = ? AND type = 'income'
    """, session["user_id"])[0]["total"]

    expenses = db.execute("""
        SELECT COALESCE(SUM(amount), 0) AS total FROM transactions WHERE user_id = ? AND type = 'expense'
    """, session["user_id"])[0]["total"]

    balance = db.execute("""
        SELECT COALESCE(SUM(CASE WHEN type='income' THEN amount ELSE -amount END), 0) AS balance
        FROM transactions WHERE user_id = ?
    """, session["user_id"])[0]["balance"]

    return render_template("index.html", incomes=incomes, expenses=expenses, balance=balance)

@app.route("/transactions", methods=["GET", "POST"])
@login_required
def transactions():
    if request.method == "POST":
        type_ = request.form.get("type")
        category = request.form.get("category")
        amount_raw = request.form.get("amount")
        description = request.form.get("description")

        if not type_ or not category or not amount_raw:
            return apology("Fill in all fields", 400)

        try:
            amount_raw = amount_raw.strip().replace(",", ".")
            amount = float(amount_raw)
        except ValueError:
            return apology("Invalid Amount", 400)

        if amount <= 0:
            return apology("Amount must be positive", 400)

        try:
            db.execute(
                "INSERT INTO transactions (user_id, type, category, amount, description) VALUES (?, ?, ?, ?, ?)",
                session["user_id"], type_, category, amount, description
            )
        except Exception as e:
            app.logger.exception("DB insert failed in add_transaction")
            return apology("Could not save transaction", 500)

        return redirect("/transactions")

    # GET → user transaction list
    rows = db.execute(
        "SELECT id, date, type, category, amount, description FROM transactions WHERE user_id = ? ORDER BY id DESC",
        session["user_id"]
    )
    return render_template("transactions.html", transactions=rows)

@app.route("/add", methods=["GET", "POST"])
@login_required
def add_transaction():
    if request.method == "POST":
        type_ = request.form.get("type")
        category = request.form.get("category")
        amount_raw = request.form.get("amount")
        description = request.form.get("description")

        if not type_ or not category or not amount_raw:
            return apology("Fill in all fields", 400)

        try:
            amount_raw = amount_raw.strip().replace(",", ".")
            amount = float(amount_raw)
        except ValueError:
            return apology("Invalid Amount", 400)

        if amount <= 0:
            return apology("Amount must be positive", 400)

        try:
            db.execute("""
                INSERT INTO transactions (user_id, type, category, amount, description) VALUES (?, ?, ?, ?, ?), DATE('now')""",
                session["user_id"], type_, category, amount, description
            )
        except Exception as e:
            app.logger.exception("DB insert failed in add_transaction")
            return apology("Could not save transaction", 500)

        return redirect("/")

    return render_template("add_transaction.html")

# Register
@app.route("/register", methods = ["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username or not password or not confirmation:
            flash("Fill in all fields")
            return redirect("/register")
        if password != confirmation:
            flash("Passwords do not match")
            return redirect("/register")

        try:
            user_id = db.execute(
                "INSERT INTO users (username, hash) VALUES (?, ?)",
                username, generate_password_hash(password)
            )
        except Exception:
            flash("User already exists")
            return redirect("/register")

        session["user_id"] = user_id
        return redirect("/")
    else:
        return render_template("register.html")

# Login
@app.route("/login", methods = ["GET", "POST"])
def login():
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash("Enter username and password")
            return redirect("/login")

        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", username
        )

        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            flash("Username and/or passwords invalid")
            return redirect("/login")

        session["user_id"] = rows[0]["id"]
        return redirect("/")
    else:
        return render_template("login.html")

@app.route("/reports", methods=["GET", "POST"])
@login_required
def reports():
    # If user dont filter, show the actual year
    year = request.form.get("year")
    if not year:
        from datetime import datetime
        year = datetime.now().year

    # Total incomes/expenses by month
    monthly = db.execute("""
        SELECT strftime('%m', date) AS month,
              type,
              SUM(amount) AS total
        FROM transactions
        WHERE user_id = ? AND strftime('%Y', date) = ?
        GROUP BY month, type
        ORDER BY month ASC
    """, session["user_id"], str(year))

    #Total by category
    categories = db.execute("""
        SELECT category,
                type,
                SUM(amount) AS total
        FROM transactions
        WHERE user_id = ? AND strftime('%Y', date) = ?
        GROUP BY category, type
        ORDER BY total DESC
    """, session["user_id"], str(year))

    return render_template("reports.html", monthly=monthly, categories=categories, year=year)

@app.route("/goals", methods=["GET","POST"])
@login_required
def goals():
    if request.method == "POST":
        name = request.form.get("name")
        target = request.form.get("target")
        deadline = request.form.get("deadline")

        if not name or not target or not deadline:
            flash("Fill in all fields")
            return redirect("/goals")

        db.execute(
            "INSERT INTO goals (user_id, name, target, deadline) VALUES (?, ?, ?, ?)",
            session["user_id"], name, float(target), deadline
        )
        flash("Goal created successfully")
        return redirect("/goals")

    goals = db.execute("SELECT * FROM goals WHERE user_id = ?", session["user_id"])

    balance = db.execute("""
        SELECT
            (IFNULL(SUM(CASE WHEN type='income' THEN amount ELSE 0 END), 0) -
            IFNULL(SUM(CASE WHEN type='expense' THEN amount ELSE 0 END), 0)) AS balance
        FROM transactions WHERE user_id = ?
    """, session["user_id"])[0]["balance"]

    for g in goals:
        g["progress"] = min(100, round((balance / g["target"]) * 100, 2))

    return render_template("goals.html", goals=goals, balance=balance)

@app.route("/goals/progress")
@login_required
def goals_progress():
    goals = db.execute("""
        SELECT g.*,
            (SELECT SUM(amount) FROM transactions
             WHERE user_id = g.user_id AND type='income') AS saved
        FROM goals g WHERE g.user_id = ?
    """, session["user_id"])

    for g in goals:
        g["progress"] = round(g["saved"] / g["target"]) * 100, 2

    return render_template("goals_progress.html", goals=goals)

@app.route("/export/csv")
@login_required
def export_csv_stream():
    rows = db.execute(
        "SELECT id, type, category, amount, description, date FROM transactions WHERE user_id = ? ORDER BY date DESC",
        session["user_id"]
    )

    def generate():
        si = io.StringIO()
        writer = csv.writer(si)

        # header
        writer.writerow(["id", "type", "category", "amount", "description", "date"])
        yield si.getvalue()
        si.truncate(0); si.seek(0)

        # linhas
        for r in rows:
            writer.writerow([r["id"], r["type"], r["category"], r["amount"], r["description"], r["date"]])
            yield si.getvalue()
            si.truncate(0); si.seek(0)

    headers = {"Content-Disposition": "attachment; filename=transactions.csv"}
    return Response(generate(), mimetype="text/csv; charset=utf-8", headers=headers)

# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug = True)
