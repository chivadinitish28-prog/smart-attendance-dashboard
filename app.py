from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
import os

# Firebase imports
import firebase_admin
from firebase_admin import credentials, db

app = Flask(__name__)
app.secret_key = "smart_attendance_secret_key"

# ------------------ Firebase Setup ------------------

cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://smartattendancesystem-84bfc-default-rtdb.firebaseio.com/'
})

# ------------------ Login Credentials ------------------

USERNAME = "DCME"
PASSWORD = "DCME155"

# ------------------ Read Attendance From Firebase ------------------

def read_attendance(date_filter=None):
    records = []
    ref = db.reference("Attendance")
    data = ref.get()

    if not data:
        return records

    for date, students in data.items():
        for student_id, details in students.items():

            if date_filter and date != date_filter:
                continue

            records.append({
                "ID": student_id,
                "Name": details.get("name", ""),
                "Date": date,
                "Time": details.get("time", "")
            })

    records.sort(key=lambda r: (r["Date"], r["Time"]), reverse=True)
    return records

# ------------------ Routes ------------------

@app.route("/")
def home():
    if session.get("logged_in"):
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form.get("username", "").strip()
        p = request.form.get("password", "").strip()

        if u == USERNAME and p == PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("dashboard"))
        return render_template("login.html", error="Invalid username or password")

    return render_template("login.html", error=None)

@app.route("/dashboard")
def dashboard():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    date_filter = request.args.get("date", "").strip()
    if date_filter == "":
        date_filter = None

    records = read_attendance(date_filter=date_filter)
    today = datetime.now().strftime("%Y-%m-%d")

    return render_template(
        "dashboard.html",
        records=records,
        selected_date=date_filter or "",
        today=today,
        total=len(records)
    )

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ------------------ Run App ------------------

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
