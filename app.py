from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import re
import praw

app = Flask(__name__)

# Reddit API credentials
REDDIT_CLIENT_ID = 'xxx'
REDDIT_SECRET = 'xxx'
REDDIT_USER_AGENT = 'search4me69'

# Initialize Reddit instance
reddit = praw.Reddit(client_id=REDDIT_CLIENT_ID,
                     client_secret=REDDIT_SECRET,
                     user_agent=REDDIT_USER_AGENT)

def fetch_text_from_url(url):
    if 'reddit.com' in url:
        return fetch_reddit_content(url)
    else:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        content = soup.get_text(separator='\n', strip=True)
        html_content = f"<html><body><p>{content.replace('\n', '<br>')}</p></body></html>"
        return html_content

def fetch_reddit_content(url):
    submission = reddit.submission(url=url)
    content = f"Title: {submission.title}<br>Selftext: {submission.selftext}<br>Comments:<br>"
    for top_level_comment in submission.comments:
        if isinstance(top_level_comment, praw.models.MoreComments):
            continue
        content += f"{top_level_comment.body}<br>"
    return f"<html><body>{content}</body></html>"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    sender = data.get('sender')
    email_body = data.get('link')
    match = re.search(r'\{(.*?)\}', email_body)
    
    if match:
        url = match.group(1)
    else:
        return jsonify({'error': 'No URL found in the provided email body'}), 400

    html_content = fetch_text_from_url(url)
    return jsonify({'content': html_content, 'sender': sender})

if __name__ == '__main__':
    app.run(debug=True)
