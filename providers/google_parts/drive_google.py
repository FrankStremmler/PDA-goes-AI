
import os
from providers.google_parts import google_constants as google_constants
from providers.google_parts import google_base as google_base
from google_auth_oauthlib.flow import InstalledAppFlow


# volle Berechtigung für Zugriff auf Google Drive API
SCOPES = google_constants.GOOGLE_SCOPES


def list_files(service, folder_id='root'):
    # Query: Zeige nur Dateien/Ordner im aktuellen Ordner, die nicht im Papierkorb sind
    query = f"'{folder_id}' in parents and trashed = false"

    results = service.files().list(
        q=query,
        fields="nextPageToken, files(id, name, mimeType)"
    ).execute()
    items = results.get('files', [])

    if not items:
        print('\n--- Dieser Ordner ist leer ---')
        return []

    print(f"\nInhalt von Ordner [{folder_id}]:")
    print(f"{'NAME':<40} {'TYP':<20} {'ID'}")
    print("-" * 80)

    for item in items:
        is_folder = item['mimeType'] == 'application/vnd.google-apps.folder'
        item_type = "[ORDNER]" if is_folder else "Datei"
        print(f"{item['name']:<40} {item_type:<20} {item['id']}")

    return items

def main():
    service = google_base.create_service(google_base.AppType.DRIVE)

    current_folder = 'root'
    while True:
        list_files(service, current_folder)

        print("\nOptionen: [ID eines Ordners] zum Navigieren | 'root' für Hauptmenü | 'exit' zum Beenden")
        choice = input("Deine Wahl: ").strip()

        if choice.lower() == 'exit':
            break
        elif choice:
            current_folder = choice

if __name__ == '__main__':
    main()
