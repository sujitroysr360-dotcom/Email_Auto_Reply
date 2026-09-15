import sqlite3

DATABASE = "database/email.db"

ALLOWED_SENDERS = [
    "swapnilmukherzee9@gmail.com",
    "shucheepaul09@gmail.com",
    "sujit.roy.sr360@gmail.com",
    "roysujit2004@gmail.com",
]


def add_sender(email):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO allowed_senders (email) VALUES (?)",
            (email.lower().strip(),)
        )
        conn.commit()
        print(f"{email} added successfully!")

    except sqlite3.IntegrityError:
        print(f"{email} is already in the allowed list.")

    conn.close()


def remove_sender(email):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM allowed_senders WHERE email = ?",
        (email.lower().strip(),)
    )

    conn.commit()
    conn.close()

    print(f"{email} removed successfully!")


def is_allowed_sender(email):
    email = email.lower().strip()

    # First check the fixed allowed list
    if email in [sender.lower() for sender in ALLOWED_SENDERS]:
        return True

    # Then check the database
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM allowed_senders WHERE email = ?",
        (email,)
    )

    result = cursor.fetchone()

    conn.close()

    return result is not None


def get_allowed_senders():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("SELECT email FROM allowed_senders")

    senders = [row[0] for row in cursor.fetchall()]

    conn.close()

    return senders