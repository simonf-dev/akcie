import logging
import pathlib
from typing import Optional, Sequence

from stock_summary.clouds.azure import Azure
from stock_summary.settings import (
    AZURE_CONNECTION_STR,
    CLOUD_TYPE,
    DIVIDEND_PATH,
    ENTRIES_PATH,
    PORTFOLIO_PATH,
    CloudType,
)


def get_cloud(cloud_type: CloudType = CLOUD_TYPE) -> Optional[Azure]:
    """Returns needed type of the cloud."""
    if cloud_type == CloudType.NONE:
        return None
    if AZURE_CONNECTION_STR == "":
        err_msg = (
            "Using Azure cloud without connection string is impossible. "
            "Set connection string, or turn off the cloud."
        )
        logging.error(err_msg)

        raise ValueError(err_msg)
    cloud = Azure(AZURE_CONNECTION_STR)
    return cloud


def sync_files_down(
    cloud_type: CloudType = CLOUD_TYPE, paths: Optional[Sequence[pathlib.Path]] = None
) -> None:
    logging.info("Syncing paths %s up to the cloud %s", paths, cloud_type.value)
    cloud = get_cloud(cloud_type=cloud_type)
    if cloud is None:
        logging.info("Cloud not set, nothing to sync. Continuing with local data.")
        return
    paths = (
        paths if paths is not None else [ENTRIES_PATH, DIVIDEND_PATH, PORTFOLIO_PATH]
    )
    for path in paths:
        cloud.sync_file_down(path)


def sync_files_up(
    cloud_type: CloudType = CLOUD_TYPE, paths: Optional[Sequence[pathlib.Path]] = None
) -> None:
    logging.info("Syncing paths %s down from the cloud %s", paths, cloud_type.value)
    cloud = get_cloud(cloud_type=cloud_type)
    if cloud is None:
        logging.info("Cloud not set, nothing to sync. Continuing with local data.")
        return
    paths = (
        paths if paths is not None else [ENTRIES_PATH, DIVIDEND_PATH, PORTFOLIO_PATH]
    )

    for path in paths:
        cloud.sync_file_up(path)
