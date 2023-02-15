# harness-autostopping-python

create a basic (no http or tcp workloads) autostopping rule

```python
rule = create_ec2_autostopping_rule("myec2srule", "i-02ddfd484e2ee6016", "ondemand", "rileyharnessccm")
create_autostopping_schedule("rileyharnessccm", rule["response"]["id"], [1,2,3,4,5], 8, 17)
```

```python
rule = create_k8s_autostopping_rule("myk8srule", "web-app", "web", "rileyharnessccm", "codeserverCostaccess")
create_autostopping_schedule("rileyharnessccm", rule["response"]["id"], [1,2,3,4,5], 8, 17)
```

functions for both ec2 and kubernetes workloads

attach an uptime schedule for created rule

## Configuration

### Environment

- HARNESS_PLATFORM_API_KEY
- HARNESS_ACCOUNT_ID
