import os
import pyadaptivecard
from github import Github, Auth
from typing import List, Dict

class GitHubWorkflow:
    def __init__(self):
        self.git_token = os.getenv("token")
        self.owner = os.getenv("GITHUB_REPOSITORY").split('/')[0]
        self.repo_name = os.getenv("GITHUB_REPOSITORY").split('/')[-1]
        self.run_id = os.getenv("GITHUB_RUN_ID")
        self.sha = os.getenv("GITHUB_SHA")
        self.workflow = {}
        self.all_success = os.getenv("job_status", "unknown")

    def get_status(self, conclusion):
        statuses = [
            {
                "id": "success",
                "icon": "✓",
                "activityTitle": "Success!",
                "activitySubtitle": str(self.workflow["sha"].commit.author.date),
                "activityImage": "https://raw.githubusercontent.com/nikhilesh-sdie/gitFlowNotifier/main/icons/success.png",
                "colour": "Good"
            },
            {
                "id": "failure",
                "icon": "✗",
                "activityTitle": "Failure",
                "activitySubtitle": str(self.workflow["sha"].commit.author.date),
                "activityImage": "https://raw.githubusercontent.com/nikhilesh-sdie/gitFlowNotifier/main/icons/failure.png",
                "colour": "Attention"
            },
            {
                "id": "cancelled",
                "icon": "o",
                "activityTitle": "Cancelled",
                "activitySubtitle": str(self.workflow["sha"].commit.author.date),
                "activityImage": "https://raw.githubusercontent.com/nikhilesh-sdie/gitFlowNotifier/main/icons/cancelled.png",
                "colour": "Default"
            },
            {
                "id": "skipped",
                "icon": "⤼",
                "activityTitle": "Skipped",
                "activitySubtitle": str(self.workflow["sha"].commit.author.date),
                "activityImage": "https://raw.githubusercontent.com/nikhilesh-sdie/gitFlowNotifier/main/icons/skipped.png",
                "colour": "Default"
            },
            {
                "id": "unknown",
                "icon": "?",
                "activityTitle": "No job context has been provided",
                "activitySubtitle": str(self.workflow["sha"].commit.author.date),
                "activityImage": "https://raw.githubusercontent.com/nikhilesh-sdie/gitFlowNotifier/main/icons/unknown.png",
                "colour": "Default"
            }
            # Add other statuses here...
        ]
        return next((status for status in statuses if status['id'] == conclusion), None)

    def authenticate(self):
        access_token = Auth.Token(str(self.git_token))
        return Github(auth=access_token)

    def fetch_repository(self):
        github = self.authenticate()
        return github.get_repo(f"{self.owner}/{self.repo_name}")

    def fetch_workflow_details(self):
        repo = self.fetch_repository()
        self.workflow["work"] = repo.get_workflow_run(int(self.run_id))
        self.workflow["sha"] = repo.get_commit(self.sha)
        self.workflow["status"] = self.get_status(self.all_success)
        print(self.workflow)


    def get_workflow(self):
        self.fetch_workflow_details()
        return self.workflow



class NotificationCard:
    def __init__(self):
        self.webhook_url = os.getenv("MS_TEAMS_WEBHOOK_URL")
        self.release_tag = os.getenv("GITHUB_REF")
        self.rootPath = os.getenv("GITHUB_WORKSPACE")
        self.note_path = os.getenv("realease_note_path", "Release-Notes.txt")
        self.repo_url = f"https://github.com/{os.getenv('GITHUB_REPOSITORY')}/tree/{self.release_tag.split('/')[-1]}"
        self.repo_name = os.getenv("GITHUB_REPOSITORY").split('/')[-1]

    def send_notification(self, result_status):
        card = pyadaptivecard.AdaptiveCard(self.webhook_url)
        card.title(f"Realtime Release: {self.release_tag}")

        card.addSection(self._create_title_section(result_status))
        card.addSection(self._create_project_status_section(result_status))
        
        # Add release notes only if it's a success
        if result_status["status"]["id"] == "success":
            card.addSection(self._create_release_notes_section())

        card.addSection(self._create_button_section(result_status["work"].html_url))

        return card

    def _create_title_section(self, result_status):
        section = pyadaptivecard.ActivitySection()
        section.activityTitle(f"Release Tag: {self.release_tag}")
        section.activitySubtitle(result_status["status"]["activitySubtitle"])
        section.activityImage(result_status["status"]["activityImage"])
        return section

    def _create_project_status_section(self, result_status):
        section = pyadaptivecard.CardSection()
        section.addFact("Project", f"[{self.repo_name}]({self.repo_url})")
        section.addFact(
            "Status",
            f"{result_status['work'].conclusion} {result_status['status']['icon']}",
            result_status["status"]["colour"]
        )
        return section

    def _create_release_notes_section(self):
        if os.path.exists(self.note_path):
            print("found the file")
            with open(self.note_path, 'r') as file:
                release_notes = file.read()
        else:
            release_notes = f"No release note found."
        section = pyadaptivecard.CardSection()
        section.title("Release Notes")
        section.text(release_notes)
        return section

    def _create_button_section(self, deployment_logs_url):
        section = pyadaptivecard.CardSection()
        section.addLinkButton("Deployment Logs", deployment_logs_url)
        return section


def check_result():
    workflow = GitHubWorkflow()

    result_status = workflow.get_workflow()
    notification = NotificationCard()

    if result_status["status"]["id"] == "success":
        return notification.send_notification(result_status)
    elif result_status["status"]["id"] == "failure":
        return notification.send_notification(result_status)
