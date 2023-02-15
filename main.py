from os import getenv
from logging import warning, info, error

from ccm import (
    get_autostopping_rules,
    create_ec2_autostopping_rule,
    create_autostopping_schedule,
)
from ec2 import get_tagged_instances


if __name__ == "__main__":
    print("let's go")

    # target instance
    instance = "i-02ddfd484e2ee6016"

    # get existing ec2 rules
    instances = [x for x in get_autostopping_rules(10) if "instance" in x["routing"]]

    # find exsting rules for target instance
    matching = [
        x["id"]
        for x in instances
        if x["routing"]["instance"]["filter"]["ids"].pop() == instance
    ]

    if not matching:
        rule = create_ec2_autostopping_rule(
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
