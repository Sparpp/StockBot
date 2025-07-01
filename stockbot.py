from stockcheckv2 import stock_check
from datetime import datetime
import os
from sendmessage import *

# token = 'Bearer t-g10171h0ABLDXOPS25BOCWQ3I5AR4A7K7JEH5EIT'
app_id = 'cli_a8e81b2f1a38d062'
app_secret = 'VwY0XK13YWi3tZ40NiWd8bSN8Gtcwsri'

if __name__ == '__main__':
    filename, save_path = stock_check()

    token = "Bearer "
    token += get_tenant_access_token(app_id, app_secret)

    file_key = upload(token, filename, save_path)

    send_file(token, "mingda@xiaomi.com", file_key)
