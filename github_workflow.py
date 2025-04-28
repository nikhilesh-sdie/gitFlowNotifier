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
        self.github = self.authenticate()

    def authenticate(self):
        access_token = Auth.Token(self.git_token)
        return Github(auth=access_token)

    def fetch_repository(self):
        return self.github.get_repo(f"{self.owner}/{self.repo_name}")

    def fetch_workflow_details(self):
        repo = self.fetch_repository()
        self.workflow["work"] = repo.get_workflow_run(int(self.run_id))
        self.workflow["sha"] = repo.get_commit(self.sha)
        self.workflow["status"] = self.get_status(self.workflow["work"].conclusion.lower())

    def get_status(self, conclusion):
        statuses = [
            {
                "id": "success",
                "icon": "✓",
                "activityTitle": "Success!",
                "activitySubtitle": str(self.workflow["sha"].commit.author.date),
                "activityImage": "https://raw.githubusercontent.com/nikhilesh-sdie/poc/main/icons/success.png",
                "colour": "Good"
            },
            {
                "id": "failure",
                "icon": "✗",
                "activityTitle": "Failure",
                "activitySubtitle": str(self.workflow["sha"].commit.author.date),
                "activityImage": "https://raw.githubusercontent.com/nikhilesh-sdie/poc/main/icons/failure.png",
                "colour": "Attention"
            },
            {
                "id": "cancelled",
                "icon": "o",
                "activityTitle": "Cancelled",
                "activitySubtitle": str(self.workflow["sha"].commit.author.date),
                "activityImage": "https://raw.githubusercontent.com/nikhilesh-sdie/poc/main/icons/cancelled.png",
                "colour": "Default"
            },
            {
                "id": "skipped",
                "icon": "⤼",
                "activityTitle": "Skipped",
                "activitySubtitle": str(self.workflow["sha"].commit.author.date),
                "activityImage": "https://raw.githubusercontent.com/nikhilesh-sdie/poc/main/icons/skipped.png",
                "colour": "Default"
            },
            {
                "id": "unknown",
                "icon": "?",
                "activityTitle": "No job context has been provided",
                "activitySubtitle": str(self.workflow["sha"].commit.author.date),
                "activityImage": "https://raw.githubusercontent.com/nikhilesh-sdie/poc/main/icons/unknown.png",
                "colour": "Default"
            }
            # Add other statuses here...
        ]
        return next((status for status in statuses if status['id'] == conclusion), None)

    def get_workflow(self):
        self.fetch_workflow_details()
        return self.workflow


class JobStatus:
    def __init__(self, workflow: GitHubWorkflow):
        self.workflow = workflow.get_workflow()
        self.job_count = 0
        self.step_count = 0

    def fetch_jobs(self):
        return self.workflow["work"].jobs(_filter="all")

    def fetch_job_details(self):
        jobs = self.fetch_jobs()
        results = []

        for job in jobs:
            self.job_count += 1
            job_info = {
                "jobUrl": job.html_url,
                "jobCount": self.job_count,
                "Job Number": self.job_count,
                "Job Name": job.name,
                "Status": job.status,
                "Conclusion": job.conclusion,
                "Started At": job.started_at,
                "Completed At": job.completed_at,
                "Steps": self.fetch_steps(job)
            }
            results.append(job_info)

        return results

    def fetch_steps(self, job):
        steps = []
        for step in job.steps:
            self.step_count += 1
            step_info = {
                "Step Number": self.step_count,
                "Step Name": step.name,
                "Status": step.status,
                "Conclusion": step.conclusion
            }
            steps.append(step_info)
        return steps


class NotificationCard:
    def __init__(self):
        self.webhook_url = os.getenv("webhook")
        self.release_tag = os.getenv("GITHUB_REF")
        self.rootPath = os.getenv("GITHUB_WORKSPACE")
        self.note_path = os.getenv("realease_note_path", "{rootPath}/Release-Notes.txt")
        self.repo_url = f"https://github.com/{os.getenv('GITHUB_REPOSITORY')}/tree/{self.release_tag.split('/')[-1]}"
        self.repo_name = os.getenv("GITHUB_REPOSITORY").split('/')[-1]

    def send_notification(self, result_status, job_details):
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
        release_notes = open(f"{self.note_path}").read() or "No release note found"
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
    job_status = JobStatus(workflow)

    result_status = workflow.get_workflow()
    notification = NotificationCard()

    if result_status["status"]["id"] == "success":
        return notification.send_notification(result_status, job_status.fetch_job_details())
    elif result_status["status"]["id"] == "failure":
        return notification.send_notification(result_status, job_status.fetch_job_details())