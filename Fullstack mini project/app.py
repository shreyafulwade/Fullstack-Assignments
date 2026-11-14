
from flask import Flask, render_template, request, redirect, url_for, flash, session
from database import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "kalaconnect_secret_key"


# HOME PAGE
@app.route("/")
def home():
    if "user" in session:
        return redirect(url_for("dashboard"))

    return redirect(url_for("register"))


# REGISTRATION PAGE
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        fullname = request.form.get("fullname", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not fullname or not email or not password or not confirm_password:
            flash("Please fill all fields!")
            return redirect(url_for("register"))

        if len(password) < 8:
            flash("Password must be at least 8 characters!")
            return redirect(url_for("register"))

        if password != confirm_password:
            flash("Passwords do not match!")
            return redirect(url_for("register"))

        conn = get_db_connection()

        if conn is None:
            flash("Database connection failed!")
            return redirect(url_for("register"))

        cur = None

        try:
            cur = conn.cursor()

            cur.execute(
                "SELECT id FROM users WHERE email = %s",
                (email,)
            )

            if cur.fetchone():
                flash("Email already registered!")
                return redirect(url_for("register"))

            hashed_password = generate_password_hash(password)

            cur.execute(
                """INSERT INTO users
                (fullname, email, password)
                VALUES (%s, %s, %s)""",
                (fullname, email, hashed_password)
            )

            conn.commit()

            flash("Registration Successful! Please Login.")
            return redirect(url_for("login"))

        except Exception as e:
            conn.rollback()
            print("Registration Error:", e)
            flash("Something went wrong!")

        finally:
            if cur:
                cur.close()
            conn.close()

    return render_template("register.html")


# LOGIN PAGE
@app.route("/login", methods=["GET", "POST"])
def login():

    if "user" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        conn = get_db_connection()

        if conn is None:
            flash("Database connection failed!")
            return redirect(url_for("login"))

        cur = None

        try:
            cur = conn.cursor()

            cur.execute(
                "SELECT fullname, password FROM users WHERE email = %s",
                (email,)
            )

            user = cur.fetchone()

            if user and check_password_hash(user[1], password):

                session["user"] = user[0]

                return redirect(url_for("dashboard"))

            else:
                flash("Invalid Email or Password!")

        except Exception as e:
            print("Login Error:", e)
            flash("Something went wrong!")

        finally:
            if cur:
                cur.close()
            conn.close()

    return render_template("login.html")


# DASHBOARD PAGE
@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        flash("Please login first!")
        return redirect(url_for("login"))

    return render_template(
        "dashboard.html",
        fullname=session["user"]
    )


# LOGOUT PAGE
@app.route("/logout")
def logout():

    session.clear()

    flash("You have logged out successfully!")

    return redirect(url_for("login"))


# RUN APPLICATION
if __name__ == "__main__":
    app.run(debug=True)
