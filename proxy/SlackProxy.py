import requests

class SlackProxy:
    def __init__(self, oauth_token):
        self.oauth_token = oauth_token
        self.headers = {'Authorization': f'Bearer {self.oauth_token}'}

    def fetch_channels(self):
        url = 'https://slack.com/api/conversations.list'
        print('auth header', self.headers)
        response = requests.get(url, headers=self.headers)
        print('slack response', response.json())
        if response.json()['ok']:
            return response.json()['channels']
        else:
            print('Failed to fetch channel list')
            return None

    def fetch_messages_from_channel(self, channel_id):
        url = f'https://slack.com/api/conversations.history?channel={channel_id}'
        response = requests.get(url, headers=self.headers)
        print('slack response', response.json())
        if response.json()['ok']:
            return response.json()['messages']
        else:
            print(f'Failed to fetch messages for channel {channel_id}')
            return None
        
    def convert_messages_into_text(self, messages):
        text = ''
        for message in messages:
            # convert messages into text, including the user name and timestamp
            text += message['text']
            text += '\n\n'
            
        return text