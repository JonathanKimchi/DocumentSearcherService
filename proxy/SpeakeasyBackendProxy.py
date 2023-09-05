import json
import os
import requests

def is_production():
    return os.environ['ENV_STAGE'] == 'production'

class SpeakeasyBackendProxy:
    def __init__(self):
        self.backend_url = "https://speakeasy-auth-backend.onrender.com/api" if is_production() else "http://localhost:4242/api"

    def get_headers(self, token):
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}',
        }

    def post_request(self, url, data, token):
        headers = self.get_headers(token)
        response = requests.post(url, headers=headers, json=data)
        print(f"Response status code: {response.status_code}")
        print(f"Response text: {response.text}")
        return response.json()

    def create_user(self, user, token):
        url = f"{self.backend_url}/user"
        data = {'user': user, 'token': token}
        return self.post_request(url, data, token)

    def get_slack_access_token_for_chatbot(self, chatbot_id, token):
        url = f"{self.backend_url}/chatbot/slack/get-access-token-for-chatbot"
        data = {'chatbotId': chatbot_id}
        result = self.post_request(url, data, token)
        return result.get("accessToken", None)


# Initialize the SpeakeasyBackendProxy
speakeasy_backend_proxy = SpeakeasyBackendProxy()
