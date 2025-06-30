#!/usr/bin/env python3
"""
YouTube Terminal Player - TUIベースのYouTube音楽プレイヤー
"""

import asyncio
import threading
import time
from pathlib import Path
from typing import Optional, List, Dict, Any
from urllib.parse import urlparse, parse_qs

import yt_dlp
import vlc
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, Center, Middle
from textual.widgets import (
    Header, Footer, Input, Button, Static, ProgressBar, 
    ListView, ListItem, Label, DataTable
)
from textual.binding import Binding
from textual.reactive import reactive
from textual.message import Message
from textual.screen import ModalScreen


class VideoInfo:
    """動画情報を管理するクラス"""
    
    def __init__(self, url: str, title: str = "", duration: int = 0, 
                 channel: str = "", audio_url: str = ""):
        self.url = url
        self.title = title
        self.duration = duration
        self.channel = channel
        self.audio_url = audio_url
        self.is_loaded = False


class MediaPlayer:
    """VLCベースのメディアプレイヤー"""
    
    def __init__(self):
        self.instance = vlc.Instance('--intf=dummy', '--no-video')
        self.player = self.instance.media_player_new()
        self.current_video: Optional[VideoInfo] = None
        self.playlist: List[VideoInfo] = []
        self.current_index = 0
        self.is_playing = False
        self.volume = 70
        
        # VLCイベントマネージャー
        self.event_manager = self.player.event_manager()
        self.event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, self._on_end_reached)
        
    def _on_end_reached(self, event):
        """再生終了時の処理"""
        self.next_track()
    
    def add_to_playlist(self, video: VideoInfo):
        """プレイリストに動画を追加"""
        self.playlist.append(video)
    
    def remove_from_playlist(self, index: int):
        """プレイリストから動画を削除"""
        if 0 <= index < len(self.playlist):
            self.playlist.pop(index)
            if self.current_index >= len(self.playlist) and self.playlist:
                self.current_index = len(self.playlist) - 1
    
    def play_current(self):
        """現在選択されている動画を再生"""
        if not self.playlist or self.current_index >= len(self.playlist):
            return False
            
        video = self.playlist[self.current_index]
        if not video.audio_url:
            return False
            
        media = self.instance.media_new(video.audio_url)
        self.player.set_media(media)
        self.player.play()
        self.current_video = video
        self.is_playing = True
        self.player.audio_set_volume(self.volume)
        return True
    
    def pause(self):
        """一時停止"""
        self.player.pause()
        self.is_playing = not self.is_playing
    
    def stop(self):
        """停止"""
        self.player.stop()
        self.is_playing = False
    
    def next_track(self):
        """次の曲"""
        if self.current_index < len(self.playlist) - 1:
            self.current_index += 1
            return self.play_current()
        return False
    
    def previous_track(self):
        """前の曲"""
        if self.current_index > 0:
            self.current_index -= 1
            return self.play_current()
        return False
    
    def set_volume(self, volume: int):
        """音量設定（0-100）"""
        self.volume = max(0, min(100, volume))
        self.player.audio_set_volume(self.volume)
    
    def get_position(self) -> float:
        """再生位置を取得（0.0-1.0）"""
        return self.player.get_position()
    
    def set_position(self, position: float):
        """再生位置を設定（0.0-1.0）"""
        self.player.set_position(position)
    
    def get_time(self) -> int:
        """現在の再生時間（ミリ秒）"""
        return self.player.get_time()
    
    def get_length(self) -> int:
        """総再生時間（ミリ秒）"""
        return self.player.get_length()


