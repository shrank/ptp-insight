# ptp-insight
Collect metrics from ptp4l, store in InfluxDB and show in web interface 

**the metrics collection service is starting a ptp4l process by itself and is not suitable for collecting metrics from an existing ptp4l process** 

## description
The metrics collection service uses the ptp4l stdout logs, the pmc client and packet capturing to collect metrics and data about ptp. This allows for a range of interesting applications from testing networks for PTP readiness to troubleshooting. It could even be used to measure and monitor L2 links with nanosecond precision or evaluate and compair the delay, jitter of switching hardware and the impact specific switching features have on traffic forwarding.

Further, he Raspberry PI 5 provides an inexpensive platform to use as sensors or even handheld testing devices. 

Setup Examples:
![Example Setups](/blob/main/doc/Setup Examples.png?raw=true)

Screenshot:
![WebUI Screenshot](/blob/main/doc/screenshot1.png?raw=true)

## hardware
It should run on any hardware that supports ptp4l. 

It's currently tested on Raspberry 5.

## quick start
```
apt install victoria-metrics ./ptp-insight-0.0.1.deb
systemctl start victoria-metrics
systemctl start ptp-insight
systemctl start ptp-insight-web
```

## known issues

### Last 30s are a flat line in the graphs 
By default, victoria metrics will not give you any values for the last 30s. Thats why you'll see a 30s flat line at the end of each graph.
To overcome this. Add `-search.latencyOffset=1s` to the list of arguments in `/etc/default/victoria-metrics`  

### GM MAC and network delay are missing in L2 mode(gPTP) 
The packet capture code needs yet to be extended to support L2 mode for PTP

### It shows wrong values and status on a Raspberry PI
The Raspberry PI has not Realtime Clock by default. That means that the time is reset when you bootup the device and measurements will overlap. 

There are multiple ways to overcome this:
- Add a Realtime Clock
- Use NTP to sync the clock on startup
- In a future update, there will be a "clear all data" button

## Contribution and feedback
This project is still in an early stage and I'm still figuring out which values are interesting and how to interpret them. Feel free to join the discussion or submit any suggestions or pull requests on github:

https://github.com/shrank/ptp-insight