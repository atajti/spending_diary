import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json

def get_config(config_path: str = "conf/app_config.json") -> dict:
    with open(config_path, "r") as config_file:
        app_conf = json.load(config_file)
    with open(app_conf["sheet_info"], "r") as sheet_file:
        app_conf["sheet_info"] = json.load(sheet_file)
    with open(app_conf["limit_info"], "r") as limit_file:
        app_conf["limit_info"] = json.load(limit_file)
    return app_conf


    
def authenticate(app_config: dict = {"oauth_json_path": "secrets/oauth_file.json",
                                     "token_path": "secrets/token.json",
                                     "scopes":["https://www.googleapis.com/auth/spreadsheets.readonly"]}
    ) -> Credentials:
    """Get permission fom user
    :param app_config: dict of necessary constants: oauth_json, token_path and scopes.
    :return: credential to use in operations on Google APIs
    """
    oauth_json = app_config["oauth_json_path"]
    token_path = app_config["token_path"]
    scopes = app_config["scopes"]
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    # If modifying these scopes, delete the file token.json.
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, scopes)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
          creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                     oauth_json, scopes
                   )
            creds = flow.run_local_server(port=8888,
                                          access_type="offline" )
        # Save the credentials for the next run
        with open(token_path, "w") as token:
            token.write(creds.to_json())
    return creds


def get_values_from_sheet(creds: Credentials,
                          spreadsheet_id: str,
                          range: str) -> list:
    """Collects data from Google Sheet.
    :param creds: Cerdential, provided by authenticate()
    :param spreadsheet_id: ID of Google Sheets document
    :param range: ange to get data from in the form of 'sheetname!first_cell:last_cell'
    :returns: list of values by row
    :raises: HttpError
    """
    try:
        service = build("sheets", "v4", credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = (
            sheet.values()
                 .get(spreadsheetId=spreadsheet_id,
                      range=range)
                 .execute())
        values = result.get("values", [])
    except HttpError as err:
        raise(err)



def main():
    """Gets values from GSheet.
    """

    app_config = get_config("conf/app_config.json")
    credential = authenticate(app_config)
    values = get_values_from_sheet(credential,
                                   spreadsheet_id=app_config["sheet_info"]["spreadsheet_id"],
                                   range=app_config["sheet_info"]["range"])
    if not values:
        print("No data found.")
        return

    else:
        pprint(values)
        #for row in values:
        #    # Print columns A and E, which correspond to indices 0 and 4.
        #    print(f"{row[0]}, {row[4]}")


if __name__ == "__main__":
    main()
