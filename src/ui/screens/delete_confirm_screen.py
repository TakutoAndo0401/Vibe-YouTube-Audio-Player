"""
削除確認用のモーダルスクリーン
"""

import asyncio
from typing import Callable
from textual.screen import ModalScreen
from textual.containers import Container, Horizontal
from textual.widgets import Button, Static
from textual.app import ComposeResult


class DeleteConfirmScreen(ModalScreen):
    """削除確認用のモーダルスクリーン"""
    
    CSS = """
    DeleteConfirmScreen {
        align: center middle;
    }
    
    #delete_confirm_dialog {
        width: 70%;
        height: 12;
        border: thick $warning 80%;
        background: $surface;
        padding: 1;
    }
    
    #confirm_title {
        text-align: center;
        margin-bottom: 1;
        color: $warning;
    }
    
    #song_info {
        text-align: center;
        margin: 1 0;
        color: $text;
    }
    
    #confirm_message {
        text-align: center;
        margin-bottom: 1;
        color: $text-muted;
    }
    
    #button_container {
        height: 3;
        align: center middle;
    }
    
    #delete_button {
        margin: 0 1;
        background: $error;
    }
    
    #cancel_button {
        margin: 0 1;
    }
    """
    
    def __init__(self, video_title: str, callback: Callable[[bool], None]):
        """
        削除確認スクリーンを初期化
        
        Args:
            video_title: 削除対象の動画タイトル
            callback: 確認結果のコールバック関数
        """
        super().__init__()
        self.video_title = video_title
        self.callback = callback
    
    def compose(self) -> ComposeResult:
        """スクリーンの構成"""
        with Container(id="delete_confirm_dialog"):
            yield Static("⚠️ 削除の確認", id="confirm_title")
            
            # 曲名を短縮表示
            display_title = self._truncate_title(self.video_title, 40)
            
            yield Static(f'"{display_title}"', id="song_info")
            yield Static("この曲をプレイリストから削除しますか？", id="confirm_message")
            
            with Horizontal(id="button_container"):
                yield Button("🗑️ 削除", variant="error", id="delete_button")
                yield Button("キャンセル", variant="default", id="cancel_button")
    
    def _truncate_title(self, title: str, max_length: int) -> str:
        """
        タイトルを指定した長さに短縮
        
        Args:
            title: 元のタイトル
            max_length: 最大長
            
        Returns:
            短縮されたタイトル
        """
        if len(title) <= max_length:
            return title
        return title[:max_length - 3] + "..."
    
    async def on_button_pressed(self, event: Button.Pressed):
        """ボタン押下時の処理"""
        if event.button.id == "delete_button":
            await self.callback(True)  # 削除実行
            self.dismiss()
        elif event.button.id == "cancel_button":
            await self.callback(False)  # キャンセル
            self.dismiss()
    
    def on_key(self, event):
        """キー操作"""
        if event.key == "escape":
            # ESCキーでキャンセル
            asyncio.create_task(self.callback(False))
            self.dismiss()
        elif event.key == "enter":
            # Enterキーで削除実行
            asyncio.create_task(self.callback(True))
            self.dismiss() 