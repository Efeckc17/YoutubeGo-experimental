import pytest
from core.downloader import DownloadTask

def test_download_task_attributes():
    task = DownloadTask(
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        resolution="720p",
        folder="/tmp",
        audio_only=True,
        playlist=False,
        subtitles=False,
        output_format="mp3",
        from_queue=False,
        priority=1,
        recurrence=None,
        max_rate="500K"
    )
    assert task.url.startswith("https://")
    assert task.audio_only is True
    assert task.output_format == "mp3"
