# What is Fritzbox-monitor?
Fritzbox-Monitor is a real-time service that checks Fritzbox system errors against a set of configured rules. The errors are published to a pre-configured platform (not included in this Docker image). For visualization, any open-source analytics and monitoring solution with [supported protocols](#supported-protocols) can be integrated.

![Architecture Overview](/docs/fritzbox-monitor.svg)

## Error Rules

Each rule is checked every cycle against the system logs and is published as an independent entity with the count of errors per minute. Extension of the rules is done by editing `.env` file. Please refer to the section [How to configure fritzbox-manager?](#how-to-configure-fritzbox-monitor) 

The list of default rules used for this documentation is as follow: 

- PPPoE error: Timeout
- Timeout during PPP negotiation

## Supported Protocols

- JSON for MQTT
- LINE for InfluxDB v2


## Supported Platforms

The supported integration platforms are **not** part of fritzbox-monitor docker image. 

> [!NOTE]  
> Please create a feature request if you want the supported platforms to be part of the fritzbox-monitor docker image.

- [Home Assistant](https://www.home-assistant.io/):
    
    Step 1: Enable sensors in Home Assistant's main `configuration.yaml`

    ```
    mqtt:
       sensor:
         - name: "fritzbox_monitor_error_Timeout_during_PPP_negotiation"
           unique_id: fritzbox_monitor_error_Timeout_during_PPP_negotiation
           state_topic: "tele/fritzbox/monitor/rule/Timeout_during_PPP_negotiation"
           value_template: "{{ value_json[0].fields.count }}"
           state_class: measurement
           icon: mdi:set-top-box
         - name: "fritzbox_monitor_error_PPPoE_error:_Timeout"
           unique_id: PPPoE_error:_Timeout
           state_topic: "tele/fritzbox/monitor/rule/PPPoE_error:_Timeout"
           value_template: "{{ value_json[0].fields.count }}"
           state_class: measurement
           icon: mdi:set-top-box
       binary_sensor:
        - name: "fritzbox_monitor_connection"
           unique_id: fritzbox_monitor_connection
           state_topic: "tele/fritzbox/monitor/connectivity"
           value_template: "{{ value_json[0].fields.state }}"
           device_class: connectivity
    ```

    Step 2: Enable the graph

    Go to **Dashboard** -> Click on **ADD CARD** -> Search for the **"Manual" card** -> Paste the code below into the **CODE EDITOR**. 
    
    The preview should look like the sample image below.
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

- [Grafana + InfluxDB](https://www.influxdata.com/blog/getting-started-influxdb-grafana/)
   
   Go to **Home** -> Click on **Dashboard** -> **New** -> **Import** -> Paste the contents of the exported [JSON file](/docs/Fritzbox-Monitor-1725566680804.json) into the **Import via dashboard JSON model** section.

   The preview should look like the sample image below.
  ![Integration Preview in Home Assistant](/docs/2024-09-05%2022_00_55-Fritzbox-Monitor_Grafana.png)


# How to Configure Fritzbox-monitor?

Before launching Fritzbox-Monitor, provide a `.env` file. All configurable parameters mentioned in the file below without OPTIONAL tag are mandatory.

```
LOG_LEVEL=INFO
TZ=Europe/Berlin

# JSON (MQTT), LINE (InfluxDB)
PROTOCOL=LINE

# Publish interval in seconds >=30
PUBLISH_INTERVAL=30

# Fritzbox Connection
FRITZ_IP=<your_fritzbox_ip>
FRITZ_USERNAME=<your_fritzbox_username>
FRITZ_PASSWORD=<your_fritzbox_password>
# Add rules to monitor
FRITZ_DETECTION_RULES=Timeout during PPP negotiation,PPPoE error: Timeout

# [OPTIONAL] MQTT Connection 
MQTT_BROKER_IP=<your_broker_ip>
MQTT_BROKER_PORT=1883
MQTT_USERNAME=<your_broker_username>
MQTT_PASSWORD=<your_broker_password>

# [OPTIONAL] InfluxDB v2 Connection
INFLUXDB_IP=<your_influxdb_ip>
INFLUXDB_PORT=<your_influxdb_port>
INFLUXDB_ORG=<your_influxdb_organization>
INFLUXDB_TOKEN=<your_influxdb_token>
INFLUXDB_BUCKET=<your_influxdb_bucket>
```

# How to launch?

```
mkdir logs
docker run --env-file .env navitohan/fritzbox-monitor:latest
```

# How to build locally?

```
docker compose up --build
```

# How to Debug?

Please refer to the [Dev guidelines](/docs/DEBUG.md).

# Where is fritzbox-monitor image published?

[DockerHub/navitohan/fritzbox-monitor](https://hub.docker.com/r/navitohan/fritzbox-monitor)

## Setting the correct timezone
The timezone in the .env file must match the Fritzbox timezone settings (FRITZ!OS(7.81): System -> Region and Language -> Time Zone).

Search for your timezone code in the format, e.g., Europe/Berlin, from the [detailed list on this page](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones).

## Limitation
Fritzbox-monitor starts publishing errors from the time the application is launched because data with old timestamps is not properly handled in time-series by the visualization tools in use, such as Home Assistant and Grafana.

At start-up, Fritzbox-monitor logs errors that occurred before its launch.

> [!IMPORTANT]  
> Errors that occurred in the Fritzbox before the Fritzbox-monitor service was started are not published to any supported protocols.

## Credit
Part of the Fritzbox-Monitor work is inspired by and based on this [Fritzbox-Monitor GitHub repository](https://github.com/paulknewton/fritzbox-monitor). 
