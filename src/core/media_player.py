"""
VLCベースのメディアプレイヤー
"""

import vlc
from typing import Optional, List, Callable
from ..models.video_info import VideoInfo


class MediaPlayer:
    """VLCベースのメディアプレイヤー"""
    
    def __init__(self):
        """メディアプレイヤーを初期化"""
        # VLCのログ出力を完全に抑制
        self.instance = vlc.Instance('--intf=dummy', '--no-video', '--quiet', '--no-sout-all', '--sout-keep')
        self.player = self.instance.media_player_new()
        self.current_video: Optional[VideoInfo] = None
        self.playlist: List[VideoInfo] = []
        self.current_index = 0
        self.is_playing = False
        
        # コールバック関数
        self._on_track_end_callback: Optional[Callable] = None
        
        # VLCイベントマネージャー
        self.event_manager = self.player.event_manager()
        self.event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, self._on_end_reached)
    
    def set_on_track_end_callback(self, callback: Callable):
        """曲終了時のコールバック関数を設定"""
        self._on_track_end_callback = callback
        
    def _on_end_reached(self, event):
        """再生終了時の処理"""
        if self._on_track_end_callback:
            self._on_track_end_callback()
        else:
            self.next_track()
    
    def add_to_playlist(self, video: VideoInfo) -> bool:
        """
        プレイリストに動画を追加
        
        Args:
            video: 追加する動画情報
            
        Returns:
            追加成功時True
        """
        if not video or not video.is_valid():
            return False
            
        self.playlist.append(video)
        return True
    
    def remove_from_playlist(self, index: int) -> bool:
        """
        プレイリストから動画を削除
        
        Args:
            index: 削除するインデックス
            
        Returns:
            削除成功時True
        """
        if not (0 <= index < len(self.playlist)):
            return False
            
        self.playlist.pop(index)
        
        # 現在のインデックスを調整
        if self.current_index >= len(self.playlist) and self.playlist:
            self.current_index = len(self.playlist) - 1
        elif not self.playlist:
            self.current_index = 0
            self.current_video = None
            self.is_playing = False
            
        return True
    
    def play_current(self) -> bool:
        """
        現在選択されている動画を再生
        
        Returns:
            再生開始成功時True
        """
        if not self.playlist or self.current_index >= len(self.playlist):
            return False
            
        video = self.playlist[self.current_index]
        if not video.audio_url:
            return False
            
        try:
            media = self.instance.media_new(video.audio_url)
            self.player.set_media(media)
            self.player.play()
            self.current_video = video
            self.is_playing = True
            return True
        except Exception:
            return False
    
    def pause(self) -> bool:
        """
        一時停止/再開
        
        Returns:
            操作成功時True
        """
        try:
            self.player.pause()
            self.is_playing = not self.is_playing
            return True
        except Exception:
            return False
    
    def stop(self) -> bool:
        """
        停止
        
        Returns:
            停止成功時True
        """
        try:
            self.player.stop()
            self.is_playing = False
            return True
        except Exception:
            return False
    
    def next_track(self) -> bool:
        """
        次の曲
        
        Returns:
            次の曲再生成功時True
        """
        if self.current_index < len(self.playlist) - 1:
            self.current_index += 1
            return self.play_current()
        return False
    
    def previous_track(self) -> bool:
        """
        前の曲
        
        Returns:
            前の曲再生成功時True
        """
        if self.current_index > 0:
            self.current_index -= 1
            return self.play_current()
        return False
    
    def get_position(self) -> float:
        """
        再生位置を取得（0.0-1.0）
        
        Returns:
            現在の再生位置
        """
        try:
            return self.player.get_position()
        except Exception:
            return 0.0
    
    def set_position(self, position: float) -> bool:
        """
        再生位置を設定（0.0-1.0）
        
        Args:
            position: 設定する位置（0.0-1.0）
            
        Returns:
            設定成功時True
        """
        try:
            position = max(0.0, min(1.0, position))
            self.player.set_position(position)
            return True
        except Exception:
            return False
    
    def get_time(self) -> int:
        """
        現在の再生時間（ミリ秒）
        
        Returns:
            現在の再生時間
        """
        try:
            return self.player.get_time()
        except Exception:
            return 0
    
    def get_length(self) -> int:
        """
        総再生時間（ミリ秒）
        
        Returns:
            総再生時間
        """
        try:
            return self.player.get_length()
        except Exception:
            return 0
    
    def get_playlist_size(self) -> int:
        """
        プレイリストのサイズを取得
        
        Returns:
            プレイリストの曲数
        """
        return len(self.playlist)
    
    def clear_playlist(self):
        """プレイリストをクリア"""
        self.stop()
        self.playlist.clear()
        self.current_index = 0
        self.current_video = None
    
    def get_current_video(self) -> Optional[VideoInfo]:
        """現在再生中の動画情報を取得"""
        return self.current_video
    
    def is_playlist_empty(self) -> bool:
        """プレイリストが空かチェック"""
        return len(self.playlist) == 0 