'''
This module contains functions for handling Cloudspace data for the household budget.
using hb_cloud for accessing the cloudspace for the household budget, you can do the following:
- Uploading receipts (.jpg, .png, .pdf, ...) to the cloud.
-checking if the needed files are in the cloud and if notcreating them if they don't exist.
- Storing the extracted data in a database (e.g., SQLite) for further analysis and budget tracking.
'''
import core.household_budget.hb_constants as hb_constants
import core.global_functions as global_functions

import providers.google_parts.drive_google as drive_google


import os
import io
import tempfile
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from sqlalchemy import create_engine, text

# Falls Sie Zugriffsprobleme haben, ändern Sie den Scope auf 'https://googleapis.com'
SCOPES = ['https://googleapis.com.file']
DRIVE_FILE_ID = 'DEINE_GOOGLE_DRIVE_FILE_ID_HIER' # <--- HIER DEINE FILE-ID EINTRAGEN

def get_drive_service():
    """Authentifiziert den Nutzer und gibt den Drive API Service zurück."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('drive', 'v3', credentials=creds)

def download_sqlite(service, file_id, local_path):
    """Lädt die SQLite-Datei von Google Drive in den lokalen Pfad."""
    print("⏳ Downloade Datenbank von Google Drive...")
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()

    with open(local_path, 'wb') as f:
        f.write(fh.getvalue())
    print("✅ Download abgeschlossen.")

def upload_sqlite(service, file_id, local_path):
    """Überschreibt die existierende Datei auf Google Drive mit der lokalen Datei."""
    print("⏳ Upload der aktualisierten Datenbank zu Google Drive...")
    media = MediaFileUpload(local_path, mimetype='application/octet-stream', resumable=True)
    updated_file = service.files().update(
        fileId=file_id,
        media_body=media
    ).execute()
    print(f"✅ Upload erfolgreich abgeschlossen. Datei-ID: {updated_file.get('id')}")

def db_bearbeiten(local_path):
    """Hier führen Sie Ihre SQLAlchemy-Befehle aus."""
    print("⚙️ Bearbeite Datenbank mit SQLAlchemy...")

    # Verbindung zur lokalen temporären Datei herstellen
    engine = create_engine(f"sqlite:///{local_path}", echo=False)

    with engine.begin() as connection:
        # BEISPIEL: Ein einfacher SQL-Befehl (Ersetzen Sie dies durch Ihre Tabellen-Operationen)
        # connection.execute(text("INSERT INTO category (description) VALUES ('Lebensmittel')"))

        # Test-Abfrage zur Kontrolle
        print("   Datenbank erfolgreich geladen. Führe Test-Query aus...")
        # result = connection.execute(text("SELECT * FROM category"))
        # print(f"   Aktuelle Kategorien: {result.all()}")
        pass

def main():
    service = get_drive_service()

    # Erstellt einen sicheren, plattformunabhängigen temporären Dateipfad
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_db:
        temp_path = temp_db.name

    try:
        # 1. Download von Drive
        download_sqlite(service, DRIVE_FILE_ID, temp_path)

        # 2. Lokale Bearbeitung mit SQLAlchemy
        db_bearbeiten(temp_path)

        # 3. Upload zurück zu Drive
        upload_sqlite(service, DRIVE_FILE_ID, temp_path)

    finally:
        # Lokale temporäre Datei nach der Arbeit immer sauber löschen
        if os.path.exists(temp_path):
            os.remove(temp_path)
            print("🧹 Temporäre lokale Datei gelöscht.")

if __name__ == '__main__':
    main()

