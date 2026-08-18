from pathlib import Path

import pytest

from iglink.common.config import ConfigLoader
from iglink.common.header_extractor import HeaderExtractor
from iglink.common.http_client import HttpClient
from iglink.common.request_delayer import RequestDelayer
from iglink.downloader.pagination_downloader import PaginationDownloader
from iglink.downloader.follower_downloader import FollowerDownloader


@pytest.fixture
def downloader():
    base_dir = Path(__file__).resolve().parents[1]

    config = ConfigLoader().load_config(base_dir/"config.yaml")

    header_extractor = HeaderExtractor(base_dir/config.headers_file)
    http_client = HttpClient(header_extractor.get_headers())
    request_delayer = RequestDelayer( 10, 5, 5)

    pagination_downloader = PaginationDownloader(request_delayer)

    return FollowerDownloader(
        http_client ,
        request_delayer,
        header_extractor.get_ig_id(),
        config.follower_pull_max_amount,
        pagination_downloader
    )

def test_download_followers(downloader):
    downloader.download_followers('test_friends.jsonl')