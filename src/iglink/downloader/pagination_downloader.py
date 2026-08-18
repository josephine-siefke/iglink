from typing import Callable

from iglink.common.request_delayer import RequestDelayer


class PaginationDownloader:

    request_call = None

    def __init__(self, request_delayer:RequestDelayer):
        self.request_delayer = request_delayer

    def set_request_call(self, request_call:Callable[[int|None], dict]):
        self.request_call = request_call

    def call(self, after_call:Callable[[int, bool, list[dict], int], None], next_max_id=None):
        has_more = True

        index = 0
        users_amount_sum = 0
        while (has_more):
            request_follower_response = self.request_call(next_max_id)

            users = request_follower_response['users']
            has_more = self._has_more(request_follower_response)
            users_amount_sum += len(users)

            after_call(index, has_more, users, users_amount_sum)

            if has_more is False:
                break
            else:
                next_max_id = request_follower_response['next_max_id']
                print(f"next_max_id: {next_max_id}")
                index += 1

                self.request_delayer.delay_request()

    def _has_more(self, response:dict):
        if 'has_more' in response and response['has_more']:
            return True
        if 'next_max_id' in response and response['next_max_id'] is not None:
            return True
        return False
