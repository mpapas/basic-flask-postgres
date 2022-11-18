import os
import psycopg2

from dotenv import load_dotenv

#import the flask class from the Flask package
from flask import Flask, render_template, request
from connect_tcp import init_connection_pool
from migrate import migrate_db

#create an object that allows us to listen / respond to incoming requests
app = Flask(__name__)

# added to help support AWS EBS deployment
application = app

#create a python list to store data in-memory for now
# transactions = [
#     ("2022-08-25", 70.00, "Checking"),
#     ("2022-08-25", 150.00, "Savings"),
#     ("2022-08-25", 15.34, "Checking"),
# ]

# initiate a connection pool to a Cloud SQL database
global db
db = init_connection_pool()

# creates required 'votes' table in database (if it does not exist)
migrate_db(db)

#register an endpoint using a decorator and specify how to respond
# @app.route("/")
# def hello():
#     return "Hello, world!"

#respond to browser request with HTML page (requires a static and templates folder)
@app.route("/", methods=["GET", "POST"])
def home():
    print(request.args) #print the query strings received with the GET request

    if request.method == "POST":
        print(request.form) #print any form data received as part of the request
        print(request.form.get("account")) #print specific form data received

        # append a tuple containing 3 fields of data to our transactions list
        # transactions.append(
        #     (
        #         request.form.get("date"),
        #         float(request.form.get("amount")),
        #         request.form.get("account"),
        #     )
        # )
        
        connection = db.getconn()
        
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO transactions VALUES (%s, %s, %s);", (
                    request.form.get("date"),
                    float(request.form.get("amount")),
                    request.form.get("account"),
                ))

        db.putconn(connection)

    context = {
        "title": "Add transaction"
    }

    return render_template("form.html", **context)


@app.route("/transactions", methods=["GET"])
def show_transactions():
    
    connection = db.getconn()

    with connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM transactions;")
            transactions = cursor.fetchall()

    db.putconn(connection)

    context = {
        "title": "Transactions",
        "entries": transactions
    }
    
    return render_template("transactions.html", **context)
