
# # Berechtigungen für die APIS - volle Berechtigung für Zugriff auf Google Calendar, Contacts und Drive API.
# # Unterfuntionen wie calender.readonly oder drive.file können später hinzugefügt werden, um die Berechtigungen zu begrenzen.

# # interne Bibliotheken
# # Datum/Zeit implementation
# import datetime
# # zoneinfo für Zeitzonen-Umwandlung (tzdata muss installiert sein)
# from zoneinfo import ZoneInfo

# import os
# # import json

#externe Bibliotheken
# from google.auth.transport.requests import Request
# from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import InstalledAppFlow
# from googleapiclient.discovery import build

# eigene Module importieren
import os as os
from enum import Enum
import core.global_functions as global_functions
import providers.google_parts.google_constants as google_constants
from google_auth_oauthlib.flow import InstalledAppFlow
from pydantic import BaseModel, Field


class AppType(Enum):
    CALENDAR = 'calendar'
    CONTACTS = 'contacts'
    DRIVE = 'drive'

class DriveFolders(BaseModel):
    # Klassen-Variable für das Autoincrement
    _counter: int = 1

    folder_id: str = Field(default=None)
    id: str
    name: str

    def __init__(self, **data):
        super().__init__(**data)
        # Wenn keine folder_id übergeben wurde, automatisch generieren
        if not self.folder_id:
            self.folder_id = f"fol_{DriveFolders._counter}"
            DriveFolders._counter += 1


class DriveFiles(BaseModel):
    _counter: int = 1

    file_id: str = Field(default=None)
    id: str
    name: str

    def __init__(self, **data):
        super().__init__(**data)
        if not self.file_id:
            self.file_id = f"fil_{DriveFiles._counter}"
            DriveFiles._counter += 1

# class DriveFiles(BaseModel):
#     id_file: int
#     name: str
#     mimeType: str
#     id_drive: str

#     def __init__(self, id_file, name, mimeType, id_drive):
#         super().__init__(id_file=id_file, name=name, mimeType=mimeType, id_drive=id_drive)

# class DriveFolders(BaseModel):
#     id_folder: int
#     name: str
#     id_drive: str

#     def __init__(self, id_folder, name, id_drive):
#         super().__init__(id_folder=id_folder, name=name, id_drive=id_drive)

    # @property
    # def id(self):
    #     return self['id']
    # @setter
    # def id(self, value):
    #     self['id'] = value

    # @property
    # def name(self):
    #     return self['name']
    # @setter
    # def name(self, value):
    #     self['name'] = value

    # @property
    # def mimeType(self):
    #     return self['mimeType']
    # @setter
    # def mimeType(self, value):
    #     self['mimeType'] = value

    # @property # read-only, so not setter
    # def drive_id(self):
    #     return self['drive_id']


GOOGLE_SCOPES = google_constants.GOOGLE_SCOPES
CREDENTIALS_FILE = os.path.join(google_constants.CONFIG_PATH, 'credentials.json')
TOKEN_FILE = os.path.join(google_constants.CONFIG_PATH, 'token.json')

# Standradfunktion für die Erstellung eines Dienstes, um mit der Google API zu kommunizieren.
def create_service(apptype: AppType = AppType.CALENDAR):
    '''
    Erstellt einen Dienst, um mit Google API's zu kommunizieren.
    Handhabt die Authentifizierung und Token-Verwaltung.
    Gibt ein Service-Objekt zurück, das für API-Aufrufe verwendet werden kann.
    '''
    creds = None
    # Token speichert die Benutzeranmeldung für den nächsten Lauf
    if os.path.exists(TOKEN_FILE):
        creds = google_constants.Credentials.from_authorized_user_file(TOKEN_FILE, GOOGLE_SCOPES)

    # Login, falls kein gültiger Token existiert, ruft die Login-Seite auf, um die Berechtigungen zu erteilen
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(google_constants.Request())
        else:
            flow = google_constants.InstalledAppFlow.from_client_secrets_file(
                client_secrets_file=CREDENTIALS_FILE,
                scopes=GOOGLE_SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    match apptype:
        case AppType.CALENDAR:
            service = google_constants.build('calendar', 'v3', credentials=creds)
        case AppType.CONTACTS:
            service = google_constants.build('contacts', 'v1', credentials=creds)
        case AppType.DRIVE:
            service = google_constants.build('drive', 'v3', credentials=creds)
        case _:
            raise ValueError(f"Unbekannter AppType: {apptype}")
    return service


if __name__ == '__main__':
    pass
    # service = create_service()
    # print("Google Service erfolgreich erstellt:", service)
