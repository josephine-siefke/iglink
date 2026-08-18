import jsonlines

from iglink.common.http_client import HttpClient
from iglink.common.request_delayer import RequestDelayer
from iglink.downloader.pagination_downloader import PaginationDownloader


class FollowerDownloader:

    followers_path: str

    def __init__(self,
                 http_client: HttpClient,
                 request_delayer: RequestDelayer,
                 ig_id: str,
                 max_count: int,
                 pagination_downloader: PaginationDownloader
                 ):
        self.http_client = http_client
        self.request_delayer = request_delayer
        self.ig_id = ig_id
        self.max_count = max_count

        self.pagination_downloader = pagination_downloader
        self.pagination_downloader.set_request_call(self._request_followers)

    def download_followers(self, followers_path: str, next_max_id=None):
        self.followers_path = followers_path
        self.pagination_downloader.call(self._save_followers, next_max_id)

    def _save_followers(self, index:int, has_more:bool, users:list[dict], users_amount_sum:int):
        print(f"Pull #{index + 1}: follower amount sum: {users_amount_sum}, has_more: {has_more}")

        with jsonlines.open(self.followers_path, mode='a') as writer:
            writer.write(users)

    # def download_followers(self, followers_path: str, next_max_id=None):
    #     has_more = True
    #
    #     index = 0
    #     user_amount = 0
    #     while (has_more):
    #         request_follower_response = self._request_followers(next_max_id)
    #
    #         users = request_follower_response['users']
    #         has_more = request_follower_response['has_more']
    #
    #         user_amount += len(users)
    #         print(f"Pull #{index + 1}: follower amount sum: {user_amount}, has_more: {has_more}")
    #
    #         with jsonlines.open(followers_path, mode='a') as writer:
    #             writer.write(users)
    #
    #         if has_more is False:
    #             break
    #         else:
    #             next_max_id = request_follower_response['next_max_id']
    #             print(f"next_max_id: {next_max_id}")
    #             index += 1
    #
    #             self.request_delayer.delay_request()
    #
    def _request_followers(self, max_id:int|None=None) -> dict:
        if max_id is None:
            url = f"https://www.instagram.com/api/v1/friendships/{self.ig_id}/followers/?count={self.max_count}&search_surface=follow_list_page"
        else:
            url = f"https://www.instagram.com/api/v1/friendships/{self.ig_id}/followers/?count={self.max_count}&max_id={max_id}&search_surface=follow_list_page"

        return self.http_client.get_request(url=url).json()