from pymongo import MongoClient


client = MongoClient(
    "mongodb+srv://gopinath:admin1234@cluster0.7cobbpr.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
)


db = client["multiagent"]



users_collection = db["users"]

tasks_collection = db["tasks"]

reports_collection = db["reports"]

workflows_collection = db["workflows"]

workflow_history_collection = db["workflow_history"]

activity_collection = db["activity_logs"]

notifications_collection = db["notifications"]

ai_logs_collection = db["ai_decision_logs"]

ai_reports_collection = db["ai_reports"]

from datetime import datetime


def add_notification(message):

    notifications_collection.insert_one({

        "message": message,

        "time": datetime.now().strftime(
            "%d-%m-%Y %H:%M:%S"
        )

    })

from datetime import datetime


def save_workflow_history(data):

    workflow_collection = db["workflow_history"]

    data["saved_at"] = datetime.now()

    workflow_collection.insert_one(data)

    return True



def get_workflow_history():

    workflow_collection = db["workflow_history"]

    records = list(workflow_collection.find({}, {"_id":0}))

    return records



print("Database Connected Successfully")