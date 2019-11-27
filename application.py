from flask import Flask
from flask import request
from dotenv import load_dotenv
import os
import requests
import sys
import pymysql
import logger
import json

connection = None
# list of server urls
servers = []


def sayHello():
    return '<p>GIVE ME YOUR BLOOD!</p>\n'


def connectDB():
    # this method creates a connection if an open one does not yet exist
    # this method should be called whenever you want to execute a query
    global connection
    try:
        if connection is None:
            connection = pymysql.connect(host='bloodbasedb.cr4zxbqsmtxm.us-east-1.rds.amazonaws.com',
                                         user='root',
                                         password='capstone2019',
                                         port=3306,
                                         db='bloodbase',
                                         connect_timeout=5)
        elif not connection.open:
            connection = pymysql.connect(host='bloodbasedb.cr4zxbqsmtxm.us-east-1.rds.amazonaws.com',
                                         user='root',
                                         password='capstone2019',
                                         port=3306,
                                         db='bloodbase',
                                         connect_timeout=5)
    except:
        logger.error("ERROR: Unexpected error: Could not connect to MySql instance.")


def executePostQuery(query):
    try:
        connectDB()
        with connection.cursor() as cur:
            cur.execute(query)
            connection.commit()
            cur.close()
            connection.close()
            return "200"
    except Exception as e:
        print(e)
        return "400: " + e


def executeGetQuery(query):
    try:
        connectDB()
        with connection.cursor() as cur:
            cur.execute(query)
            result = cur.fetchall()
            cur.close()
            connection.close()
            jsonResponse = json.dumps(result)
            return jsonResponse
    except Exception as e:
        print(e)
        return "400: " + e


def getClients():
    query = "SELECT * FROM Clients"
    response = executeGetQuery(query)
    return response


def createClient():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')

    exists = checkIfClientExists(email)

    if exists:
        return "Account exists already"
    else:
        query = "INSERT INTO bloodbase.Clients (`Name`, `Email`, `Password`) VALUES ('{}', '{}', '{}');".format(name, email, password)
        print("Query: " + query, file=sys.stdout)
        response = executePostQuery(query)
        return response


def checkIfClientExists(email):
    query = "SELECT Email FROM Clients WHERE Email = '{}';".format(email)
    result = executeGetQuery(query)
    decodedResult = json.loads(result)
    if len(decodedResult) == 0:
        return False
    else:
        return True

# EB looks for an 'application' callable by default.
application = Flask(__name__)

# add a rule for the index page.
application.add_url_rule('/', 'index', (lambda: sayHello()))

application.add_url_rule('/getClients', 'clients', (lambda: getClients()))

application.add_url_rule('/createClient', 'client', (lambda: createClient()), methods=['POST'])

# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    load_dotenv()
    application.debug = True
    application.run()
