# import slack
from slack_sdk import WebClient
# from slack_sdk.errors import SlackApiError

import os
import json
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request, Response
from slackeventsapi import SlackEventAdapter # slack events

import datetime

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(os.environ['SIGNING_SECRET'], '/slack/events', app)

client = WebClient(token=os.environ['SLACK_TOKEN'])

# client.chat_postMessage(channel='#test-bot', text="<@U03RXABEPBR> fuck you")

BOT_ID = client.api_call('auth.test')['user_id']
print(client.api_call('auth.test'))

welcome_messages = {}

class WelcomeMessage:
  START_TEXT = {
    'type': 'section',
    'text': {
      'type': 'mrkdwn',
      'text': (
        'Welcome to my world! \n\n'
        '*Get started by comleting the tasks!*'
      )
    }
  }
  
  DIVIDER = {'type': 'divider'}

  def __init__(self, channel, user):
    self.channel = channel
    self.user = user
    self.icon_emoji = ':aprs:'
    self.timestamp = ''
    self.completed = False
    
  def get_message(self):
    return {
      'ts': self.timestamp,
      'channel': self.channel,
      'username': 'Welcome to my world!',
      'icon_emoji': self.icon_emoji,
      'blocks': [
        self.START_TEXT,
        self.DIVIDER,
        self._get_reaction_task()
      ]
    }
  
  def _get_reaction_task(self):
    checkmark = ':white_check_mark:'
    if not self.completed:
      checkmark = ':white_large_square:'

    text = f'{checkmark} *React to this message!*'
    
    return [{'type': 'section', 'text': {'type': 'mrkdwn', 'text': text}}]

def send_welcome_message(channel, user):
  welcome = WelcomeMessage(channel, user)
  message = welcome.get_message()
  response = client.chat_postMessage(**message)
  welcome.timestamp = response['ts']

  if channel not in welcome_messages:
    welcome_messages[channel] = {}
  welcome_messages[channel][user] = welcome

@app.route('/')
def home():
  return "The bot is alive!!"

@slack_event_adapter.on('app_mention')
def handle_message(payload):
  print(payload)
  event = payload.get('event', {})
  channel_id = event.get('channel')
  
  user_id = event.get('user')
  user_message = event.get('text')
  ts = event.get('ts')

  if BOT_ID != user_id:
    # send_welcome_message(channel_id, user_id)
    if 'checkin' in user_message:
      date = datetime.datetime.fromtimestamp(int(float(ts)))
      checkin_time = date.strftime('%m/%d/%y %H:%M')
      try:
        print("ahihi do ngoc")
      except:
        print("")
      
      client.chat_postMessage(channel=channel_id, text=f"<@{user_id}>\nCheckin: {checkin_time}", thread_ts=ts)
    else:
      export_member_template = get_templates("export_members")
      client.chat_postEphemeral(
        channel=channel_id,
        blocks=export_member_template,
        user=user_id
      )



@app.route('/commands', methods=['POST'])
def message_count():
  data = request.form
  print(data)
  channel_id = data.get('channel_id')
  user_id = data.get('user')
  client.chat_postMessage(channel=channel_id, text="I got your command")
  return Response(), 200

def get_templates(template):
  with open(f"templates/{template}.json", 'r') as f:
    template = json.load(f)

  return template

if __name__ == "__main__":
  app.run(debug=True, port='3003')