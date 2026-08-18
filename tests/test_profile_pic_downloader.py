from pathlib import Path

import pytest

from iglink.common.config import ConfigLoader
from iglink.common.follower_reader import FollowersReader
from iglink.common.header_extractor import HeaderExtractor
from iglink.common.http_client import HttpClient
from iglink.common.request_delayer import RequestDelayer
from iglink.downloader.profile_pic_downloader import ProfilePicDownloader


@pytest.fixture
def config():
    base_dir = Path(__file__).resolve().parents[1]
    return ConfigLoader().load_config(base_dir / "config.yaml")

@pytest.fixture
def downloader(config):
    header_extractor = HeaderExtractor(config.data_dir / config.headers_file_name)
    http_client = HttpClient(header_extractor.get_headers())
    request_delayer = RequestDelayer( 10, 5, 5)
    follower_reader = FollowersReader()

    return ProfilePicDownloader(
        http_client,
        request_delayer,
        follower_reader
    )

def test_download_profile_pics(downloader,config):
    downloader.download_profile_pics(
        config.data_dir / config.followers_file_name,
        config.data_dir / config.profile_pics_dir
    )