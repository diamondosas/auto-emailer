import csv
import os
import json
import time
import socket
from datetime import datetime
from smtplib import SMTP, SMTP_SSL
import smtplib
import markdown
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import ssl

class AutoMailerCore:
    def __init__(self, limits_file="send_limits.json"):
        self.limits_file = limits_file
        self.max_per_day = 500
        self._load_limits()

    def _load_limits(self):
        self.today_str = datetime.now().strftime("%Y-%m-%d")
        if os.path.exists(self.limits_file):
            try:
                with open(self.limits_file, "r") as f:
                    data = json.load(f)
                    if data.get("date") == self.today_str:
                        self.sent_today = data.get("sent_count", 0)
                    else:
                        self.sent_today = 0
            except json.JSONDecodeError:
                self.sent_today = 0
        else:
            self.sent_today = 0

    def _save_limits(self):
        with open(self.limits_file, "w") as f:
            json.dump({"date": self.today_str, "sent_count": self.sent_today}, f)

    def can_send(self):
        return self.sent_today < self.max_per_day

    def get_msg_generator(self, csv_file_path, template, subject_template=None):
        with open(csv_file_path, "r", encoding="utf-8") as file:
            headers = [h.strip() for h in file.readline().split(",")]
        # Intentionally opening twice to parse headers first, then read dicts
        with open(csv_file_path, "r", encoding="utf-8") as file:
            data = csv.DictReader(file)
            for row in data:
                required_string = template
                curr_subject = subject_template if subject_template else ""
                for header in headers:
                    value = row.get(header, "")
                    required_string = required_string.replace(f"${header}", value)
                    if subject_template:
                        curr_subject = curr_subject.replace(f"${header}", value)
                if "EMAIL" in row:
                    yield row["EMAIL"], required_string, curr_subject

    def get_attachments(self, attach_dir="ATTACH", confirmed_files=None):
        file_contents = []
        file_names = []
        if not os.path.exists(attach_dir):
            return None

        if confirmed_files is not None:
            # GUI or confirmed list provided
            for filename in confirmed_files:
                filepath = os.path.join(attach_dir, filename)
                if os.path.exists(filepath):
                    file_names.append(filename)
                    with open(filepath, "rb") as f:
                        file_contents.append(f.read())
            return {"names": file_names, "contents": file_contents} if file_names else None
        else:
            # CLI mode logic
            try:
                for filename in os.listdir(attach_dir):
                    entry = input(
                        f"TYPE IN 'Y' AND PRESS ENTER IF YOU CONFIRM T0 ATTACH {filename}\nTO SKIP PRESS ENTER: "
                    )
                    if entry.strip().upper() == "Y":
                        file_names.append(filename)
                        with open(os.path.join(attach_dir, filename), "rb") as f:
                            file_contents.append(f.read())
                return {"names": file_names, "contents": file_contents} if file_names else None
            except FileNotFoundError:
                print("No ATTACH directory found...")
                return None

    def connect_smtp(self, email, password):
        host = "smtp.gmail.com"
        port = 465
        context = ssl.create_default_context()
        try:
            server = SMTP_SSL(host=host, port=port, context=context)
            server.ehlo()
            server.login(user=email, password=password)
            return server, None
        except Exception as e:
            return None, str(e)

    def verify_credentials(self, email, password):
        server, error = self.connect_smtp(email, password)
        if server:
            server.quit()
            return True, "Success"
        return False, error

    def _wait_for_network(self, log_callback=None):
        while True:
            try:
                # Try to resolve a reliable host to check for internet connection
                socket.create_connection(("8.8.8.8", 53), timeout=3)
                return
            except OSError:
                if log_callback:
                    log_callback("Network unavailable. Waiting for connection...")
                time.sleep(5)

    def send_emails(
        self,
        sender_email,
        password,
        display_name,
        csv_file_path,
        template,
        subject,
        is_html,
        attachments_data=None,
        interval=0,
        log_callback=None
    ):
        sent_count = 0
        server, error = self.connect_smtp(sender_email, password)
        if not server:
            if log_callback: log_callback(f"Failed to connect: {error}")
            return 0

        def log(msg):
            if log_callback:
                log_callback(msg)
            else:
                print(msg)

        msg_gen = self.get_msg_generator(csv_file_path, template, subject)

        for receiver, message, curr_subject in msg_gen:
            if not self.can_send():
                log("Daily limit of 500 emails reached. Stopping.")
                break

            multipart_msg = MIMEMultipart("mixed") if attachments_data else MIMEMultipart("alternative")

            if curr_subject:
                multipart_msg["Subject"] = curr_subject
            else:
                first_line = message.splitlines()[0] if message.splitlines() else "(no subject)"
                if is_html and first_line.startswith("<"):
                    multipart_msg["Subject"] = "(no subject)"
                else:
                    multipart_msg["Subject"] = first_line

            multipart_msg["From"] = f"{display_name} <{sender_email}>"
            multipart_msg["To"] = receiver

            if not is_html:
                text = message
                html = markdown.markdown(text, extensions=["nl2br"])
                part1 = MIMEText(text, "plain")
                part2 = MIMEText(html, "html")
                multipart_msg.attach(part1)
                multipart_msg.attach(part2)
            else:
                html = message
                part2 = MIMEText(html, "html")
                multipart_msg.attach(part2)

            if attachments_data:
                for content, name in zip(attachments_data["contents"], attachments_data["names"]):
                    attach_part = MIMEBase("application", "octet-stream")
                    attach_part.set_payload(content)
                    encoders.encode_base64(attach_part)
                    attach_part.add_header(
                        "Content-Disposition", f"attachment; filename={name}"
                    )
                    multipart_msg.attach(attach_part)

            # Retry loop for sending individual email
            sent_successfully = False
            while not sent_successfully:
                try:
                    self._wait_for_network(log_callback)
                    log(f"Sending email to: {receiver}...")
                    server.sendmail(sender_email, receiver, multipart_msg.as_string())
                    log(f"SUCCESS: {receiver}")
                    self.sent_today += 1
                    self._save_limits()
                    sent_count += 1
                    sent_successfully = True
                except (smtplib.SMTPServerDisconnected, socket.error):
                    log("Connection lost. Reconnecting...")
                    self._wait_for_network(log_callback)
                    # Try to reconnect
                    server, _ = self.connect_smtp(sender_email, password)
                    if not server:
                        time.sleep(5) # wait before retrying to connect
                except Exception as err:
                    log(f"FAILED to send to {receiver}. Retrying...")
                    time.sleep(5)

            if interval > 0 and self.can_send():
                log(f"Waiting {interval} seconds before next email...")
                time.sleep(interval)

        server.quit()
        log(f"Sent {sent_count} emails.")
        return sent_count
