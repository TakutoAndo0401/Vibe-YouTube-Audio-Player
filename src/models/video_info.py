"""
動画情報を管理するデータモデル
"""

from typing import Optional


class VideoInfo:
    """動画情報を管理するクラス"""
    
    def __init__(self, url: str, title: str = "", duration: int = 0, 
                 channel: str = "", audio_url: str = ""):
        """
        動画情報を初期化
        
        Args:
            url: YouTube動画のURL
            title: 動画タイトル
            duration: 動画の長さ（秒）
            channel: チャンネル名
            audio_url: 音声ストリームのURL
        """
        self.url = url
        self.title = title
        self.duration = duration
        self.channel = channel
        self.audio_url = audio_url
        self.is_loaded = False
    
    def __str__(self) -> str:
        """文字列表現"""
        return f"VideoInfo(title='{self.title}', channel='{self.channel}', duration={self.duration})"
    
    def __repr__(self) -> str:
        """デバッグ用文字列表現"""
        return (f"VideoInfo(url='{self.url}', title='{self.title}', "
                f"channel='{self.channel}', duration={self.duration}, "
                f"is_loaded={self.is_loaded})")
    
    def format_duration(self) -> str:
        """
        再生時間を mm:ss 形式でフォーマット
        
        Returns:
            フォーマットされた時間文字列
        """
        if self.duration <= 0:
            return "00:00"
        
        minutes = self.duration // 60
        seconds = self.duration % 60
        return f"{minutes}:{seconds:02d}"
    
    def is_valid(self) -> bool:
        """
        動画情報が有効かチェック
        
        Returns:
            True if valid, False otherwise
        """
        return bool(self.url and self.title and self.audio_url and self.is_loaded) 