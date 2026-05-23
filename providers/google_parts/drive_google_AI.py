
import os
from providers.google_parts import google_constants as google_constants
from providers.google_parts import google_base as google_base
# from google_auth_oauthlib.flow import InstalledAppFlow


# volle Berechtigung für Zugriff auf Google Drive API
SCOPES = google_constants.GOOGLE_SCOPES


import mimetypes
import os
import tempfile
from googleapiclient.discovery import Resource
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload


class GoogleDriveHelper:

    def __init__(self, drive_service: Resource):
        """Initialisiert den Helfer mit dem Google Drive Service-Objekt."""
        self.service = drive_service
        self.current_folder_id = "root"

        # Interne Speicher für die vereinfachten IDs (Fortlaufende Nummern)
        self.folder_registry = {}  # Format: {"fol_1": {"id": "drive_id", "name": "..."}}
        self.file_registry = {}  # Format: {"fil_1": {"id": "drive_id", "name": "..."}}

        self._folder_counter = 1
        self._file_counter = 1

    def _resolve_folder_id(self, folder_var: str) -> str:
        """Löst 'root', benutzerdefinierte IDs (fol_x) oder echte Drive-IDs auf."""
        if not folder_var:
            return "root"
        if folder_var in self.folder_registry:
            return self.folder_registry[folder_var]["id"]
        return folder_var

    def _resolve_file_id(self, file_var: str) -> str:
        """Löst benutzerdefinierte IDs (fil_x) oder echte Drive-IDs auf."""
        if file_var in self.file_registry:
            return self.file_registry[file_var]["id"]
        return file_var

    def _generate_folder_id(self) -> str:
        """Generiert eine eindeutige, kurze ID für Ordner."""
        fid = f"fol_{self._folder_counter}"
        self._folder_counter += 1
        return fid

    def _generate_file_id(self) -> str:
        """Generiert eine eindeutige, kurze ID für Dateien."""
        fid = f"fil_{self._file_counter}"
        self._file_counter += 1
        return fid

    def list_directory(self, folder_id: str = None) -> dict:
        """Erstellt eine Liste aller Ordner und Dateien im Verzeichnis."""
        target_id = self._resolve_folder_id(folder_id or self.current_folder_id)

        query = f"'{target_id}' in parents and trashed = false"
        fields = "files(id, name, mimeType)"

        results = (
            self.service.files()
            .list(q=query, fields=fields, supportsAllDrives=True, includeItemsFromAllDrives=True)
            .execute()
        )
        items = results.get("files", [])

        output_folders = []
        output_files = []

        for item in items:
            is_folder = item.get("mimeType") == "application/vnd.google-apps.folder"

            if is_folder:
                custom_id = self._generate_folder_id()
                folder_data = {"folder_id": custom_id, "id": item["id"], "name": item["name"]}
                self.folder_registry[custom_id] = folder_data
                output_folders.append(folder_data)
            else:
                custom_id = self._generate_file_id()
                file_data = {"file_id": custom_id, "id": item["id"], "name": item["name"]}
                self.file_registry[custom_id] = file_data
                output_files.append(file_data)

        return {"Folders": output_folders, "Files": output_files}

    def list_files(self, folder_id: str = None) -> list:
        """Erstellt eine Liste mit allen Dateien exklusiv Ordner im Verzeichnis."""
        full_dir = self.list_directory(folder_id)
        return full_dir["Files"]

    def list_folders(self, folder_id: str = None) -> list:
        """Erstellt eine Liste aller Ordner im Verzeichnis."""
        full_dir = self.list_directory(folder_id)
        return full_dir["Folders"]

    def create_folder(self, name: str, folder_id: str = None) -> dict:
        """Erstellt ein neues Verzeichnis im angegebenen Verzeichnis."""
        target_id = self._resolve_folder_id(folder_id or self.current_folder_id)

        file_metadata = {"name": name, "mimeType": "application/vnd.google-apps.folder", "parents": [target_id]}

        folder = self.service.files().create(body=file_metadata, fields="id, name", supportsAllDrives=True).execute()

        custom_id = self._generate_folder_id()
        folder_data = {"folder_id": custom_id, "id": folder["id"], "name": folder["name"]}
        self.folder_registry[custom_id] = folder_data

        return folder_data

    def change_folder(self, folder_id: str = "root") -> None:
        """Wechselt in das angegebene Verzeichnis (beeinflusst Folgebefehle)."""
        resolved_id = self._resolve_folder_id(folder_id)
        self.current_folder_id = resolved_id

    def get_file(self, file_id: str, target_dir: str = None) -> str:
        """Liest eine Datei und speichert sie lokal im Zielordner oder im Temp-Ordner."""
        resolved_file_id = self._resolve_file_id(file_id)

        # Metadaten holen, um den echten Dateinamen zu erfahren
        metadata = self.service.files().get(fileId=resolved_file_id, fields="name", supportsAllDrives=True).execute()
        filename = metadata.get("name", "downloaded_file")

        if target_dir:
            # Expliziter Zielordner
            os.makedirs(target_dir, exist_ok=True)
            local_path = os.path.join(target_dir, filename)
        else:
            # Temporärer Ordner mit generiertem Präfix/Suffix
            name_part, ext_part = os.path.splitext(filename)
            temp_file = tempfile.NamedTemporaryFile(prefix=f"{name_part}_", suffix=ext_part, delete=False)
            local_path = temp_file.name
            temp_file.close()

        request = self.service.files().get_media(fileId=resolved_file_id, supportsAllDrives=True)

        with open(local_path, "wb") as f:
            downloader = MediaIoBaseDownload(f, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()

        return local_path

    def update_file(self, file_id: str, local_file_path: str) -> dict:
        """Ersetzt eine existierende Datei in Drive durch eine neue lokale Version."""
        resolved_file_id = self._resolve_file_id(file_id)

        if not os.path.exists(local_file_path):
            raise FileNotFoundError(f"Lokale Datei nicht gefunden: {local_file_path}")

        filename = os.path.basename(local_file_path)
        mime_type, _ = mimetypes.guess_type(local_file_path)
        if not mime_type:
            mime_type = "application/octet-stream"

        file_metadata = {"name": filename}
        media = MediaFileUpload(local_file_path, mimetype=mime_type, resumable=True)

        updated_file = (
            self.service.files()
            .update(fileId=resolved_file_id, body=file_metadata, media_body=media, fields="id, name", supportsAllDrives=True)
            .execute()
        )

        # Registry aktualisieren, falls sich der Name geändert hat
        for custom_id, data in self.file_registry.items():
            if data["id"] == updated_file["id"]:
                self.file_registry[custom_id]["name"] = updated_file["name"]
                return self.file_registry[custom_id]

        custom_id = self._generate_file_id()
        file_data = {"file_id": custom_id, "id": updated_file["id"], "name": updated_file["name"]}
        self.file_registry[custom_id] = file_data
        return file_data

if __name__ == '__main__':
    # main()
    pass
