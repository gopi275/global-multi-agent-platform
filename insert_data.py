from database import (
    users_collection,
    tasks_collection,
    reports_collection,
    workflows_collection
)


# Users Data

users_collection.insert_many([

    {
        "name": "Admin",
        "email": "admin@gmail.com",
        "role": "admin"
    },

    {
        "name": "Arun",
        "email": "arun@gmail.com",
        "role": "user"
    },

    {
        "name": "Kumar",
        "email": "kumar@gmail.com",
        "role": "user"
    }

])


# Tasks Data

tasks_collection.insert_many([

    {
        "task_name": "Research AI",
        "status": "Completed",
        "priority": "High"
    },

    {
        "task_name": "Coding Agent",
        "status": "Running",
        "priority": "Medium"
    }

])


# Reports Data

reports_collection.insert_many([

    {
        "report_name": "AI Workflow Report",
        "type": "PDF"
    }

])


from database import workflows_collection


workflow_data = {

    "agent": "Research Agent",

    "task": "AI Workflow Automation",

    "status": "Active",

    "date": "12-07-2026"

}


workflows_collection.insert_one(workflow_data)


print("Workflow Added")

from database import workflow_history_collection


workflow_history_collection.insert_one({

"workflow_name":"Multi Agent Automation",

"status":"Completed",

"date":"12-07-2026"

})


print("Workflow History Added")



from database import activity_collection
from datetime import datetime


activity_collection.insert_one({

    "action": "Admin Login",

    "user": "Admin",

    "date": datetime.now().strftime("%d-%m-%Y %H:%M:%S")

})


activity_collection.insert_one({

    "action": "Workflow Executed",

    "user": "System",

    "date": datetime.now().strftime("%d-%m-%Y %H:%M:%S")

})


print("Activity logs inserted")