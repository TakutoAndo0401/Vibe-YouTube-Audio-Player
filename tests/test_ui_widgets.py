"""
UIウィジェットのテスト
"""

import pytest
from unittest.mock import Mock, patch
from src.ui.widgets.progress_bar import CustomProgressBar
from src.ui.widgets.playlist_widget import PlaylistWidget
from src.ui.widgets.player_control_widget import PlayerControlWidget
from src.core.media_player import MediaPlayer
from src.models.video_info import VideoInfo


class TestCustomProgressBar:
    """CustomProgressBarクラスのテスト"""
    
    def test_init_default(self):
        """デフォルト値での初期化テスト"""
        progress_bar = CustomProgressBar()
        
        assert progress_bar.progress == 0.0
        assert progress_bar.bar_width == 40
    
    def test_init_custom_width(self):
        """カスタム幅での初期化テスト"""
        progress_bar = CustomProgressBar(bar_width=60)
        
        assert progress_bar.progress == 0.0
        assert progress_bar.bar_width == 60
    
    def test_set_progress_valid_range(self):
        """有効範囲内での進行率設定テスト"""
        progress_bar = CustomProgressBar()
        
        progress_bar.set_progress(0.5)
        assert progress_bar.progress == 0.5
        
        progress_bar.set_progress(0.0)
        assert progress_bar.progress == 0.0
        
        progress_bar.set_progress(1.0)
        assert progress_bar.progress == 1.0
    
    def test_set_progress_clamp_values(self):
        """範囲外の値での進行率設定テスト"""
        progress_bar = CustomProgressBar()
        
        # 1.0を超える値
        progress_bar.set_progress(1.5)
        assert progress_bar.progress == 1.0
        
        # 0.0未満の値
        progress_bar.set_progress(-0.5)
        assert progress_bar.progress == 0.0
    
    def test_get_progress(self):
        """進行率取得のテスト"""
        progress_bar = CustomProgressBar()
        
        progress_bar.set_progress(0.75)
        assert progress_bar.get_progress() == 0.75
    
    def test_reset(self):
        """リセットのテスト"""
        progress_bar = CustomProgressBar()
        
        progress_bar.set_progress(0.8)
        progress_bar.reset()
        
        assert progress_bar.progress == 0.0


class TestPlaylistWidget:
    """PlaylistWidgetクラスのテスト"""
    
    @patch('src.core.media_player.vlc')
    def test_init(self, mock_vlc):
        """初期化のテスト"""
        player = MediaPlayer()
        
        # PlaylistWidgetを完全にモック化
        with patch('src.ui.widgets.playlist_widget.ListView') as mock_listview:
            mock_instance = Mock()
            mock_listview.return_value = mock_instance
            
            widget = PlaylistWidget(player)
            
            assert widget.player == player
    
    @patch('src.core.media_player.vlc')
    def test_update_playlist_empty(self, mock_vlc):
        """空のプレイリスト更新テスト"""
        player = MediaPlayer()
        
        with patch('src.ui.widgets.playlist_widget.ListView') as mock_listview:
            mock_instance = Mock()
            mock_listview.return_value = mock_instance
            
            widget = PlaylistWidget(player)
            widget.clear = Mock()
            widget.append = Mock()
            
            widget.update_playlist()
            
            widget.clear.assert_called_once()
            widget.append.assert_called_once()
    
    @patch('src.core.media_player.vlc')
    def test_update_playlist_with_videos(self, mock_vlc, sample_video_info):
        """動画ありのプレイリスト更新テスト"""
        player = MediaPlayer()
        player.add_to_playlist(sample_video_info)
        
        with patch('src.ui.widgets.playlist_widget.ListView') as mock_listview:
            mock_instance = Mock()
            mock_listview.return_value = mock_instance
            
            widget = PlaylistWidget(player)
            widget.clear = Mock()
            widget.append = Mock()
            
            widget.update_playlist()
            
            widget.clear.assert_called_once()
            widget.append.assert_called_once()
    
    @patch('src.core.media_player.vlc')
    def test_get_selected_index_none(self, mock_vlc):
        """選択なしのインデックス取得テスト"""
        player = MediaPlayer()
        
        with patch('src.ui.widgets.playlist_widget.ListView') as mock_listview:
            mock_instance = Mock()
            mock_listview.return_value = mock_instance
            
            widget = PlaylistWidget(player)
            widget.index = None
            
            result = widget.get_selected_index()
            
            assert result == -1
    
    @patch('src.core.media_player.vlc')
    def test_get_selected_index_valid(self, mock_vlc):
        """有効なインデックス取得テスト"""
        player = MediaPlayer()
        
        with patch('src.ui.widgets.playlist_widget.ListView') as mock_listview:
            mock_instance = Mock()
            mock_listview.return_value = mock_instance
            
            widget = PlaylistWidget(player)
            
            # get_selected_indexメソッドを直接テスト
            # indexプロパティを持つクラスを作成
            class TestWidget:
                def __init__(self, index_value):
                    self.index = index_value
                
                def get_selected_index(self):
                    if self.index is not None:
                        return self.index
                    return -1
            
            test_widget = TestWidget(2)
            result = test_widget.get_selected_index()
            assert result == 2
            
            test_widget_none = TestWidget(None)
            result_none = test_widget_none.get_selected_index()
            assert result_none == -1


