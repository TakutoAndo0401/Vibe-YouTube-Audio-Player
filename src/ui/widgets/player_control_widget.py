"""
プレイヤーコントロールウィジェット
"""

from textual.containers import Container, Vertical
from textual.widgets import Static
from textual.app import ComposeResult

from .progress_bar import CustomProgressBar
from ...core.media_player import MediaPlayer


class PlayerControlWidget(Container):
    """プレイヤーコントロールウィジェット"""
    
    def __init__(self, player: MediaPlayer):
        """
        プレイヤーコントロールウィジェットを初期化
        
        Args:
            player: メディアプレイヤーインスタンス
        """
        super().__init__()
        self.player = player
        self.progress_bar = CustomProgressBar()
        self.time_label = Static("00:00 / 00:00")
        self.remaining_label = Static("残り: --:--")
        self.status_label = Static("停止中")
        
    def compose(self) -> ComposeResult:
        """ウィジェットの構成"""
        with Vertical():
            yield self.status_label
            yield Static("")  # スペーサー
            yield self.progress_bar
            yield Static("")  # スペーサー
            yield self.time_label
            yield self.remaining_label
    
    def update_display(self):
        """表示を更新"""
        current_video = self.player.get_current_video()
        
        if current_video and self.player.is_playing:
            # タイトルを短縮表示
            title = current_video.title
            if len(title) > 30:
                title = title[:27] + "..."
            self.status_label.update(f"🎵 [bold]{title}[/bold]")
            
            current_time = self.player.get_time() // 1000
            total_time = self.player.get_length() // 1000
            
            if total_time > 0:
                # 進行率計算
                progress = current_time / total_time
                self.progress_bar.set_progress(progress)
                
                # 時間表示
                current_str = self._format_time(current_time)
                total_str = self._format_time(total_time)
                self.time_label.update(f"⏱️  {current_str} / {total_str}")
                
                # 残り時間表示
                remaining_time = total_time - current_time
                remaining_str = self._format_time(remaining_time)
                self.remaining_label.update(f"⏳ 残り: {remaining_str}")
            else:
                self._reset_display()
        else:
            # 停止中または曲なし
            if current_video:
                # 一時停止中
                title = current_video.title
                if len(title) > 30:
                    title = title[:27] + "..."
                self.status_label.update(f"⏸️ [dim]{title}[/dim]")
            else:
                self.status_label.update("⏸️  [dim]停止中[/dim]")
            
            self._reset_display()
    
    def _format_time(self, seconds: int) -> str:
        """
        秒数を mm:ss 形式にフォーマット
        
        Args:
            seconds: 秒数
            
        Returns:
            フォーマットされた時間文字列
        """
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes}:{seconds:02d}"
    
    def _reset_display(self):
        """表示をリセット"""
        self.progress_bar.reset()
        self.time_label.update("⏱️  00:00 / 00:00")
        self.remaining_label.update("⏳ 残り: --:--") 