import json
import requests
from requests_toolbelt import MultipartEncoder

def get_tenant_access_token(app_id, app_secret):
    url = "https://open.f.mioffice.cn/open-apis/auth/v3/tenant_access_token/internal"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "app_id": app_id,
        "app_secret": app_secret
    }

    response = requests.post(url, json=payload, headers=headers)
    data = response.json()

    if response.status_code == 200 and data.get("code") == 0:
        return data["tenant_access_token"]
    else:
        print("Error getting token:", data)
        return None

def send(token, email, msg):
    url = "https://open.f.mioffice.cn/open-apis/im/v1/messages"
    params = {"receive_id_type":"email"}
    msgContent = {
        "text": msg,
    }
    req = {
        "receive_id": email,
        "msg_type": "text",
        "content": json.dumps(msgContent)
    }
    payload = json.dumps(req)
    headers = {
        'Authorization': token,
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, params=params, headers=headers, data=payload)
    print(response.content)

def send_file(token, email, file_id):
    url = "https://open.f.mioffice.cn/open-apis/im/v1/messages"
    params = {"receive_id_type":"email"}
    msgContent = {
        "file_key": file_id,
    }
    req = {
        "receive_id": email,
        "msg_type": "file",
        "content": json.dumps(msgContent)
    }
    payload = json.dumps(req)
    headers = {
        'Authorization': token,
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, params=params, headers=headers, data=payload)
    print(response.content)

def upload(token, filename, filepath):
    url = "https://open.f.mioffice.cn/open-apis/im/v1/files"
    form = {'file_type': 'xls',
            'file_name': filename,
            'file':  (filename, open(filepath, 'rb'), "application/vnd.ms-excel")}
    multi_form = MultipartEncoder(form)
    headers = {
    'Authorization': token, 
    }
    headers['Content-Type'] = multi_form.content_type
    response = requests.request("POST", url, headers=headers, data=multi_form)
    print(response.content)

    response_json = response.json()

    return response_json["data"]["file_key"]
