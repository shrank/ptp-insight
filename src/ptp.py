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

import subprocess
import re

def parse_ptp_log(line):
  parts = line.split(":")
  msg = ":".join(parts[1:]).strip()
  res = {
    "type": "unknown",
    "raw": msg
  }
  if(len(parts) > 1):
    item = parts[1].strip()
    if(item.startswith("port") and len(parts) >= 3):
      match = re.search(r'([A-Z0-9]+)\s+to\s+([A-Z0-9]+)\s+', parts[2])
      if match:
        res["value"] = match.group(2)
        res["item"] = item
        res["type"] = "port_status"
        return res

  match = re.search(r'selected ([a-z]+) clock ([a-z0-9.]+) as best master', msg)
  if match:
    res["value"] = match.group(2) + "(" + match.group(1) +")"
    res["type"] = "gm"
    return res

  match = re.search(r'selected best master clock ([a-z0-9.]+)', msg)
  if match:
    res["value"] = match.group(1)
    res["type"] = "gm"
    return res

  match = re.search(r'rms\s+([0-9]+)\s+max\s+([z0-9-]+)\s+freq\s+([z0-9-]+)\s+\+\/-\s+([z0-9-]+)\s+delay\s+([z0-9-]+)\s+\+\/-\s+([z0-9-]+)', msg)
  if match:
    res["value"] = int(match.group(1))
    res["max"] = int(match.group(2))
    res["freq"] = int(match.group(3))
    res["freq_deviation"] = int(match.group(4))
    res["delay"] = int(match.group(5))
    res["delay_deviation"] = int(match.group(6))
    res["type"] = "clock_stats"
    return res

  return res

def parse_config(data):
    config = {}
    current_section = None

    for line in data.split("\n"):
      line = line.strip()

      # Skip empty lines and comments
      if not line or line.startswith('#'):
          continue

      # Check for section headers (e.g., [global])
      match_section = re.match(r'^\[(\w+)\]$', line)
      if match_section:
          current_section = match_section.group(1)
          config[current_section] = {}
          continue

      # Check for key-value pairs (e.g., key=value or key		value)
      match_kv = re.match(r'^\s*(\S+)\s*(.*)$', line)
      if match_kv and current_section:
          key = match_kv.group(1)
          value = match_kv.group(2).strip()

          # Handle different value types (int, float, string, mac address, hex)
          if value.isdigit():
              value = int(value)
          elif re.match(r'^-?\d+\.\d+$', value):
              value = float(value)
          elif value.lower() in ['true','y','yes', '1']:
              value = True
          elif value.lower() in ['false','n','no', '0']:
              value = False
          config[current_section][key] = value

    return config

class pmc:

  class MGMT_IDS:

    ANNOUNCE_RECEIPT_TIMEOUT	=	"ANNOUNCE_RECEIPT_TIMEOUT"

    CLOCK_ACCURACY	=	"CLOCK_ACCURACY"

    CLOCK_DESCRIPTION	=	"CLOCK_DESCRIPTION"

    CURRENT_DATA_SET	=	"CURRENT_DATA_SET"

    DEFAULT_DATA_SET	=	"DEFAULT_DATA_SET"

    DELAY_MECHANISM	=	"DELAY_MECHANISM"

    DOMAIN	=	"DOMAIN"

    GRANDMASTER_SETTINGS_NP	=	"GRANDMASTER_SETTINGS_NP"

    LOG_ANNOUNCE_INTERVAL	=	"LOG_ANNOUNCE_INTERVAL"

    LOG_MIN_PDELAY_REQ_INTERVAL	=	"LOG_MIN_PDELAY_REQ_INTERVAL"

    LOG_SYNC_INTERVAL	=	"LOG_SYNC_INTERVAL"

    NULL_MANAGEMENT	=	"NULL_MANAGEMENT"

    PARENT_DATA_SET	=	"PARENT_DATA_SET"

    PORT_DATA_SET	=	"PORT_DATA_SET"

    PORT_DATA_SET_NP	=	"PORT_DATA_SET_NP"

    PORT_HWCLOCK_NP	=	"PORT_HWCLOCK_NP"

    PORT_PROPERTIES_NP	=	"PORT_PROPERTIES_NP"

    PORT_SERVICE_STATS_NP	=	"PORT_SERVICE_STATS_NP"

    PORT_STATS_NP	=	"PORT_STATS_NP"

    PRIORITY1	=	"PRIORITY1"

    PRIORITY2	=	"PRIORITY2"

    SLAVE_ONLY	=	"SLAVE_ONLY"

    TIMESCALE_PROPERTIES	=	"TIMESCALE_PROPERTIES"

    TIME_PROPERTIES_DATA_SET	=	"TIME_PROPERTIES_DATA_SET"

    TIME_STATUS_NP	=	"TIME_STATUS_NP"

    TRACEABILITY_PROPERTIES	=	"TRACEABILITY_PROPERTIES"

    UNICAST_MASTER_TABLE_NP	=	"UNICAST_MASTER_TABLE_NP"

    USER_DESCRIPTION	=	"USER_DESCRIPTION"

    VERSION_NUMBER	=	"VERSION_NUMBER"


  class Transport:
    IEEE802_3 = "-2"
    UDP_IPV4 = "-4"
    UDP_IPV6 = -6
    UDS_LOCAL = "-u"

  pmc_cmd = 'pmc'
  sudo_cmd = 'sudo'
  def __init__(self, configfile, use_sudo=False, transport=None, global_flags=[]):
    self.use_sudo = use_sudo
    self.transport=transport
    self.global_flags = global_flags
    self.configfile = configfile

  def _run_pmc(self, action, flags=[]):
    cmd = []
    if(self.use_sudo):
      cmd.append(self.sudo_cmd)
    cmd.append(self.pmc_cmd)
    if(self.transport is not None):
      cmd.append(self.transport)
    cmd.append("-f")
    cmd.append(self.configfile)
    cmd += self.global_flags
    cmd += flags
    cmd.append(action)
    result = subprocess.run(cmd, stdout=subprocess.PIPE)
    return result.stdout.decode('utf-8')

  '''
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
'''
  def _parse_pmc_output(self, output):
    res = {}
    resp_block = False
    for a in output.split("\n"):
      a = a.strip()
      if(a.startswith("sending:")):
        continue
      
      if("RESPONSE MANAGEMENT" in a):
        resp_block = True
        # @TD: parse this line
        continue
      if(resp_block is False):
        continue

      b = a.split(" ")
      if(b[0] == ""):
        continue
      res[b[0]] = " ".join(b[1:]).strip() 
    return res

  def get(self, cmd):
    res = self._run_pmc("GET " + cmd)
    return self._parse_pmc_output(res)
