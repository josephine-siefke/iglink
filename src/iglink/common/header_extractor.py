import re
from pathlib import Path


class HeaderExtractor:

    headers = []
    ig_id = None

    def __init__(self, header_path: Path):
        self.header_path = header_path
        self._extract()

    def _extract(self):
        with open(self.header_path) as f:
            header_lines = f.readlines()

        self.headers = self._extract_headers(header_lines)
        self.ig_id = re.search(r'friendships/(\d+)/followers', header_lines[0]).group(1)

    def _extract_headers(self, header_lines: list[str]) -> dict[str, str]:
        headers = {}
        for header_line in header_lines[1:]:
            attribute = header_line.split(':')[0]
            # Don't include Accept-Encoding because this with encode it into gibberish
            if attribute != "Accept-Encoding":
                headers[attribute] = str(header_line.split(':', maxsplit=1)[1]).strip()
        return headers

    def get_headers(self):
        return self.headers

    def get_ig_id(self):
        return self.ig_id