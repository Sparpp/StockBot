from stockcheck import *
from sendmessage import *

app_id = os.environ.get("FEISHU_APP_ID")
app_secret = os.environ.get("FEISHU_APP_SECRET")
emails_str = os.environ.get("RECIPIENTS", "")
recipient_emails = emails_str.split(",") if emails_str else []

if __name__ == '__main__':
    # check stock via webpages
    # filename, save_path = stock_check()

    print("test")

    # # request token
    # token = "Bearer "
    # token += get_tenant_access_token(app_id, app_secret)

    # # upload latest stock statuses
    # file_key = upload(token, filename, save_path)

    # # compare current stock status with previous
    # summary = stock_compare()

    # # send stock spreadsheet and summary of changes to recipients via bot
    # for email in recipient_emails:
    #     send_file(token, email, file_key)
    #     send(token, email, summary)
