from pathlib import Path
from unittest.mock import MagicMock

import pytest
from requests import Response

from iglink.common.config import ConfigLoader
from iglink.common.follower_reader import FollowersReader
from iglink.common.header_extractor import HeaderExtractor
from iglink.common.http_client import HttpClient
from iglink.common.request_delayer import RequestDelayer
from iglink.downloader.pagination_downloader import PaginationDownloader
from iglink.downloader.mutual_downloader import MutualDownloader


@pytest.fixture()
def config():
    base_dir = Path(__file__).resolve().parents[1]
    return ConfigLoader().load_config(base_dir / "config.yaml")

@pytest.fixture
def http_client():
    return MagicMock(spec=HttpClient)

def make_response(status_code, json_body):
    response = MagicMock(spec=Response)
    response.status_code = status_code
    response.json.return_value = json_body
    return response

@pytest.fixture
def downloader(config, http_client):
    request_delayer = RequestDelayer(10, 5, 5)
    friends_reader = FollowersReader()
    pagination_downloader = PaginationDownloader(request_delayer)

    return MutualDownloader(
        http_client,
        request_delayer,
        friends_reader,
        100,
        pagination_downloader
    )


def test_download_mutuals_2_pagination_till_end(downloader, config, http_client):
    http_client.get_request.side_effect = [
        make_response(200, {"page": 1, "items": [...]}),
    ]

    downloader.download_mutuals(
        config.data_dir / config.followers_file_name,
        config.data_dir / config.mutuals_file_name
    )

