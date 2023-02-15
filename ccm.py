from logging import error
from os import getenv
from json import dumps, loads

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


def create_ec2_autostopping_rule(
    name: str,
    instance_id: str,
    instance_type: str,
    cloud_account_id: str,
    idle_time: int = 5,
) -> dict:
    """
    Creates a simple autostopping rule

    name: name of the rule
    instance_id: ec2 instance id
    instance_type: ondemand or spot
    cloud_account_id: harness cloud connector id
    idle_time: min before shutdown after schedule expires
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


def create_k8s_autostopping_rule(
    name: str,
    workload: str,
    namespace: str,
    cloud_account_id: str,
    k8s_connector_id: str,
    idle_time: int = 5,
) -> dict:
    """
    Creates a simple autostopping rule

    name: name of the rule
    workload: name of the deployment in kubernetes
    namespace: namespace the workload is located in
    cloud_account_id: harness cloud connector id
    k8s_connector_id: harness k8s connector id
    idle_time: min before shutdown after schedule expires
    """

    resp = post(
        f"https://app.harness.io/gateway/lw/api/accounts/{getenv('HARNESS_ACCOUNT_ID')}/autostopping/v2/rules",
        headers=HEADERS,
        params=PARAMS,
        json={
            "service": {
                "name": name,
                "account_identifier": getenv("HARNESS_ACCOUNT_ID"),
                "fulfilment": "kubernetes",
                "kind": "k8s",
                "cloud_account_id": cloud_account_id,
                "idle_time_mins": idle_time,
                "routing": {
                    "ports": [],
                    "k8s": {
                        "RuleJson": dumps(
                            {
                                "apiVersion": "ccm.harness.io/v1",
                                "kind": "AutoStoppingRule",
                                "metadata": {
                                    "name": name,
                                    "namespace": namespace,
                                    "annotations": {
                                        "harness.io/cloud-connector-id": cloud_account_id
                                    },
                                },
                                "spec": {
                                    "idleTimeMins": 5,
                                    "workloadName": workload,
                                    "workloadType": "Deployment",
                                    "hideProgressPage": False,
                                    "dependencies": [],
                                },
                            }
                        ),
                        "ConnectorID": k8s_connector_id,
                        "Namespace": namespace,
                    },
                },
                "metadata": {
                    "cloud_provider_details": {"name": cloud_account_id},
                    "kubernetes_connector_id": k8s_connector_id,
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

    cloud_account_id: harness cloud connector id
    rule_id: id of the rule to apply the schedule to
    days: days of the week to apply the schedule, 0 = sunday 6 = satuday
    start_hour: hour of the day to start the schedule, 24hr time
    end_hour: hour of the day to stop the schedule, 24hr time
    timezone: timezone to base the rule in
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


def get_autostopping_rules(limit: int = 5) -> dict:
    """
    Get existing rules

    limit: page size
    """

    resp = post(
        f"https://app.harness.io/gateway/lw/api/accounts/{getenv('HARNESS_ACCOUNT_ID')}/autostopping/rules/list",
        headers=HEADERS,
        params=PARAMS,
        json={"page": 1, "limit": limit},
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
            json={"page": page, "limit": limit},
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

    return final_data["response"]["records"]


def existing_k8s_rule(
    workload: str, namespace: str, cloud_account_id: str, k8s_connector_id: str
):
    """
    See if a rule exists for a given workload in a cluster
    """

    for rule in [
        x for x in get_autostopping_rules(10) if x["fulfilment"] == "kubernetes"
    ]:
        rule_data = loads(rule["routing"]["k8s"]["RuleJson"])
        if (
            (rule_data["metadata"]["namespace"] == namespace)
            and (rule_data["spec"]["workloadName"] == workload)
            and (
                rule_data["metadata"]["annotations"]["harness.io/cloud-connector-id"]
                == cloud_account_id
            )
            and (rule["metadata"]["kubernetes_connector_id"] == k8s_connector_id)
        ):
            return rule["id"]

    return 0


if __name__ == "__main__":
    if not existing_k8s_rule(
        "baby-app", "baby", "rileyharnessccm", "codeserverCostaccess"
    ):
        print("Create")
        # rule = create_k8s_autostopping_rule("python", "baby-app", "baby", "rileyharnessccm", "codeserverCostaccess")
        # print(create_autostopping_schedule("rileyharnessccm", rule["response"]["id"], [1,2,3,4,5], 8, 17))
