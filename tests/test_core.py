"""
コアロジックのテスト
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from src.core.media_player import MediaPlayer
from src.core.youtube_downloader import YouTubeDownloader
from src.models.video_info import VideoInfo


class TestMediaPlayer:
    """MediaPlayerクラスのテスト"""
    
    @patch('src.core.media_player.vlc')
    def test_init(self, mock_vlc):
        """初期化のテスト"""
        mock_instance = Mock()
        mock_player = Mock()
        mock_event_manager = Mock()
        
        mock_vlc.Instance.return_value = mock_instance
        mock_instance.media_player_new.return_value = mock_player
        mock_player.event_manager.return_value = mock_event_manager
        
        player = MediaPlayer()
        
        assert player.current_video is None
        assert player.playlist == []
        assert player.current_index == 0
        assert player.is_playing is False
        
        mock_vlc.Instance.assert_called_once_with('--intf=dummy', '--no-video', '--quiet', '--no-sout-all', '--sout-keep')
        mock_instance.media_player_new.assert_called_once()
    
    @patch('src.core.media_player.vlc')
    def test_add_to_playlist_valid_video(self, mock_vlc, sample_video_info):
        """有効な動画をプレイリストに追加するテスト"""
        player = MediaPlayer()
        
        result = player.add_to_playlist(sample_video_info)
        
        assert result is True
        assert len(player.playlist) == 1
        assert player.playlist[0] == sample_video_info
    
    @patch('src.core.media_player.vlc')
    def test_add_to_playlist_invalid_video(self, mock_vlc):
        """無効な動画をプレイリストに追加するテスト"""
        player = MediaPlayer()
        invalid_video = VideoInfo("", "", 0, "", "")  # 無効な動画
        
        result = player.add_to_playlist(invalid_video)
        
        assert result is False
        assert len(player.playlist) == 0
    
    @patch('src.core.media_player.vlc')
    def test_add_to_playlist_none(self, mock_vlc):
        """Noneをプレイリストに追加するテスト"""
        player = MediaPlayer()
        
        result = player.add_to_playlist(None)
        
        assert result is False
        assert len(player.playlist) == 0
    
    @patch('src.core.media_player.vlc')
    def test_remove_from_playlist_valid_index(self, mock_vlc, sample_video_info):
        """有効なインデックスでプレイリストから削除するテスト"""
        player = MediaPlayer()
        player.add_to_playlist(sample_video_info)
        
        result = player.remove_from_playlist(0)
        
        assert result is True
        assert len(player.playlist) == 0
    
    @patch('src.core.media_player.vlc')
    def test_remove_from_playlist_invalid_index(self, mock_vlc, sample_video_info):
        """無効なインデックスでプレイリストから削除するテスト"""
        player = MediaPlayer()
        player.add_to_playlist(sample_video_info)
        
        result = player.remove_from_playlist(1)
        
        assert result is False
        assert len(player.playlist) == 1
    
    @patch('src.core.media_player.vlc')
    def test_remove_from_playlist_negative_index(self, mock_vlc, sample_video_info):
        """負のインデックスでプレイリストから削除するテスト"""
        player = MediaPlayer()
        player.add_to_playlist(sample_video_info)
        
        result = player.remove_from_playlist(-1)
        
        assert result is False
        assert len(player.playlist) == 1
    
    @patch('src.core.media_player.vlc')
    def test_get_playlist_size(self, mock_vlc, sample_video_info):
        """プレイリストサイズ取得のテスト"""
        player = MediaPlayer()
        
        assert player.get_playlist_size() == 0
        
        player.add_to_playlist(sample_video_info)
        assert player.get_playlist_size() == 1
    
    @patch('src.core.media_player.vlc')
    def test_is_playlist_empty(self, mock_vlc, sample_video_info):
        """プレイリスト空判定のテスト"""
        player = MediaPlayer()
        
        assert player.is_playlist_empty() is True
        
        player.add_to_playlist(sample_video_info)
        assert player.is_playlist_empty() is False
    
    @patch('src.core.media_player.vlc')
    def test_clear_playlist(self, mock_vlc, sample_video_info):
        """プレイリストクリアのテスト"""
        player = MediaPlayer()
        player.add_to_playlist(sample_video_info)
        
        player.clear_playlist()
        
        assert len(player.playlist) == 0
        assert player.current_index == 0
        assert player.current_video is None
    
    @patch('src.core.media_player.vlc')
    def test_set_position_valid_range(self, mock_vlc):
        """有効範囲内での再生位置設定のテスト"""
        player = MediaPlayer()
        
        result = player.set_position(0.5)
        
        assert result is True
        player.player.set_position.assert_called_once_with(0.5)
    
    @patch('src.core.media_player.vlc')
    def test_set_position_clamp_values(self, mock_vlc):
        """範囲外の値での再生位置設定のテスト"""
        player = MediaPlayer()
        
        # 1.0を超える値
        result1 = player.set_position(1.5)
        assert result1 is True
        player.player.set_position.assert_called_with(1.0)
        
        # 0.0未満の値
        result2 = player.set_position(-0.5)
        assert result2 is True
        player.player.set_position.assert_called_with(0.0)


class TestYouTubeDownloader:
    """YouTubeDownloaderクラスのテスト"""
    
    def test_init(self):
        """初期化のテスト"""
        downloader = YouTubeDownloader()
        
        expected_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
        }
        
        assert downloader.ydl_opts == expected_opts
    
    def test_is_youtube_url_valid_youtube_com(self):
        """youtube.comの有効URLテスト"""
        downloader = YouTubeDownloader()
        
        assert downloader._is_youtube_url("https://www.youtube.com/watch?v=test") is True
        assert downloader._is_youtube_url("http://youtube.com/watch?v=test") is True
        assert downloader._is_youtube_url("youtube.com/watch?v=test") is True
    
    def test_is_youtube_url_valid_youtu_be(self):
        """youtu.beの有効URLテスト"""
        downloader = YouTubeDownloader()
        
        assert downloader._is_youtube_url("https://youtu.be/test") is True
        assert downloader._is_youtube_url("http://youtu.be/test") is True
        assert downloader._is_youtube_url("youtu.be/test") is True
    
    def test_is_youtube_url_invalid(self):
        """無効URLテスト"""
        downloader = YouTubeDownloader()
        
        assert downloader._is_youtube_url("https://example.com/video") is False
        assert downloader._is_youtube_url("https://vimeo.com/123456") is False
        assert downloader._is_youtube_url("") is False
    
    def test_validate_url_valid(self):
        """有効URL検証のテスト"""
        downloader = YouTubeDownloader()
        
        assert downloader.validate_url("https://www.youtube.com/watch?v=test") is True
        assert downloader.validate_url("https://youtu.be/test") is True
    
    def test_validate_url_invalid(self):
        """無効URL検証のテスト"""
        downloader = YouTubeDownloader()
        
        assert downloader.validate_url("https://example.com/video") is False
        assert downloader.validate_url("") is False
        assert downloader.validate_url(None) is False
    
    def test_validate_url_whitespace(self):
        """空白文字を含むURL検証のテスト"""
        downloader = YouTubeDownloader()
        
        assert downloader.validate_url("  https://www.youtube.com/watch?v=test  ") is True
        assert downloader.validate_url("   ") is False
    
    @pytest.mark.asyncio
    async def test_get_video_info_empty_url(self):
        """空URLでの動画情報取得テスト"""
        downloader = YouTubeDownloader()
        
        result = await downloader.get_video_info("")
        assert result is None
        
        result = await downloader.get_video_info(None)
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_video_info_invalid_url(self):
        """無効URLでの動画情報取得テスト"""
        downloader = YouTubeDownloader()
        
        result = await downloader.get_video_info("https://example.com/video")
        assert result is None
    
    @pytest.mark.asyncio
    @patch('src.core.youtube_downloader.yt_dlp.YoutubeDL')
    async def test_get_video_info_success(self, mock_yt_dlp, mock_yt_dlp_info):
        """成功時の動画情報取得テスト"""
        downloader = YouTubeDownloader()
        
        # YoutubeDLのモック設定
        mock_ydl_instance = Mock()
        mock_yt_dlp.return_value.__enter__.return_value = mock_ydl_instance
        mock_ydl_instance.extract_info.return_value = mock_yt_dlp_info
        
        # asyncio.get_event_loop().run_in_executor をモック
        with patch('asyncio.get_event_loop') as mock_get_loop:
            mock_loop = Mock()
            mock_get_loop.return_value = mock_loop
            mock_loop.run_in_executor.return_value = asyncio.Future()
            mock_loop.run_in_executor.return_value.set_result(mock_yt_dlp_info)
            
            result = await downloader.get_video_info("https://www.youtube.com/watch?v=test")
        
        assert result is not None
        assert result.url == "https://www.youtube.com/watch?v=test"
        assert result.title == "Test Video Title"
        assert result.duration == 180
        assert result.channel == "Test Channel"
        assert result.audio_url == "https://example.com/audio.mp3"
        assert result.is_loaded is True
    
    @pytest.mark.asyncio
    @patch('src.core.youtube_downloader.yt_dlp.YoutubeDL')
    async def test_get_video_info_no_info(self, mock_yt_dlp):
        """情報取得失敗時のテスト"""
        downloader = YouTubeDownloader()
        
        # YoutubeDLのモック設定（None を返す）
        mock_ydl_instance = Mock()
        mock_yt_dlp.return_value.__enter__.return_value = mock_ydl_instance
        mock_ydl_instance.extract_info.return_value = None
        
        # asyncio.get_event_loop().run_in_executor をモック
        with patch('asyncio.get_event_loop') as mock_get_loop:
            mock_loop = Mock()
            mock_get_loop.return_value = mock_loop
            mock_loop.run_in_executor.return_value = asyncio.Future()
            mock_loop.run_in_executor.return_value.set_result(None)
            
            result = await downloader.get_video_info("https://www.youtube.com/watch?v=test")
        
        assert result is None
    
    @pytest.mark.asyncio
    @patch('src.core.youtube_downloader.yt_dlp.YoutubeDL')
    async def test_get_video_info_exception(self, mock_yt_dlp):
        """例外発生時のテスト"""
        downloader = YouTubeDownloader()
        
        # YoutubeDLのモック設定（例外を発生させる）
        mock_ydl_instance = Mock()
        mock_yt_dlp.return_value.__enter__.return_value = mock_ydl_instance
        mock_ydl_instance.extract_info.side_effect = Exception("Test error")
        
        # asyncio.get_event_loop().run_in_executor をモック
        with patch('asyncio.get_event_loop') as mock_get_loop:
            mock_loop = Mock()
            mock_get_loop.return_value = mock_loop
            mock_loop.run_in_executor.return_value = asyncio.Future()
            mock_loop.run_in_executor.return_value.set_exception(Exception("Test error"))
            
            result = await downloader.get_video_info("https://www.youtube.com/watch?v=test")
        
        assert result is None 