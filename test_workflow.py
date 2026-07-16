from workflow.engine import run_workflow
from database import save_workflow_history


result = run_workflow(
    "Create AI Automation System"
)


save_workflow_history(result)


print("\nFINAL RESULT")
print(result)

print("\nWorkflow Saved To MongoDB ✅")