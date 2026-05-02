# email-GPT

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue?style=for-the-badge&logo=python)
![Build Status](https://img.shields.io/badge/build-passing-brightgreen?style=for-the-badge&logo=githubactions)
![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)

Efficient bulk email automation. Simple, fast, and built from first principles.

![App Screenshot](assets/screenshot.png)

## Overview

Existing bulk email tools are unnecessarily complex. AutoMailer is designed to be direct. It takes data from a CSV, injects it into a template, and sends it. That's it.

## Features

- **Dynamic Templates:** Unlimited variables from CSV columns.
- **HTML & Markdown:** Support for formatted text and links.
- **Attachments:** Send any file type.
- **Dark Mode GUI:** Real-time tracking of sent emails.
- **Rate Limiting:** Automatic daily limits to prevent account suspension.

## Usage

1. **Install Dependencies:**
   ```shell
   pip install -r requirements.txt
   ```

2. **Setup Template:**
   Write your email in `compose.md` or `compose.html`. Use `$VARIABLE` to match CSV headers.
   > *Example: "Hi $NAME, your order for $ITEM is ready."*

3. **Setup Data:**
   Add recipient data to `data.csv`. The file **must** have an `EMAIL` column.

4. **Add Attachments:**
   Place files in the `ATTACH` folder.

5. **Set Credentials:**
   Create a `.env` file:
   ```text
   display_name=Your Name
   sender_email=your@gmail.com
   password=your-app-password
   ```
   *Use a Gmail [App Password](https://support.google.com/accounts/answer/185833), not your main password.*

6. **Run:**
   ```shell
   python gui.py
   ```

Verify your settings in the GUI and start. It just works.

## Support

Report bugs in the issues section. Keep it technical.
