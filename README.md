# What is Fritzbox-monitor?
Fritzbox-Monitor is a real-time service that checks Fritzbox system errors against a set of configured rules. The errors are published to a pre-configured MQTT broker (not included in this Docker image). For visualization, any open-source analytics and monitoring solution with MQTT support can be integrated.

![Architecture Overview](/docs/fritzbox-monitor.png)

## Integration support
- [Home Assistant](https://www.home-assistant.io/):
    Go to Dashboard -> Click on ADD CARD -> Search for the "Manual" card -> Paste the code below into the CODE EDITOR. The preview should look like the sample image below.
    ```
    title: FRITZ!Box Monitor
    type: history-graph
    hours_to_show: 168
    entities:
    - binary_sensor.fritzbox_monitor_connection
    - sensor.fritzbox_monitor_error_pppoe_error_timeout
    - sensor.fritzbox_monitor_error_timeout_during_ppp_negotiation

    ```
    ![Integration Preview in Home Assistant](/docs/integration_home_assistant.png)

## Error search rules

- PPPoE error: Timeout
- Timeout during PPP negotiation
- ...

# How to configure Fritzbox-monitor?

Before launching Fritzbox-Monitor, provide a .env file. All configurable parameters mentioned in the file below are mandatory.

```
LOG_LEVEL=INFO
TZ=Europe/Berlin

FRITZ_IP=<your_fritzbox_ip>
FRITZ_USERNAME=<your_fritzbox_username>
FRITZ_PASSWORD=<your_fritzbox_password>
# Add rules to monitor
FRITZ_DETECTION_RULES=Timeout during PPP negotiation,PPPoE error: Timeout

MQTT_BROKER_IP=<your_broker_ip>
MQTT_BROKER_PORT=1883
MQTT_USERNAME=<your_broker_username>
MQTT_PASSWORD=<your_broker_password>
# Publish interval in seconds >=30
MQTT_PUBLISH_INTERVAL=30
```

# How to launch?

```
docker run --env-file .env navitohan/fritzbox-monitor:latest
```

# How to build locally?

```
docker compose up --build
```
# Where is fritzbox-monitor image published?

https://hub.docker.com/r/navitohan/fritzbox-monitor

## Setting the correct timezone
The timezone in the .env file must match the Fritzbox timezone settings (FRITZ!OS(7.81): System -> Region and Language -> Time Zone).

Search for your timezone code in the format, e.g., Europe/Berlin, from the [detailed list on this page](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones).

## Credit
Part of the Fritzbox-Monitor work is inspired by and based on this [Fritzbox-Monitor GitHub repository](https://github.com/paulknewton/fritzbox-monitor). 
