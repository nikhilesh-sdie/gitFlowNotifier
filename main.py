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
 
    # Step 4: Send the notification based on the workflow status
    if result_status["status"]["id"] == "success":
        card = notification.send_notification(result_status)
        print("Success Notification Card Generated")
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