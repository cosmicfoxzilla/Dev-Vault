from flask import Flask, jsonify, request, render_template, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import timedelta
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///devvault.db"
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.permanent_session_lifetime = timedelta(days=30)
db = SQLAlchemy(app)

#user model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

#data model
class DevData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    level = db.Column(db.String(100), nullable=False)

#routes
@app.route("/api/home")
@app.route("/")
@app.route("/index")
@app.route("/home")
def home():
    if "user_id" in session:
        return redirect(url_for("dashboard_page"))
    return render_template("index.html")
#===========================USER REGISTER===========================
@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data:
        return jsonify({
            "error": "cant access details"
        }), 400
    username = data.get("username")
    password = data.get("password")
    if username is None or not isinstance(username, str) or username == "":
        return jsonify({
            "error": "username must be a string"
        }), 400
    if password is None or not isinstance(password, str) or password == "":
        return jsonify({
            "error": "Password should be defined"
        }), 400
    if len(password) < 8:
        return jsonify({
            "error": "Password must be atleast 8 characters"
        }), 400
    if not any(c.isupper() for c in password):
        return jsonify({
            "error": "Password must contain atleast one uppercase character (A, B)"
        }), 400
    if not any(c.islower() for c in password):
        return jsonify({
            "error": "Password must contain atleast one lowercase character (a, b)"
        }), 400
    if not any(c.isdigit() for c in password):
        return jsonify({
            "error": "Password must contain atleast one digit"
        }), 400
    if not any(not c.isalnum() for c in password):
        return jsonify({
            "error": "Password must contain atleast one special character"
        }), 400
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({
            "message": "Username already exist"
        }), 409
    user_register = User(username=username, password=generate_password_hash(password))
    db.session.add(user_register)
    db.session.commit()
    session.permanent = True
    session["user_id"] = user_register.id
    session["username"] = user_register.username
    return jsonify({
        "message": "Account created successfully!"
    }), 201

#===========================USER LOGIN===========================
@app.route("/login")
def loginPage():
    if "user_id" in session:
        return redirect(url_for("dashboard_page"))
    return render_template("login.html")

@app.route("/register")
def RegisterPage():
    if "user_id" in session:
        return redirect(url_for("dashboard_page"))
    return render_template("register.html")


@app.route("/dashboard")
def dashboard_page():
    if not "user_id" in session:
        return redirect(url_for("loginPage"))
    return render_template("dashboard.html")


@app.route("/add")
def add():
    return render_template("add.html")



@app.route("/api/login", methods=["POST"])
def login():
    if "user_id" in session:
        return jsonify({
            "loginAlert": "User is already logged in"
        }), 409
    data = request.get_json()
    if not data:
        return jsonify({
            "error": "cant access data"
        })
    username = data.get("username")
    password = data.get("password")
    if username is None or not isinstance(username, str) or username == "":
        return jsonify({
            "error": "username must be a string"
        }), 400
    if password is None or not isinstance(password, str) or password == "":
        return jsonify({
            "error": "Password should be defined"
        }), 400
    if len(password) < 8:
        return jsonify({
            "error": "Password must be atleast 8 characters"
        }), 400
    if not any(c.isupper() for c in password):
        return jsonify({
            "error": "Password must contain atleast one uppercase character (A, B)"
        }), 400
    if not any(c.islower() for c in password):
        return jsonify({
            "error": "Password must contain atleast one lowercase character (a, b)"
        }), 400
    if not any(c.isdigit() for c in password):
        return jsonify({
            "error": "Password must contain atleast one digit"
        }), 400
    if not any(not c.isalnum() for c in password):
        return jsonify({
            "error": "Password must contain atleast one special character"
        }), 400
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({
            "error": "Invalid username or password"
        }), 404
    check_hashed_password = check_password_hash(user.password, password)
    if check_hashed_password:
        session.permanent = True
        session["user_id"] = user.id
        session["username"] = user.username
        return jsonify({
            "loginMsg": "Login successful!"
        }), 200
    else:
        return jsonify({
            "error": "invalid username or password"
        }), 404

#===========================LOGOUT ROUTE===========================
@app.route("/api/logout")
def logout():
    session.clear()
    if not "user_id" in session:
        return redirect(url_for("dashboard_page"))
    return jsonify({
        "loginMsg": "User logout successfully"
    }), 200

#===========================SESSION USER PROFILE===========================
@app.route("/api/users/<int:user_id>", methods=["GET"])
def getUserProfile(user_id):
    user = User.query.filter_by(id=user_id).first()

    # Check if user exists first
    if not user:
        return jsonify({
            "error": "User not found"
        }), 404

    # Check if the logged-in user owns this profile
    if session.get("user_id") != user.id:
        return jsonify({
            "error": "Unauthorized access"
        }), 403

    return jsonify({
        "message": "Found user!",
        "user_details": {
            "username": user.username
        }
    }), 200

