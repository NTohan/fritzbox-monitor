# fritzbox-monitor


This is a fork of https://github.com/paulknewton/fritzbox-monitor


## Error search rules

- Timeout during PPP negotiation
- ...


## TODO
- Add credit for fork
- Add architecture overview diagram
- Add rules to config yaml file 
- Add search rule in a config file
- Add docker compose with .env file
- Remove CLI options and add a main loop
- Add poll time to the config
- Add MQTT publish support
- Add MQTT reconnect support
- Remove CLI options


## How to launch?

```
docker run -it -v .:/shared --env-file .env fritzbox-monitor
```

## Setting the correct timezone
Attention! Timezone from .env shall match to Fritzbox timezone settings (FRITZ!OS(7.81): System -> Region and Language -> Time Zone). 
https://en.wikipedia.org/wiki/List_of_tz_database_time_zones