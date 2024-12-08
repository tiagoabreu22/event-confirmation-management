import smtplib
from email.mime.text import MIMEText
from config import Config


class EmailSender:
    def __init__(self):
        self.smtp = None

    def connect(self):
        if self.smtp is None:
            self.smtp = smtplib.SMTP_SSL(Config.SMTP_SERVER, Config.SMTP_PORT)
            self.smtp.login(Config.SMTP_USERNAME, Config.SMTP_PASSWORD)

    def send_emails(self, recipients):
        try:
            self.connect()
            print("Connected to SMTP server")
            for to, subject, body in recipients:
                msg = MIMEText(body)
                msg["Subject"] = subject
                msg["From"] = Config.SMTP_USERNAME
                msg["To"] = to

                self.smtp.sendmail(Config.SMTP_USERNAME, to, msg.as_string())
                print(f"Email sent to {to}")
        except Exception as e:
            print(f"Error sending email: {e}")
        finally:
            print("Closing connection")
            self.close()

    def close(self):
        if self.smtp:
            self.smtp.quit()
            self.smtp = None


email_sender = EmailSender()


def send_emails(recipients):
    email_sender.send_emails(recipients)
