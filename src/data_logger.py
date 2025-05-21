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

from influxdb import InfluxDBClient

class Target:
  def __init__(self, URL, database, port=8086, Username='root', Password='root'):
    self.client = InfluxDBClient(host=URL, port=port, username=Username, password=Password, database=database)
    #self.client.create_database(database)
    self.clockId = "1"
  def insert_data(self, json_data):
    self.client.write_points(json_data)
