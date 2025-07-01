"""
メインアプリケーションの統合テスト
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from src.ui.app import YouTubePlayerApp
from src.models.video_info import VideoInfo


class TestYouTubePlayerAppIntegration:
    """YouTubePlayerAppの統合テスト"""
    
    @patch('src.ui.app.MediaPlayer')
    @patch('src.ui.app.YouTubeDownloader')
    def test_init(self, mock_downloader_class, mock_player_class):
        """初期化のテスト"""
        app = YouTubePlayerApp()
        
        assert app.title == "YouTube Audio Player"
        assert app._processing_urls == set()
        mock_player_class.assert_called_once()
        mock_downloader_class.assert_called_once()
    
    @patch('src.ui.app.MediaPlayer')
    @patch('src.ui.app.YouTubeDownloader')
    def test_update_instruction_banner_empty_playlist(self, mock_downloader_class, mock_player_class):
        """空のプレイリストでのバナー更新テスト"""
        app = YouTubePlayerApp()
        
        # モックプレイヤーの設定
        mock_player = Mock()
        mock_player.get_playlist_size.return_value = 0
        app.player = mock_player
        
        # query_oneのモック設定
        mock_banner = Mock()
        app.query_one = Mock(return_value=mock_banner)
        
        app._update_instruction_banner()
        
        expected_text = "YouTube音楽プレイヤー | 'a'キーでURL追加 | プレイリストが空です"
        mock_banner.update.assert_called_once_with(expected_text)
    
    @patch('src.ui.app.MediaPlayer')
    @patch('src.ui.app.YouTubeDownloader')
    def test_update_instruction_banner_with_videos(self, mock_downloader_class, mock_player_class):
        """動画ありのプレイリストでのバナー更新テスト"""
        app = YouTubePlayerApp()
        
        # モックプレイヤーの設定
        mock_player = Mock()
        mock_player.get_playlist_size.return_value = 3
        app.player = mock_player
        
        # query_oneのモック設定
        mock_banner = Mock()
        app.query_one = Mock(return_value=mock_banner)
        
        app._update_instruction_banner()
        
        expected_text = "YouTube音楽プレイヤー | 'a'キーでURL追加 | 3曲がプレイリストにあります"
        mock_banner.update.assert_called_once_with(expected_text)
    
    @patch('src.ui.app.MediaPlayer')
    @patch('src.ui.app.YouTubeDownloader')
    def test_update_instruction_banner_exception_handling(self, mock_downloader_class, mock_player_class):
        """バナー更新時の例外処理テスト"""
        app = YouTubePlayerApp()
        
        # query_oneで例外を発生させる
        app.query_one = Mock(side_effect=Exception("Test error"))
        
        # 例外が発生しても処理が継続することを確認
        app._update_instruction_banner()  # 例外が発生しないことを確認
    
    @pytest.mark.asyncio
    @patch('src.ui.app.MediaPlayer')
    @patch('src.ui.app.YouTubeDownloader')
    async def test_handle_url_input_empty_url(self, mock_downloader_class, mock_player_class):
        """空URL処理のテスト"""
        app = YouTubePlayerApp()
        
        with pytest.raises(ValueError, match="URLが入力されていません"):
            await app._handle_url_input("")
    
    @pytest.mark.asyncio
    @patch('src.ui.app.MediaPlayer')
    @patch('src.ui.app.YouTubeDownloader')
    async def test_handle_url_input_invalid_url(self, mock_downloader_class, mock_player_class):
        """無効URL処理のテスト"""
        app = YouTubePlayerApp()
        
        # モックダウンローダーの設定
        mock_downloader = Mock()
        mock_downloader.validate_url.return_value = False
        app.downloader = mock_downloader
        
        with pytest.raises(ValueError, match="無効なYouTube URLです"):
            await app._handle_url_input("https://example.com/invalid")
        
        # validate_urlが呼ばれることを確認
        mock_downloader.validate_url.assert_called_once_with("https://example.com/invalid")
    
    @pytest.mark.asyncio
    @patch('src.ui.app.MediaPlayer')
    @patch('src.ui.app.YouTubeDownloader')
    async def test_handle_url_input_duplicate_processing(self, mock_downloader_class, mock_player_class):
        """重複処理防止のテスト"""
        app = YouTubePlayerApp()
        
        url = "https://www.youtube.com/watch?v=test"
        
        # 既に処理中URLリストに追加
        app._processing_urls.add(url)
        
        # モックダウンローダーの設定
        mock_downloader = Mock()
        app.downloader = mock_downloader
        
        with pytest.raises(ValueError, match="このURLは既に処理中です"):
            await app._handle_url_input(url)
        
        # validate_urlが呼ばれないことを確認（重複処理が防止される）
        mock_downloader.validate_url.assert_not_called()
    
    @pytest.mark.asyncio
    @patch('src.ui.app.MediaPlayer')
    @patch('src.ui.app.YouTubeDownloader')
    async def test_handle_url_input_successful_processing(self, mock_downloader_class, mock_player_class):
        """成功時のURL入力処理テスト"""
        app = YouTubePlayerApp()
        
        url = "https://www.youtube.com/watch?v=test"
        
        # モックビデオ情報を作成
        mock_video_info = VideoInfo(
            url=url,
            title="Test Video",
            duration=180,
            channel="Test Channel",
            audio_url="https://example.com/audio.mp3"
        )
        mock_video_info.is_loaded = True
        
        # モックダウンローダーの設定
        mock_downloader = Mock()
        mock_downloader.validate_url.return_value = True
        mock_downloader.get_video_info = AsyncMock(return_value=mock_video_info)
        app.downloader = mock_downloader
        
        # モックプレイヤーの設定
        mock_player = Mock()
        mock_player.add_to_playlist.return_value = True
        app.player = mock_player
        
        # モックプレイリストウィジェットの設定
        mock_playlist_widget = Mock()
        app.playlist_widget = mock_playlist_widget
        
        # _update_instruction_bannerをモック化
        app._update_instruction_banner = Mock()
        
        await app._handle_url_input(url)
        
        # URL検証が呼ばれることを確認
        mock_downloader.validate_url.assert_called_once_with(url)
        # 動画情報取得が呼ばれることを確認
        mock_downloader.get_video_info.assert_called_once_with(url)
        # プレイリストに追加されることを確認
        mock_player.add_to_playlist.assert_called_once_with(mock_video_info)
        # プレイリストウィジェットが更新されることを確認
        mock_playlist_widget.update_playlist.assert_called_once()
        # バナーが更新されることを確認
        app._update_instruction_banner.assert_called_once()
        # 処理完了後にURLが処理中リストから削除されることを確認
        assert url not in app._processing_urls
    
    @pytest.mark.asyncio
    @patch('src.ui.app.MediaPlayer')
    @patch('src.ui.app.YouTubeDownloader')
    async def test_handle_url_input_failed_processing(self, mock_downloader_class, mock_player_class):
        """失敗時のURL入力処理テスト"""
        app = YouTubePlayerApp()
        
        url = "https://www.youtube.com/watch?v=test"
        
        # モックダウンローダーの設定（None を返す）
        mock_downloader = Mock()
        mock_downloader.validate_url.return_value = True
        mock_downloader.get_video_info = AsyncMock(return_value=None)
        app.downloader = mock_downloader
        
        # _update_instruction_bannerをモック化
        app._update_instruction_banner = Mock()
        
        with pytest.raises(ValueError, match="動画情報の取得に失敗しました"):
            await app._handle_url_input(url)
        
        # 処理完了後にURLが処理中リストから削除されることを確認
        assert url not in app._processing_urls
    
    @pytest.mark.asyncio
    @patch('src.ui.app.MediaPlayer')
    @patch('src.ui.app.YouTubeDownloader')
    async def test_handle_url_input_exception_handling(self, mock_downloader_class, mock_player_class):
        """例外発生時のURL入力処理テスト"""
        app = YouTubePlayerApp()
        
        url = "https://www.youtube.com/watch?v=test"
        
        # モックダウンローダーの設定（例外を発生させる）
        mock_downloader = Mock()
        mock_downloader.validate_url.return_value = True
        mock_downloader.get_video_info = AsyncMock(side_effect=Exception("Test error"))
        app.downloader = mock_downloader
        
        # _update_instruction_bannerをモック化
        app._update_instruction_banner = Mock()
        
        with pytest.raises(ValueError, match="処理中にエラーが発生しました: Test error"):
            await app._handle_url_input(url)
        
        # 処理完了後にURLが処理中リストから削除されることを確認
        assert url not in app._processing_urls
    
    @patch('src.ui.app.MediaPlayer')
    @patch('src.ui.app.YouTubeDownloader')
    def test_action_add_url(self, mock_downloader_class, mock_player_class):
        """URL追加アクションのテスト"""
        app = YouTubePlayerApp()
        
        # push_screenをモック化
        app.push_screen = Mock()
        
        app.action_add_url()
        
        # URLInputScreenがプッシュされることを確認
        app.push_screen.assert_called_once()
        # 引数がURLInputScreenのインスタンスであることを確認
        args = app.push_screen.call_args[0]
        assert len(args) == 1
        # コールバックが設定されていることを確認
        assert hasattr(args[0], 'callback')
    
    @patch('src.ui.app.MediaPlayer')
    @patch('src.ui.app.YouTubeDownloader')
    def test_action_play_pause_not_playing(self, mock_downloader_class, mock_player_class):
        """再生/一時停止アクション（停止中）のテスト"""
        app = YouTubePlayerApp()
        
        # モックプレイヤーの設定
        mock_player = Mock()
        mock_player.is_playing = False
        mock_player.get_current_video.return_value = None
        app.player = mock_player
        
        # モックプレイリストウィジェットの設定
        mock_playlist_widget = Mock()
        app.playlist_widget = mock_playlist_widget
        
        app.action_play_pause()
        
        # play_currentが呼ばれることを確認
        mock_player.play_current.assert_called_once()
        # プレイリストウィジェットが更新されることを確認
        mock_playlist_widget.update_playlist.assert_called_once()
    
    @patch('src.ui.app.MediaPlayer')
    @patch('src.ui.app.YouTubeDownloader')
    def test_action_play_pause_playing(self, mock_downloader_class, mock_player_class):
        """再生/一時停止アクション（再生中）のテスト"""
        app = YouTubePlayerApp()
        
        # モックプレイヤーの設定
        mock_player = Mock()
        mock_player.is_playing = True
        app.player = mock_player
        
        # モックプレイリストウィジェットの設定
        mock_playlist_widget = Mock()
        app.playlist_widget = mock_playlist_widget
        
        app.action_play_pause()
        
        # pauseが呼ばれることを確認
        mock_player.pause.assert_called_once()
        # プレイリストウィジェットが更新されることを確認
        mock_playlist_widget.update_playlist.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('src.ui.app.MediaPlayer')
    @patch('src.ui.app.YouTubeDownloader')
    async def test_handle_delete_confirmation_confirmed(self, mock_downloader_class, mock_player_class):
        """削除確認（確認済み）のテスト"""
        app = YouTubePlayerApp()
        
        # モックプレイヤーの設定
        mock_player = Mock()
        mock_player.current_index = 0
        mock_player.remove_from_playlist.return_value = True
        app.player = mock_player
        
        # モックプレイリストウィジェットの設定
        mock_playlist_widget = Mock()
        app.playlist_widget = mock_playlist_widget
        
        # _update_instruction_bannerをモック化
        app._update_instruction_banner = Mock()
        
        await app._handle_delete_confirmation(True)
        
        # remove_from_playlistが呼ばれることを確認
        mock_player.remove_from_playlist.assert_called_once_with(0)
        # プレイリストウィジェットが更新されることを確認
        mock_playlist_widget.update_playlist.assert_called_once()
        # バナーが更新されることを確認
        app._update_instruction_banner.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('src.ui.app.MediaPlayer')
    @patch('src.ui.app.YouTubeDownloader')
    async def test_handle_delete_confirmation_cancelled(self, mock_downloader_class, mock_player_class):
        """削除確認（キャンセル）のテスト"""
        app = YouTubePlayerApp()
        
        # モックプレイヤーの設定
        mock_player = Mock()
        app.player = mock_player
        
        await app._handle_delete_confirmation(False)
        
        # remove_from_playlistが呼ばれないことを確認
        mock_player.remove_from_playlist.assert_not_called()
    
    @pytest.mark.asyncio
    @patch('src.ui.app.asyncio.create_task')
    @patch('src.ui.app.MediaPlayer')
    @patch('src.ui.app.YouTubeDownloader')
    async def test_start_update_loop(self, mock_downloader_class, mock_player_class, mock_create_task):
        """更新ループ開始のテスト"""
        app = YouTubePlayerApp()
        
        app._start_update_loop()
        
        # asyncio.create_taskが呼ばれることを確認
        mock_create_task.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('src.ui.app.asyncio.sleep', new_callable=AsyncMock)
    @patch('src.ui.app.MediaPlayer')
    @patch('src.ui.app.YouTubeDownloader')
    async def test_update_loop_iteration(self, mock_downloader_class, mock_player_class, mock_sleep):
        """更新ループの1回の実行テスト"""
        app = YouTubePlayerApp()
        
        # モックコントロールウィジェットの設定
        mock_control_widget = Mock()
        app.control_widget = mock_control_widget
        
        # 1回だけ実行するためにsleepで例外を発生させる
        mock_sleep.side_effect = Exception("Stop loop")
        
        try:
            await app._update_loop()
        except Exception:
            pass  # 例外を無視
        
        # コントロールウィジェットの更新が呼ばれることを確認
        mock_control_widget.update_display.assert_called_once()
        # sleepが呼ばれることを確認
        mock_sleep.assert_called_once_with(0.5) 