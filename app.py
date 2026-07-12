from flask import Flask, render_template, request, redirect, send_file
from pymongo import MongoClient
from bson.objectid import ObjectId
from reportlab.pdfgen import canvas
from flask_mail import Mail, Message
import io

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
from routes.admin import admin

app = Flask(__name__)
app.register_blueprint(admin)
app.secret_key = "global-agent-secret-key"


client = MongoClient("mongodb://localhost:27017/")
db = client["agentflow"]

tasks_collection = db["tasks"]
notifications_collection = db["notifications"]
users_collection = db["users"]
activity_collection = db["activity_logs"]
workflow_collection = db["workflow_history"]



@app.route('/')
def home():
    return render_template("index.html")


@app.route('/login', methods=['POST'])
def login():

    username = request.form['username']
    password = request.form['password']

    user = users_collection.find_one({
        "username": username
    })

    if user and user.get("password") == password:

     activity_collection.insert_one({
        "activity": f"{username} Logged In"
    })

    return redirect('/dashboard')

@app.route('/dashboard')
def dashboard():

    total_users = users_collection.count_documents({})

    total_tasks = tasks_collection.count_documents({})

    completed_tasks = tasks_collection.count_documents(
        {"status": "Completed"}
    )

    total_reports = notifications_collection.count_documents({})

    return render_template(
        "dashboard.html",
        total_users=total_users,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        total_reports=total_reports
    )


@app.route('/agents')
def agents():
    return render_template("agents.html")


@app.route('/workflow')
def workflow():
    return render_template("workflow.html")


@app.route('/reports')
def reports():
    return render_template("reports.html")


@app.route('/assistant')
def assistant():
    return render_template("assistant.html")




@app.route('/ask_ai', methods=['POST'])
def ask_ai():

    question = request.form['question']

    answer = ""

    if "login" in question.lower():

        answer = """
Use Flask Authentication

Create Login Form

Store Users in MongoDB

Validate Username and Password
"""

    elif "dashboard" in question.lower():

        answer = """
Create Dashboard Page

Display Task Statistics

Display Charts

Display Agent Status
"""

    elif "report" in question.lower():

        answer = """
Generate PDF Report

Use ReportLab Library

Download Report
"""

    else:

        answer = """
AI Suggestion:

Use Flask
Use MongoDB
Use Automation Workflow
"""

    return render_template(
        "assistant.html",
        answer=answer
    )


@app.route('/analytics')
def analytics():
    return render_template("analytics.html")


@app.route('/tasks')
def tasks():

    all_tasks = list(tasks_collection.find())

    return render_template(
        "tasks.html",
        tasks=all_tasks
    )


@app.route('/create_task', methods=['POST'])
def create_task():

    task = {

        "task_name": request.form['task_name'],

        "agent_name": request.form['agent_name'],

        "priority": request.form['priority'],

        "due_date": request.form['due_date'],

        "status": "Pending"

    }

    tasks_collection.insert_one(task)

    return redirect('/tasks')


@app.route('/complete_task/<task_id>')
def complete_task(task_id):

    tasks_collection.update_one(
        {"_id": ObjectId(task_id)},
        {"$set": {"status": "Completed"}}
    )

    activity_collection.insert_one({
        "activity": "Task Completed"
    })
    add_notification(
    "Task Completed Successfully"
)

    return redirect('/tasks')

@app.route('/delete_task/<task_id>')
def delete_task(task_id):

    tasks_collection.delete_one(
        {"_id": ObjectId(task_id)}
    )

    return redirect('/tasks')


@app.route('/notifications')
def notifications():

    notifications = list(
        notifications_collection.find()
    )

    return render_template(
        "notifications.html",
        notifications=notifications
    )


@app.route('/chart')
def chart():

    pending = tasks_collection.count_documents(
        {"status": "Pending"}
    )

    completed = tasks_collection.count_documents(
        {"status": "Completed"}
    )

    labels = ["Pending", "Completed"]
    values = [pending, completed]

    if sum(values) == 0:
        labels = ["No Tasks"]
        values = [1]

    plt.figure(figsize=(4, 4))
    plt.pie(values, labels=labels, autopct='%1.1f%%')

    img = io.BytesIO()

    plt.savefig(img, format='png')
    plt.close()

    img.seek(0)

    return send_file(
        img,
        mimetype='image/png'
    )


