""" Azure cloud instance"""
import logging
import pathlib

from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from azure.storage.fileshare import ShareClient, ShareFileClient, ShareServiceClient

from stock_summary.settings import DIVIDEND_PATH, ENTRIES_PATH, PORTFOLIO_PATH

logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(
    logging.WARNING
)


class Azure:
    """
    API for the Azure cloud. It provides needed methods to sync data files
    """

    FILE_SHARE = "stocksummary"
    CLOUD_FILES_MAPPING = {
        ENTRIES_PATH: ENTRIES_PATH.name,
        DIVIDEND_PATH: DIVIDEND_PATH.name,
        PORTFOLIO_PATH: PORTFOLIO_PATH.name,
    }

    def __init__(self, connection_str: str):
        self.connection_str = connection_str
        self._service_client: ShareServiceClient = (
            ShareServiceClient.from_connection_string(connection_str)
        )
        self.check_connection()
        self._share_client = self.get_share_client()
        try:
            self._share_client.create_share()
            logging.info("Creating share: %s", self.FILE_SHARE)

        except ResourceExistsError:
            logging.info(
                "Share already exists, using the existing one %s", self.FILE_SHARE
            )

    def check_connection(self) -> None:
        """Checks connection and raises error if there is some problem."""
        try:
            self._service_client.get_service_properties(timeout=5)
        except Exception as err:
            logging.error(
                "Unable to connect to the Azure client with connection string.",
                exc_info=True,
            )
            raise err

    def get_share_client(self) -> ShareClient:
        """Returns SharClient which can be used further."""
        share_client = self._service_client.get_share_client(self.FILE_SHARE)
        return share_client

    def sync_file_up(self, local_path: pathlib.Path) -> None:
        """
        Syncs file up to the cloud. Only paths from CLOUD_FILES_MAPPING are supported.
        Cloud path is taken automatically from the mapping.
        """
        try:
            with open(local_path, "rb") as source_file:
                data = source_file.read()
                dest_path = self.CLOUD_FILES_MAPPING[local_path]
                file_client: ShareFileClient = ShareFileClient.from_connection_string(
                    self.connection_str, self.FILE_SHARE, dest_path
                )

                logging.info("Uploading to: %s/%s", self.FILE_SHARE, dest_path)
                file_client.upload_file(data)

        except ResourceExistsError as err:
            logging.error("ResourceExistsError:", exc_info=True)
            raise err

        except ResourceNotFoundError as err:
            logging.error("ResourceNotFoundError:", exc_info=True)
            raise err
        except KeyError as err:
            logging.error(
                "Trying to sync path which doesn't have mapping in the cloud.",
                exc_info=True,
            )
            raise err

    def sync_file_down(self, dst_file_name: pathlib.Path) -> None:
        """
        Syncs file down from the cloud. Only paths from CLOUD_FILES_MAPPING are supported.
        Cloud path is taken automatically from the mapping.
        """
        try:
            source_file_name = self.CLOUD_FILES_MAPPING[dst_file_name]

            # Create a ShareFileClient from a connection string
            file_client: ShareFileClient = ShareFileClient.from_connection_string(
                self.connection_str, self.FILE_SHARE, source_file_name
            )

            logging.info("Downloading to: %s", dst_file_name)

            # Open a file for writing bytes on the local system
            with open(dst_file_name, "wb") as data:
                # Download the file from Azure into a stream
                stream = file_client.download_file()
                # Write the stream to the local file
                data.write(stream.readall())

        except ResourceNotFoundError as err:
            logging.error("ResourceNotFoundError:", exc_info=True)
            raise err
        except KeyError as err:
            logging.error(
                "Trying to sync path which doesn't have mapping in the cloud.",
                exc_info=True,
            )
            raise err
