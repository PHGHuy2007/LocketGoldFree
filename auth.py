# locket/auth.py
import json
import uuid
import requests

class Auth:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.device_id = self.generate_device_id()
        self.token = None

    @staticmethod
    def generate_device_id():
        return str(uuid.uuid4()).upper()

    def create_token(self):
        request_data = {
            "email": self.email,
            "password": self.password,
            "clientType": "CLIENT_TYPE_IOS",
            "returnSecureToken": True
        }

        url = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key=AIzaSyCQngaaXQIfJaH0aS2l7REgIjD7nL431So"
        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en",
            "baggage": "sentry-environment=production,sentry-public_key=78fa64317f434fd89d9cc728dd168f50,sentry-release=com.locket.Locket@1.82.0+3,sentry-trace_id=90310ccc8ddd4d059b83321054b6245b",
            "Connection": "keep-alive",
            "Content-Length": "117",
            "Content-Type": "application/json",
            "Host": "www.googleapis.com",
            "sentry-trace": "90310ccc8ddd4d059b83321054b6245b-3a4920b34e94401d-0",
            "User-Agent": "FirebaseAuth.iOS/10.23.1 com.locket.Locket/1.82.0 iPhone/18.0 hw/iPhone12_1",
            "X-Client-Version": "iOS/FirebaseSDK/10.23.1/FirebaseCore-iOS",
            "X-Firebase-AppCheck": "eyJraWQiOiI5ekZsSFEiLCJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiIxOjY0MTAyOTA3NjA4Mzppb3M6Y2M4ZWI0NjI5MGQ2OWIyMzRmYTYwNiIsImF1ZCI6WyJwcm9qZWN0cy82NDEwMjkwNzYwODMiLCJwcm9qZWN0cy9sb2NrZXQtNDI1MmEiXSwicHJvdmlkZXIiOiJkZXZpY2VfY2hlY2tfZGV2aWNlX2lkZW50aWZpY2F0aW9uIiwiaXNzIjoiaHR0cHM6Ly9maXJlYmFzZWFwcGNoZWNrLmdvb2dsZWFwaXMuY29tLzY0MTAyOTA3NjA4MyIsImV4cCI6MTc4Nzg1NTc5NSwiaWF0IjoxNzg3ODUyMTk1LCJqdGkiOiJJWnZzel9rckdodG5ZRG9JZFFOZzlRQk1ocDlhNWNHMllvRmkxbTZJOXFjIn0.mwEMzo2D5FeLqpKpFmc6_dnBGw47Y0EGDisyCqk1ImLMjbehyJAhKxKTqGGr0DTEtjsfj0R7WxhY7BD_Ig5UJiZFb_iUodVfx29X4rsVanmkMKmMON-1Oa1uPonUUr4Su-k2BNe2EqxEhFyGYbJlIccqBJcsTz_I8AEY0fOmE6nY4EyQnMW61GEz4cITa3X9Irjsen0GuxoC3wL1rK3BcZU5GbSxmfkDmNKKxkMRabWbdHtG4aoVmMAGUF0dzeFmiyBeevhgdWEAiYudm9C3IHox2OPdAP3t04Wyb257Q1ZxkK8LB_HE1NOyvlPasu1nr4ht-y6pjUspRf5twFVBvfIzJ5WF29CpS6dfmMhpZAYjczwjgAXZESPfdt75-kPl_n8b4Qy9TtO7vbAXodSVe6KNE9jVse-HzstHNK0azD54yTfrK8nyrM3dGPbK3wU_epz7MAmaLSxiRsyapgdLhtYfaSVeyg_dWsarcouGtcJh3W5_ZE8vnAQ-GylsPkhW",
            "X-Firebase-GMPID": "1:641029076083:ios:cc8eb46290d69b234fa606",
            "X-Ios-Bundle-Identifier": "com.locket.Locket"
        }

        response = requests.post(url, headers=headers, json=request_data)

        if response.ok:
            self.token = response.json().get('idToken')
            return self.token
        else:
            raise Exception('Failed to login')

    def get_token(self):
        if not self.token:
            self.create_token()
        return self.token