#===========================USER DETAILS UPDATE===========================
@app.route("/api/users/edit/<int:user_id>", methods=["PATCH"])
def edituser(user_id):
    data = request.get_json()
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({
            "error": "user not found"
        }), 404
    user_session_id = session.get("user_id")
    if user_session_id == user.id:
        if "username" in data:
            username = data.get("username")
            if not isinstance(username, str):
                return jsonify({"message": "Username must be a string"})
            if username is None or username == "":
                return jsonify({"message": "Username must be a string or valid character"})
            existing = User.query.filter_by(username=username).first()
            if existing and existing.id != user.id:
                return jsonify({
                    "error": "username already exists!"
                }), 409
            user.username = username
        db.session.commit()
        return jsonify({
            "username": user.username
        })
    return jsonify({
        "error": "cant access other user's data"
    }), 401

#===========================USER Dev Project===========================
@app.route("/api/dashboard", methods=["GET"])
def dashboard():
    session_info = session.get("user_id")
    if not session_info:
        return redirect(url_for("loginPage"))
    devdata = DevData.query.filter_by(user_id=session["user_id"]).all()
    userdata = User.query.filter_by(id=session_info).first()
    if userdata:
        return jsonify({
            "username": userdata.username
        })
    return jsonify([
        {
        "projectID": project.id,
        "name": project.name,
        "level": project.level
        }
        for project in devdata
    ])


@app.route("/api/add", methods=["POST"])
def addProject():
    data = request.get_json()
    devCntName = data.get("devCntName")
    devcntlvl = data.get("devcntlvl")
    differentLvls = ["easy", "medium", "hard"]
    if "user_id" not in session:
        return jsonify({
            "error": "Login required!"
        }), 401
    if devCntName is None or devCntName == "" or not isinstance(devCntName, str):
        return jsonify({
            "error": "the dev project name must be a valid string"
        }), 400
    if devcntlvl not in differentLvls:
        return jsonify({
            "error": "Project level is invalid"
        }), 404
    if devcntlvl is None or devcntlvl == "":
        return jsonify({
            "error": "Project level is invalid"
        }), 404
    add_project = DevData(user_id=session["user_id"], name=devCntName, level=devcntlvl)
    db.session.add(add_project)
    db.session.commit()
    return jsonify({
        "mmessage": "project data created successfully!",
        "content": {
            "projectName": add_project.name,
            "projectLvl": add_project.level
        }
    }), 201 

@app.route("/api/dashboard/projects/edit/<int:id>", methods=["PATCH"])
def edit(id):
    data = request.get_json()
    devdata = DevData.query.filter_by(id=id, user_id=session.get("user_id")).first()
    differentLvls = ["easy", "medium", "hard"]
    if not devdata:
        return jsonify({
            "error": "Content not found!"
        }), 404
    if "devCntName" in data:
        devdatacntname = data.get("devCntName")
        if devdatacntname is None or not isinstance(devdatacntname, str) or devdatacntname == "":
            return jsonify({
                "error": "The project name must be a string"
            }), 400
        devdata.name = devdatacntname
    if "devcntlvl" in data:
        devdatacntlvl = data.get("devcntlvl")
        if devdatacntlvl is None or not isinstance(devdatacntlvl, str) or devdatacntlvl == "" or devdatacntlvl not in differentLvls:
            return jsonify({
                "error": "The project level must be (easy, medium or hard)"
            }), 400
        devdata.level = devdatacntlvl
    db.session.commit()
    return jsonify({
        "message": "Data saved succesfully!"
    })

@app.route("/api/dashboard/projects/delete/<int:id>", methods=["DELETE"])
def deleteProject(id):
    devdata = DevData.query.filter_by(id=id, user_id=session.get("user_id")).first()
    if not devdata:
        return jsonify({
            "error": "data nor found"
        }), 404
    db.session.delete(devdata)
    db.session.commit()
    return jsonify({
        "message": "data deleted successfully"
    }), 201
    
@app.route("/api/dashboard/projects/<int:id>", methods=["GET"])
def getProject(id):
    devdata = DevData.query.filter_by(id=id, user_id=session.get("user_id")).first()
    if not devdata:
        return jsonify({
            "error": "project details not found!"
        }), 404
    projectCreator = devdata.user_id
    user = User.query.filter_by(id=projectCreator).first()
    return jsonify({
        "message": "project found successfuly!",
        "projectName": devdata.name,
        "projectLevel": devdata.level,
        "projectID": devdata.id,
        "projectCreator": user.username 
    })

@app.route("/api/projects", methods=["GET"])
def getProjects():
    if not "user_id" in session:
        return jsonify({
            "error": "Authintication Failed"
        })
    projects = DevData.query.filter_by(user_id=session.get("user_id")).all()
    if not projects:
        return jsonify({
            "error": "No projects found"
        })
    return jsonify([{
        "projectName": p.name,
        "projectLevel": p.level,
        "projectByUser": p.user_id,
        "projectId": p.id,
    } for p in projects
    ])

@app.route("/edit/<int:project_id>")
def editpage(project_id):
    project = DevData.query.filter_by(id=project_id, user_id=session.get("user_id")).first()
    return render_template("edit.html", projectData = project)


with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
