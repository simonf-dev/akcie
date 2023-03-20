from unittest.mock import patch

import pytest
from azure.core.exceptions import ServiceRequestError
from stock_summary import settings
from stock_summary.clouds.logic import get_cloud
from stock_summary.clouds import azure
from stock_summary.help_structures import CloudType

def test_invalid_azure_settings() -> None:
    """ Tests invalid azure settings and thrown exceptions."""
    settings.AZURE_CONNECTION_STR = None
    with pytest.raises(ValueError):
        get_cloud(cloud_type=CloudType.AZURE)
    settings.AZURE_CONNECTION_STR = "DefaultEndpointsProtocol=https;AccountName=invalid;AccountKey=invalid==;EndpointSuffix=core.windows.net"
    with patch.object(azure.Azure, "check_connection") as check_connection:
        check_connection.return_value = None
        with patch.object(azure.Azure, "get_share_client") as share_client:
            share_client.return_value.create_share.return_value = None
            cloud = get_cloud(cloud_type=CloudType.AZURE)
            assert isinstance(cloud, azure.Azure)
            settings.CLOUD_TYPE = CloudType.AZURE
            cloud = get_cloud()
            assert isinstance(cloud, azure.Azure)

    with pytest.raises(ServiceRequestError):
        cloud.check_connection()
