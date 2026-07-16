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

import io
import os


import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt


from routes.admin import admin



app = Flask(__name__)

app.register_blueprint(admin)
app.secret_key = "global-agent-secret-key"

app.secret_key = "AgentFlowAI@123"




# ==========================
# MongoDB Connection
# ==========================


client = MongoClient(
    "mongodb+srv://....",
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





# ==========================
# User Login Page
# ==========================


@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]


        # Permanent Admin Login

        if username == "admin" and password == "1234":

            session["username"] = "admin"
            session["role"] = "Admin"
            session["email"] = "admin@gmail.com"

            return redirect("/dashboard")


        # Registered User Login

        user = users_collection.find_one({

            "username": username,
            "password": password

        })


        if user:

            session["username"] = user["username"]
            session["role"] = user["role"]
            session["email"] = user["email"]

            return redirect("/dashboard")


        else:

            return "Invalid Username or Password"


    return render_template("login.html")





# ==========================
# User Dashboard
# ==========================

@app.route("/dashboard")
def dashboard():

    return render_template(
        "dashboard.html",
        total_tasks=0,
        completed_tasks=0,
        pending_tasks=0,
        total_reports=0,
        total_workflows=0,
        total_chats=0,
        total_agents=0
    )

# ==========================
# Register User
# ==========================


@app.route("/register", methods=["GET","POST"])
def register():

    if request.method=="POST":


        user = {

            "username":request.form["username"],

            "email":request.form["email"],

            "password":request.form["password"],

            "role":"User"

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
# Run Application
# ==========================


if __name__=="__main__":


    app.run(
    host="0.0.0.0",
    port=5000,
    debug=False
)

   