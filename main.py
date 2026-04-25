import os

from fastapi import FastAPI
from fastapi.responses import Response
from Functions.create_offset_epg import create_combined_offset_epg_v2
from Functions.cron_schedule import start_scheduler
from Functions.config import get_epg_offset_config
from Functions.download_epg import download_epg_files

base_dir = os.path.dirname(__file__)
config_dir = os.path.join(base_dir, 'Config')
data_dir = os.path.join(base_dir, 'Data')
epg_offset_config = get_epg_offset_config(config_dir)

print(f"BASE DIR:{base_dir}",
      f"CONFIG DIR:{config_dir}",
      f"DATA DIR:{data_dir}", sep="\n\r")

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.get("/create_epg")
async def create_epg():
    create_combined_offset_epg_v2(epg_offset_config, data_dir)
    return {"message": "EPG created successfully"}


@app.get("/offset_epg.xml")
async def download_epg_offset():
    epg_file_path = os.path.join(data_dir, 'offset_epg.xml')
    if not os.path.exists(epg_file_path):
        return {"error": "EPG file not found"}
    with open(epg_file_path, 'rb') as f:
        content = f.read()
    return Response(content=content, media_type='application/xml')


def download_epg_files_cron():
    download_epg_files(data_dir)
    create_combined_offset_epg_v2(epg_offset_config, data_dir)


scheduler = start_scheduler(download_epg_files_cron)
