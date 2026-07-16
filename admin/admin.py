from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    request,
    session
)

from functools import wraps
from bson.objectid import ObjectId
from datetime import datetime


from database import (
    users_collection,
    tasks_collection,
    reports_collection,
    workflows_collection,
    notifications_collection
)



# ==========================
# Blueprint
# ==========================

admin = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin"
)



# ==========================
# Admin Protection
# ==========================

def admin_required(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        if "admin" not in session:

            return redirect(
                url_for("admin.admin_login")
            )

        return func(*args, **kwargs)


    return wrapper




# ==========================
# Admin Login
# ==========================

@admin.route("/login", methods=["GET","POST"])
def admin_login():

    if request.method == "POST":

        username = request.form["username"]

        password = request.form["password"]


        if username == "admin" and password == "1234":


            session["admin"] = username


            return redirect(
                url_for(
                    "admin.admin_dashboard"
                )
            )


        else:

            return "Invalid Username or Password"



    return render_template(
        "admin_login.html"
    )





# ==========================
# Logout
# ==========================

@admin.route("/logout")
def admin_logout():


    session.pop(
        "admin",
        None
    )


    return redirect(
        url_for(
            "admin.admin_login"
        )
    )






# ==========================
# Dashboard
# ==========================

@admin.route("/")
@admin_required
def admin_dashboard():


    data = {


        "users":
        users_collection.count_documents({}),



        "online_users":
        users_collection.count_documents({
            "status":"Online"
        }),



        "offline_users":
        users_collection.count_documents({
            "status":"Offline"
        }),



        "tasks":
        tasks_collection.count_documents({}),



        "reports":
        reports_collection.count_documents({}),



        "workflows":
        workflows_collection.count_documents({}),



        "notifications":
        notifications_collection.count_documents({})

    }



    print(
        "ADMIN DATA ==========>",
        data
    )



    return render_template(

        "admin.html",

        total_users=data["users"],

        online_users=data["online_users"],

        offline_users=data["offline_users"],

        total_tasks=data["tasks"],

        total_reports=data["reports"],

        total_workflows=data["workflows"],

        total_notifications=data["notifications"]

    )







# ==========================
# Users Management
# ==========================

@admin.route("/users")
@admin_required
def manage_users():


    users = list(
        users_collection.find()
    )


    return render_template(

        "users.html",

        users=users

    )







# ==========================
# Delete User
# ==========================

@admin.route("/delete-user/<id>")
@admin_required
def delete_user(id):


    users_collection.delete_one(

        {
            "_id":ObjectId(id)
        }

    )


    return redirect(

        url_for(
            "admin.manage_users"
        )

    )







# ==========================
# Notifications
# ==========================

@admin.route("/notifications")
@admin_required
def admin_notifications():


    notifications = list(

        notifications_collection.find().sort(
            "_id",
            -1
        )

    )


    return render_template(

        "notifications.html",

        notifications=notifications

    )







# ==========================
# System Health
# ==========================

@admin.route("/system-health")
@admin_required
def system_health():


    data = {


        "mongodb":"Connected",


        "server":"Running",


        "agents":"Active",


        "time":
        datetime.now().strftime(
            "%d-%m-%Y %H:%M:%S"
        )

    }



    return render_template(

        "system_health.html",

        data=data

    )






# ==========================
# Profile
# ==========================

@admin.route("/profile")
@admin_required
def admin_profile():


    admin_data = {

        "username":session.get("admin"),

        "role":"Administrator",

        "email":"admin@gmail.com"

    }



    return render_template(

        "admin_profile.html",

        admin=admin_data

    )


# ==========================
# Agent Monitor
# ==========================

@admin.route("/agent-monitor")
@admin_required
def agent_monitor():

    agents = [

        {
            "name":"Research Agent",
            "status":"Running",
            "tasks":25,
            "performance":95,
            "time":"Just Now"
        },


        {
            "name":"Coding Agent",
            "status":"Running",
            "tasks":18,
            "performance":92,
            "time":"2 Minutes Ago"
        },


        {
            "name":"Testing Agent",
            "status":"Waiting",
            "tasks":15,
            "performance":88,
            "time":"5 Minutes Ago"
        },


        {
            "name":"Report Agent",
            "status":"Completed",
            "tasks":20,
            "performance":98,
            "time":"10 Minutes Ago"
        }

    ]


    return render_template(
        "agent_monitor.html",
        agents=agents
    )

# ==========================
# Workflow Center
# ==========================

@admin.route("/workflow-center")
@admin_required
def workflow_center():


    workflow = {


        "name":"AI Automation Workflow",


        "overall":"Running",


        "steps":[


            {
                "agent":"Research Agent",
                "status":"Completed"
            },


            {
                "agent":"Coding Agent",
                "status":"Running"
            },


            {
                "agent":"Testing Agent",
                "status":"Waiting"
            },


            {
                "agent":"Report Agent",
                "status":"Waiting"
            }


        ]


    }



    print(
        "WORKFLOW CENTER DATA =",
        workflow
    )



    return render_template(

        "workflow_center.html",

        workflow=workflow

    )

# ==========================
# Run Full Workflow
# ==========================

@admin.route("/run-full-workflow")
@admin_required
def run_full_workflow():


    workflow_data = {


        "workflow_name":
        "AI Automation Workflow",


        "agents":[

            "Research Agent",
            "Coding Agent",
            "Testing Agent",
            "Report Agent"

        ],


        "status":
        "Completed",


        "date":
        datetime.now().strftime(
            "%d-%m-%Y %H:%M:%S"
        )

    }



    # Save Workflow

    workflows_collection.insert_one(
        workflow_data
    )



    # Notification Save

    notifications_collection.insert_one({

        "title":
        "Workflow Completed",


        "message":
        "AI Automation Workflow executed successfully",


        "date":
        datetime.now().strftime(
            "%d-%m-%Y %H:%M:%S"
        )

    })



    return redirect(

        url_for(
            "admin.workflow_center"
        )

    )


# ==========================
# Live Workflow Execution
# ==========================

import time


@admin.route("/execute-workflow")
@admin_required
def execute_workflow():


    current_time = datetime.now().strftime(
        "%d-%m-%Y %H:%M:%S"
    )


    workflow_history_collection.insert_one({

        "workflow":
        "AI Automation Workflow",

        "status":
        "Started",

        "current_agent":
        "Research Agent",

        "date":
        current_time

    })


    activity_collection.insert_one({

        "action":
        "Workflow Started",

        "user":
        "Admin",

        "date":
        current_time

    })


    workflow = {


        "name":
        "AI Automation Workflow",


        "overall":
        "Running",


        "steps":[


            {
                "agent":
                "Research Agent",

                "status":
                "Running"

            },


            {
                "agent":
                "Coding Agent",

                "status":
                "Waiting"

            },


            {
                "agent":
                "Testing Agent",

                "status":
                "Waiting"

            },


            {
                "agent":
                "Report Agent",

                "status":
                "Waiting"

            }

        ]

    }



    return render_template(

        "workflow_live.html",

        workflow=workflow

    )

@admin.route("/workflow-status")
def workflow_status():

    from workflow.live import get_status

    return get_status()