import os
import pyadaptivecard
from github import Github, Auth
from typing import List, Dict
import pytz
from datetime import datetime
import json

class GitHubWorkflow:
    def __init__(self):
        self.git_token = os.getenv("token", "").strip()
        self.owner = os.getenv("GITHUB_REPOSITORY").split('/')[0]
        self.repo_name = os.getenv("GITHUB_REPOSITORY").split('/')[-1]
        self.run_id = os.getenv("GITHUB_RUN_ID")
        self.sha = os.getenv("GITHUB_SHA")
        self.workflow = {}
        self.all_success = os.getenv("job_status", "unknown")

    def convert_to_ist(self, time):
        utc_time = datetime.strptime(time, '%Y-%m-%d %H:%M:%S%z')
        ist_timezone = pytz.timezone("Asia/Kolkata")
        ist_time = utc_time.astimezone(ist_timezone)
        formatted_ist_time = ist_time.strftime("%Y-%m-%d %I:%M:%S %p") + " IST"
        return formatted_ist_time

    def get_status(self, conclusion):
        statuses = [
            {
                "id": "success",
                "icon": "✓",
                "activityTitle": "Success!",
                "activitySubtitle": self.convert_to_ist(str(self.workflow["sha"].commit.author.date)),
                "activityImage": "https://raw.githubusercontent.com/nikhilesh-sdie/gitFlowNotifier/main/icons/success.png",
                "colour": "Good"
            },
            {
                "id": "failure",
                "icon": "✗",
                "activityTitle": "Failure",
                "activitySubtitle": self.convert_to_ist(str(self.workflow["sha"].commit.author.date)),
                "activityImage": "https://raw.githubusercontent.com/nikhilesh-sdie/gitFlowNotifier/main/icons/failure.png",
                "colour": "Attention"
            },
            {
                "id": "cancelled",
                "icon": "o",
                "activityTitle": "Cancelled",
                "activitySubtitle": self.convert_to_ist(str(self.workflow["sha"].commit.author.date)),
                "activityImage": "https://raw.githubusercontent.com/nikhilesh-sdie/gitFlowNotifier/main/icons/cancelled.png",
                "colour": "Default"
            },
            {
                "id": "skipped",
                "icon": "⤼",
                "activityTitle": "Skipped",
                "activitySubtitle": self.convert_to_ist(str(self.workflow["sha"].commit.author.date)),
                "activityImage": "https://raw.githubusercontent.com/nikhilesh-sdie/gitFlowNotifier/main/icons/skipped.png",
                "colour": "Default"
            },
            {
                "id": "unknown",
                "icon": "?",
                "activityTitle": "No job context has been provided",
                "activitySubtitle": self.convert_to_ist(str(self.workflow["sha"].commit.author.date)),
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
        print(self.all_success)
        print(self.workflow)


    def get_workflow(self):
        self.fetch_workflow_details()
        return self.workflow



class NotificationCard:
    def __init__(self):
        self.all_success = os.getenv("job_status", "unknown")
        self.webhook_url = os.getenv("MS_TEAMS_WEBHOOK_URL")
        self.release_tag = os.getenv("GITHUB_REF")
        self.rootPath = os.getenv("GITHUB_WORKSPACE")
        self.note_path = os.getenv("release_note_path", "Release-Notes.txt")
        self.repo_url = f"https://github.com/{os.getenv('GITHUB_REPOSITORY')}/tree/{self.release_tag.split('/')[-1]}"
        self.repo_name = os.getenv("GITHUB_REPOSITORY").split('/')[-1]
        self.mobile_os = os.getenv("mobile_os")
        self.version_name = os.getenv("version_name")
        self.version_code = os.getenv("version_code")
        self.play_console_url = os.getenv("play_console_url")
        self.testflight_url = os.getenv("testflight_url")
        self.allure_report_url = os.getenv("allure_report_url")
        self.apk_name = os.getenv("apk_name")
        self.mode = "api" if self.repo_name == "checkpoint-api" else "mobile" if self.repo_name == "checkpoint-mobile-app" else "appium" if self.repo_name == "qrt-mobile-automation" else None
        self.raw_text = os.getenv("raw_text", "").strip()
    def send_raw_text(self, raw_text):
        if not raw_text:
            print("⚠️ raw_text is empty or None — skipping send_raw_text()")
            return None

        try:
            payload = json.loads(raw_text) if isinstance(raw_text, str) else raw_text
            print("\n======= Sending raw JSON payload to Teams =======")
            print(json.dumps(payload, indent=4))
            print("=================================================\n")
            response = requests.post(self.webhook_url, json=payload)
            print(f"✅ Teams Response: {response.status_code} {response.text}")
            return response
        except Exception as e:
            print(f"⚠️ Failed to send raw JSON to Teams: {e}")
            return None

    def send_notification(self, result_status):
        card = pyadaptivecard.AdaptiveCard(self.webhook_url)
        title_text = (
            f"Realtime Release: {self.release_tag}" if self.mode == "api"
            else f"Realtime {self.mobile_os} release" if self.mode == "mobile"
            else f"Realtime Apk Testing" if self.mode == "appium" 
            else "Unknown release mode"
        )
        card.title(f"{title_text}")

        card.addSection(self._create_title_section(result_status))
        card.addSection(self._create_project_status_section(result_status))
        
        # Add release notes only if it's a success
        if result_status["status"]["id"] == "success":
            card.addSection(self._create_release_notes_section())

        # url = result_status["work"].html_url if self.mode == "api" else self.play_console_url if self.mobile_os.lower() == "android" else self.testflight_url
        url = (
            result_status["work"].html_url if self.mode == "api"
            else self.allure_report_url if self.mode == "appium"
            else self.play_console_url if (self.mobile_os and self.mobile_os.lower() == "android")
            else self.testflight_url if (self.mobile_os and self.mobile_os.lower() == "ios")
            else None
        )
        card.addSection(self._create_button_section(url))

        return card

    def _create_title_section(self, result_status):
        section = pyadaptivecard.ActivitySection()
        title_text = (
            f"Release Tag: {self.release_tag}" if self.mode == "api" 
            else f"Release version: {self.version_name}({self.version_code})" if self.mode == "mobile"
            else f"Apk: {self.apk_name}" if self.mode == "appium"
            else "Unknown release code"
        )    
        section.activityTitle(f"{title_text}")
        section.activitySubtitle(result_status["status"]["activitySubtitle"])
        section.activityImage(result_status["status"]["activityImage"])
        return section

    def _create_project_status_section(self, result_status):
        section = pyadaptivecard.CardSection()
        section.addFact("Project", f"[{self.repo_name}]({self.repo_url})")
        section.addFact(
            "Status",
            f"{self.all_success} {result_status['status']['icon']}",
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
        section.addLinkButton(
            "Deployment Logs" if self.mode == "api" else
            "Google Play console" if self.mode == "mobile" and self.mobile_os.lower() == "android" else
            "Testflight" if self.mode == "mobile" and self.mobile_os.lower() == "ios" else
            "Appium Report" if self.mode == "appium" else
            None,
            deployment_logs_url
        )
        return section


def check_result():
    workflow = GitHubWorkflow()

    result_status = workflow.get_workflow()
    notification = NotificationCard()

    if raw_text:
        print("Detected raw_text — sending raw payload instead of generated card.")
        return notification.send_raw_text(raw_text)
    else:
        print("raw_text not provided — sending structured Adaptive Card.")
        if result_status["status"]["id"] in ["success", "failure"]:
            return notification.send_notification(result_status)


