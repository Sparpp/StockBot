from stockcheckv2 import *
from sendmessage import *

app_id = os.environ.get("FEISHU_APP_ID")
app_secret = os.environ.get("FEISHU_APP_SECRET")
emails_str = os.environ.get("RECIPIENTS", "")
recipient_emails = emails_str.split(",") if emails_str else []

if __name__ == '__main__':
    # check stock via webpages
    filename, save_path = stock_check()

    # request token
    token = "Bearer "
    token += get_tenant_access_token(app_id, app_secret)

    # upload latest stock statuses
    file_key = upload(token, filename, save_path)

    # compare current stock status with previous
    summary = stock_compare()

    # send stock spreadsheet and summary of changes to recipients via bot
    for email in recipient_emails:
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
