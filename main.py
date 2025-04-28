from github_workflow import GitHubWorkflow
from github_workflow import JobStatus
from github_workflow import NotificationCard
import os

def main():
    # Step 1: Initialize the GitHubWorkflow instance
    workflow = GitHubWorkflow()

    # Step 2: Get the workflow details
    workflow.fetch_workflow_details()

    # Step 3: Pass the workflow to the JobStatus class and fetch job details
    job_status = JobStatus(workflow)
    job_details = job_status.fetch_job_details()

    # Step 4: Determine the status and prepare the notification
    notification = NotificationCard()
    result_status = workflow.get_workflow()

    # Step 5: Send the notification based on the workflow status
    if result_status["status"]["id"] == "success":
        card = notification.send_notification(result_status, job_details)
        print("Success Notification Card Generated")
    elif result_status["status"]["id"] == "failure":
        card = notification.send_notification(result_status, job_details)
        print("Failure Notification Card Generated")
    else:
        print("No notification sent due to unknown status.")
    
    # Step 6: (Optional) Display or send the generated card
    dry_run = os.getenv("dry_run", "false").lower() == "true"

    if dry_run:
        card.printme()  # Display the JSON representation of the adaptive card.
    else:
        card.send()  # Send the card.

if __name__ == "__main__":
    main()