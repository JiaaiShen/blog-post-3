from flask import Flask, g, current_app, render_template, request

import sqlite3

app = Flask(__name__)

def get_message_db():
    if 'message_db' not in g:
        g.message_db = sqlite3.connect("messages_db.sqlite")

    with current_app.open_resource('init.sql') as f:
        g.message_db.executescript(f.read().decode('utf8'))

    return g.message_db

def insert_message(request):
    message = request.form["message"]
    handle = request.form["handle"]

    db = get_message_db()

    cursor = db.cursor()
    cursor.execute(
        'INSERT INTO messages (handle, message) VALUES (?, ?)',
        (handle, message)
    )
    db.commit()

    db.close()

    return(message, handle)

def random_messages(n):
    db = get_message_db()

    cursor = db.cursor
    cursor.execute(f'SELECT * FROM messages ORDER BY RANDOM() LIMIT {n}')
    result = cursor.fetchall()
    db.close()
    
    return result

@app.route("/", methods = ["POST", "GET"])
def submit():
    if request.method == "GET":
        return render_template("submit.html")
    else:
        message, handle = insert_message(request)
        return render_template("submit.html", message=message, handle=handle)

@app.route("/view/")
def view():
    messages = random_messages(5)
    return render_template("view.html", messages=messages)
