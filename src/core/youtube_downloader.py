"""
YouTube動画情報取得・音声URL抽出
"""

import asyncio
import yt_dlp
from typing import Optional
from ..models.video_info import VideoInfo


class YouTubeDownloader:
    """YouTube動画情報取得・音声URL抽出"""
    
    def __init__(self):
        """YouTubeDownloaderを初期化"""
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
        }
    
    def _is_youtube_url(self, url: str) -> bool:
        """
        YouTube URLかどうかを判定
        
        Args:
            url: 判定するURL
            
        Returns:
            YouTube URLの場合True
        """
        return 'youtube.com' in url or 'youtu.be' in url
    
    async def get_video_info(self, url: str) -> Optional[VideoInfo]:
        """
        YouTube URLから動画情報を取得
        
        Args:
            url: YouTube動画のURL
            
        Returns:
            取得成功時はVideoInfo、失敗時はNone
        """
        if not url or not url.strip():
            return None
            
        url = url.strip()
        
        if not self._is_youtube_url(url):
            return None
        
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
    
    def validate_url(self, url: str) -> bool:
        """
        URLの形式を検証
        
        Args:
            url: 検証するURL
            
        Returns:
            有効なYouTube URLの場合True
        """
        if not url or not url.strip():
            return False
            
        url = url.strip()
        return self._is_youtube_url(url) 