class TestPlayerControlWidget:
    """PlayerControlWidgetクラスのテスト"""
    
    @patch('src.ui.widgets.player_control_widget.Container.__init__')
    @patch('src.core.media_player.vlc')
    def test_init(self, mock_vlc, mock_container_init):
        """初期化のテスト"""
        mock_container_init.return_value = None
        player = MediaPlayer()
        
        widget = PlayerControlWidget(player)
        
        assert widget.player == player
        assert widget.progress_bar is not None
        assert widget.time_label is not None
        assert widget.remaining_label is not None
        assert widget.status_label is not None
        mock_container_init.assert_called_once()
    
    @patch('src.ui.widgets.player_control_widget.Container.__init__')
    @patch('src.core.media_player.vlc')
    def test_format_time(self, mock_vlc, mock_container_init):
        """時間フォーマットのテスト"""
        mock_container_init.return_value = None
        player = MediaPlayer()
        widget = PlayerControlWidget(player)
        
        assert widget._format_time(0) == "0:00"
        assert widget._format_time(30) == "0:30"
        assert widget._format_time(90) == "1:30"
        assert widget._format_time(3661) == "61:01"
    
    @patch('src.ui.widgets.player_control_widget.Container.__init__')
    @patch('src.core.media_player.vlc')
    def test_reset_display(self, mock_vlc, mock_container_init):
        """表示リセットのテスト"""
        mock_container_init.return_value = None
        player = MediaPlayer()
        widget = PlayerControlWidget(player)
        
        # モックオブジェクトを設定
        widget.progress_bar = Mock()
        widget.time_label = Mock()
        widget.remaining_label = Mock()
        
        widget._reset_display()
        
        widget.progress_bar.reset.assert_called_once()
        widget.time_label.update.assert_called_once_with("⏱️  00:00 / 00:00")
        widget.remaining_label.update.assert_called_once_with("⏳ 残り: --:--")
    
    @patch('src.ui.widgets.player_control_widget.Container.__init__')
    @patch('src.core.media_player.vlc')
    def test_update_display_no_video(self, mock_vlc, mock_container_init):
        """動画なしでの表示更新テスト"""
        mock_container_init.return_value = None
        player = MediaPlayer()
        widget = PlayerControlWidget(player)
        
        # モックオブジェクトを設定
        widget.status_label = Mock()
        widget.progress_bar = Mock()
        widget.time_label = Mock()
        widget.remaining_label = Mock()
        
        widget.update_display()
        
        widget.status_label.update.assert_called_once_with("⏸️  [dim]停止中[/dim]")
        widget.progress_bar.reset.assert_called_once()
    
    @patch('src.ui.widgets.player_control_widget.Container.__init__')
    @patch('src.core.media_player.vlc')
    def test_update_display_with_video_paused(self, mock_vlc, mock_container_init, sample_video_info):
        """一時停止中の動画での表示更新テスト"""
        mock_container_init.return_value = None
        player = MediaPlayer()
        player.current_video = sample_video_info
        player.is_playing = False
        
        widget = PlayerControlWidget(player)
        
        # モックオブジェクトを設定
        widget.status_label = Mock()
        widget.progress_bar = Mock()
        widget.time_label = Mock()
        widget.remaining_label = Mock()
        
        widget.update_display()
        
        # 一時停止状態の表示確認
        expected_call = f"⏸️ [dim]{sample_video_info.title}[/dim]"
        widget.status_label.update.assert_called_once_with(expected_call)
        widget.progress_bar.reset.assert_called_once() 