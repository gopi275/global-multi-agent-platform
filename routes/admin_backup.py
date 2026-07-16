from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    request,
    session,
    send_file
)

from functools import wraps
from bson.objectid import ObjectId

from datetime import datetime

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import getSampleStyleSheet


from database import (
    users_collection,
    tasks_collection,
    reports_collection,
    workflows_collection,
    workflow_history_collection,
    activity_collection
)



admin = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin"
)



# ==========================
# Admin Login Protection
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

        print("USERNAME =", username)
        print("PASSWORD =", password)

        if username == "admin" and password == "1234":

            print("LOGIN SUCCESS")

            session["admin"] = username

            return redirect(
                url_for("admin.admin_dashboard")
            )

        else:

            print("LOGIN FAILED")


    return render_template("admin_login.html")



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
        url_for("admin.admin_login")
    )





# ==========================
# Dashboard
# ==========================

@admin.route("/")
@admin_required
def admin_dashboard():

    data = {

        "users": users_collection.count_documents({}),

        "tasks": tasks_collection.count_documents({}),

        "reports": reports_collection.count_documents({}),

        "workflows": workflows_collection.count_documents({})

    }


    print("ADMIN DATA ==========>", data)


    return render_template(
        "admin_dashboard.html",
        data=data
    )




# ==========================
# Users Management
# ==========================

@admin.route("/users")
@admin_required
def manage_users():


    users = users_collection.find()


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



    activity_collection.insert_one({

        "action":"Deleted User",

        "user":"Admin",

        "date":
        datetime.now().strftime(
            "%d-%m-%Y %H:%M:%S"
        )

    })



    return redirect(

        url_for(
            "admin.manage_users"
        )

    )





# ==========================
# Workflow Monitor
# ==========================

@admin.route("/workflows")
@admin_required
def workflow_monitor():


    workflows = workflows_collection.find()



    return render_template(

        "workflow.html",

        workflows=workflows

    )





# ==========================
# Analytics
# ==========================

@admin.route("/analytics")
@admin_required
def admin_analytics():

    total_users = users_collection.count_documents({})

    total_tasks = tasks_collection.count_documents({})

    completed_tasks = tasks_collection.count_documents(
        {"status":"Completed"}
    )

    pending_tasks = tasks_collection.count_documents(
        {"status":"Pending"}
    )

    total_reports = reports_collection.count_documents({})

    total_workflows = workflows_collection.count_documents({})


    if total_tasks > 0:
        completion_rate = int(
            (completed_tasks / total_tasks) * 100
        )
    else:
        completion_rate = 0



    data = {

        "users": total_users,

        "tasks": total_tasks,

        "completed": completed_tasks,

        "pending": pending_tasks,

        "reports": total_reports,

        "workflows": total_workflows,

        "rate": completion_rate,

        "agents": 4

    }


    return render_template(
        "admin_analytics.html",
        data=data
    )




# ==========================
# Notifications
# ==========================

@admin.route("/notifications")
@admin_required
def admin_notifications():


    notifications=[


        {
            "title":"New User Registered",

            "message":
            "New user joined platform"
        },


        {
            "title":"Workflow Completed",

            "message":
            "AI workflow completed successfully"
        },


        {
            "title":"Report Generated",

            "message":
            "New report created"
        }

    ]



    return render_template(

        "notifications.html",

        notifications=notifications

    )





# ==========================
# Agent Leaderboard
# ==========================

@admin.route("/leaderboard")
@admin_required
def agent_leaderboard():


    agents=[


        {
            "name":"Research Agent",
            "tasks":45,
            "success":"95%"
        },


        {
            "name":"Coding Agent",
            "tasks":38,
            "success":"92%"
        },


        {
            "name":"Testing Agent",
            "tasks":32,
            "success":"90%"
        },


        {
            "name":"Report Agent",
            "tasks":28,
            "success":"96%"
        }


    ]



    return render_template(

        "leaderboard.html",

        agents=agents

    )





# ==========================
# Workflow History
# ==========================

from database import workflow_history_collection

@admin.route("/workflow-history")
def workflow_history():

    history = list(
        workflow_history_collection.find()
    )

    print("WORKFLOW DATA ==========>")
    for item in history:
        print(item)

    return render_template(
        "workflow_history.html",
        history=history
    )





