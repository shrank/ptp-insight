"""
This file is part of ptp-insight

ptp-insight is free software: you can redistribute it and/or modify it under the terms 
of the GNU General Public License as published by the Free Software Foundation,  
version 3 of the License.

ptp-insight is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; 
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with ptp-insight. 
If not, see <https://www.gnu.org/licenses/>. 
"""

import logging
import signal
import sys
import argparse
from os import path
from time import sleep
from queue import Queue 
from requests.exceptions import ConnectionError
from data_logger import Target
from runners import bg_runner, pmc_runner

from ptp import parse_config, parse_ptp_log
from common import config
from capture import ptp_sniffer

terminate = False
# Signal handler function
def handle_sigterm(signum, frame):
    global terminate
    print("Caught SIGTERM signal! Exiting gracefully...")
    terminate=True

# Register the SIGTERM signal with the handler
signal.signal(signal.SIGTERM, handle_sigterm)

def main():
    global terminate
    # Configure the logging
    logging.basicConfig(
        stream=sys.stdout,  # Direct logs to stdout
        level=logging.INFO,  # Set the logging level (DEBUG, INFO, etc.)
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Include thread name
        datefmt='%Y-%m-%d %H:%M:%S'  # Date format for the timestamp
    )
    log = logging.getLogger(name="main")               
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    parser = argparse.ArgumentParser(description='runs ptp4l and collect statistic data')
    parser.add_argument('configfile', help='config file')
    args = parser.parse_args()

    with open(args.configfile) as f:
      r = parse_config(f.read())
      if("global" in r):
        config.update(r["global"])

    metrics = Target(config["influx_server"], config["influx_database"], port=int(config["influx_port"]), Username=config["influx_username"], Password=config["influx_password"])

    log_queue = Queue()
    ptp_config = ""
    ptp = bg_runner([
      "ptp4l", 
      "-i",
      config["eth_interface"],
      "-p",
      config["ptp_inerface"],
      "-s",
      "-l",
      "6",
      "-m",
      "-q",
      "-f",
      config["ptp_config"]
    ], queue=log_queue)

    pmc = pmc_runner(["TIME_STATUS_NP"], config["ptp_config"], queue=log_queue)
    new_metrics = []


    sniffer = ptp_sniffer()
    sniffer.queue = log_queue
    sniffer.start_bg()

    while terminate is False:
      config_raw = ""
      if(not path.exists(config["ptp_config"])):
         log.warning("missing config: %s, waiting for it to appear"%config["ptp_config"])
         sleep(10)
         continue

      with open(config["ptp_config"]) as f:
        config_raw = f.read()
      if(ptp_config != config_raw):
        log.info("config changed, restart ptp")
        ptp_config = config_raw
        if(ptp.is_running):
          ptp.stop()
        if(pmc.is_running):
           pmc.stop()
        ptp.start()
        pmc.start()
      while terminate is False:
        a = ptp.get_stdout()
        if(a is None):
          break
        if("pmc" in a):
            if(a["type"] == "TIME_STATUS_NP" and "gmIdentity" in a["pmc"]):
              new_metrics.append(
                {
                    "measurement": a["type"].lower(),
                    "tags": {
                      "reporter_id": config["reporter_id"],
                      "gm_identity": a["pmc"]["gmIdentity"],
                    },
                    "time": a["ts"].isoformat(),
                    "fields": {
                      "master_offset": int(a["pmc"]["master_offset"]),
                      "ingress_time": int(a["pmc"]["ingress_time"]),
                      "gm_present": 1 if (a["pmc"]["gmPresent"] == "true") else -1
                    }
                })
        if("scapy" in a):
              r ={
                    "measurement": "network",
                    "tags": {
                      "reporter_id": config["reporter_id"],
                      "master_ip":"",
                      "master_mac": "",
                      "dscp": 0
                    },
                    "time": a["ts"].isoformat(),
                    "fields": {
                      "delay": a["scapy"]["ptp"].correctionFieldUpper
                    }
                }
              if("ip" in a["scapy"]):
                  r["tags"].update({
                    "master_ip": a["scapy"]["ip"].src,
                    "master_mac": a["scapy"]["mac"].src,
                    "dscp": str(a["scapy"]["ip"].tos >> 2)
                  })
              new_metrics.append(r)

        if("line" in a):
          r = parse_ptp_log(a["line"])
          if(r["type"] == "clock_stats"):
              new_metrics.append(
                {
                    "measurement": r["type"],
                    "tags": {
                      "reporter_id": config["reporter_id"]
                    },
                    "time": a["ts"].isoformat(),
                    "fields": {
                      "rms": r["value"],
                      "max": r["max"],
                      "freq": r["freq"],
                      "freq_deviation": r["freq_deviation"],
                      "delay": r["delay"],
                      "delay_deviation": r["delay_deviation"]
                    }
                })
      if(len(new_metrics) > 0):
        try:
          metrics.insert_data(new_metrics)
          new_metrics = []
        except ConnectionError:
          log.error("Faild to connect to influxdb")
      else:
        sleep(1)

    pmc.stop()
    ptp.stop()
    sniffer.stop()
    exit(0)

if __name__ == "__main__":
    main()

