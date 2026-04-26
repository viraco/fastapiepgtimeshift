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
from anyio import open_file
import gzip

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

logger.info(f"BASE DIR:{base_dir}\n{" "*10}CONFIG DIR:{config_dir}\n{" "*10}DATA DIR:{data_dir}")

app = FastAPI()


@app.get("/", include_in_schema=False,summary="Redirect to Swagger UI")
async def root():
    return RedirectResponse(url="/docs")


@app.get("/create_offset_epg",summary="Create offset_epg.xml")
async def create_epg_async():
    create_combined_offset_epg_v2(_default_config._load_epg_offset_config(), data_dir)
    return {"message": "EPG created successfully"}


@app.get("/create_combined_epg",summary="Create combined_epg.xml")
async def create_combined_epg_async():
    create_combined_epg(_default_config._load_epg_combine_config(), data_dir)
    return {"message": "Combined EPG created successfully"}


@app.get("/{file_name:str}", summary="Download EPG file in gzip format", response_class=Response)
async def download_epg_file_async(file_name: str):
    if file_name not in _default_config.get_epg_file_names():
        raise HTTPException(status_code=400, detail=f"Invalid EPG file name: {file_name}")
    epg_file_path = os.path.join(data_dir, file_name)
    if not os.path.exists(epg_file_path):
        raise HTTPException(status_code=404, detail=f"EPG file not found: {file_name}")
    async with await open_file(epg_file_path, 'rb') as f:
        content = await f.read()

    # Compress the XML content as gzip
    compressed_content = gzip.compress(content)

    return Response(content=compressed_content, media_type='application/gzip', headers={
        'Content-Disposition': f'attachment; filename="{file_name}.gz"'
    })


@app.get("/refresh_config_files",summary="Reload offset_config and combine_epg json config files")
async def refresh_config_files_async():
    _default_config.refresh_epg_configs()
    return {"message": "Config files refreshed successfully"}


@app.post("/upload_offset_config", summary="Upload offset_config.json file")
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


@app.post("/upload_combine_config", summary="Upload combine_epg.json file")
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