# ==========================
# PDF Report
# ==========================

@admin.route("/download-report")
@admin_required
def download_report():


    filename="admin_report.pdf"



    doc=SimpleDocTemplate(filename)



    styles=getSampleStyleSheet()



    content=[]



    content.append(

        Paragraph(

            "AI Workflow Automation Admin Report",

            styles["Title"]

        )

    )



    content.append(

        Spacer(1,20)

    )



    report_data=[


        f"Total Users : {users_collection.count_documents({})}",

        f"Total Tasks : {tasks_collection.count_documents({})}",

        f"Total Reports : {reports_collection.count_documents({})}",

        f"Total Workflows : {workflows_collection.count_documents({})}"

    ]



    for item in report_data:


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



    return send_file(

        filename,

        as_attachment=True

    )





# ==========================
# System Stats
# ==========================

@admin.route("/system-stats")
@admin_required
def system_stats():


    data={


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

        "system_stats.html",

        data=data

    )





# ==========================
# System Health
# ==========================

@admin.route("/system-health")
@admin_required
def system_health():


    return render_template(

        "system_health.html"

    )





# ==========================
# Activity Logs
# ==========================

@admin.route("/activity")
@admin_required
def admin_activity():


    logs = activity_collection.find().sort(
        "_id",
        -1
    )


    return render_template(

        "admin_activity.html",

        logs=logs

    )


@admin.route("/agent-monitor")
@admin_required
def agent_monitor():

    agents = [

        {
            "name":"Research Agent",
            "status":"Completed"
        },

        {
            "name":"Coding Agent",
            "status":"Running"
        },

        {
            "name":"Testing Agent",
            "status":"Waiting"
        },

        {
            "name":"Report Agent",
            "status":"Waiting"
        }

    ]

    return render_template(
        "agent_monitor.html",
        agents=agents
    )

from datetime import datetime

@admin.route("/workflow-center")
@admin_required
def workflow_center():

    return render_template(
        "workflow_center.html"
    )


@admin.route("/run-full-workflow")
@admin_required
def run_full_workflow():

    workflows_collection.insert_one({

        "agent": "Multi Agent Workflow",

        "task": "Complete Automation",

        "status": "Completed",

        "date": datetime.now().strftime(
            "%d-%m-%Y %H:%M:%S"
        )

    })

    activity_collection.insert_one({

        "action": "Full Workflow Executed",

        "user": "Admin",

        "date": datetime.now().strftime(
            "%d-%m-%Y %H:%M:%S"
        )

    })

    notifications_collection.insert_one({

        "message": "Workflow Completed Successfully"

    })

    return redirect(
        url_for("admin.workflow_monitor")
    )

@admin.route("/agent-performance")
@admin_required
def agent_performance():

    agents = [

        {
            "name":"Research Agent",
            "score":95
        },

        {
            "name":"Coding Agent",
            "score":92
        },

        {
            "name":"Testing Agent",
            "score":88
        },

        {
            "name":"Report Agent",
            "score":98
        }

    ]

    best_agent = max(
        agents,
        key=lambda x: x["score"]
    )

    avg_score = round(
        sum(a["score"] for a in agents) /
        len(agents),
        2
    )

    return render_template(
        "agent_performance.html",
        agents=agents,
        best_agent=best_agent,
        avg_score=avg_score
    )

@admin.route("/search", methods=["GET","POST"])
@admin_required
def search():

    users = []
    tasks = []
    workflows = []

    if request.method == "POST":

        keyword = request.form["keyword"]

        users = list(
            users_collection.find({
                "username": {
                    "$regex": keyword,
                    "$options": "i"
                }
            })
        )

        tasks = list(
            tasks_collection.find({
                "task_name": {
                    "$regex": keyword,
                    "$options": "i"
                }
            })
        )

        workflows = list(
            workflows_collection.find({
                "workflow_name": {
                    "$regex": keyword,
                    "$options": "i"
                }
            })
        )

        print("USERS =", users)
        print("TASKS =", tasks)
        print("WORKFLOWS =", workflows)

    return render_template(
        "search.html",
        users=users,
        tasks=tasks,
        workflows=workflows
    )

@admin.route("/all-users")
def all_users():

    users = list(users_collection.find())

    for user in users:
        print(user)

    return "Check Terminal"