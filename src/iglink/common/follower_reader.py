from pathlib import Path
from typing import Any

import jsonlines


class FollowersReader:

    def read_follower_ids_from_file(self, follower_file: Path) -> list[Any]:
        follower_ids = []
        with jsonlines.open(follower_file) as reader:
            for obj in reader:
                for follower in obj:
                    follower_ids.append(follower['id'])
        return follower_ids
