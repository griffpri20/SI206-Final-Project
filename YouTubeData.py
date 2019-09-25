## Copied from YouTube documentation

import os
import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow

CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

## Function sets up authentication to use YouTube API
## Input: Nothing
## Output: returns credentials to access YouTube API
def get_authenticated_service():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    credentials = flow.run_console()
    return build(API_SERVICE_NAME, API_VERSION, credentials = credentials)

## Function takes in video ID for YouTube video and provides information on it
## Input: Client that allows access to API, a number of potential parameters specified in documentation
## Output: Dictionary of information given by a specified video ID
def videos_list_by_id(client, **kwargs):
    response = client.videos().list(
                **kwargs
                ).execute()
    return response
#3 Function allows to search video on YouTube by keyword, and provides videos the querey found
## Input: Client that allows access to API, a number of potential parameters specified in documentation
## Output: response, which is a list of dictioanries each representing a YouTube video
def search_list_by_keyword(client, **kwargs):
    response = client.search().list(
                **kwargs
                ).execute()
    return response

## Main function for the YouTube file
## Input: Three movie titles
## Ouptut: List of tuples with data on movies to be manipulated. Tuple looks like (info, movie title)
def main(q1, q2, q3):
    client = get_authenticated_service()
    print('Running...')
    vid_details = []
    for i in [q1, q2, q3]:
        x = search_list_by_keyword(client,
            part = 'snippet',
            maxResults = 50,
            q = i,
            type = '')
        for video in x['items']:
            try:
                vidID = video['id']['videoId']
                x = videos_list_by_id(client,
                    part='snippet,contentDetails,statistics',
                    id=vidID)
                vid_details.append((x, i))
            except:
                continue
    return vid_details
