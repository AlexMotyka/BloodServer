from flask import Flask
from dotenv import load_dotenv
import os
import requests

# list of server urls
servers = []


# print a nice greeting.
def sayHello():
    return '<p>GIVE ME YOUR BLOOD!</p>\n'


# EB looks for an 'application' callable by default.
application = Flask(__name__)

# add a rule for the index page.
application.add_url_rule('/', 'index', (lambda: sayHello()))

# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    load_dotenv()
    application.debug = True
    application.run()
