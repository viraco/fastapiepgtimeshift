import os
import unittest
import asyncio
from unittest.mock import patch
from fastapi import HTTPException
from Functions.config import Config
from Functions.download_epg import download_epg_files
from main import download_epg_file_async, download_epg_files_cron


class TestEpgDownloadCount(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.config = Config()

    @patch.dict(os.environ, {
        "EPG_DOWNLOAD_COUNT": "0",
        "DOWNLOAD_URL1": "https://example.com/test1.xml.gz",
        "FILE_NAME1": "test1.xml",
        "DOWNLOAD_URL2": "https://example.com/test2.xml.gz",
        "FILE_NAME2": "test2.xml"
    }, clear=False)
    @patch("Functions.download_epg.download_file")
    def test_epg_download_count_zero_does_not_download(self, mock_download):
        download_epg_files()
        mock_download.assert_not_called()

    @patch.dict(os.environ, {
        "EPG_DOWNLOAD_COUNT": "0",
        "DOWNLOAD_URL1": "https://example.com/test1.xml.gz",
        "FILE_NAME1": "test1.xml"
    }, clear=False)
    def test_epg_download_count_zero_file_names(self):
        file_names = self.config.get_epg_file_names()
        self.assertEqual(file_names, ["combined_epg.xml", "offset_epg.xml"])
        self.assertNotIn("test1.xml", file_names)

    @patch.dict(os.environ, {
        "EPG_DOWNLOAD_COUNT": "2",
        "DOWNLOAD_URL1": "https://example.com/test1.xml.gz",
        "FILE_NAME1": "test1.xml",
        "DOWNLOAD_URL2": "https://example.com/test2.xml.gz",
        "FILE_NAME2": "test2.xml"
    }, clear=False)
    def test_epg_download_count_positive_file_names(self):
        file_names = self.config.get_epg_file_names()
        self.assertEqual(file_names, ["test1.xml", "test2.xml", "combined_epg.xml", "offset_epg.xml"])

    @patch.dict(os.environ, {
        "EPG_DOWNLOAD_COUNT": "0",
        "DOWNLOAD_URL1": "https://example.com/test1.xml.gz",
        "FILE_NAME1": "test1.xml"
    }, clear=False)
    async def test_api_blocks_existing_files_when_count_zero(self):
        # Attempt to download existing or unlisted file when EPG_DOWNLOAD_COUNT=0
        with self.assertRaises(HTTPException) as cm:
            await download_epg_file_async("test1.xml")
        self.assertEqual(cm.exception.status_code, 400)
        self.assertIn("Invalid EPG file name", cm.exception.detail)

        with self.assertRaises(HTTPException) as cm:
            await download_epg_file_async("epg_ripper_US2.xml")
        self.assertEqual(cm.exception.status_code, 400)
        self.assertIn("Invalid EPG file name", cm.exception.detail)

    @patch.dict(os.environ, {
        "EPG_DOWNLOAD_COUNT": "0",
        "DOWNLOAD_URL1": "https://example.com/test1.xml.gz",
        "FILE_NAME1": "test1.xml"
    }, clear=False)
    @patch("main.download_epg_files")
    @patch("main.create_combined_offset_epg_v2")
    @patch("main.create_combined_epg")
    def test_cron_behavior_when_count_zero(self, mock_combine, mock_offset, mock_download):
        download_epg_files_cron()
        mock_download.assert_called_once()
        mock_offset.assert_called_once()
        mock_combine.assert_called_once()


if __name__ == '__main__':
    unittest.main()
