from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, make_response
from functools import wraps
import secrets
import jwt
# import RPi.GPIO as GPIO

flaskApp = Flask(__name__)
flaskApp.secret_key = secrets.token_hex(16)

users = {
    "admin": "password"
}

# Generate a JWT token for a user
def generate_token(username):
    payload = {"username": username}
    token = jwt.encode(payload, flaskApp.secret_key, algorithm = "HS256")
    return token


def tokenRequired(func):
    @wraps(func)
    def decoratedFunction(*args, **kwargs):
        token = request.cookies.get("token")

        if not token:
            # If the token is missing, return an error message
            return redirect(url_for("login"))

        try:
            # Verify and decode the token
            payload = jwt.decode(token, flaskApp.secret_key, algorithms = ["HS256"])
            username = payload.get("username")

            # You can perform additional checks here, e.g., verify the user in a database

        except jwt.ExpiredSignatureError:
            return redirect(url_for("login"))
        except jwt.DecodeError:
            return redirect(url_for("login"))

        # If token validation is successful, call the original view function
        return func(*args, **kwargs)

    return decoratedFunction

@flaskApp.route("/")
@tokenRequired
def index():
    return render_template('index.html')


@flaskApp.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    userName = request.form["username"]
    password = request.form["password"]

    if userName in users and users[userName] == password:
        token = generate_token(userName)
        response = make_response(jsonify({"token": token}))
        response.set_cookie("token", token)
        return response
    else:
        return jsonify({"message": "Login failed. Please check your credentials."}), 401


@flaskApp.route('/toggle/<buttonNo>')
@tokenRequired
def toggle(buttonNo):
    print(f"button pressed: {buttonNo}")
    return redirect(url_for("index"))

if __name__ == "__main__":
    flaskApp.run(debug = True)