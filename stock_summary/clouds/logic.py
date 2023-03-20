""" Main cloud logic which is then delegated to Cloud instances"""
import logging
import pathlib
from typing import Optional, Sequence

from stock_summary import settings
from stock_summary.clouds.azure import Azure
from stock_summary.help_structures import CloudType


def get_cloud(cloud_type: CloudType = settings.CLOUD_TYPE) -> Optional[Azure]:
    """Returns needed type of the cloud."""
    if cloud_type == CloudType.NONE:
        return None
    if settings.AZURE_CONNECTION_STR == "":
        err_msg = (
            "Using Azure cloud without connection string is impossible. "
            "Set connection string, or turn off the cloud."
        )
        logging.error(err_msg)

        raise ValueError(err_msg)
    cloud = Azure(settings.AZURE_CONNECTION_STR)
    return cloud


def sync_files_down(
    cloud_type: CloudType = settings.CLOUD_TYPE,
    paths: Optional[Sequence[pathlib.Path]] = None,
) -> None:
    """
    Sync files down from the cloud. You can specify type of the cloud and paths to local
    files that you want to sync. They are mapped in Cloud logic to their paths inside
    the cloud.
    """
    logging.info("Syncing files %s down from the cloud %s", paths, cloud_type.value)
    cloud = get_cloud(cloud_type=cloud_type)
    if cloud is None:
        logging.info("Cloud not set, nothing to sync. Continuing with local data.")
        return
    paths = (
        paths
        if paths is not None
        else [settings.ENTRIES_PATH, settings.DIVIDEND_PATH, settings.PORTFOLIO_PATH]
    )
    for path in paths:
        cloud.sync_file_down(path)


def sync_files_up(
    cloud_type: CloudType = settings.CLOUD_TYPE,
    paths: Optional[Sequence[pathlib.Path]] = None,
) -> None:
    """
    Sync files to the cloud. You can specify type of the cloud and paths to local
    files that you want to sync. They are mapped in Cloud logic to their paths inside
    the cloud.
    """
    logging.info("Syncing files %s up to the cloud %s", paths, cloud_type.value)
    cloud = get_cloud(cloud_type=cloud_type)
    if cloud is None:
        logging.info("Cloud not set, nothing to sync. Continuing with local data.")
        return
    paths = (
        paths
        if paths is not None
        else [settings.ENTRIES_PATH, settings.DIVIDEND_PATH, settings.PORTFOLIO_PATH]
    )

    for path in paths:
        cloud.sync_file_up(path)
