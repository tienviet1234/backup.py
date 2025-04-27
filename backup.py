import os
import shutil
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from datetime import datetime
import schedule
import time

load_dotenv()

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")
print(f"SENDER_EMAIL={SENDER_EMAIL}")
print(f"SENDER_PASSWORD={SENDER_PASSWORD}")
print(f"RECEIVER_EMAIL={RECEIVER_EMAIL}")


DATABASE_DIR = 'database'
BACKUP_DIR = 'backup'

def send_email(subject, body):
    """Gửi email thông báo"""
    message = MIMEMultipart()
    message['From'] = SENDER_EMAIL
    message['To'] = RECEIVER_EMAIL
    message['Subject'] = subject

    message.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(message)
        print("Email đã được gửi.")
    except Exception as e:
        print(f"Gửi email thất bại: {e}")

def backup_database():
    try:
        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)

        files = [f for f in os.listdir(DATABASE_DIR) if f.endswith(('.sql', '.sqlite3'))]
        if not files:
            raise Exception("Không tìm thấy file database để backup.")

        for file in files:
            src = os.path.join(DATABASE_DIR, file)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            dest = os.path.join(BACKUP_DIR, f"{timestamp}_{file}")
            shutil.copy2(src, dest)
        send_email(
            subject="tin nhắn này đã được gửi đến bạn",
            body=f"tin nhắn được gửi đến lúc: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.\nCác file đã backup: {', '.join(files)}"
        )

    except Exception as e:
        send_email(
            subject="Backup Database Thất Bại",
            body=f"Backup thất bại: {e}"
        )
        print(f"Lỗi khi backup: {e}")

schedule.every().day.at("00:00").do(backup_database)

print("Đang tiến hành gửi...")

while True:
    schedule.run_pending()
    time.sleep(1)
