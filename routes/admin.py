from flask import send_file
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from database import activity_collection
from datetime import datetime

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    request,
    session,
    send_file
)

from database import (
    users_collection,
    tasks_collection,
    reports_collection,
    workflows_collection,
    workflow_history_collection
)

from functools import wraps

from database import (
    users_collection,
    tasks_collection,
    reports_collection,
    workflows_collection
)

from bson.objectid import ObjectId

from reportlab.pdfgen import canvas

import os



admin = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin"
)



# -------------------------
# Admin Login Protection
# -------------------------

def admin_required(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        if "admin" not in session:

            return redirect(
                url_for("admin.admin_login")
            )

        return func(*args, **kwargs)

    return wrapper




# -------------------------
# Admin Login
# -------------------------

@admin.route("/login", methods=["GET","POST"])
def admin_login():

    if request.method == "POST":

        username = request.form["username"]

        password = request.form["password"]


        if username == "admin" and password == "admin123":

            session["admin"] = username


            return redirect(
                url_for("admin.admin_dashboard")
            )


    return render_template(
        "admin_login.html"
    )





# -------------------------
# Logout
# -------------------------

@admin.route("/logout")
def admin_logout():

    session.pop(
        "admin",
        None
    )


    return redirect(
        url_for("admin.admin_login")
    )





# -------------------------
# Admin Dashboard
# -------------------------

@admin.route("/")
@admin_required
def admin_dashboard():


    data = {


        "users":
        users_collection.count_documents({}),


        "tasks":
        tasks_collection.count_documents({}),


        "reports":
        reports_collection.count_documents({}),


        "workflows":
        workflows_collection.count_documents({})

    }



    return render_template(

        "admin_dashboard.html",

        data=data

    )





# -------------------------
# User Management
# -------------------------

@admin.route("/users")
@admin_required
def manage_users():


    users = users_collection.find()


    return render_template(

        "users.html",

        users=users

    )





# -------------------------
# Delete User
# -------------------------

@admin.route("/delete-user/<id>")
def delete_user(id):

    users_collection.delete_one(
        {
            "_id": ObjectId(id)
        }
    )


    activity_collection.insert_one({

        "action": "Deleted User",

        "user": "Admin",

        "date": datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    })


    return redirect(
        url_for("admin.manage_users")
    )


# -------------------------
# Workflow Monitor
# -------------------------

@admin.route("/workflows")
@admin_required
def workflow_monitor():


    workflows = workflows_collection.find()


    activity_collection.insert_one({

    "action": "Workflow Executed",

    "user": "System",

    "date": datetime.now().strftime("%d-%m-%Y %H:%M:%S")

})


    return render_template(

        "workflow.html",

        workflows=workflows

    )





# -------------------------
# Analytics
# -------------------------

@admin.route("/analytics")
@admin_required
def admin_analytics():


    data = {


        "users":
        users_collection.count_documents({}),


        "tasks":
        tasks_collection.count_documents({}),


        "reports":
        reports_collection.count_documents({}),


        "workflows":
        workflows_collection.count_documents({})

    }



    return render_template(

        "admin_analytics.html",

        data=data

    )





# -------------------------
# Notifications
# -------------------------

@admin.route("/notifications")
@admin_required
def admin_notifications():


    notifications = [


        {
            "title":
            "New User Registered",

            "message":
            "New user joined platform"

        },


        {
            "title":
            "Workflow Completed",

            "message":
            "AI workflow completed successfully"

        },


        {
            "title":
            "Report Generated",

            "message":
            "New report created"

        }

    ]



    return render_template(

        "notifications.html",

        notifications=notifications

    )





# -------------------------
# Agent Leaderboard
# -------------------------

@admin.route("/leaderboard")
@admin_required
def agent_leaderboard():


    agents = [


        {
            "name":
            "Research Agent",

            "tasks":
            45,

            "success":
            "95%"

        },


        {
            "name":
            "Coding Agent",

            "tasks":
            38,

            "success":
            "92%"

        },


        {
            "name":
            "Testing Agent",

            "tasks":
            32,

            "success":
            "90%"

        },


        {
            "name":
            "Report Agent",

            "tasks":
            28,

            "success":
            "96%"

        }

    ]



    return render_template(

        "leaderboard.html",

        agents=agents

    )

@admin.route("/workflow-history")
def workflow_history():

    history = workflow_history_collection.find()

    return render_template(
        "workflow_history.html",
        history=history
    )

# -------------------------
# Download PDF Report
# -------------------------

@admin.route("/download-report")
def download_report():

    filename = "admin_report.pdf"


    doc = SimpleDocTemplate(filename)


    styles = getSampleStyleSheet()


    content = []


    title = Paragraph(
        "AI Workflow Automation - Admin Report",
        styles["Title"]
    )

    content.append(title)

    content.append(Spacer(1,20))


    users = users_collection.count_documents({})

    tasks = tasks_collection.count_documents({})

    reports = reports_collection.count_documents({})

    workflows = workflows_collection.count_documents({})


    data = [

        f"Total Users : {users}",

        f"Total Tasks : {tasks}",

        f"Total Reports : {reports}",

        f"Total Workflows : {workflows}"

    ]


    for item in data:

        content.append(
            Paragraph(
                item,
                styles["Normal"]
            )
        )

        content.append(
            Spacer(1,10)
        )


    doc.build(content)

    activity_collection.insert_one({

    "action": "Downloaded PDF Report",

    "user": "Admin",

    "date": datetime.now().strftime("%d-%m-%Y %H:%M:%S")

})


    return send_file(
        filename,
        as_attachment=True
    )

@admin.route("/system-stats")
def system_stats():

    data = {

        "users": users_collection.count_documents({}),

        "tasks": tasks_collection.count_documents({}),

        "reports": reports_collection.count_documents({}),

        "workflows": workflows_collection.count_documents({})

    }


    return render_template(
        "system_stats.html",
        data=data
    )

@admin.route("/system-health")
def system_health():

    return render_template(
        "system_health.html"
    )

@admin.route("/activity")
def admin_activity():

    logs = activity_collection.find().sort(
        "_id",
        -1
    )


    return render_template(
        "admin_activity.html",
        logs=logs
    )

