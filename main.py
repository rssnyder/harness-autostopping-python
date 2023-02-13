from logging import error
from os import getenv

from requests import get, post, exceptions


HEADERS = {
    "accept": "*/*",
    "content-type": "application/json",
    "x-api-key": getenv("HARNESS_PLATFORM_API_KEY"),
}

PARAMS = {
    "routingId": getenv("HARNESS_ACCOUNT_ID"),
    "accountIdentifier": getenv("HARNESS_ACCOUNT_ID"),
}


def create_autostopping_rule(
    name: str,
    instance_id: str,
    instance_type: str,
    cloud_account_id: str,
    idle_time: int,
) -> dict:
    """
    Creates a simple autostopping rule
    """

    resp = post(
        f"https://app.harness.io/gateway/lw/api/accounts/{getenv('HARNESS_ACCOUNT_ID')}/autostopping/v2/rules",
        headers=HEADERS,
        params=PARAMS,
        json={
            "service": {
                "name": name,
                "account_identifier": getenv("HARNESS_PLATFORM_API_KEY"),
                "fulfilment": instance_type,
                "kind": "instance",
                "cloud_account_id": cloud_account_id,
                "idle_time_mins": idle_time,
                "routing": {
                    "ports": [],
                    "instance": {"filter": {"ids": [instance_id]}},
                },
                "metadata": {"cloud_provider_details": {"name": cloud_account_id}},
            }
        },
    )

    try:
        resp.raise_for_status()
    except Exception as e:
        try:
            data = resp.json()
        except exceptions.JSONDecodeError as f:
            raise e
        else:
            error(data.get("errors", data))
            return {}

    return resp.json()


def create_autostopping_schedule(
    cloud_account_id: str,
    rule_id: str,
    days: list,
    start_hour: int,
    end_hour: int,
    timezone: str = "America/Chicago",
) -> dict:
    """
    Creates a simple autostopping schedule for an existing rule
    """

    resp = post(
        f"https://app.harness.io/gateway/lw/api/accounts/{getenv('HARNESS_ACCOUNT_ID')}/schedules",
        headers=HEADERS,
        params=PARAMS.update({"cloud_account_id": cloud_account_id}),
        json={
            "schedule": {
                "name": f"{rule_id}-schedule",
                "account_id": getenv("HARNESS_ACCOUNT_ID"),
                "description": "",
                "resources": [{"ID": str(rule_id), "Type": "autostop_rule"}],
                "details": {
                    "timezone": timezone,
                    "uptime": {
                        "days": {
                            "days": days,
                            "all_day": False,
                            "start_time": {"hour": start_hour, "min": 0},
                            "end_time": {"hour": end_hour, "min": 0},
                        }
                    },
                },
            }
        },
    )

    try:
        resp.raise_for_status()
    except Exception as e:
        try:
            data = resp.json()
        except exceptions.JSONDecodeError as f:
            raise e
        else:
            error(data.get("errors", data))
            return ""

    return resp.json()


def get_autostopping_rules() -> dict:
    """
    Get existing rules
    """

    resp = post(
        f"https://app.harness.io/gateway/lw/api/accounts/{getenv('HARNESS_ACCOUNT_ID')}/autostopping/rules/list",
        headers=HEADERS,
        params=PARAMS,
        json={"page": 1, "limit": 5},
    )

    try:
        resp.raise_for_status()
    except Exception as e:
        try:
            data = resp.json()
        except exceptions.JSONDecodeError as f:
            raise e
        else:
            error(data.get("errors", data))
            return {}

    final_data = resp.json()

    for page in range(2, final_data.get("response", {}).get("pages") + 1):
        resp = post(
            f"https://app.harness.io/gateway/lw/api/accounts/{getenv('HARNESS_ACCOUNT_ID')}/autostopping/rules/list",
            headers=HEADERS,
            params=PARAMS,
            json={"page": page, "limit": 5},
        )

        try:
            resp.raise_for_status()
        except Exception as e:
            try:
                data = resp.json()
            except exceptions.JSONDecodeError as f:
                raise e
            else:
                error(data.get("errors", data))
                return {}

        data = resp.json()

        final_data["response"]["records"] += data["response"]["records"]

    return final_data


if __name__ == "__main__":
    print("let's go")

    # target instance
    instance = "i-02388d6e6d0f204f9"

    # get existing ec2 rules
    instances = [
        x
        for x in get_autostopping_rules()["response"]["records"]
        if "instance" in x["routing"]
    ]

    # find exsting rules for target instance
    matching = [
        x["id"]
        for x in instances
        if x["routing"]["instance"]["filter"]["ids"].pop() == instance
    ]

    if not matching:
        rule = create_autostopping_rule(
            "pythontest", instance, "ondemand", "rileyharnessccm", 12
        )

        if rule == {}:
            exit()

        rule_id = rule.get("response", {}).get("id", "")

        sched = create_autostopping_schedule(
            "rileyharnessccm", rule_id, [1, 2, 3, 4, 5], 8, 17, "America/Chicago"
        )

        schedule_id = sched.get("response", {}).get("id")

        print(
            f"{rule_id} -> {schedule_id} -> https://app.harness.io/ng/#/account/{getenv('HARNESS_ACCOUNT_ID')}/ce/autostopping-rules/rule/{rule_id}"
        )
