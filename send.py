import csv
import os
from settings import SENDER_EMAIL, PASSWORD, DISPLAY_NAME, MAIL_COMPOSE, SUBJECT

from smtplib import SMTP
import smtplib
import markdown
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import ssl


def get_msg(csv_file_path, template, subject_template=None):
    with open(csv_file_path, "r", encoding="utf-8") as file:
        headers = [h.strip() for h in file.readline().split(",")]
    # i am opening the csv file two times above and below INTENTIONALLY, changing will cause error
    with open(csv_file_path, "r", encoding="utf-8") as file:
        data = csv.DictReader(file)
        for row in data:
            required_string = template
            curr_subject = subject_template if subject_template else ""
            for header in headers:
                value = row[header]
                required_string = required_string.replace(f"${header}", value)
                if subject_template:
                    curr_subject = curr_subject.replace(f"${header}", value)
            yield row["EMAIL"], required_string, curr_subject


def confirm_attachments():
    file_contents = []
    file_names = []
    try:
        for filename in os.listdir("ATTACH"):

            entry = input(
                f"""TYPE IN 'Y' AND PRESS ENTER IF YOU CONFIRM T0 ATTACH {filename}
                                    TO SKIP PRESS ENTER: """
            )
            confirmed = True if entry == "Y" else False
            if confirmed:
                file_names.append(filename)
                with open(f"{os.getcwd()}/ATTACH/{filename}", "rb") as f:
                    content = f.read()
                file_contents.append(content)

        return {"names": file_names, "contents": file_contents}
    except FileNotFoundError:
        print("No ATTACH directory found...")


def send_emails(server: SMTP, template, is_html):

    attachments = confirm_attachments()
    sent_count = 0

    for receiver, message, subject in get_msg("data.csv", template, SUBJECT):

        multipart_msg = MIMEMultipart("mixed") if attachments else MIMEMultipart("alternative")

        if subject:
            multipart_msg["Subject"] = subject
        else:
            first_line = message.splitlines()[0]
            if is_html and first_line.startswith("<"):
                multipart_msg["Subject"] = "(no subject)"
            else:
                multipart_msg["Subject"] = first_line

        multipart_msg["From"] = DISPLAY_NAME + f" <{SENDER_EMAIL}>"
        multipart_msg["To"] = receiver

        if not is_html:
            text = message
            html = markdown.markdown(text)
            part1 = MIMEText(text, "plain")
            part2 = MIMEText(html, "html")
            multipart_msg.attach(part1)
            multipart_msg.attach(part2)
        else:
            html = message
            part2 = MIMEText(html, "html")
            multipart_msg.attach(part2)

        if attachments:
            print(f"Attaching {len(attachments['names'])} files...")
            for content, name in zip(attachments["contents"], attachments["names"]):
                attach_part = MIMEBase("application", "octet-stream")
                attach_part.set_payload(content)
                encoders.encode_base64(attach_part)
                attach_part.add_header(
                    "Content-Disposition", f"attachment; filename={name}"
                )
                multipart_msg.attach(attach_part)

        try:
            print(f"Sending email to: {receiver}...", end=" ", flush=True)
            server.sendmail(SENDER_EMAIL, receiver, multipart_msg.as_string())
        except Exception as err:
            print("FAILED")
            print(f"Problem occurend while sending to {receiver} ")
            print(err)
            input("PRESS ENTER TO CONTINUE")
        else:
            print("SUCCESS")
            sent_count += 1

    print(f"Sent {sent_count} emails")


if __name__ == "__main__":
    host = "smtp.gmail.com"
    port = 587  # TLS replaced SSL in 1999

    is_html = MAIL_COMPOSE.lower().endswith((".html", ".htm"))

    with open(MAIL_COMPOSE, "r", encoding="utf-8") as f:
        template = f.read()

    context = ssl.create_default_context()

    server = SMTP(host=host, port=port)
    server.ehlo()
    # server.starttls(context=context)
    server.starttls()
    server.ehlo()
    server.login(user=SENDER_EMAIL, password=PASSWORD)

    # with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
    #     server.login(SENDER_EMAIL, PASSWORD)
    send_emails(server, template, is_html)


# AAHNIK 2023
