import unittest
import sys

sys.path.append("..")
from ptp import pmc, parse_config, parse_ptp_log

class TestLogParser(unittest.TestCase):
  def test_parse_clock_stats(self):
    data = "ptp4l[693.323]: rms  219 max  342 freq -54550 +/- 301 delay  2703 +/-   0"
    res = parse_ptp_log(data)
    self.assertEqual(res["type"], "clock_stats")
    self.assertEqual(res["value"], 219)
    self.assertEqual(res["max"], 342)
    self.assertEqual(res["freq"], -54550)
    self.assertEqual(res["freq_deviation"], 301)
    self.assertEqual(res["delay"], 2703)
    self.assertEqual(res["delay_deviation"], 0)

  def test_parse_gm(self):
    data = "ptp4l[733.428]: selected local clock 2ccf67.fffe.555875 as best master"
    res = parse_ptp_log(data)
    self.assertEqual(res["type"], "gm")
    self.assertEqual(res["value"], "2ccf67.fffe.555875(local)")

    data = "ptp4l[680.492]: selected best master clock 00197c.fffe.02ed93"
    res = parse_ptp_log(data)
    self.assertEqual(res["type"], "gm")
    self.assertEqual(res["value"], "00197c.fffe.02ed93")


  def test_parse_port_status(self):
    data = "ptp4l[681.695]: port 1: UNCALIBRATED to SLAVE on MASTER_CLOCK_SELECTED"
    res = parse_ptp_log(data)
    self.assertEqual(res["type"], "port_status")
    self.assertEqual(res["item"], "port 1")
    self.assertEqual(res["value"], "SLAVE")

class TestPmcParser(unittest.TestCase):
  def test_parse_pmc_output(self):
    data = """
sending: GET TIME_STATUS_NP
        38f3ab.fffe.9c3830-0 seq 0 RESPONSE MANAGEMENT TIME_STATUS_NP
                master_offset              0
                ingress_time               0
                cumulativeScaledRateOffset +0.000000000
                scaledLastGmPhaseChange    0
                gmTimeBaseIndicator        0
                lastGmPhaseChange          0x0000'0000000000000000.0000
                gmPresent                  false
                gmIdentity                 38f3ab.fffe.9c3830
"""
    app = pmc("config.ini")
    res = app._parse_pmc_output(data)
    self.assertEqual(len(res.keys()), 8)
    self.assertEqual(res["master_offset"], "0")
    self.assertEqual(res["ingress_time"], "0")
    self.assertEqual(res["cumulativeScaledRateOffset"], "+0.000000000")
    self.assertEqual(res["scaledLastGmPhaseChange"], "0")
    self.assertEqual(res["gmTimeBaseIndicator"], "0")
    self.assertEqual(res["lastGmPhaseChange"], "0x0000'0000000000000000.0000")
    self.assertEqual(res["gmPresent"], "false")
    self.assertEqual(res["gmIdentity"], "38f3ab.fffe.9c3830")


class TestConfigParser(unittest.TestCase):
  def test_parse_config(self):
    data = """
[global]
run_victoria        yes
victoria_password   893hrer0iu3q0rj43qirn4nrjnofndsoiajfpewaf
run_vicotria_logs   yes
eth_interface       eth0
ptp_inerface        /dev/ptp0
use_influx_server   no
influxdb_server     my influx influx server
influxdb_db         metrics
influxdb_user       root
influxdb_pasword    root
"""
    res = parse_config(data)
    self.assertIn("global", res)
    self.assertEqual(len(res["global"].keys()), 10)
    self.assertEqual(res["global"]["run_victoria"], True)
    self.assertEqual(res["global"]["victoria_password"], "893hrer0iu3q0rj43qirn4nrjnofndsoiajfpewaf")
    self.assertEqual(res["global"]["run_vicotria_logs"], True)
    self.assertEqual(res["global"]["eth_interface"], "eth0")
    self.assertEqual(res["global"]["ptp_inerface"], "/dev/ptp0")


    self.assertEqual(res["global"]["use_influx_server"], False)
    self.assertEqual(res["global"]["influxdb_server"], "my influx influx server")
    self.assertEqual(res["global"]["influxdb_db"], "metrics")
    self.assertEqual(res["global"]["influxdb_user"], "root")
    self.assertEqual(res["global"]["influxdb_pasword"], "root")
    
if __name__ == '__main__':
    unittest.main()