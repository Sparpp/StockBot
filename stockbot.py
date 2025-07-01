from stockcheckv2 import *
from datetime import datetime
import os
from sendmessage import *

# app_id = os.environ.get("FEISHU_APP_ID")
# app_secret = os.environ.get("FEISHU_APP_SECRET")
app_id = 'cli_a8e81b2f1a38d062'
app_secret = 'VwY0XK13YWi3tZ40NiWd8bSN8Gtcwsri'
emails_str = os.environ.get("RECIPIENTS", "")
recipient_emails = emails_str.split(",") if emails_str else []

if __name__ == '__main__':
    filename, save_path = stock_check()

    token = "Bearer "
    token += get_tenant_access_token(app_id, app_secret)

    file_key = upload(token, filename, save_path)

    summary = stock_compare()

    # for email in recipient_emails:
    email = 'mingda@xiaomi.com'
    send_file(token, email, file_key)
    send(token, email, summary)

    # delete backfill
    qiantian = datetime.now() - timedelta(days=2)
    date = qiantian.strftime("(%Y-%m-%d)")
    base, ext = os.path.splitext("XiaomiStock.xlsx")
    delete_path = os.path.join("stock_checks", f"{base}{date}{ext}")
    if os.path.exists(delete_path):
        os.remove(delete_path)
        print(f"Deleted old file: {delete_path}")
    else:
        print(f"File not found: {delete_path}")

