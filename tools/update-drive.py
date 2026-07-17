import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import logging

# If modifying these scopes, delete the file token.json.
# Available scopes are listed at
# https://developers.google.com/identity/protocols/oauth2/scopes
SCOPES = ["https://www.googleapis.com/auth/drive"]

input_dir = "JEX HAR files"
output_dir = "JEX HTML files"

logger = logging.getLogger(__name__)

def ex(msg, exit_code=1):
    logging.error(msg)
    sys.exit(exit_code)


def get_creds():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "/home/dmarti/credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds

def main():
    creds = get_creds()

    try:
        service = build("drive", "v3", credentials=creds)
    except Exception as ex:
        error_out(ex)

    # Call the Drive v3 API to list folders
    results = service.files().list(
        q="mimeType = 'application/vnd.google-apps.folder' and trashed = false and name contains '%s'" % input_dir,
        fields="nextPageToken, files(id, name)"
    ).execute()

    items = results.get('files', [])

    if not items or len(items) != 1:
        error("Input folder %s not found or too many matching folders" % input_dir)
    else:
        print('Folders found:')
        for item in items:
            print(f"{item['name']} (ID: {item['id']})")


if __name__ == "__main__":
    main()
