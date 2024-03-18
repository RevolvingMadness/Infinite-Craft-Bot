from dataclasses import dataclass
import json
import cloudscraper
from user_agent import generate_user_agent
from rich import print

scraper = cloudscraper.create_scraper()
headers = {
    "Accept": "*/*",
    "Referer": "https://neal.fun/infinite-craft/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": generate_user_agent(),
}


@dataclass
class Result:
    name: str
    emoji: str
    is_new_discovery: bool
    is_nothing: bool
    combination: list[str]

    @staticmethod
    def from_json(json_: dict[str, str], combination: list[str]) -> "Result":
        return Result(
            json_["result"],
            json_["emoji"],
            json_["isNew"],
            False,
            sorted(combination),
        )

    @staticmethod
    def nothing(combination: list[str]) -> "Result":
        return Result("Nothing", "", False, True, sorted(combination))


def craft(first: str, second: str) -> Result:
    params = {"first": first, "second": second}

    response = scraper.get(
        "https://neal.fun/api/infinite-craft/pair",
        params=params,
        headers=headers,
    )

    if response.status_code == 429:
        print("[red][ERROR] You are sending too many requests to the neal.fun servers.")
        return None

    if response.status_code == 403:
        print(
            "[red][ERROR] Got error code 403. This could be because you are using a VPN."
        )
        return None

    if response.status_code != 200:
        print(f"[red][ERROR] Got error code {response.status_code}.")

        with open("error.txt", "w") as f:
            f.write(response.text)

        return None

    combination = [first, second]
    response_dict = json.loads(response.text)

    if response_dict["result"] == "Nothing":
        return Result.nothing(combination)

    return Result.from_json(response_dict, combination)
