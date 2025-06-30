"""
メインアプリケーション
"""

import asyncio
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Header, Footer, Static
from textual.binding import Binding

from .widgets import PlaylistWidget, PlayerControlWidget
from .screens import URLInputScreen, DeleteConfirmScreen
from ..core import MediaPlayer, YouTubeDownloader


class YouTubePlayerApp(App):
    """メインアプリケーション"""
    
    CSS = """
    #main_container {
        height: 1fr;
    }
    
    #playlist_container {
        width: 1fr;
        border: solid $secondary;
    }
    
    #control_container {
        width: 40%;
        border: solid $accent;
        padding: 1;
    }
    
    #instruction_banner {
        dock: top;
        height: 3;
        background: $primary 20%;
        text-align: center;
        content-align: center middle;
        border: solid $primary;
    }
    
    CustomProgressBar {
        text-align: center;
        height: 1;
        margin: 1 0;
    }
    """
    
    BINDINGS = [
        Binding("a", "add_url", "URL追加"),
        Binding("space", "play_pause", "再生/一時停止"),
        Binding("n", "next_track", "次の曲"),
        Binding("p", "previous_track", "前の曲"),
        Binding("left", "seek_backward", "巻き戻し"),
        Binding("right", "seek_forward", "早送り"),
        Binding("d", "delete_current", "削除"),
        Binding("q", "quit", "終了"),
    ]
    
    def __init__(self):
        """アプリケーションを初期化"""
        super().__init__()
        self.title = "YouTube Audio Player"
        self.player = MediaPlayer()
        self.downloader = YouTubeDownloader()
        self.playlist_widget = None
        self.control_widget = None
        
        # 定期更新タスク
        self._update_task = None
        # URL処理中フラグ
        self._processing_urls = set()
    
    def compose(self) -> ComposeResult:
        """アプリケーションの構成"""
        yield Header()
        
        yield Static(
            "YouTube音楽プレイヤー | 'a'キーでURL追加 | プレイリストが空です", 
            id="instruction_banner"
        )
        
        with Horizontal(id="main_container"):
            with Container(id="playlist_container"):
                self.playlist_widget = PlaylistWidget(self.player)
                yield self.playlist_widget
            
            with Container(id="control_container"):
                self.control_widget = PlayerControlWidget(self.player)
                yield self.control_widget
        
        yield Footer()
    
    def on_mount(self):
        """アプリケーション起動時の処理"""
        self._start_update_loop()
        self._update_instruction_banner()
    
    def _start_update_loop(self):
        """定期更新ループを開始"""
        self._update_task = asyncio.create_task(self._update_loop())
    
    async def _update_loop(self):
        """定期的にプレイヤー状態を更新"""
        while True:
            if self.control_widget:
                self.control_widget.update_display()
            await asyncio.sleep(0.5)
    
    def _update_instruction_banner(self):
        """指示バナーを更新"""
        if hasattr(self, 'query_one'):
            try:
                banner = self.query_one("#instruction_banner")
                playlist_size = self.player.get_playlist_size()
                
                if playlist_size == 0:
                    banner.update("YouTube音楽プレイヤー | 'a'キーでURL追加 | プレイリストが空です")
                else:
                    banner.update(f"YouTube音楽プレイヤー | 'a'キーでURL追加 | {playlist_size}曲がプレイリストにあります")
            except:
                pass
    
    async def _handle_url_input(self, url: str):
        """URL入力処理のコールバック"""
        if not url:
            return
        
        # 既に処理中のURLかチェック
        if url in self._processing_urls:
            return
        
        # URL検証
        if not self.downloader.validate_url(url):
            return
        
        # 処理中URLリストに追加
        self._processing_urls.add(url)
        
        try:
            video_info = await self.downloader.get_video_info(url)
            
            if video_info and self.player.add_to_playlist(video_info):
                self.playlist_widget.update_playlist()
                self._update_instruction_banner()
            else:
                # バナーを元に戻す
                self._update_instruction_banner()
        except Exception as e:
            # バナーを元に戻す
            try:
                self._update_instruction_banner()
            except:
                pass
        finally:
            # 処理完了後に処理中URLリストから削除
            self._processing_urls.discard(url)
    
    def action_add_url(self):
        """URL追加アクション"""
        self.push_screen(URLInputScreen(self._handle_url_input))
    
    def action_play_pause(self):
        """再生/一時停止"""
        if self.player.is_playing:
            self.player.pause()
        else:
            if not self.player.get_current_video():
                self.player.play_current()
            else:
                self.player.pause()
        self.playlist_widget.update_playlist()
    
    def action_next_track(self):
        """次の曲"""
        if self.player.next_track():
            self.playlist_widget.update_playlist()
    
    def action_previous_track(self):
        """前の曲"""
        if self.player.previous_track():
            self.playlist_widget.update_playlist()
    
    def action_seek_forward(self):
        """早送り"""
        position = self.player.get_position()
        self.player.set_position(min(1.0, position + 0.05))
    
    def action_seek_backward(self):
        """巻き戻し"""
        position = self.player.get_position()
        self.player.set_position(max(0.0, position - 0.05))
    
    def action_delete_current(self):
        """現在の曲を削除"""
        if (self.player.playlist and 
            self.player.current_index < len(self.player.playlist)):
            video = self.player.playlist[self.player.current_index]
            self.push_screen(DeleteConfirmScreen(video.title, self._handle_delete_confirmation))
    
    async def _handle_delete_confirmation(self, confirmed: bool):
        """削除確認のコールバック"""
        if confirmed:
            if self.player.remove_from_playlist(self.player.current_index):
                self.playlist_widget.update_playlist()
                self._update_instruction_banner()
    
    async def on_unmount(self):
        """アプリケーション終了時の処理"""
        if self._update_task:
            self._update_task.cancel()
        self.player.stop() 