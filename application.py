from flask import Flask
from dotenv import load_dotenv
import os
import requests
import sys
import pymysql
import logger

connection = None
# list of server urls
servers = []



# print a nice greeting.
def sayHello():
    return '<p>GIVE ME YOUR BLOOD!</p>\n'

def connectDB():
    global connection
    try:
        if(connection is None):
            connection = pymysql.connect(host='bloodbasedb.cr4zxbqsmtxm.us-east-1.rds.amazonaws.com',
                                         user='root',
                                         password='capstone2019',
                                         port=3306,
                                         db='bloodbase',
                                         connect_timeout=5)
        elif(not connection.open):
            connection = pymysql.connect(host='bloodbasedb.cr4zxbqsmtxm.us-east-1.rds.amazonaws.com',
                                         user='root',
                                         password='capstone2019',
                                         port=3306,
                                         db='bloodbase',
                                         connect_timeout=5)
    except:
        logger.error("ERROR: Unexpected error: Could not connect to MySql instance.")


def getClients():
    try:
        connectDB()
        with connection.cursor() as cur:
            sql = "SELECT * FROM Clients"
            cur.execute(sql)
            result = cur.fetchall()
            cur.close()
            connection.close()
            # log to console
            print(result, file=sys.stdout)
            return "200"
    except Exception as e:
        print(e)
        return "400: " + e


# EB looks for an 'application' callable by default.
application = Flask(__name__)

# add a rule for the index page.
application.add_url_rule('/', 'index', (lambda: sayHello()))

application.add_url_rule('/clients', 'clients', (lambda: getClients()))

# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    load_dotenv()
    application.debug = True
    application.run()
