from dataclasses import dataclass
import json
import cloudscraper

scraper = cloudscraper.CloudScraper()


@dataclass
class Result:
    name: str
    emoji: str
    is_new_discovery: bool

    @staticmethod
    def from_json(json_: dict[str, str]) -> "Result":
        return Result(json_["result"], json_["emoji"], json_["isNew"])


def craft(first: str, second: str) -> Result:
    params = {"first": first, "second": second}

    headers = {
        "Accept": "*/*",
        "Referer": "https://neal.fun/infinite-craft/",
        "Sec-Fetch-Dest": "empty",
    }

    response = scraper.get(
        "https://neal.fun/api/infinite-craft/pair", params=params, headers=headers
    )

    return Result.from_json(json.loads(response.text))
