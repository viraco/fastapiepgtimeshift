import os
import logging
import json

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import Response, RedirectResponse
from Functions.create_offset_epg import create_combined_offset_epg_v2
from Functions.cron_schedule import start_scheduler
from Functions.config import Config
from Functions.download_epg import download_epg_files
from Functions.create_combined_epg import create_combined_epg
from Functions.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

_default_config = Config()
_default_config.base_dir = os.path.dirname(__file__)
_default_config.config_dir = os.path.join(os.path.dirname(__file__), 'Config')
_default_config.data_dir = os.path.join(os.path.dirname(__file__), 'Data')
base_dir = _default_config.base_dir
config_dir = _default_config.config_dir
data_dir = _default_config.data_dir

_default_config.load_env_config()
_default_config.refresh_epg_configs()

logger.info(f"BASE DIR:{base_dir}\nCONFIG DIR:{config_dir}\nDATA DIR:{data_dir}")

app = FastAPI()


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")


@app.get("/create_offset_epg")
async def create_epg_async():
    create_combined_offset_epg_v2(_default_config._load_epg_offset_config(), data_dir)
    return {"message": "EPG created successfully"}


@app.get("/create_combined_epg")
async def create_combined_epg_async():
    create_combined_epg(_default_config._load_epg_combine_config(), data_dir)
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


@app.get("/refresh_config_files")
async def refresh_config_files_async():
    _default_config.refresh_epg_configs()
    return {"message": "Config files refreshed successfully"}


@app.post("/upload_offset_config")
async def upload_offset_config_async(file: UploadFile = File(...)):
    content = await file.read()

    # Validate JSON
    try:
        json.loads(content)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=422, detail=f"Invalid JSON file: {str(e)}")

    config_file_path = os.path.join(config_dir, 'offset_config.json')
    with open(config_file_path, 'wb') as f:
        f.write(content)
    _default_config.refresh_epg_offset_config()
    return {"message": "offset_config.json uploaded and replaced successfully"}


@app.post("/upload_combine_config")
async def upload_combine_config_async(file: UploadFile = File(...)):
    content = await file.read()

    # Validate JSON
    try:
        json.loads(content)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=422, detail=f"Invalid JSON file: {str(e)}")

    config_file_path = os.path.join(config_dir, 'combine_epg.json')
    with open(config_file_path, 'wb') as f:
        f.write(content)
    _default_config.refresh_epg_combine_config()
    return {"message": "combine_epg.json uploaded and replaced successfully"}


def download_epg_files_cron():
    download_epg_files(data_dir)
    create_combined_offset_epg_v2(_default_config._load_epg_offset_config(), data_dir)
    create_combined_epg(_default_config._load_epg_combine_config(), data_dir)


scheduler = start_scheduler(download_epg_files_cron)
