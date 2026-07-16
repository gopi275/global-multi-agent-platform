# ==========================
# Live Workflow Status
# ==========================

workflow_status = {


    "Research Agent":"Waiting",

    "Coding Agent":"Waiting",

    "Testing Agent":"Waiting",

    "Report Agent":"Waiting"


}



def update_status(agent,status):

    workflow_status[agent]=status



def get_status():

    return workflow_status