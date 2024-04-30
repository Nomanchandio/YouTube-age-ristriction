import re
import os
import json
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

API_KEY = os.getenv('API_KEY', 'AIzaSyBw-ER74Nr2LAdpnWnG0xL9ZOgbWdExYZY')
youtube = build('youtube', 'v3', developerKey=API_KEY)

def extract_video_id(url):
    # Extract video ID from URL using regular expression
    match = re.search(r'(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})', url)
    if match:
        return match.group(1)
    else:
        return None

def check_age_restriction(video_id):
    try:
        video_response = youtube.videos().list(
            part='contentDetails',
            id=video_id
        ).execute()

        if 'items' in video_response and video_response['items']:
            content_details = video_response['items'][0]['contentDetails']
            if 'regionRestriction' in content_details:
                return "Age-restricted"
            else:
                return "Not age-restricted"
        else:
            return "Not found or does not exist"
    except HttpError as e:
        return f"Error: {e}"

def lambda_handler(event, context):
    if event['httpMethod'] == 'POST':
        body = json.loads(event['body'])
        video_url = body.get('video_url', '')

        video_id = extract_video_id(video_url)

        if video_id:
            result = check_age_restriction(video_id)
            response = {
                "statusCode": 200,
                "body": json.dumps({"result": result})
            }
        else:
            response = {
                "statusCode": 400,
                "body": json.dumps({"error": "Invalid YouTube video URL."})
            }
    else:
        response = {
            "statusCode": 200,
            "body": json.dumps({"message": "Not Age Ristricted!"})
        }

    return response

if __name__ == '__main__':
    event = {
        'httpMethod': 'POST',
        'body': json.dumps({'video_url': 'https://www.youtube.com/watch?v=VvhcsmVMhmg&list=RDVvhcsmVMhmg&start_radio=1&ab_channel=TrackDollar'})
    }
    context = {}
    print(lambda_handler(event, context))