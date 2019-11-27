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
    print("Query: " + query,file=sys.stdout)
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


def authenticateClient():
    password = request.args.get('password')
    email = request.args.get('email')

    query = "SELECT * FROM bloodbase.Clients WHERE Password = '{}' AND Email = '{}';".format(password, email)

    repsonse = executeGetQuery(query)
    decodedRes = json.loads(repsonse)

    if len(decodedRes) == 0:
        return "False"
    else:
        return "True"


def checkIfClientExists(email):
    query = "SELECT Email FROM Clients WHERE Email = '{}';".format(email)
    result = executeGetQuery(query)
    decodedResult = json.loads(result)
    if len(decodedResult) == 0:
        return False
    else:
        return True


def createBPActivity():

    bp = request.form.get('bp')
    clientId = request.form.get('clientId')
    timestamp = request.form.get('timestamp')
    systolic = request.form.get('systolic')
    diastolic = request.form.get('diastolic')

    query = """INSERT INTO `bloodbase`.`BloodPressure` (`BPID`, `ClientID`, `Time`, `Systolic`, `Diastolic`) 
                    VALUES ({}, {}, {}, {}, {});""".format(bp, clientId, timestamp, systolic, diastolic)

    response = executePostQuery(query)

    return response


def getBP():

    clientId = request.args.get('clientId')

    query = "SELECT * FROM bloodbase.BloodPressure WHERE ClientID = {}".format(clientId)

    response = executeGetQuery(query)
    return response


def getMedications():

    clientId = request.args.get('id')

    query = "SELECT * FROM bloodbase.MedSchedule WHERE ClientMedID = '{}';".format(clientId)

    response = executeGetQuery(query)

    return response

def getMedicationDetails():
    clientMedId = request.args.get('clientMedId')

    query = "SELECT * FROM `bloodbase`.`MedSchedule` WHERE `ClientMedID` = {}".format(clientMedId)

    response = executeGetQuery(query)

    return response


def createMedication():

    clientMedId = request.form.get('clientMedId')
    clientId = request.form.get('clientId')
    medId = request.form.get('medId')
    time = request.form.get('time')
    days = request.form.get('days')
    notes = request.form.get('notes')
    # TODO: figure out how this will be stored in the db
    startDate = request.form.get('startDate')
    # TODO: not sure how to store this in the database
    currentlyTaking = request.form.get('currentlyTaking')

    query = """INSERT INTO `bloodbase`.`MedSchedule` (`ClientMedID`, `MedID`, `Time`, `Days`, `Notes`, `StartDate`,
            `currentlyTaking`) VALUES ({}, {}, '{}', '{}', '{}', '{}', '{}');""".format(clientMedId, medId, time, days, notes, startDate, currentlyTaking)

    print("Query: " + query, file=sys.stdout)
    response = executePostQuery(query)
    return response

def updateMedication():

    clientMedId = request.form.get('clientMedId')
    clientId = request.form.get('clientId')
    medId = request.form.get('medId')
    time = request.form.get('time')
    # TODO: figure out how this will be stored in the db
    days = request.form.get('days')
    notes = request.form.get('notes')
    # TODO: figure out how this will be stored in the db
    startDate = request.form.get('startDate')
    currentlyTaking = request.form.get('currentlyTaking')

    query = """UPDATE `bloodbase`.`MedSchedule` SET `ClientMedID` = '{}',
            `MedID` = '{}', `Time` = '{}', `Days` = '{}', `Notes` = '{}', `StartDate` = '{}',
            `currentlyTaking` = '{}' WHERE `ClientMedID` = '{}';""".format(clientMedId, medId, time, days,
                                                                           notes, startDate, currentlyTaking, clientId)

    response = executePostQuery(query)
    return response


# EB looks for an 'application' callable by default.
application = Flask(__name__)

# add a rule for the index page.
application.add_url_rule('/', 'index', (lambda: sayHello()))

application.add_url_rule('/getClients', 'clients', (lambda: getClients()))
application.add_url_rule('/authenticate', 'authenticate', (lambda: authenticateClient()))
application.add_url_rule('/createClient', 'client', (lambda: createClient()), methods=['POST'])

application.add_url_rule('/createBP', 'bp', (lambda: createBPActivity()), methods=['POST'])
application.add_url_rule('/getBP', 'getBp', (lambda: getBP()))

application.add_url_rule('/updateMed', 'medUpdate', (lambda: updateMedication()), methods=['POST'])
application.add_url_rule('/createMed', 'medCreate', (lambda: createMedication()), methods=['POST'])
application.add_url_rule('/getMeds', 'meds', (lambda: getMedications()))
application.add_url_rule('/getMedDetails', 'medDetails', (lambda: getMedicationDetails()))


# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    load_dotenv()
    application.debug = True
    application.run()
