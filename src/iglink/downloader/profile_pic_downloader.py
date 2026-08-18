import os
from pathlib import Path
from typing import Any

import jsonlines

from iglink.common.follower_reader import FollowersReader
from iglink.common.http_client import HttpClient
from iglink.common.request_delayer import RequestDelayer


class ProfilePicDownloader:

    def __init__(self,
                 http_client: HttpClient,
                 request_delayer: RequestDelayer,
                 followers_reader: FollowersReader
                 ):
        self.http_client = http_client
        self.request_delayer = request_delayer
        self.followers_reader = followers_reader

    def download_profile_pics(self, followers_file: Path, profile_pic_dir: Path):
        os.makedirs(profile_pic_dir, exist_ok=True)

        followers_ids_all = self.followers_reader.read_follower_ids_from_file(followers_file)
        followers_ids_already_downloaded = [Path(file).stem for file in os.listdir(profile_pic_dir)]
        followers_ids_to_download = list(set(followers_ids_all) - set(followers_ids_already_downloaded))

        followers_to_download = self._create_followers_to_download(followers_file, followers_ids_to_download)
        self._download_profile_pic_list(followers_to_download, len(followers_ids_already_downloaded), profile_pic_dir)


    def _create_followers_to_download(self, followers_file: Path, followers_ids_to_download: list[Any]) -> list[Any]:
        followers_to_download = []
        with jsonlines.open(followers_file) as reader:
            for obj in reader:
                for follower in obj:
                    if follower['id'] in followers_ids_to_download:
                        followers_to_download.append({'username': follower['username'], 'id': follower['id'],
                                                    'profile_pic_url': follower['profile_pic_url']})
        return followers_to_download

    def _download_profile_pic_list(self, users:list, start_offset:int, profile_pic_dir: Path):
        for i, user in enumerate(users):
            self._download_profile_pic(user['id'], user['profile_pic_url'], profile_pic_dir)

            print(f'Downloaded pic (#{i+start_offset+1}/{start_offset+len(users)}): {user["username"]} under {user["id"]}.jpg')
            self.request_delayer.delay_request()

    def _download_profile_pic(self, id:int, url:str, profile_pic_dir:Path):
        response = self.http_client.get_request(url, headers_enabled=False)

        with open(f'{profile_pic_dir}/{id}.jpg', 'wb') as fd:
            fd.write(response.content)
