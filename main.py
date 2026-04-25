import os

from fastapi import FastAPI
from fastapi.responses import Response, RedirectResponse
from Functions.create_offset_epg import create_combined_offset_epg_v2
from Functions.cron_schedule import start_scheduler
from Functions.config import get_epg_offset_config, get_epg_combine_config
from Functions.download_epg import download_epg_files
from Functions.create_combined_epg import create_combined_epg

base_dir = os.path.dirname(__file__)
config_dir = os.path.join(base_dir, 'Config')
data_dir = os.path.join(base_dir, 'Data')
epg_offset_config = get_epg_offset_config(config_dir)
epg_combine_config = get_epg_combine_config(config_dir)

print(f"BASE DIR:{base_dir}",
      f"CONFIG DIR:{config_dir}",
      f"DATA DIR:{data_dir}", sep="\n\r")

app = FastAPI()


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")


@app.get("/create_offset_epg")
async def create_epg_async():
    create_combined_offset_epg_v2(epg_offset_config, data_dir)
    return {"message": "EPG created successfully"}


@app.get("/create_combined_epg")
async def create_combined_epg_async():
    create_combined_epg(epg_combine_config, data_dir)
    return {"message": "Combined EPG created successfully"}


@app.get("/offset_epg.xml")
async def download_epg_offset_async():
    epg_file_path = os.path.join(data_dir, 'offset_epg.xml')
    if not os.path.exists(epg_file_path):
        return {"error": "EPG file not found"}
    with open(epg_file_path, 'rb') as f:
        content = f.read()
    return Response(content=content, media_type='application/xml')


@app.get("/combined_epg.xml")
async def download_combined_epg_async():
    epg_file_path = os.path.join(data_dir, 'combined_epg.xml')
    if not os.path.exists(epg_file_path):
        return {"error": "Combined EPG file not found"}
    with open(epg_file_path, 'rb') as f:
        content = f.read()
    return Response(content=content, media_type='application/xml')


@app.get("/combined_epg.xml")
def download_epg_files_cron():
    download_epg_files(data_dir)
    create_combined_offset_epg_v2(epg_offset_config, data_dir)
    create_combined_epg(epg_combine_config, data_dir)


scheduler = start_scheduler(download_epg_files_cron)