class YouTubeDownloader:
    """YouTube動画情報取得・音声URL抽出"""
    
    def __init__(self):
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
        }
    
    async def get_video_info(self, url: str) -> Optional[VideoInfo]:
        """YouTube URLから動画情報を取得"""
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = await asyncio.get_event_loop().run_in_executor(
                    None, ydl.extract_info, url, False
                )
                
                if not info:
                    return None
                
                video = VideoInfo(
                    url=url,
                    title=info.get('title', 'Unknown Title'),
                    duration=info.get('duration', 0),
                    channel=info.get('uploader', 'Unknown Channel'),
                    audio_url=info.get('url', '')
                )
                video.is_loaded = True
                return video
                
        except Exception as e:
            print(f"Error extracting video info: {e}")
            return None


class PlaylistWidget(ListView):
    """プレイリスト表示ウィジェット"""
    
    def __init__(self, player: MediaPlayer):
        super().__init__()
        self.player = player
        self.border_title = "プレイリスト"
    
    def update_playlist(self):
        """プレイリストを更新"""
        self.clear()
        for i, video in enumerate(self.player.playlist):
            prefix = "▶ " if i == self.player.current_index else "  "
            duration_str = f"{video.duration // 60}:{video.duration % 60:02d}" if video.duration else "00:00"
            item_text = f"{prefix}{video.title} - {video.channel} [{duration_str}]"
            self.append(ListItem(Label(item_text)))


class URLInputScreen(ModalScreen):
    """URL入力用のモーダルスクリーン"""
    
    CSS = """
    URLInputScreen {
        align: center middle;
    }
    
    #url_input_dialog {
        width: 80%;
        height: 15;
        border: thick $primary 80%;
        background: $surface;
        padding: 1;
    }
    
    #url_input_field {
        width: 1fr;
        margin: 1 0;
    }
    
    #button_container {
        height: 3;
        align: center middle;
    }
    
    #add_button, #cancel_button {
        margin: 0 1;
    }
    """
    
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        self.url_input = None
    
    def compose(self) -> ComposeResult:
        with Container(id="url_input_dialog"):
            yield Static("YouTube URLを入力してください:", id="title")
            self.url_input = Input(
                placeholder="https://www.youtube.com/watch?v=...",
                id="url_input_field"
            )
            yield self.url_input
            
            with Horizontal(id="button_container"):
                yield Button("追加", variant="primary", id="add_button")
                yield Button("キャンセル", variant="default", id="cancel_button")
    
    def on_mount(self):
        """モーダル表示時にフォーカス設定"""
        self.url_input.focus()
    
    async def on_button_pressed(self, event: Button.Pressed):
        """ボタン押下時の処理"""
        if event.button.id == "add_button":
            url = self.url_input.value.strip()
            if url:
                await self.callback(url)
            self.dismiss()
        elif event.button.id == "cancel_button":
            self.dismiss()
    
    async def on_input_submitted(self, event: Input.Submitted):
        """Enter キー押下時の処理"""
        if event.input == self.url_input:
            url = self.url_input.value.strip()
            if url:
                await self.callback(url)
            self.dismiss()
    
    def on_key(self, event):
        """ESCキーでキャンセル"""
        if event.key == "escape":
            self.dismiss()


