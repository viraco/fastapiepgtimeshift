# FastAPI EPG Time Shift & Combiner

A FastAPI application designed to download, process, and combine XMLTV EPG (Electronic Program Guide) files. It allows for time-shifting specific channels (e.g., creating a Pacific feed from an Eastern feed) and merging multiple EPG sources into a single file.

I created this application to help with the process of creating time-shifted epg guides for my [Dispatcharr](https://github.com/Dispatcharr/Dispatcharr) instance.

## Features

- **Automated EPG Downloads**: Automatically downloads EPG files from configured URLs.
- **Time-Shifting**: Create new channels with time-shifted programs (e.g., +180 minutes).
- **EPG Merging**: Combine specific channels from multiple XMLTV files into a single master EPG.
- **Dynamic Configuration**: Update offset and combination rules via API without restarting the server.
- **Gzip Support**: Serves processed EPG files with gzip compression for efficient delivery to clients (like IPTV players).
- **Scheduled Updates**: Integrated scheduler to keep EPG data fresh.

## API Endpoints

### EPG Generation
- `GET /create_offset_epg`: Manually trigger the creation of `offset_epg.xml` based on `offset_config.json`.
- `GET /create_combined_epg`: Manually trigger the creation of `combined_epg.xml` based on `combine_epg.json`.

### Downloads
- `GET /{file_name}`: Download a processed EPG file (e.g., `combined_epg.xml`). Files are returned as `application/gzip`.

### Configuration Management
- `GET /refresh_config_files`: Reload the JSON configuration files from disk.
- `POST /upload_offset_config`: Upload and replace the `offset_config.json` file. A refresh of the config data occurs automatically.
- `POST /upload_combine_config`: Upload and replace the `combine_epg.json` file. A refresh of the config data occurs automatically.

### Documentation
- `GET /`: Redirects to the Swagger UI (`/docs`) for interactive API exploration.

## Configuration

The application uses two main configuration files in the `Config/` directory:

### `offset_config.json`
Defines which channels to shift and by how much.\
*find and replace are optional, and are case-sensitive and match on whole string*
```json
[
  {
    "channelid": "original.channel.id",
    "offset_minutes": "180",
    "new_channelid": "new.channel.id.offset180",
    "update_displayname": [
      { "find": "East", "replace": "West" }
    ],
    "epg_file": "source_file.xml"
  }
]
```

### `combine_epg.json`
Defines which channels from which files should be included in the master `combined_epg.xml`.
If `merge_channels` is set to true, all channels from the specified files will be merged the combined EPG.
```json
[
  {
    "epg_file": "source_file.xml",
    "channels": [
      { "channelid": "channel.one" },
      { "channelid": "channel.two" }
    ]
  },
  {
    "epg_file": "source_file2.xml",
    "merge_channels": true
]
```

### Environment Variables
Configure source URLs and download settings in `Config/config.env`:
- `CRON_SCHEDULE`: String for setting cron schedule used to automatically download and process EPG files
- `EPG_DOWNLOAD_COUNT`: Number of EPG files to download.
- `URL#`: URL for the #th EPG file.
- `FILE_NAME#`: Local filename for the #th EPG file.
```aiignore
CRON_SCHEDULE = 0 5 * * *
EPG_DOWNLOAD_COUNT=2
DOWNLOAD_URL1=https://epgshare01.online/epgshare01/epg_ripper_US_LOCALS1.xml.gz
FILE_NAME1=epg_ripper_US_LOCALS1.xml
DOWNLOAD_URL2=https://epgshare01.online/epgshare01/epg_ripper_US2.xml.gz
FILE_NAME2=epg_ripper_US2.xml
```
*config.env file used for urls instead of json as urls might contain credentials*\
*cron schedule set in env file to require restart of docker image*

## Running the Application

### Using Docker
```bash
docker build -t fastapiepgtimeshift .
docker run -p 8000:8000 fastapiepgtimeshift
```

### Using uv (Local)
```bash
uv sync
uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

### Using docker-compose
```
services:
  fastapi-epg-timeshift:
    container_name: fastapi-epg-timeshift
    image: ghcr.io/viraco/fastapiepgtimeshift:latest
    ports:
      - "8000:8000"
    volumes:
      - ./Config:/app/Config
      - ./Data:/app/Data
    restart: unless-stopped
```
*i personally have the /app/Data volume pointing to dispatcharr epgs directory*

## Directory Structure
- `Config/`: Configuration files (`.json`, `.env`).
- `Data/`: Downloaded and processed EPG files.
- `Functions/`: Core logic for EPG processing and scheduling.
