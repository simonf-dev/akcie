import logging
import pathlib
from typing import Optional, Mapping

from stock_summary.settings import CloudType, CLOUD_TYPE, AZURE_CONNECTION_STR, ENTRIES_PATH, PORTFOLIO_PATH, DIVIDEND_PATH
from stock_summary.clouds.azure import  Azure


def get_cloud(cloud_type: CloudType = CLOUD_TYPE) -> Optional[Azure]:
    if cloud_type == CloudType.NONE:
        return None
    if AZURE_CONNECTION_STR == "":
        err_msg = "Using Azure cloud without connection string is impossible. " \
                  "Set connection string, or turn off the cloud."
        logging.error(err_msg)

        raise ValueError(err_msg)
    cloud = Azure(AZURE_CONNECTION_STR)
    return cloud

def sync_files_down(cloud_type: CloudType = CLOUD_TYPE,paths: Optional[Mapping[pathlib.Path, str]] = None) -> None:
    cloud = get_cloud(cloud_type=cloud_type)
    if cloud is None:
        logging.info("Cloud not set, nothing to sync. Continuing with local data.")
        return
    paths = paths if paths is not None else {
            ENTRIES_PATH: ENTRIES_PATH.name, PORTFOLIO_PATH: PORTFOLIO_PATH.name, DIVIDEND_PATH: DIVIDEND_PATH.name
        }
    for path, cloud_path in paths.items():
        cloud.sync_file_up(cloud_path, path)

def sync_files_up(cloud_type: CloudType = CLOUD_TYPE, paths: Optional[Mapping[pathlib.Path, str]] = None) -> None:
    cloud = get_cloud(cloud_type=cloud_type)
    paths = paths if paths is not None else {
    ENTRIES_PATH: ENTRIES_PATH.name, PORTFOLIO_PATH: PORTFOLIO_PATH.name, DIVIDEND_PATH: DIVIDEND_PATH.name
}
    if cloud is None:
        logging.info("Cloud not set, nothing to sync. Continuing with local data.")
        return
    for path, cloud_path in paths.items():
        cloud.sync_file_up(path, cloud_path)
