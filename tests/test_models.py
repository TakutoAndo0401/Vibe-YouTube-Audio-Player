"""
モデルクラスのテスト
"""

import pytest
from src.models.video_info import VideoInfo


class TestVideoInfo:
    """VideoInfoクラスのテスト"""
    
    def test_init_default_values(self):
        """デフォルト値での初期化テスト"""
        video = VideoInfo("https://example.com/video")
        
        assert video.url == "https://example.com/video"
        assert video.title == ""
        assert video.duration == 0
        assert video.channel == ""
        assert video.audio_url == ""
        assert video.is_loaded is False
    
    def test_init_with_values(self):
        """値を指定した初期化テスト"""
        video = VideoInfo(
            url="https://www.youtube.com/watch?v=test",
            title="Test Title",
            duration=120,
            channel="Test Channel",
            audio_url="https://example.com/audio.mp3"
        )
        
        assert video.url == "https://www.youtube.com/watch?v=test"
        assert video.title == "Test Title"
        assert video.duration == 120
        assert video.channel == "Test Channel"
        assert video.audio_url == "https://example.com/audio.mp3"
        assert video.is_loaded is False
    
    def test_str_representation(self):
        """文字列表現のテスト"""
        video = VideoInfo(
            url="https://example.com/video",
            title="Test Video",
            duration=180,
            channel="Test Channel"
        )
        
        expected = "VideoInfo(title='Test Video', channel='Test Channel', duration=180)"
        assert str(video) == expected
    
    def test_repr_representation(self):
        """デバッグ用文字列表現のテスト"""
        video = VideoInfo(
            url="https://example.com/video",
            title="Test Video",
            duration=180,
            channel="Test Channel"
        )
        video.is_loaded = True
        
        expected = ("VideoInfo(url='https://example.com/video', title='Test Video', "
                   "channel='Test Channel', duration=180, is_loaded=True)")
        assert repr(video) == expected
    
    def test_format_duration_zero(self):
        """再生時間0秒のフォーマットテスト"""
        video = VideoInfo("https://example.com/video", duration=0)
        assert video.format_duration() == "00:00"
    
    def test_format_duration_negative(self):
        """負の再生時間のフォーマットテスト"""
        video = VideoInfo("https://example.com/video", duration=-10)
        assert video.format_duration() == "00:00"
    
    def test_format_duration_seconds_only(self):
        """秒のみの再生時間のフォーマットテスト"""
        video = VideoInfo("https://example.com/video", duration=45)
        assert video.format_duration() == "0:45"
    
    def test_format_duration_minutes_and_seconds(self):
        """分と秒の再生時間のフォーマットテスト"""
        video = VideoInfo("https://example.com/video", duration=125)  # 2分5秒
        assert video.format_duration() == "2:05"
    
    def test_format_duration_hours(self):
        """時間を含む再生時間のフォーマットテスト"""
        video = VideoInfo("https://example.com/video", duration=3665)  # 1時間1分5秒
        assert video.format_duration() == "61:05"
    
    def test_is_valid_true(self):
        """有効な動画情報のテスト"""
        video = VideoInfo(
            url="https://www.youtube.com/watch?v=test",
            title="Test Video",
            audio_url="https://example.com/audio.mp3"
        )
        video.is_loaded = True
        
        assert video.is_valid() is True
    
    def test_is_valid_false_no_url(self):
        """URL無しの無効な動画情報のテスト"""
        video = VideoInfo(
            url="",
            title="Test Video",
            audio_url="https://example.com/audio.mp3"
        )
        video.is_loaded = True
        
        assert video.is_valid() is False
    
    def test_is_valid_false_no_title(self):
        """タイトル無しの無効な動画情報のテスト"""
        video = VideoInfo(
            url="https://www.youtube.com/watch?v=test",
            title="",
            audio_url="https://example.com/audio.mp3"
        )
        video.is_loaded = True
        
        assert video.is_valid() is False
    
    def test_is_valid_false_no_audio_url(self):
        """音声URL無しの無効な動画情報のテスト"""
        video = VideoInfo(
            url="https://www.youtube.com/watch?v=test",
            title="Test Video",
            audio_url=""
        )
        video.is_loaded = True
        
        assert video.is_valid() is False
    
    def test_is_valid_false_not_loaded(self):
        """未ロードの無効な動画情報のテスト"""
        video = VideoInfo(
            url="https://www.youtube.com/watch?v=test",
            title="Test Video",
            audio_url="https://example.com/audio.mp3"
        )
        # is_loaded = False のまま
        
        assert video.is_valid() is False 