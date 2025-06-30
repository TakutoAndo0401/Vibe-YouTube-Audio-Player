"""
カスタムプログレスバーウィジェット
"""

from textual.widgets import Static


class CustomProgressBar(Static):
    """カスタムプログレスバーウィジェット"""
    
    def __init__(self, bar_width: int = 40):
        """
        プログレスバーを初期化
        
        Args:
            bar_width: バーの幅（文字数）
        """
        super().__init__()
        self.progress = 0.0  # 0.0 - 1.0
        self.bar_width = bar_width
    
    def set_progress(self, progress: float):
        """
        進行率を設定（0.0-1.0）
        
        Args:
            progress: 進行率（0.0-1.0）
        """
        self.progress = max(0.0, min(1.0, progress))
        self._update_bar()
    
    def _update_bar(self):
        """プログレスバーの表示を更新"""
        if self.progress == 0:
            # 停止中
            bar = "─" * self.bar_width
            self.update(f"[dim]│{bar}│[/dim] 0%")
        else:
            # 進行中
            filled_width = int(self.progress * self.bar_width)
            empty_width = self.bar_width - filled_width
            
            # YouTubeスタイルのバー
            filled_bar = "█" * filled_width
            empty_bar = "░" * empty_width
            percentage = int(self.progress * 100)
            
            # 色付きのバー表示
            self.update(f"[red]│[bold white on red]{filled_bar}[/bold white on red][dim white]{empty_bar}[/dim white]│[/red] {percentage}%")
    
    def get_progress(self) -> float:
        """
        現在の進行率を取得
        
        Returns:
            現在の進行率（0.0-1.0）
        """
        return self.progress
    
    def reset(self):
        """プログレスバーをリセット"""
        self.set_progress(0.0) 