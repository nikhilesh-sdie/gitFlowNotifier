# GitHub Action: Teams Notifications
## Overview
This repository contains a GitHub Action written in Python to send notifications to a Microsoft Teams channel. Automate your updates, alerts, or messages within your workflows effortlessly.

---
## Features
- Real-time notifications to Microsoft Teams channels.
- Customizable message content and formatting.
- Simple integration with GitHub workflows.

## Prerequisites
- Microsoft Teams Webhook: Configure an incoming webhook for your Teams channel. To set up:- Open Microsoft Teams.
- Navigate to Connectors in your channel settings.
- Choose Incoming Webhook, follow the setup steps, and copy the provided URL.
- GitHub Secrets: Save your webhook URL in GitHub Actions secrets (e.g., TEAMS_WEBHOOK_URL).

---
## Usage
Example Workflow Configuration
Add the following snippet to your GitHub workflow file (.github/workflows/your-workflow.yml):

```name: Notify Teams Example

on:
  push:
    branches:
      - main

jobs:
  send-teams-notification:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v3

      - name: Teams Notification
        uses: ./ # Path to the action
        with:
          webhook_url: ${{ secrets.TEAMS_WEBHOOK_URL }}
          token: ${{ secrets.gitToken }}
          dry_run: true
```

---
### Inputs
| Input | Description | Required | Default Value | 
| ----- | ----------- | -------- | ------------- |
| webhook_url | Teams incoming webhook url. | Yes | None | 
| token | Github access token. | Yes | None | 
| dry_run | Do not actually send the message. | No | false |  

---
## Local Development & Testing
### Run Locally
To test this action locally:
- Install dependencies: ```pip install requests```

- Run the script:```python main.py --webhook-url <your_webhook_url> --token <your_git_token> dry_run <true/false> ```

---

## GitHub Actions Testing
Push the changes to a branch, create a pull request, and review the triggered workflow in the Actions tab.

---
## Contributing
Contributions are welcome! Feel free to open issues or submit pull requests for enhancements.
