from stockcheckv2 import stock_check
from datetime import datetime
import os
from sendmessage import *

app_id = os.environ.get("FEISHU_APP_ID")
app_secret = os.environ.get("FEISHU_APP_SECRET")
emails_str = os.environ.get("RECIPIENTS", "")
recipient_emails = emails_str.split(",") if emails_str else []

if __name__ == '__main__':
    filename, save_path = stock_check()

    token = "Bearer "
    token += get_tenant_access_token(app_id, app_secret)

    file_key = upload(token, filename, save_path)

    for email in recipient_emails:
        send_file(token, email, file_key)
