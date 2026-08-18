from pathlib import Path

import jsonlines

from iglink.common.follower_reader import FollowersReader
from iglink.common.http_client import HttpClient
from iglink.common.request_delayer import RequestDelayer
from iglink.downloader.pagination_downloader import PaginationDownloader


class MutualDownloader:

    def __init__(self,
                 http_client: HttpClient,
                 request_delayer: RequestDelayer,
                 followers_reader: FollowersReader,
                 mutuals_pull_max_amount:int,
                 pagination_downloader: PaginationDownloader
                 ):
        self.http_client = http_client
        self.request_delayer = request_delayer
        self.followers_reader = followers_reader
        self.mutuals_pull_max_amount = mutuals_pull_max_amount
        self.pagination_downloader = pagination_downloader

    def download_mutuals(self, followers_file: Path, mutuals_file: Path):
        mutuals_file.touch(exist_ok=True)

        follower_ids_all = self.followers_reader.read_follower_ids_from_file(followers_file)
        followers_mutuals_already_downloaded = self._read_mutals_already_downloaded(mutuals_file)
        followers_mutuals_to_download = list(set(follower_ids_all) - set(followers_mutuals_already_downloaded))

        followers_mutuals_to_download = self.get_mutuals_to_download(followers_mutuals_to_download, followers_file)
        for indx, mutual in enumerate(followers_mutuals_to_download):
            follower_id = mutual['id']
            follower_username = mutual['username']

            self.pagination_downloader.set_request_call(self._request_mutuals(follower_id, follower_username))
            self.pagination_downloader.call(
                self._after_call(
                    follower_id,
                    follower_username,
                    indx,
                    len(followers_mutuals_already_downloaded),
                    len(followers_mutuals_to_download),
                    mutuals_file)
            )
            if indx < len(followers_mutuals_to_download) - 1:
                self.request_delayer.delay_request()

    def _read_mutals_already_downloaded(self, mutuals_file: Path):
        mutals_ids = []
        with jsonlines.open(mutuals_file) as reader:
            for mutual_item in reader:
                mutals_ids.append(mutual_item['follower_id'])
        return mutals_ids

    def get_mutuals_to_download(self, followers_mutuals_to_download, followers_file: Path):
        followers_to_download = []
        with jsonlines.open(followers_file) as reader:
            for obj in reader:
                for follower in obj:
                    if follower['id'] in followers_mutuals_to_download:
                        followers_to_download.append({'username': follower['username'], 'id': follower['id']})
        return followers_to_download


    mutuals = []
    def _after_call(
            self,
            id: str,
            username: str,
            index: int,
            index_offset: int,
            remaining_amount: int,
            mutuals_file: Path
    ):
        def _call(index_from_partial:int, has_more:bool, users:list[dict], users_amount_sum:int):
            print(f"Partial download mutual #{index_from_partial+1}. Current amount: {users_amount_sum} for {username}")
            self.mutuals += users

            if not has_more:
                with jsonlines.open(mutuals_file, 'a') as writer:
                    writer.write({'follower_id': id, 'username': username, 'mutuals': self.mutuals})
                self.mutuals = []

                print(f"#{index_offset + index + 1}/" f"{index_offset + remaining_amount}: " f"{username}: " f"{len(users)}")

        return _call

    def _request_mutuals(self, follower_id: str, follower_username: str):
        def _call(max_id:int|None=None):
            extra_headers = {
                'Referer': f'https://www.instagram.com/{follower_username}/followers/mutualOnly'
            }
            if max_id == None:
                url = f"https://www.instagram.com/api/v1/friendships/{follower_id}/mutual_followers/?page_size={self.mutuals_pull_max_amount}"
            else:
                url = f"https://www.instagram.com/api/v1/friendships/{follower_id}/mutual_followers/?page_size={self.mutuals_pull_max_amount}&max_id={max_id}"
            return self.http_client.get_request(url, extra_headers).json()

        return _call


