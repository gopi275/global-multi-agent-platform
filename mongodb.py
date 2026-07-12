from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["agentflow"]

tasks_collection = db["tasks"]

notifications_collection = db["notifications"]


db = client["agentflow"]

tasks_collection = db["tasks"]


print("AgentFlow Database Ready")

