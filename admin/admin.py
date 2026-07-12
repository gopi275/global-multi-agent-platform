from flask import Blueprint, render_template, redirect, url_for
from database import (
    users_collection,
    tasks_collection,
    reports_collection,
    workflows_collection
)
from bson.objectid import ObjectId


admin = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin"
)


# -------------------------
# Admin Dashboard
# -------------------------

@admin.route("/")
def admin_dashboard():

    data = {

        "users": users_collection.count_documents({}),
        "tasks": tasks_collection.count_documents({}),
        "reports": reports_collection.count_documents({}),
        "workflows": workflows_collection.count_documents({})

    }

    return render_template(
        "admin_dashboard.html",
        data=data
    )


# -------------------------
# User Management
# -------------------------

@admin.route("/users")
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

    return redirect(
        url_for("admin.manage_users")
    )