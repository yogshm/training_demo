from flask import Flask, render_template, request, redirect, url_for, session
import jwt
import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = "9876543211111"
JWT_SECRET = "jwtsecret123"

# here i'm using force data for login
USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "employee": {"password": "emp123", "role": "employee"}
}

# jwt decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = session.get("token")
        if not token:
            return redirect(url_for("index"))

        try:
            data = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            request.user = data
        except:
            return redirect(url_for("index"))

        return f(*args, **kwargs)
    return decorated

# endpoints
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    user = USERS.get(username)

    if user and user["password"] == password:
        token = jwt.encode({
            "username": username,
            "role": user["role"],
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        }, JWT_SECRET, algorithm="HS256")

        session["token"] = token
        return redirect(url_for("dashboard"))

    return "Invalid Credentials"

@app.route("/dashboard")
@token_required
def dashboard():
    return render_template(
        "dashboard.html",
        role=request.user["role"],
        username=request.user["username"]
    )

@app.route("/payment")
@token_required
def payment():
    if request.user["role"] != "admin":
        return "Access Denied"
    return "<h2>Payment Service (Admin Only)</h2>"


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

# main funtion
if __name__ == "__main__":
    app.run(debug=True)
    
