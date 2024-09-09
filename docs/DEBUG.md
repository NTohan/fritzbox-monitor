## How to Debug Fritzbox-monitor?

## Logs

By default, Fritzbox-monitor writes stdout and stderr to a log file with the format `logs/<start_time>-fritzbox-monitor.log`. A new log file is created with each restart to capture the logs for each session.

```
tail -f logs/$(ls logs/ -Art | tail -n 1)
```

OR

```
docker logs --tail 1000 -f fritzbox-monitor 
```

## Connection to Fritzbox Failed
- Check if parameter `FRITZ_IP` in `.env` is set correctly.
- Fritzbox-monitor will restart after 20 failed connection attempts. The Docker image policy is set to `restart: unless-stopped`, meaning the Docker container will automatically restart to reconnect to Fritzbox.

## Data Not visible in Home Assistant
Please ensure the `configuration.yaml` of Home Assistant is correctly configured according to the sensor setup described in [Section, Home Assistant, Step1](../README.md#integrations). 

> [!TIP]  
> Restart Home Assistant after making changes to `configuration.yaml`.

## Data Not Visible in Grafana
Please check [logs](#logs) to see if connection to InfluxDB v2 is created successfully.

## How to Contribute?
Please create a new branch and submit a Merge Request to the `main` branch.

`fix/<>`
`feature/<>`
`refactor/<>`

> [!IMPORTANT]  
> Committing directly to the `main` branch is restricted and is not considered good practice.


## How to Request a New Feature or Report Issues?

Please choose a relevant template on the [GitHun repo](https://github.com/NTohan/fritzbox-monitor/issues/new/choose).

## How to Release a New Docker Image?

Admins of the GitHub repo will trigger the deployment process after the review process is complete.