@app.route('/download_report')
def download_report():

    pdf_file = "task_report.pdf"

    c = canvas.Canvas(pdf_file)

    c.setFont("Helvetica-Bold", 18)
    c.drawString(100, 800, "AgentFlow Task Report")

    tasks = list(tasks_collection.find())

    y = 750

    for task in tasks:

        task_name = task.get("task_name", "N/A")
        agent_name = task.get("agent_name", "N/A")
        priority = task.get("priority", "N/A")
        status = task.get("status", "Pending")

        text = (
            f"{task_name} | "
            f"{agent_name} | "
            f"{priority} | "
            f"{status}"
        )

        c.drawString(50, y, text)

        y -= 25

        if y < 50:
            c.showPage()
            y = 750

    c.save()

    return send_file(
        pdf_file,
        as_attachment=True
    )

@app.route('/profile')
def profile():
    return render_template("profile.html")

@app.route('/settings')
def settings():
    return render_template("settings.html")

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        user = {
            "username": request.form['username'],
            "email": request.form['email'],
            "password": request.form['password']
        }

        users_collection.insert_one(user)

        return redirect('/')

    return render_template("register.html")


@app.route('/users')
def users():

    all_users = list(users_collection.find())

    html = "<h1>Registered Users</h1>"

    for user in all_users:
        html += f"""
        Username: {user.get('username')} <br>
        Email: {user.get('email')} <br><br>
        """

    return html


@app.route('/run_research')
def research_agent():

    result = run_research()

    return f"""
    <h1>Research Agent</h1>
    <pre>{result}</pre>
    <a href='/agents'>Back</a>
    """


@app.route('/run_coding')
def coding_agent():

    result = run_coding()

    return f"""
    <h1>Coding Agent</h1>
    <pre>{result}</pre>
    <a href='/agents'>Back</a>
    """


@app.route('/run_testing')
def testing_agent():

    result = run_testing()

    return f"""
    <h1>Testing Agent</h1>
    <pre>{result}</pre>
    <a href='/agents'>Back</a>
    """


@app.route('/run_report')
def report_agent():

    result = run_report()

    return f"""
    <h1>Report Agent</h1>
    <pre>{result}</pre>
    <a href='/agents'>Back</a>
    """



@app.route('/workflow_history')
def workflow_history():

    workflows = list(
        workflow_collection.find()
    )

    return render_template(
        "workflow_history.html",
        workflows=workflows
    )

from datetime import datetime
@app.route('/run_workflow')
def run_workflow():

    workflow_collection.insert_one({
        "workflow_name": "Multi Agent Workflow",
        "status": "Completed"
    })
    add_notification(
    "Workflow Executed Successfully"
)

    return redirect('/workflow_history')

@app.route('/activity_logs')
def activity_logs():

    logs = list(
        activity_collection.find()
    )

    return render_template(
        "activity_logs.html",
        logs=logs
    )

@app.route('/agent_monitor')
def agent_monitor():

    agents = [

        {
            "name": "Research Agent",
            "status": "Running"
        },

        {
            "name": "Coding Agent",
            "status": "Idle"
        },

        {
            "name": "Testing Agent",
            "status": "Running"
        },

        {
            "name": "Report Agent",
            "status": "Completed"
        }

    ]

    return render_template(
        "agent_monitor.html",
        agents=agents
    )


@app.route('/admin_analytics')
def admin_analytics():

    total_users = users_collection.count_documents({})
    total_tasks = tasks_collection.count_documents({})
    completed_tasks = tasks_collection.count_documents(
        {"status":"Completed"}
    )

    total_reports = notifications_collection.count_documents({})

    return render_template(
        "admin_analytics.html",
        total_users=total_users,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        total_reports=total_reports
    )

@app.route('/leaderboard')
def leaderboard():

    agents = [

        {
            "name": "Research Agent",
            "score": 95
        },

        {
            "name": "Coding Agent",
            "score": 90
        },

        {
            "name": "Testing Agent",
            "score": 85
        },

        {
            "name": "Report Agent",
            "score": 80
        }

    ]

    agents = sorted(
        agents,
        key=lambda x: x["score"],
        reverse=True
    )

    return render_template(
        "leaderboard.html",
        agents=agents
    )



if __name__ == "__main__":
   app.run(debug=True)