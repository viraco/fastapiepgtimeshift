import os
import requests
import gzip
import zipfile
import io
from Functions.config import load_config


def download_file(url, file_path):
    """Download a file from URL and save it to the specified path"""
    file_name = os.path.split(file_path)[-1]
    try:
        print(f"Downloading file {file_name}...")
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        content = response.content

        # Check if content is gzip compressed
        if content[:2] == b'\x1f\x8b':
            print("Detected gzip compression, decompressing...")
            content = gzip.decompress(content)
        # Check if content is zip compressed
        elif content[:4] == b'PK\x03\x04' or content[:4] == b'PK\x05\x06':
            print("Detected zip compression, decompressing...")
            with zipfile.ZipFile(io.BytesIO(content)) as zip_file:
                # Extract the first file in the archive
                first_file = zip_file.namelist()[0]
                content = zip_file.read(first_file)
                print(f"Extracted: {first_file}")

        with open(file_path, 'wb') as f:
            f.write(content)

        print(f"Successfully saved to {file_path}")
        return True
    except Exception as e:
        print(f"Error downloading {file_name}: {e}")
        return False


def download_epg_files(base_dir=None):
    """Download all EPG files based on config.env configuration"""
    load_config()

    epg_download_count = int(os.getenv('EPG_DOWNLOAD_COUNT', '0'))

    if epg_download_count == 0:
        print("No EPG files to download (EPG_DOWNLOAD_COUNT is 0 or not set)")
        return

    print(f"Starting download of {epg_download_count} EPG file(s)...")

    for i in range(1, epg_download_count + 1):
        url = os.getenv(f'DOWNLOAD_URL{i}')
        file_name = os.getenv(f'FILE_NAME{i}')

        if not url or not file_name:
            print(f"Skipping index {i}: DOWNLOAD_URL{i} or FILE_NAME{i} not configured")
            continue

        # Construct full file path relative to Data directory
        if base_dir is None:
            base_dir = os.path.join(os.path.dirname(__file__), '..', 'Data')
        file_path = os.path.join(base_dir, file_name)

        download_success = download_file(url, file_path)
        if not download_success:
            print(f"Download failed for index {i}")
            continue

    print("Download process completed")