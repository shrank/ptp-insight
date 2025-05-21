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

from scapy.all import sniff, Packet, ByteField, ShortField, IntField, XBitField, bind_layers, UDP, IP, AsyncSniffer, Ether
from datetime import datetime, timezone

PTP_EVENT_PORT = 319  # Standard UDP port for PTP event messages

class PTPv2(Packet):
    name = "PTPv2"
    fields_desc = [
        XBitField('transportSpecific', 0x0, 4),
        XBitField('messageType', 0x0, 4),
        ByteField("version", 2),
        ShortField("messageLength", 0),
        ByteField("domainNumber", 0),
        ByteField("reserved1", 0),
        ShortField("flags", 0),
        ShortField("flags2", 0), #this is wrong, next field should be a 6byte integer
        IntField("correctionFieldUpper", 0),
        IntField("correctionFieldLower", 0),
        IntField("reserved2", 0),
        ShortField("sourcePortIdentity_clockIdentity1", 0),
        ShortField("sourcePortIdentity_clockIdentity2", 0),
        ShortField("sourcePortIdentity_clockIdentity3", 0),
        ShortField("sourcePortIdentity_portNumber", 0),
        ShortField("sequenceId", 0),
        ByteField("controlField", 0),
        ByteField("logMessageInterval", 0)
    ]

    def extract_padding(self, s):
        return "", s

    def to_dict(self):
        return {field.name: getattr(self, field.name) for field in self.fields_desc}

# Bind PTPv2 to UDP on port 319
bind_layers(UDP, PTPv2, dport=PTP_EVENT_PORT)

class ptp_sniffer:
  def __init__(self):
     self.queue = None
  def process_packet(self, packet):
      if PTPv2 in packet:
          ptp = packet[PTPv2]
          if(ptp.messageType == 0):
            if(self.queue is None):
              print("PTPv2 Sync Packet:")
              print(ptp.to_dict())
            else:
               self.queue.put({
                  "ts": datetime.now(timezone.utc),
                  "scapy": {
                    "mac": packet[Ether],
                    "ip": packet[IP],
                    "ptp": ptp                     
                  },
                  "type": "ptp-sync-message"
               })

  def start(self, interface="eth0"):
      print(f"Starting capture on {interface}...")
      sniff(iface=interface, filter="udp port 319 or udp port 320", prn=self.process_packet, store=0)

  def start_bg(self,  interface="eth0"):
    self.t = AsyncSniffer(iface=interface, filter="udp port 319 or udp port 320", prn=self.process_packet, store=0)
    self.t.start()

  def stop(self):
   self.t.stop()

if __name__ == "__main__":
  app = ptp_sniffer()
  app.start_bg("eth0")
  import time
  time.sleep(10)
  app.stop()