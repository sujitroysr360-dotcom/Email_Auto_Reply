from flask import Flask, render_template, request, redirect
import sqlite3
import os

app = Flask(__name__)

DATABASE = "database/email.db"


def init_database():
    os.makedirs("database", exist_ok=True)

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Allowed senders table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS allowed_senders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL
        )
    """)

    # Statistics table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS statistics (
            id INTEGER PRIMARY KEY,
            emails_checked INTEGER DEFAULT 0,
            replies_sent INTEGER DEFAULT 0,
            emails_skipped INTEGER DEFAULT 0,
            last_check TEXT DEFAULT 'Never'
        )
    """)

    # Create one statistics row
    cursor.execute("""
        INSERT OR IGNORE INTO statistics
        (id, emails_checked, replies_sent, emails_skipped, last_check)
        VALUES (1, 0, 0, 0, 'Never')
    """)

    conn.commit()
    conn.close()


@app.route("/")
def home():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("SELECT id, email FROM allowed_senders")
    senders = cursor.fetchall()

    cursor.execute("""
        SELECT emails_checked, replies_sent, emails_skipped, last_check
        FROM statistics
        WHERE id = 1
    """)

    stats = cursor.fetchone()

    conn.close()

    return render_template(
        "index.html",
        senders=senders,
        stats=stats
    )


@app.route("/add", methods=["POST"])
def add_sender():
    email = request.form.get("email", "").lower().strip()

    if email:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO allowed_senders (email) VALUES (?)",
                (email,)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            pass

        conn.close()

    return redirect("/")


@app.route("/remove/<int:sender_id>", methods=["POST"])
def remove_sender(sender_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM allowed_senders WHERE id = ?",
        (sender_id,)
    )

    conn.commit()
    conn.close()

    return redirect("/")


@app.route("/check", methods=["POST"])
def check_emails():
    from auto_reply import auto_reply

    auto_reply()

    return redirect("/")


if __name__ == "__main__":
    init_database()
    app.run(debug=True)