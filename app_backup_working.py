from flask import Flask, render_template, request, session, redirect
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    send_file
)

from pymongo import MongoClient
from bson.objectid import ObjectId

from reportlab.pdfgen import canvas

from database import add_notification
from database import workflows_collection
import io
import os


import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt





from routes.admin import admin

app = Flask(__name__)

app.secret_key = "AgentFlowAI@123"

app.register_blueprint(admin)



# ==========================
# MongoDB Connection
# ==========================


client = MongoClient(
    "mongodb+srv://gopinath:admin1234@cluster0.7cobbpr.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
    serverSelectionTimeoutMS=3000
)

db = client["multiagent"]



users_collection = db["users"]

tasks_collection = db["tasks"]

notifications_collection = db["notifications"]

reports_collection = db["reports"]

workflow_collection = db["workflow_history"]

activity_collection = db["activity_logs"]
assistant_collection = db["assistant_chats"]
workflow_execution_collection = db["workflow_execution"]



print("MongoDB Atlas Connected")



@app.route("/user_login")
def user_login():
    return render_template("user_login.html")





# ==========================
# Home
# ==========================


@app.route("/")
def home():

    return render_template(
        "index.html"
    )





from flask import (
    render_template,
    request,
    redirect,
    session
)

# ==========================
# User Login
# ==========================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        user = users_collection.find_one({
            "username": username,
            "password": password
        })

        if user:

            session["username"] = user["username"]
            session["role"] = user.get("role", "User")

            return redirect("/dashboard")

        return render_template(
            "login.html",
            error="Invalid Username or Password"
        )

    return render_template("login.html")

# ==========================
# User Dashboard
# ==========================

@app.route("/dashboard")
def dashboard():

    if "username" not in session:
        return redirect("/login")

    total_tasks = tasks_collection.count_documents({})

    completed_tasks = tasks_collection.count_documents({
        "status": "Completed"
    })

    pending_tasks = tasks_collection.count_documents({
        "status": "Pending"
    })

    total_reports = reports_collection.count_documents({})

    total_workflows = workflows_collection.count_documents({})

    total_agents = activity_collection.count_documents({})

    return render_template(
        "dashboard.html",
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks,
        total_reports=total_reports,
        total_workflows=total_workflows,
        total_agents=total_agents
    )


# ==========================
# User Logout
# ==========================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")




# ==========================
# Register User
# ==========================


@app.route("/register", methods=["GET","POST"])
def register():

    if request.method=="POST":

        user = {

            "username": request.form["username"],
            "email": request.form["email"],
            "password": request.form["password"],

            "role": "User",
            "status": "Offline",
            "last_login": "Never"

        }

        users_collection.insert_one(user)

        return redirect("/login")

    return render_template("register.html")



# ==========================
# Tasks
# ==========================


@app.route("/tasks")
def tasks():


    all_tasks=list(
        tasks_collection.find()
    )


    return render_template(

        "tasks.html",

        tasks=all_tasks

    )

@app.route("/my_tasks")
def my_tasks():

    username = session.get("username")

    if not username:
        return redirect("/login")


    tasks = list(
        tasks_collection.find({
            "username": username
        })
    )


    return render_template(
        "my_tasks.html",
        tasks=tasks
    )



@app.route("/create_task", methods=["POST"])
def create_task():

    task = {

        "task_name": request.form["task_name"],

        "agent_name": request.form["agent_name"],

        "priority": request.form["priority"],

        "due_date": request.form["due_date"],

        "status": "Pending",

        "username": session["username"]

    }


    tasks_collection.insert_one(task)


    add_notification(
        f"New Task Created: {task['task_name']}"
    )


    return render_template(
        "task_analysis.html",
        task_name=task["task_name"]
    )

@app.route("/complete_task/<task_id>")
def complete_task(task_id):


    tasks_collection.update_one(

        {
            "_id":ObjectId(task_id)
        },

        {
            "$set":
            {
                "status":"Completed"
            }
        }

    )


    add_notification(
        "Task Completed Successfully"
    )


    return redirect("/tasks")





@app.route("/delete_task/<task_id>")
def delete_task(task_id):


    tasks_collection.delete_one(

        {
            "_id":ObjectId(task_id)
        }

    )


    return redirect("/tasks")

# ==========================
# Notifications
# ==========================

@app.route("/notifications")
def notifications():

    data = list(
        notifications_collection.find()
    )

    return render_template(
        "notifications.html",
        notifications=data
    )





# ==========================
# AI Assistant
# ==========================
from datetime import datetime

@app.route("/assistant")
def assistant():

    return render_template(
        "assistant.html"
    )



@app.route("/ask_ai", methods=["POST"])
def ask_ai():

    question = request.form["question"].lower()


    if "task" in question:

        answer = "Tasks are used to manage workflow activities and track progress."


    elif "workflow" in question:

        answer = "Workflow executes Research Agent, Coding Agent, Testing Agent and Report Agent."


    elif "report" in question:

        answer = "Reports contain workflow execution summaries and project analysis."


    elif "agent" in question:

        answer = "Agents are intelligent modules that automate specific tasks."


    elif "hello" in question or "hi" in question:

        answer = "Hello! I am AgentFlow AI Assistant. How can I help you?"


    elif "who are you" in question:

        answer = "I am AgentFlow AI Assistant created to support your workflow automation platform."


    else:

        answer = "Sorry, I don't understand. Try asking about tasks, workflow, reports or agents."



    # Save chat history

    assistant_collection.insert_one({

        "question": question,

        "answer": answer,

        "time": datetime.now()

    })



    return render_template(

        "assistant.html",

        question=question,

        answer=answer

    )

