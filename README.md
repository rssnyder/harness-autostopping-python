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

curl 'https://app.harness.io/gateway/lw/api/accounts/wlgELJ0TTre5aZhzpt8gVA/autostopping/v2/rules/13161?routingId=wlgELJ0TTre5aZhzpt8gVA&accountIdentifier=wlgELJ0TTre5aZhzpt8gVA' \
  -X 'PUT' \
  -H 'authority: app.harness.io' \
  -H 'accept: */*' \
  -H 'accept-language: en-US,en;q=0.9' \
  -H 'authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhdXRoVG9rZW4iOiI2NDA2MzdhYTVkNGFjNDI4MjcyNDUyOTYiLCJpc3MiOiJIYXJuZXNzIEluYyIsImV4cCI6MTY3ODQ2MjkxMywiZW52IjoiZ2F0ZXdheSIsImlhdCI6MTY3ODM3NjQ1M30.96j7LZAmenzeq5BPKsPLB7KbpRAuXA820p-absQWRGc' \
  -H 'content-type: application/json' \
  --data-raw '{
  "service": {
    "name": "coqznkpuoszdylpaapwf-rule",
    "account_identifier": "wlgELJ0TTre5aZhzpt8gVA",
    "fulfilment": "kubernetes",
    "kind": "k8s",
    "cloud_account_id": "rileyharnessccm",
    "idle_time_mins": 5,
    "custom_domains": [],
    "health_check": null,
    "routing": {
      "k8s": {
        "RuleJson": "{\"kind\":\"AutoStoppingRule\",\"apiVersion\":\"ccm.harness.io/v1\",\"metadata\":{\"name\":\"coqznkpuoszdylpaapwf-rule\",\"namespace\":\"coqznkpuoszdylpaapwf\",\"annotations\":{\"harness.io/cloud-connector-id\":\"rileyharnessccm\"}},\"spec\":{\"idleTimeMins\":5,\"hideProgressPage\":false,\"workloadName\":\"coqznkpuoszdylpaapwf-app\",\"workloadType\":\"Deployment\",\"notifications\":{},\"dependencies\":[{\"selector\":{\"ruleName\":\"code-server\"},\"wait\":5}]}}",
        "ConnectorID": "codeserverCostaccess",
        "Namespace": "coqznkpuoszdylpaapwf"
      }
    },
    "opts": {
      "preservePrivateIP": false,
      "deleteCloudResources": false,
      "alwaysUsePrivateIP": false,
      "hide_progress_page": false,
      "dry_run": false,
      "preserve_private_ip": false,
      "always_use_private_ip": false
    },
    "metadata": {
      "target_group_details": null,
      "access_details": null,
      "cloud_provider_details": null,
      "service_errors": null,
      "kubernetes_connector_id": "codeserverCostaccess",
      "health_check_details": null,
      "custom_domain_providers": null,
      "port_config": null,
      "dns_mapping_to_retain": null,
      "autostopping_proxy_config": null,
      "host_names": null
    },
    "access_point_id": null,
    "id": 13161
  },
  "deps": [
    { "delay_secs": 5, "dep_id": 12338 }
  ],
  "apply_now": false
}' \
  --compressed