class PlayerControlWidget(Container):
    """プレイヤーコントロールウィジェット"""
    
    def __init__(self, player: MediaPlayer):
        super().__init__()
        self.player = player
        self.progress_bar = ProgressBar(show_eta=False)
        self.time_label = Static("00:00 / 00:00")
        self.volume_label = Static(f"音量: {player.volume}%")
        self.status_label = Static("停止中")
        
    def compose(self) -> ComposeResult:
        with Vertical():
            yield self.status_label
            yield self.progress_bar
            yield self.time_label
            yield self.volume_label
    
    def update_display(self):
        """表示を更新"""
        if self.player.current_video:
            self.status_label.update(f"再生中: {self.player.current_video.title}")
            
            current_time = self.player.get_time() // 1000
            total_time = self.player.get_length() // 1000
            
            if total_time > 0:
                progress = current_time / total_time * 100
                self.progress_bar.update(progress=progress)
                
                current_str = f"{current_time // 60}:{current_time % 60:02d}"
                total_str = f"{total_time // 60}:{total_time % 60:02d}"
                self.time_label.update(f"{current_str} / {total_str}")
            else:
                self.progress_bar.update(progress=0)
                self.time_label.update("00:00 / 00:00")
        else:
            self.status_label.update("停止中")
            self.progress_bar.update(progress=0)
            self.time_label.update("00:00 / 00:00")
        
        self.volume_label.update(f"音量: {self.player.volume}%")


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
    }
    
    #instruction_banner {
        dock: top;
        height: 3;
        background: $primary 20%;
        text-align: center;
        content-align: center middle;
        border: solid $primary;
    }
    """
    
    BINDINGS = [
        Binding("a", "add_url", "URL追加"),
        Binding("space", "play_pause", "再生/一時停止"),
        Binding("n", "next_track", "次の曲"),
        Binding("p", "previous_track", "前の曲"),
        Binding("up", "volume_up", "音量+"),
        Binding("down", "volume_down", "音量-"),
        Binding("left", "seek_backward", "巻き戻し"),
        Binding("right", "seek_forward", "早送り"),
        Binding("d", "delete_current", "削除"),
        Binding("q", "quit", "終了"),
    ]
    
    def __init__(self):
        super().__init__()
        self.title = "YouTube Terminal Player"
        self.player = MediaPlayer()
        self.downloader = YouTubeDownloader()
        self.playlist_widget = None
        self.control_widget = None
        
        # 定期更新タスク
        self._update_task = None
    
    def compose(self) -> ComposeResult:
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
                if len(self.player.playlist) == 0:
                    banner.update("YouTube音楽プレイヤー | 'a'キーでURL追加 | プレイリストが空です")
                else:
                    count = len(self.player.playlist)
                    banner.update(f"YouTube音楽プレイヤー | 'a'キーでURL追加 | {count}曲がプレイリストにあります")
            except:
                pass
    
    async def _handle_url_input(self, url: str):
        """URL入力処理のコールバック"""
        if not url:
            return
        
        # YouTube URLの簡単な検証
        if 'youtube.com' not in url and 'youtu.be' not in url:
            self.notify("有効なYouTube URLを入力してください", severity="error")
            return
        
        self.notify("動画情報を取得中...")
        video_info = await self.downloader.get_video_info(url)
        
        if video_info:
            self.player.add_to_playlist(video_info)
            self.playlist_widget.update_playlist()
            self._update_instruction_banner()
            self.notify(f"追加されました: {video_info.title}")
        else:
            self.notify("動画情報の取得に失敗しました", severity="error")
    
    def action_add_url(self):
        """URL追加アクション"""
        self.push_screen(URLInputScreen(self._handle_url_input))
    
    def action_play_pause(self):
        """再生/一時停止"""
        if self.player.is_playing:
            self.player.pause()
        else:
            if not self.player.current_video:
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
    
    def action_volume_up(self):
        """音量を上げる"""
        self.player.set_volume(self.player.volume + 5)
    
    def action_volume_down(self):
        """音量を下げる"""
        self.player.set_volume(self.player.volume - 5)
    
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
        if self.player.playlist and self.player.current_index < len(self.player.playlist):
            self.player.remove_from_playlist(self.player.current_index)
            self.playlist_widget.update_playlist()
            self._update_instruction_banner()
    
    async def on_unmount(self):
        """アプリケーション終了時の処理"""
        if self._update_task:
            self._update_task.cancel()
        self.player.stop()


def main():
    """メイン関数"""
    try:
        import vlc
    except ImportError:
        print("エラー: VLCライブラリが見つかりません。")
        print("システムにVLCをインストールしてください:")
        print("  brew install vlc  # Homebrewを使用する場合")
        print("  または https://www.videolan.org/vlc/ からダウンロード")
        return 1
    
    app = YouTubePlayerApp()
    try:
        app.run()
    except KeyboardInterrupt:
        print("\nアプリケーションを終了します...")
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 