import json
import time
from infinite_craft import Result, craft
from rich import print
from atexit import register

new_items = 0
new_discoveries = 0
invalid_combinations = 0
requests_sent = 0

with open("computed.json", "r") as f:
    computed: dict[str, dict[str, list[str] | bool] | list[list[str]]] = json.loads(
        f.read()
    )
    computed.setdefault("items", {})
    computed.setdefault("invalid_combinations", [])
    items = computed["items"]


@register
def on_exit() -> None:
    write_to_file()
    display_info()


def get_item_combinations(item: str) -> list[str]:
    return items[item]["combinations"]


def add_item(combination_result: Result) -> None:
    global new_items, new_discoveries, invalid_combinations

    if combination_result == None:
        print("[red]Rate limited, waiting 1 hour")
        time.sleep(3620)

    combination = combination_result.combination

    if combination_result.is_nothing:
        invalid_combinations += 1
        print(f"[red][INVALID] '{combination[0]}' + '{combination[1]}'")
        computed["invalid_combinations"].append(combination)
        return

    name = combination_result.name
    is_new_discovery = combination_result.is_new_discovery

    items.setdefault(
        name,
        {"combinations": [], "is_new": is_new_discovery},
    )

    computed_combinations = get_item_combinations(name)

    if is_new_discovery:
        new_discoveries += 1
        print(f"[yellow][NEW DISCOVERY] '" + name + "'")
    else:
        new_items += 1
        print(f"[cyan][INFO] '{combination[0]}' + '{combination[1]}' = '{name}'")

    computed_combinations.append(combination)


def get_most_combined_item() -> str:
    most_combinations = 0
    most_combined_item = ""

    for item in items.keys():
        combination_count = len(get_item_combinations(item))

        if combination_count > most_combinations:
            most_combined_item = item
            most_combinations = combination_count

    return most_combined_item


def display_info() -> None:
    print(f"[green]{new_items} new items were computed")
    print(f"[green]{new_discoveries} new discoveries were found")
    print(f"[green]{invalid_combinations} invalid combinations were tried")
    new_stuff = new_items + new_discoveries
    print(f"[green]{100-invalid_combinations/(new_stuff+1)*100:.2f}% success rate")
    print(f"[green]'{get_most_combined_item()}' has the most combinations")


def write_to_file() -> None:
    with open("computed.json", "w") as f:
        f.write(json.dumps(computed))


def already_computed(first: str, second: str) -> bool:
    combination = sorted([first, second])

    for value in items.values():
        if combination in value["combinations"]:
            return True

    return False


if __name__ == "__main__":
    items_list = list(items.keys())
    for first in items_list:
        for second in items_list:
            if requests_sent >= 350:
                print("[red]Sleeping, gonna be rate limited")
                time.sleep(90)
                requests_sent = 0

            if already_computed(first, second):
                continue

            requests_sent += 1
            add_item(craft(first, second))
