from flask import Flask, render_template, request, redirect
from datetime import date
import calendar
import sqlite3

app = Flask(__name__)

# ====================
# DB
# ====================
def get_db():
    return sqlite3.connect("db.sqlite3")

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            title TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def add_schedule(schedule_date, title):
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "INSERT INTO schedule (date, title) VALUES (?, ?)",
        (schedule_date, title)
    )
    conn.commit()
    conn.close()

def get_schedules_by_date(schedule_date):
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "SELECT id, date, title FROM schedule WHERE date = ? ORDER BY created_at",
        (schedule_date,)
    )
    rows = c.fetchall()
    conn.close()
    return rows

def get_schedule_dates():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT DISTINCT date FROM schedule")
    rows = c.fetchall()
    conn.close()
    return {row[0] for row in rows}


# ====================
# Web
# ====================
@app.route("/", methods=["GET", "POST"])
def index():
    # 予定登録（Create）
    if request.method == "POST":
        schedule_date = request.form["date"]
        title = request.form["title"]
        add_schedule(schedule_date, title)
        return redirect(f"/?date={schedule_date}")

    today = date.today()

    # 選択中の日付（クリック or 今日）
    selected_date = request.args.get("date")
    if not selected_date:
        selected_date = today.strftime("%Y-%m-%d")

    # カレンダー生成
    cal = calendar.Calendar(firstweekday=6)
    month_days = cal.monthdayscalendar(today.year, today.month)

    # 選択日の予定取得（Read）
    schedules = get_schedules_by_date(selected_date)
    schedule_dates = get_schedule_dates()



    return render_template(
        "index.html",
        year=today.year,
        month=today.month,
        month_days=month_days,
        schedules=schedules,
        selected_date=selected_date,
        schedule_dates=schedule_dates,

    )

@app.route("/delete/<int:schedule_id>", methods=["POST"])
def delete_schedule(schedule_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM schedule WHERE id = ?", (schedule_id,))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/edit/<int:schedule_id>")
def edit_schedule(schedule_id):
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "SELECT id, date, title FROM schedule WHERE id = ?",
        (schedule_id,)
    )
    schedule = c.fetchone()
    conn.close()
    return render_template("edit.html", schedule=schedule)

@app.route("/update/<int:schedule_id>", methods=["POST"])
def update_schedule(schedule_id):
    date_value = request.form["date"]
    title = request.form["title"]

    conn = get_db()
    c = conn.cursor()
    c.execute(
        "UPDATE schedule SET date = ?, title = ? WHERE id = ?",
        (date_value, title, schedule_id)
    )
    conn.commit()
    conn.close()

    return redirect(f"/?date={date_value}")


if __name__ == "__main__":
    init_db()   # DB自動生成
    app.run(host="0.0.0.0", port=5000, debug=True)

