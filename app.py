from flask import Flask, request, render_template, redirect, url_for, jsonify
from flask_login import LoginManager, UserMixin, \
                                login_required, login_user, logout_user
import json

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
import traceback


app = Flask(__name__)

# flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login" #Whenever the user needs to login, it will look for the app.route with /login

# config
app.config.update(
    DEBUG = True,
    SECRET_KEY = 'secret_xxx'
)

@app.route('/')
@app.route('/main')
@login_required
def main():

    return render_template("main.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        name = request.form["name"]
        user = User(name, email)
        login_user(user)  # Logs them in, flask makes a session

        if user.is_authenticated:
            print("authenticated")

            try:
             saveUserInSpreadsheet(name, email)
            except:
                print("rip in peace in peace")
        else:
            print("Could not authenticate")
        return redirect(url_for('main'))

    else:
        return render_template("index.html")


def saveUserInSpreadsheet(name, email):

    try:
        scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
                 "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
        client = gspread.authorize(creds)

        spreadsheet = client.open("email_subscribers").worksheet("Signups")
        spreadsheet.append_row([name, email, str(datetime.datetime.now())])
    except Exception as e:
        print("Couldn't save user in spreadsheet")
        traceback.print_exc()
        print(str(e))



# callback to reload the user object
@login_manager.user_loader
def load_user(usr):
    return User(usr, usr)

# handle login failed
@app.errorhandler(401)
def page_not_found(e):
    return ('<p>Login failed</p>')

#  user model, inheriting from the defualt UserMixin class, which contains methods like is_active and is_authenticated
class User(UserMixin):
    def __init__(self, name, id, active=True):
        self.name = str(name)
        self.id = str(id)
        self.active = active
    #just returns their ID, name, and password
    def __repr__(self):
        return "%d/%s/%s" % (self.id, self.name, self.password)

if __name__ == '__main__':
    app.run()