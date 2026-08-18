import random
import time

from tqdm import tqdm


class RequestDelayer:

    def __init__(self,
                 request_delay_seconds: int,
                 request_delay_min_deviation: int,
                 request_delay_max_deviation: int
                 ):
        self.request_delay_seconds = request_delay_seconds
        self.request_delay_min_deviation = request_delay_min_deviation
        self.request_delay_max_deviation = request_delay_max_deviation

    def delay_request(self):
        delay = int(self.request_delay_seconds + random.uniform(-self.request_delay_min_deviation,
                                                                self.request_delay_max_deviation))
        for _ in tqdm(range(delay), desc="Until next pull"):
            time.sleep(1)
