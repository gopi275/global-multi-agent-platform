from pymongo import MongoClient


client = MongoClient(
    "mongodb+srv://gopinath:admin1234@cluster0.7cobbpr.mongodb.net/?retryWrites=true&w=majority"
)


db = client["multiagent"]


users_collection = db["users"]

tasks_collection = db["tasks"]

notifications_collection = db["notifications"]

reports_collection = db["reports"]

workflows_collection = db["workflows"]

workflow_history_collection = db["workflow_history"]

activity_collection = db["activity_logs"]


def add_notification(message):

    notifications_collection.insert_one(
        {
            "message": message,
            "status": "unread"
        }
    )




print("AgentFlow Database Ready")


@admin.route("/all-users")
def all_users():

    users = list(users_collection.find())

    for user in users:
        print(user)

    return "Check Terminal"