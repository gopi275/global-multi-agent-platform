from pymongo import MongoClient


client = MongoClient(
    "mongodb://localhost:27017/"
)


db = client["multiagent"]


users_collection = db["users"]

tasks_collection = db["tasks"]

reports_collection = db["reports"]

workflows_collection = db["workflows"]

workflow_history_collection = db["workflow_history"]

activity_collection = db["admin_activity"]


