import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload

import io
import json
import logging
import subprocess
import sys

# If modifying these scopes, delete the file token.json.
# Available scopes are listed at
# https://developers.google.com/identity/protocols/oauth2/scopes
SCOPES = ["https://www.googleapis.com/auth/drive"]

SECRET = 'gdrive-secret'

remote_dir = "CONFIDENTIAL web surveillance data"

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, stream=sys.stderr, format='%(levelname)s: %(message)s')

def error_out(msg, exit_code=1):
    "Exit with an error message"
    logging.error(msg)
    sys.exit(exit_code)

def har_name_to_report_name(har_name):
    if har_name.endswith('.har'):
        return har_name[:-4]
    raise NotImplementedError

def private_open(path, flags):
    "Open files for writing with only user r/w permission"
    return os.open(path, flags, 0o700)

def get_creds():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    tstore = os.path.join(os.environ['HOME'], '.jex')
    os.makedirs(tstore, mode=0o700, exist_ok=True)
    os.chmod(tstore, 0o700)
    tfile = os.path.join(tstore, 'token.json')
    if os.path.exists(tfile):
        creds = Credentials.from_authorized_user_file(tfile, SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            process = subprocess.run(['/usr/bin/pass', 'show', SECRET], capture_output=True, text=True, check=True)
            client_secrets = json.loads(process.stdout)
            flow = InstalledAppFlow.from_client_config(client_secrets, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(tfile, "w", opener=private_open) as token:
            token.write(creds.to_json())
    return creds

def main():
    creds = get_creds()

    try:
        service = build("drive", "v3", credentials=creds)
    except Exception as ex:
        error_out(ex)

    # Call the Drive v3 API to list folders
    q = "mimeType = 'application/vnd.google-apps.folder' and trashed = false and name contains '%s'" % remote_dir
    results = service.files().list(q=q, fields="nextPageToken, files(id)").execute()

    items = results.get('files', [])
    if not items or len(items) != 1:
        error_out("Input folder %s not found or too many matching folders" % remote_dir)
    else:
        folder_id = items[0]['id']
        logging.debug("Folder id is %s" % folder_id)

    q = f"'%s' in parents and trashed = false" % folder_id
    results = service.files().list(
        q=q,
        pageSize=100,
        fields="nextPageToken, files(id, name, mimeType)"
    ).execute()

    if results.get('nextPageToken'):
        raise NotImplementedError

    items = results.get('files', [])

    if not items:
        print('No files found in this folder.')
    else:
        for item in items:
            if item['mimeType'] not in ('application/json'):
                logging.debug("Skipping file by MIME type: %s (%s)" % (item['name'], item['mimeType']))
                continue

            output_filename = item['name']
            if os.path.isfile(output_filename):
                logging.debug("Skipping existing local file %s" % output_filename)
                continue

            request = service.files().get_media(fileId=item['id'])
            fh = io.FileIO(output_filename, 'wb')
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                logging.debug("Download progress: %d%%" % int(status.progress() * 100))
            logging.info("Downloaded %s" % output_filename)

            report_name = har_name_to_report_name(output_filename)

            file_metadata = {
                'name': report_name,
                'mimeType': 'application/vnd.google-apps.document',
                'parents': [folder_id]
            }

            html_content = "<h1>Hello world</h1><p>This is the body copy</p>"

            html_bytes = io.BytesIO(html_content.encode('utf-8'))
            media = MediaIoBaseUpload(html_bytes, mimetype='text/html', resumable=True)

            file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()

            logging.info("Created new report with id %s" % file.get('id'))

if __name__ == "__main__":
    main()
