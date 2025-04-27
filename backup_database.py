import os
import shutil
from datetime import datetime
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
import schedule # type: ignore
import time

# Tải các biến môi trường từ file .env
load_dotenv()

# Cấu hình email từ file .env
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

# Thư mục chứa database và thư mục backup
DATABASE_DIR = "./"  # Thư mục chứa file database
BACKUP_DIR = "./backup"  # Thư mục lưu trữ file backup

# Tạo thư mục backup nếu chưa tồn tại
if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)

def backup_database():
    try:
        # Lấy ngày hiện tại để đặt tên file backup
        current_date = datetime.now().strftime("%Y-%m-%d")
        print("Đang kiểm tra thư mục chứa database...")

        # Tìm tất cả file có đuôi .sql và .sqlite3
        database_files = [f for f in os.listdir(DATABASE_DIR) if f.endswith(('.sql', '.sqlite3'))]
        print("Danh sách file tìm thấy:", database_files)

        if not database_files:
            print("Không tìm thấy file database nào để backup.")
            return False, "Không tìm thấy file database nào để backup."

        backed_up_files = []
        for db_file in database_files:
            # Tạo tên file backup kèm ngày
            backup_file = f"{current_date}_{db_file}"
            # Sao chép file sang thư mục backup
            shutil.copy2(os.path.join(DATABASE_DIR, db_file), os.path.join(BACKUP_DIR, backup_file))
            backed_up_files.append(backup_file)
            print(f"Đã sao lưu file: {db_file} thành {backup_file}")

        return True, f"Sao lưu hoàn tất. Các file đã sao lưu: {', '.join(backed_up_files)}"
    except Exception as e:
        print("Đã xảy ra lỗi trong quá trình backup:", e)
        return False, str(e)

def send_email(subject, body):
    try:
        # Tạo email
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_RECEIVER

        # Kết nối tới SMTP server và gửi email
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
        print("Email đã được gửi thành công.")
    except Exception as e:
        print(f"Không thể gửi email: {e}")

def job():
    # Thực hiện sao lưu
    success, message = backup_database()

    # Tiêu đề email dựa trên kết quả
    subject = "Sao lưu database thành công" if success else "Sao lưu database thất bại"

    # Gửi email thông báo
    send_email(subject, message)

    # Xuất kết quả ra console
    print(message)

# Chạy ngay lập tức để kiểm tra
if __name__ == "__main__":
    print("Đang chạy chương trình backup database...")
    job()