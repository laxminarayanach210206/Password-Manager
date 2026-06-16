from flask import Flask, render_template, request, redirect, session
import sqlite3
import os
from cryptography.fernet import Fernet

app = Flask(__name__)
app.secret_key = "secret123"

# -------------------------
# Encryption key
# -------------------------

if not os.path.exists("key.key"):
    key = Fernet.generate_key()
    with open("key.key","wb") as f:
        f.write(key)

with open("key.key","rb") as f:
    key = f.read()

cipher = Fernet(key)

# -------------------------
# Database initialization
# -------------------------

def init_db():

    conn = sqlite3.connect("secure_passwords.db")

    conn.execute("""
    CREATE TABLE IF NOT EXISTS passwords(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    website TEXT,
    username TEXT,
    password BLOB
    )
    """)

    conn.close()

init_db()

# -------------------------
# Master Login
# -------------------------

MASTER_USER = "admin"
MASTER_PASS = "1234"

@app.route("/", methods=["GET","POST"])
def login():

    if request.method == "POST":

        user = request.form["username"]
        pw = request.form["password"]

        if user == MASTER_USER and pw == MASTER_PASS:
            session["logged_in"] = True
            return redirect("/dashboard")

    return render_template("login.html")

# -------------------------
# Dashboard
# -------------------------

@app.route("/dashboard")
def dashboard():

    if not session.get("logged_in"):
        return redirect("/")

    conn = sqlite3.connect("database.db")
    data = conn.execute("SELECT * FROM passwords").fetchall()
    conn.close()

    decrypted = []

    for row in data:
        password = cipher.decrypt(row[3]).decode()
        decrypted.append((row[0],row[1],row[2],password))

    count = len(decrypted)

    return render_template("dashboard.html", data=decrypted, count=count)

# -------------------------
# Add password
# -------------------------

@app.route("/add", methods=["POST"])
def add():

    website = request.form["website"]
    username = request.form["username"]
    password = request.form["password"]

    encrypted = cipher.encrypt(password.encode())

    conn = sqlite3.connect("database.db")

    conn.execute(
        "INSERT INTO passwords (website,username,password) VALUES (?,?,?)",
        (website,username,encrypted)
    )

    conn.commit()
    conn.close()

    return redirect("/dashboard")

# -------------------------
# Edit password
# -------------------------

@app.route("/edit/<int:id>", methods=["GET","POST"])
def edit(id):

    if not session.get("logged_in"):
        return redirect("/")

    conn = sqlite3.connect("database.db")

    if request.method == "POST":

        website = request.form["website"]
        username = request.form["username"]
        password = cipher.encrypt(request.form["password"].encode())

        conn.execute(
            "UPDATE passwords SET website=?, username=?, password=? WHERE id=?",
            (website,username,password,id)
        )

        conn.commit()
        conn.close()

        return redirect("/dashboard")

    data = conn.execute(
        "SELECT * FROM passwords WHERE id=?",
        (id,)
    ).fetchone()

    decrypted = cipher.decrypt(data[3]).decode()

    conn.close()

    return render_template(
        "edit.html",
        data=(data[0],data[1],data[2],decrypted)
    )

# -------------------------
# Delete password
# -------------------------

@app.route("/delete/<int:id>")
def delete(id):

    if not session.get("logged_in"):
        return redirect("/")

    conn = sqlite3.connect("database.db")

    conn.execute("DELETE FROM passwords WHERE id=?",(id,))

    conn.commit()
    conn.close()

    return redirect("/dashboard")

# -------------------------
# Logout
# -------------------------

@app.route("/logout")
def logout():

    session.clear()
    return redirect("/")

app.run(debug=True)