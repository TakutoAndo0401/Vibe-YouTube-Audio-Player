"""
pytest設定ファイル
"""

import pytest
from unittest.mock import Mock, MagicMock
from src.models.video_info import VideoInfo


@pytest.fixture
def sample_video_info():
    """サンプル動画情報を作成"""
    video = VideoInfo(
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        title="Test Video Title",
        duration=180,  # 3分
        channel="Test Channel",
        audio_url="https://example.com/audio.mp3"
    )
    video.is_loaded = True
    return video


@pytest.fixture
def mock_vlc_instance():
    """VLCインスタンスのモックを作成"""
    mock_instance = Mock()
    mock_player = Mock()
    mock_event_manager = Mock()
    
    mock_instance.media_player_new.return_value = mock_player
    mock_player.event_manager.return_value = mock_event_manager
    mock_player.get_position.return_value = 0.5
    mock_player.get_time.return_value = 90000  # 90秒
    mock_player.get_length.return_value = 180000  # 180秒
    
    return mock_instance, mock_player, mock_event_manager


@pytest.fixture
def mock_yt_dlp_info():
    """yt-dlpの情報辞書のモックを作成"""
    return {
        'title': 'Test Video Title',
        'duration': 180,
        'uploader': 'Test Channel',
        'url': 'https://example.com/audio.mp3'
    } 