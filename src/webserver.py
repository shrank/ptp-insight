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

import os
import uvicorn
import argparse
import httpx
import time
import re
import subprocess
from fastapi import FastAPI, Request, status
from fastapi.responses import RedirectResponse, JSONResponse
from starlette.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from ptp import parse_config, pmc
from common import config


parser = argparse.ArgumentParser(description='run webserver for ptp-insight')
parser.add_argument('configfile', help='config file')
args = parser.parse_args()

with open(args.configfile) as f:
  r = parse_config(f.read())
  if("global" in r):
    config.update(r["global"])


app = FastAPI()
client = httpx.AsyncClient()

# Mount static directory to /static
app.mount("/static", StaticFiles(directory="static"), name="static")

# Redirect root path to /static/
@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/static/index.html", status_code=status.HTTP_302_FOUND)

@app.get("/api/now")
async def server_time(request: Request):
  return JSONResponse(content={"now": time.time()})

@app.get("/api/v1/query")
async def forward_query(request: Request):
    # Get query parameters from the original request
    query_params = dict(request.query_params)

    
    async def stream_response():
        async with client.stream("GET", "http://%s:%d/api/v1/query" % (config["influx_server"], config["influx_port"]), params=query_params) as proxied_response:
            async for chunk in proxied_response.aiter_bytes():
                yield chunk

    # Make a request inside generator, but call outside
    # This keeps the connection open while data is streamed
    return StreamingResponse(
        stream_response(),
        status_code=200,  # You could pass real status later
        media_type='application/octet-stream'  # Or infer from headers
    )


@app.get("/api/v1/query_range")
async def forward_query_range(request: Request):
    # Get query parameters from the original request
    query_params = dict(request.query_params)

    async def stream_response():
        async with client.stream("GET", "http://%s:%d/api/v1/query_range" % (config["influx_server"], config["influx_port"]), params=query_params) as proxied_response:
            async for chunk in proxied_response.aiter_bytes():
                yield chunk

    # Make a request inside generator, but call outside
    # This keeps the connection open while data is streamed
    return StreamingResponse(
        stream_response(),
        status_code=200,  # You could pass real status later
        media_type='application/octet-stream'  # Or infer from headers
    )

# Get server config 
@app.get("/api/serverconfig")
async def get_serverconfig():
    return JSONResponse(content=config)


# Get status of the ptp service 
@app.get("/api/config")
async def get_config():
    res = {}
    try:
      with open(config["ptp_config"]) as f:
        res["raw"] = f.read()
    except Exception as e:
      res["raw"] = "Error: " + str(e)
    return JSONResponse(content=res)

# Get status of the ptp service 
@app.get("/api/configs")
async def get_configs():
    available = [("OFF","off")]
    try:
        for f in os.listdir(config["available_configs"]):
            if os.path.isfile(os.path.join(config["available_configs"], f)):
                name = f
                with open(os.path.join(config["available_configs"], f), 'r') as file:
                    match = re.search(r'#\s*[Nn]ame: ([^\s]+)', file.read())
                    if match:
                      name = match.group(1)
                available.append((name, f))
    except FileNotFoundError as e:
        print("File not found: " + str(e))
    except PermissionError as e:
        print("Permission denied:" + str(e))
        return []
    current = "not a simlink"
    if not os.path.exists(config["ptp_config"]):
       current = "off"
    if os.path.islink(config["ptp_config"]):
        current = os.path.basename(os.readlink(config["ptp_config"]))
    
    res = {
        "available": available,
        "current": current
    }
    return JSONResponse(content=res)


@app.post("/api/config")
async def post_config(request: Request):
    body = await request.json()
    if os.path.exists(config["ptp_config"]):
      if not os.path.islink(config["ptp_config"]):
          return JSONResponse(content={"message": "Configfile is not a symlink"})
      os.remove(config["ptp_config"])  # remove the existing symlink
    new_target = os.path.join(config["available_configs"], body["new_config"])
    if not os.path.isfile(new_target):
      return JSONResponse(content={"message": "Config %s not found" % body["new_config"]})

    os.symlink(new_target, config["ptp_config"])

    return JSONResponse(content={"message": "Success"})

# Get status of the ptp service 
@app.get("/api/status")
async def get_status():
    res = {
        "time": time.time_ns(),
        "status": "online",
        "grandmaster": "00197c.fffe.02ed93",
        "config": "gPTP"
    }
    return JSONResponse(content=res)

# Get raw output of all pmc commands
@app.get("/api/raw_output")
async def get_raw_output():
    res =""
    p = pmc(config["ptp_config"], transport=pmc.Transport.UDS_LOCAL, global_flags=["-b", "0"])
    for attr_name in dir(pmc.MGMT_IDS()):
      if not attr_name.startswith('__'):
          res += "\n" +attr_name + "\n"
          res += p._run_pmc("GET " + attr_name)
    return JSONResponse(content={"time": time.time(), "output": res})

# Get logs 
@app.get("/api/logs")
async def get_logs():
    result = subprocess.run(["journalctl", "-n","200","-u", "ptp-insight.service"], stdout=subprocess.PIPE)
    return JSONResponse(content={"time": time.time(), "output": result.stdout.decode('utf-8')})


if __name__ == "__main__":
  uvicorn.run("webserver:app", host=config["webserver_ip"], port=config["webserver_port"], log_level="info") 