import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

scope = ['https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive.file',
         'https://www.googleapis.com/auth/drive']

creds = ServiceAccountCredentials.from_json_keyfile_name(os.path.expanduser('~/.servile_google_sheets_creds.json'),
                                                         scope)
client = gspread.authorize(creds)


def get_sheet_id_by_title(gspread_client: gspread.client.Client, title: str):
    for sheet in gspread_client.openall():
        if sheet.title == title:
            return sheet.id
    raise Exception(f"sheet not found: {title}")


def upload_csv(spreadsheet_title: str, csv_raw: str):
    global client
    client.import_csv(get_sheet_id_by_title(client, spreadsheet_title), csv_raw)
