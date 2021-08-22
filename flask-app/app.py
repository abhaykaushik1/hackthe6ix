from flask import *
from authenticator import Authenticator
from mongodriver import MongoDriver
from flask_cors import CORS, cross_origin
from pymongo.mongo_client import MongoClient

import sys, json

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.secret_key = "345623219"

driver = MongoDriver()
authenticator = Authenticator(driver)

def user_sanity_check():
    """
    Check the browser cookie and the login status of the user with the given email 
    Whitelist users with a cookie and login status set to true
    Returns False if the user does not have a cookie, or has login status as false
    """
    user_email = driver.get_email_with_cookie(request.cookies.get('session_id'))
    
    if not user_email:
        return False
    return authenticator.get_user_login_status(user_email)

@app.route('/', methods=['GET', 'POST'])
def index():
    # Landing page
    # Check if they have a cookie
    email = driver.get_email_with_cookie(request.cookies.get('session_id'))
    user_id = driver.get_user_id_with_cookie(request.cookies.get('session_id'))
    if email is not None:
        return redirect("/home")
    # Else, redirect them to the login page
    return redirect("/login")

@app.route('/login', methods=['GET', 'POST'])
def sign_in():

    if user_sanity_check():
        # User is already logged in
        return redirect("/home")

    if request.method == "POST":

        # Extract information from the sign-in form
        form = request.form
        email_id = form["email"]
        password = form["password"]

        if form["submit"] == 'Register Now!':
            # User clicked on the register button, redirect them to that page
            return redirect("/register")

        if email_id != "" and password != "":
            
            response_code = authenticator.authenticate(email_id, password)
            if response_code:
                # Credentials are good, redirect them to the rest of the app
                # Set this user as logged in
                authenticator.set_user_login_status(email_id, True)
                # Redirect them to the rest of the app page
                redirect_response = make_response(redirect("/home"))
                # Set the user's browser cookie to the unique cookie id
                redirect_response.set_cookie('session_id', driver.get_cookie_with_email(email_id))
                return redirect_response
            else:
                return render_template("login.html", status="Invalid login.")
        else:
            # User left one of the fields empty
            return render_template("login.html", status="Email or password field is empty.")

    if "pchange" in request.args:
        # Render the login page with password change message
        return render_template("login.html", pchange=request.args["pchange"])
    else:
        # Render the login page
        return render_template("login.html")


@app.route('/register', methods=['GET', 'POST'])
def register():

    if user_sanity_check():
        # User is already logged in
        return redirect("/home")

    if request.method == "POST":

        # Extract information from the sign-in form
        form = request.form
        email_id = form["email"]
        username = form["username"]
        password = form["password"]
        password2 = form["password2"]
        status = form["status"]

        if email_id != "" and password != "":
            
            if password != password2:
                # Passwords do not match
                return render_template("register.html", status="Passwords do not match.")

            # Register the user and add them to the database
            response = authenticator.register(email_id, username, password)

            # Refer to authenticator's register function for meaning of code
            if not response:
                # Email is already in use
                return render_template("register.html", status="Error in registering")
            else:
                # The response returned by the authenticator is a unique cookie id for the user
                redirect_response = make_response(redirect("/verify"))
                # Set the user's browser cookie to the unique cookie id
                redirect_response.set_cookie('session_id', response)
                return redirect_response

        else:
            # User left one of the fields empty            
            return render_template("register.html", status="Email or password field is empty.")

    # Render the register page
    return render_template("register.html")

@app.route('/logout')
def logout():
    # Set this user as logged out
    authenticator.set_user_login_status(driver.get_email_with_cookie(request.cookies.get('session_id')), False)
    # Redirect the user to the logged out page
    logout_response = make_response(render_template("logout.html"))
    # Delete the user's cookie
    logout_response.delete_cookie('session_id')
    return logout_response

@app.route('/home')
def home():
    """
    This is the game
    """

    if not user_sanity_check():
        # Redirect user to login page
        return redirect("/login")

    user_id = driver.get_user_id_with_cookie(request.cookies.get('session_id'))
    