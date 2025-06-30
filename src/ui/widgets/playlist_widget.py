"""
プレイリスト表示ウィジェット
"""

from textual.widgets import ListView, ListItem, Label
from ...core.media_player import MediaPlayer


class PlaylistWidget(ListView):
    """プレイリスト表示ウィジェット"""
    
    def __init__(self, player: MediaPlayer):
        """
        プレイリストウィジェットを初期化
        
        Args:
            player: メディアプレイヤーインスタンス
        """
        super().__init__()
        self.player = player
        self.border_title = "プレイリスト"
    
    def update_playlist(self):
        """プレイリストを更新"""
        self.clear()
        
        if not self.player.playlist:
            # プレイリストが空の場合
            empty_item = ListItem(Label("[dim]プレイリストが空です[/dim]"))
            self.append(empty_item)
            return
        
        for i, video in enumerate(self.player.playlist):
            # 現在再生中の曲にマークを付ける
            prefix = "▶ " if i == self.player.current_index else "  "
            
            # 時間表示
            duration_str = video.format_duration()
            
            # アイテムテキスト作成
            item_text = f"{prefix}{video.title} - {video.channel} [{duration_str}]"
            
            # 長すぎる場合は短縮
            if len(item_text) > 80:
                # タイトルを短縮
                max_title_len = 40
                if len(video.title) > max_title_len:
                    short_title = video.title[:max_title_len - 3] + "..."
                    item_text = f"{prefix}{short_title} - {video.channel} [{duration_str}]"
            
            self.append(ListItem(Label(item_text)))
    
    def get_selected_index(self) -> int:
        """
        選択されているアイテムのインデックスを取得
        
        Returns:
            選択されているインデックス、選択なしの場合は-1
        """
        if self.index is not None:
            return self.index
        return -1 