@app.route("/assistant-history")
def assistant_history():

    chats = assistant_collection.find().sort(
        "time",
        -1
    )

    return render_template(
        "assistant_history.html",
        chats=chats
    )

# ==========================
# Agents
# ==========================


@app.route("/agents")
def agents():

    return render_template(
        "agents.html"
    )



@app.route("/workflow")
def workflow():

    return render_template(
        "workflow.html"
    )





# ==========================
# Agent Execution
# ==========================


@app.route("/run_research")
def run_research():


    return """
    <h1>Research Agent</h1>
    <p>Research Completed</p>
    <a href='/agents'>Back</a>
    """



@app.route("/run_coding")
def run_coding():


    return """
    <h1>Coding Agent</h1>
    <p>Coding Completed</p>
    <a href='/agents'>Back</a>
    """



@app.route("/run_testing")
def run_testing():


    return """
    <h1>Testing Agent</h1>
    <p>Testing Completed</p>
    <a href='/agents'>Back</a>
    """



@app.route("/run_report")
def run_report():

    reports_collection.insert_one({

        "title":"Workflow Report",

        "description":"Multi Agent Workflow Completed Successfully"

    })

    return redirect("/reports")



# ==========================
# Workflow History
# ==========================

@app.route("/workflow_history")
def workflow_history():

    workflows = list(
        workflow_collection.find().sort(
            "date",
            -1
        )
    )


    return render_template(

        "workflow_history.html",

        workflows=workflows

    )




# ==========================
# Activity Logs
# ==========================

@app.route("/activity_logs")
def activity_logs():

    logs = list(
        activity_collection.find().sort(
            "_id",
            -1
        )
    )


    return render_template(
        "activity_logs.html",
        logs=logs
    )




# ==========================
# Agent Monitor
# ==========================


@app.route("/agent_monitor")
def agent_monitor():


    agents=[

        {
            "name":"Research Agent",
            "status":"Running",
            "task":"Collecting information",
            "time":"Just now"
        },


        {
            "name":"Coding Agent",
            "status":"Idle",
            "task":"Waiting for workflow",
            "time":"5 minutes ago"
        },


        {
            "name":"Testing Agent",
            "status":"Running",
            "task":"Testing generated code",
            "time":"2 minutes ago"
        },


        {
            "name":"Report Agent",
            "status":"Completed",
            "task":"Generating final report",
            "time":"10 minutes ago"
        }

    ]


    return render_template(
        "agent_monitor.html",
        agents=agents
    )



# ==========================
# PDF Report
# ==========================


@app.route("/download_report")
def download_report():


    filename="task_report.pdf"


    pdf=canvas.Canvas(filename)



    pdf.drawString(
        100,
        800,
        "AgentFlow AI Report"
    )


    y=750


    tasks=list(
        tasks_collection.find()
    )



    for task in tasks:


        text=f"""
        {task.get('task_name')}
        -
        {task.get('status')}
        """


        pdf.drawString(
            50,
            y,
            text
        )


        y-=30



    pdf.save()



    return send_file(

        filename,

        as_attachment=True

    )


@app.route("/profile")
def profile():

    user = {

        "username": session.get("username"),

        "email": session.get("email"),

        "role": session.get("role")

    }


    return render_template(
        "profile.html",
        user=user
    )


# ==========================
# Reports
# ==========================

@app.route("/reports")
def reports():

    reports = list(
        reports_collection.find().sort(
            "_id",
            -1
        )
    )

    return render_template(
        "reports.html",
        reports=reports
    )

@app.route("/test-users")
def test_users():

    users = list(users_collection.find())

    return str(users)
print(app.url_map)



@app.route("/fix-users")
def fix_users():

    users_collection.update_many(
        {},
        {
            "$set": {
                "role": "User",
                "status": "Offline",
                "last_login": "Never"
            }
        }
    )

    return "Users Fixed"



@app.route("/user_management")
def user_management():

    users = list(users_collection.find())

    return render_template(
        "user_management.html",
        users=users
    )


@app.route("/analytics")
def analytics():

    total_users = users_collection.count_documents({})

    online_users = users_collection.count_documents({
        "status":"Online"
    })

    completed_tasks = tasks_collection.count_documents({
        "status":"Completed"
    })

    pending_tasks = tasks_collection.count_documents({
        "status":"Pending"
    })

    total_reports = reports_collection.count_documents({})

    return render_template(
        "analytics.html",
        total_users=total_users,
        online_users=online_users,
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks,
        total_reports=total_reports
    )

# ==========================
# Run Workflow
# ==========================

from datetime import datetime

@app.route("/run_workflow")
def run_workflow():

    print("WORKFLOW STARTED")

    workflow_data = {

        "workflow_name": "AI Multi Agent Workflow",

        "task": "Create AI Automation System",

        "status": "Completed",

        "date": datetime.now().strftime(
            "%d-%m-%Y %H:%M:%S"
        )

    }

    try:

        workflows_collection.insert_one(workflow_data)
        

        print("WORKFLOW SAVED")

    except Exception as e:

        print("DATABASE ERROR =", e)

    return render_template(
        "workflow_result.html",
        workflow=workflow_data
    )

# ==========================
# Run Application
# ==========================


if __name__=="__main__":


    app.run(
    host="0.0.0.0",
    port=5000,
    debug=True
)

   