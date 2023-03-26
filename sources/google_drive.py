import io
import logging
import functools

from typing import List, Optional, TypeVar, Callable, Any, cast

from googleapiclient.errors import HttpError
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from googleapiclient.discovery import build
from google.auth.exceptions import GoogleAuthError

from shared.settings import config


SCOPES = ['https://www.googleapis.com/auth/drive']

F = TypeVar('F', bound=Callable[..., Any])


class GoogleDriveClientError(Exception):
    pass


def log_http_error(function: F) -> F:
    @functools.wraps(function)
    def wrapper(self, *args, **kwargs):
        try:
            return function(self, *args, **kwargs)
        except HttpError as e:
            self._logger.error(e, exc_info=True)
            raise GoogleDriveClientError(str(e)) from e
        except GoogleAuthError as e:
            self._logger.error(e, exc_info=True)
            raise GoogleDriveClientError(str(e)) from e
    return cast(F, wrapper)


class GoogleDriveClient:

    def __init__(
        self,
        logger: logging.Logger = None
    ) -> None:
        self._logger = logger or logging.getLogger(__name__)
        self._service = self._get_service()

    @staticmethod
    def _get_service():
        credentials = service_account.Credentials.from_service_account_file(
            config.GOOGLE_KEY_PATH, scopes=SCOPES)
        return build('drive', 'v3', credentials=credentials)

    @log_http_error
    def search_files(self, query: Optional[str] = None, files_fields: Optional[List[str]] = None):
        """
        https://developers.google.com/drive/api/guides/search-files?hl=ru
        """
        if files_fields is None:
            files_fields = ['id', 'name']
        files_fields_s = ', '.join(files_fields)
        try:
            files = []
            page_token = None
            while True:
                response = self._service.files().list(
                    q=query,
                    pageSize=100,
                    spaces='drive',
                    fields=f'nextPageToken, files({files_fields_s})',
                    pageToken=page_token).execute()
                files.extend(response.get('files', []))
                page_token = response.get('nextPageToken', None)
                if page_token is None:
                    break

        except HttpError as e:
            raise e
        return files

    @log_http_error
    def get_file(self, file_id: str) -> io.BytesIO:
        """
        https://developers.google.com/drive/api/guides/manage-downloads?hl=ru
        """
        request = self._service.files().get_media(fileId=file_id)
        file = io.BytesIO()
        downloader = MediaIoBaseDownload(file, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        return file

    @log_http_error
    def export_file(self, file_id: str, mime_type: str) -> io.BytesIO:
        """
        https://developers.google.com/drive/api/v3/reference/files/export
        """
        request = self._service.files().export_media(fileId=file_id, mimeType=mime_type)
        file = io.BytesIO()
        downloader = MediaIoBaseDownload(file, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        return file

    @log_http_error
    def create_file_from_bytes_io(
            self,
            filename: str,
            folder_id: str,
            mimetype: str,
            file: io.BytesIO,
    ) -> dict:
        """
        https://developers.google.com/drive/api/guides/manage-uploads?hl=ru#multipart
        """
        file_metadata = {
            'name': filename,
            'parents': [folder_id],
            }
        media = MediaIoBaseUpload(fd=file, resumable=True, mimetype=mimetype)
        result = self._service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return result

    @log_http_error
    def update_content_file(
            self,
            file_id: str,
            mimetype: str,
            file: io.BytesIO,
    ) -> dict:
        """
        https://developers.google.com/drive/api/guides/manage-uploads?hl=ru
        https://developers.google.com/drive/api/v3/reference/files?hl=ru
        """
        media = MediaIoBaseUpload(fd=file, resumable=True, mimetype=mimetype)
        result = self._service.files().update(
            fileId=file_id,
            media_body=media,
            fields='id, parents, name',
            ).execute()
        return result

    @log_http_error
    def move_file(
            self,
            file_id: str,
            new_folder_id: str,
            new_filename: Optional[str] = None,
            current_folder_id: Optional[str] = None
    ):
        """
        https://developers.google.com/drive/api/guides/folder?hl=ru#move_files_between_folders
        https://developers.google.com/drive/api/v3/reference/files/update
        """
        body = None
        if current_folder_id is None:
            files = self._service.files().get(fileId=file_id, fields='parents').execute()
            current_folder_id = ','.join(files.get('parents'))
        if new_filename is not None:
            body = {'name': new_filename}
        # Move the file to the new folder
        result = self._service.files().update(
            fileId=file_id,
            addParents=new_folder_id,
            removeParents=current_folder_id,
            body=body,
            fields='id, parents').execute()
        return result

    @log_http_error
    def delete_file(self, file_id: str):
        self._service.files().delete(fileId=file_id).execute()
