from flask import Flask, g, current_app, render_template, request

import sqlite3

app = Flask(__name__)

# root directory of our webapp
@app.route("/")
def base():
    # render the base.html template
    return render_template("base.html")

def get_message_db():
    # check whether there is a database called message_db
    # in the g attribute of the app
    if 'message_db' not in g:
        # connect to the database
        g.message_db = sqlite3.connect("messages_db.sqlite")

    # execute the SQL command in the init.sql file
    with current_app.open_resource('init.sql') as f:
        g.message_db.executescript(f.read().decode('utf8'))

    # return the connection g.message_db
    return g.message_db

def insert_message(request):
    # extract the message and the handle from request
    message = request.form["message"]
    handle = request.form["handle"]

    # connect to the database
    db = get_message_db()

    # use a cursor to insert the message into the database
    cursor = db.cursor()
    cursor.execute(
        'INSERT INTO messages (handle, message) VALUES (?, ?)',
        (handle, message)
    )
    # save the insertion
    db.commit()

    # close the database connection
    db.close()

    return(message, handle)

# ensure the submission page supports both POST and GET methods
@app.route("/submit/", methods = ["POST", "GET"])
def submit():
    # render the submit.html template in the GET case
    if request.method == "GET":
        return render_template("submit.html")
    # call the insert_message() function 
    # and render the submit.html with parameters
    # in the POST case
    else:
        message, handle = insert_message(request)
        return render_template("submit.html", message=message, handle=handle)

def random_messages(n):
    # connect to the database
    db = get_message_db()

    # use a cursor to select a collection of n random messages
    # from the database
    cursor = db.cursor()
    cursor.execute(f'SELECT * FROM messages ORDER BY RANDOM() LIMIT {n}')
    result = cursor.fetchall()

    # close the database connection
    db.close()

    return(result)

@app.route("/view/")
def view():
    # grab 5 random messages
    messages = random_messages(5)
    # render the view.html template with the messages as an argument
    return render_template("view.html", messages=messages)