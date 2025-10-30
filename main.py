from github_workflow import GitHubWorkflow
from github_workflow import NotificationCard
import os

def main():
    # Step 1: Initialize the GitHubWorkflow instance
    workflow = GitHubWorkflow()

    # Step 2: Get the workflow details
    workflow.fetch_workflow_details()

    # Step 3: Determine the status and prepare the notification
    notification = NotificationCard()
    result_status = workflow.get_workflow()

    # Step 4: Check if raw_text is provided
    raw_text = os.getenv("RAW_TEXT")

    if raw_text:
        print("Detected raw_text — sending raw payload instead of generated card.")
        card = notification.send_raw_text(raw_text)
    else:
        print("raw_text not provided — sending structured Adaptive Card.")
        if result_status["status"]["id"] in ["success", "failure"]:
            card = notification.send_notification(result_status)
        else:
            card = notification.send_notification(result_status)
        print(f"{result_status['status']['id']} Notification Card Generated")
    
    # Step 6: (Optional) Display or send the generated card
    dry_run = os.getenv("dry_run", "false").lower() == "true"

    if dry_run:
        card.printme()  # Display the JSON representation of the adaptive card.
    else:
        card.send()  # Send the card.

if __name__ == "__main__":
    main()
