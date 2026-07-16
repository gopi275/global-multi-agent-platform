from workflow.live import update_status
import time



def run_live_workflow():


    agents = [

        "Research Agent",
        "Coding Agent",
        "Testing Agent",
        "Report Agent"

    ]


    for agent in agents:


        update_status(
            agent,
            "Running"
        )


        time.sleep(3)



        update_status(
            agent,
            "Completed"
        )



    return True