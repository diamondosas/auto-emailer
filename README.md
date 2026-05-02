# email-GPT: Hardcore Bulk Communication

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue?style=for-the-badge&logo=python)
![Build Status](https://img.shields.io/badge/build-passing-brightgreen?style=for-the-badge&logo=githubactions)
![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)

*Accelerating the transition to fully automated, dynamic communications.*

![App Screenshot](assets/screenshot.png) 
*(Insert picture of the GUI terminal here)*

## The Vision

Look, the current state of bulk emailing is fundamentally broken. It’s too complex, too slow, and lacks the hardcore engineering required to scale properly. We needed to solve this from first principles. 

AutoMailer is an extremely profound leap forward. We've built a system that takes dynamic data, injects it into personalized payloads, and fires it off with order-of-magnitude greater efficiency. Nothing more, nothing less. It’s literally the rocket ship of email automation.

## What's New
- **HTML Payloads:** You can now send full HTML emails. Just write your `compose.html` and the system handles the rest. Mind-blowing.
- **Next-Level GUI:** We built a sleek, dark-mode terminal GUI that gives you real-time telemetry on your outgoing payloads. 

## Core Capabilities

1. **Dynamic Telemetry Injection:** Send dynamic emails with unlimited variables pulling directly from a CSV file.
2. **Markdown & HTML Formatting:** Embed links, images, and structure with zero friction.
3. **Payload Attachment:** Attach any kind of files seamlessly to your outgoing sequence.

## The Playbook (Usage)

To operate this system, you need to understand the physics of it:

1. **Acquire the Hardware:** Ensure Python is installed on your system.
2. **Clone the Repo:** Download the source code and move into the `automailer` directory.
3. **Install Dependencies:**
   ```shell
   pip install -r requirements.txt
   ```
4. **Draft the Blueprint:** Write your email inside **`compose.md`** (or use HTML). Use variables by prefixing them with a `$` sign.
   > *Example: "Hi $NAME, your ticket to Mars for Rs. $price is due in $months."*
5. **Load the Fuel (Data):** Put your data inside the `data.csv` file. 
   *Crucial detail: The header must contain 'EMAIL' (uppercase). This is non-negotiable.*

   ![csv_image](https://user-images.githubusercontent.com/66209958/103172846-715d0c00-487c-11eb-9419-9dceb4297e49.png)

6. **Load Attachments:** If you need to send files, drop them in the `ATTACH` directory. 
7. **Ignition Credentials:** Create an `.env` file and input your mission parameters:
   ```text
   display_name=Elon
   sender_email=your@example.com
   password=12345
   ```
   *Security Protocol: Do not use your root password. Create a Gmail Account, activate 2-Step Verification, and generate an [App Password](https://support.google.com/accounts/answer/185833?hl=en).*

8. **LIFT OFF:** 
   Run the system via the command line or our newly engineered GUI.
   ```shell
   python gui.py
   # OR
   python send.py
   ```

You will be asked to verify your attachments before launch. Upon confirmation, the sequence initiates. You will receive full telemetry and a success report once the payloads reach their destination.

## Engineering Support

If the engines fail or you detect an anomaly, please report the issue in the repository. We need to iterate fast and fix things. Let's make humanity multi-planetary.
