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
from threading import Thread 
from datetime import datetime, timezone
from queue import Queue ,Empty
from time import sleep 
from ptp import pmc

class bg_runner:
   def __init__(self, cmd, queue= None):
      self.is_running = False
      self.p = None
      self.cmd = cmd
      self.msg_queue = queue
      if(queue is None):
        self.msg_queue = Queue()
      self.stdout_thread = None

   def _read_loop (self):
    try :
      while self.is_running :
        line =self.p.stdout.readline ()
        self.msg_queue.put({
          "ts": datetime.now(timezone.utc),
          "line": line
          })
    except (ValueError ,IOError ):# pipe was closed
      pass 

   def start(self):
      if self.is_running:
          raise RuntimeError("Process is already running.")

      self.is_running = True
      if(self.msg_queue is not None):
        self.p = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, text=True)
        self.stdout_thread = Thread (target=self._read_loop)
        self.stdout_thread.start()
      else:
        self.p = subprocess.Popen(self.cmd)

   def get_stdout(self):
      try:
          return self.msg_queue.get_nowait()
      except Empty:
         return None
   
   def stop(self):
      if not self.is_running:
          raise RuntimeError("Process is not running.")

      if(self.p.poll() is None):
        self.p.terminate()
        self.p.wait()
      self.is_running = False
      self.stdout_thread = None


class pmc_runner:
   def __init__(self, cmds, config, queue=None, interval=5):
      self.is_running = False
      self.cmds = cmds
      self.pmc = pmc(config, transport=pmc.Transport.UDS_LOCAL, global_flags=["-b", "0"])
      self.interval = interval
      self.msg_queue = queue
      if(queue is None):
        self.msg_queue = Queue()

   def _loop (self):
    while self.is_running:
      sleep(self.interval)
      for a in self.cmds:
        try:
           res = self.pmc.get(a)
        except Exception as e:
           print(e)
           continue
        self.msg_queue.put({
          "ts": datetime.now(timezone.utc),
          "pmc": res,
          "type": a
          })

   def start(self):
      if self.is_running:
          raise RuntimeError("PMC is already running.")

      self.stdout_thread = Thread (target=self._loop)
      self.is_running = True
      self.stdout_thread.start()

   
   def stop(self):
      if not self.is_running:
          raise RuntimeError("Process is not running.")
      self.is_running = False
