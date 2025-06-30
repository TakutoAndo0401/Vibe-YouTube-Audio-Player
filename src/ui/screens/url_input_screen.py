"""
URL入力用のモーダルスクリーン
"""

import asyncio
from typing import Callable
from textual.screen import ModalScreen
from textual.containers import Container, Horizontal
from textual.widgets import Input, Button, Static
from textual.app import ComposeResult


class URLInputScreen(ModalScreen):
    """URL入力用のモーダルスクリーン"""
    
    CSS = """
    URLInputScreen {
        align: center middle;
    }
    
    #url_input_dialog {
        width: 80%;
        height: 18;
        border: thick $primary 80%;
        background: $surface;
        padding: 1;
    }
    
    #title {
        text-align: center;
        margin-bottom: 1;
        height: 2;
        color: $text;
    }
    
    #url_input_field {
        width: 1fr;
        margin: 1 0;
    }
    
    #url_input_field:disabled {
        opacity: 0.6;
        border: solid $warning;
        background: $surface-lighten-1;
    }
    
    #button_container {
        height: 3;
        align: center middle;
    }
    
    #add_button, #cancel_button {
        margin: 0 1;
        min-width: 12;
    }
    
    #add_button:disabled {
        opacity: 0.8;
        background: $warning;
    }
    
    #cancel_button:disabled {
        opacity: 0.6;
        background: $surface-lighten-1;
    }
    
    #status_area {
        text-align: center;
        margin: 1 0;
        height: 2;
        color: $accent;
    }
    """
    
    def __init__(self, callback: Callable[[str], None]):
        """
        URL入力スクリーンを初期化
        
        Args:
            callback: URL入力時のコールバック関数
        """
        super().__init__()
        self.callback = callback
        self.url_input = None
        self.is_processing = False  # 処理中フラグ
    
    def compose(self) -> ComposeResult:
        """スクリーンの構成"""
        with Container(id="url_input_dialog"):
            yield Static("YouTube URLを入力してください:", id="title")
            self.url_input = Input(
                placeholder="https://www.youtube.com/watch?v=...",
                id="url_input_field"
            )
            yield self.url_input
            
            # ステータス表示エリアを追加
            yield Static("", id="status_area")
            
            with Horizontal(id="button_container"):
                yield Button("追加", variant="primary", id="add_button")
                yield Button("キャンセル", variant="default", id="cancel_button")
    
    def on_mount(self):
        """モーダル表示時にフォーカス設定"""
        self.url_input.focus()
    
    async def on_button_pressed(self, event: Button.Pressed):
        """ボタン押下時の処理"""
        if event.button.id == "add_button":
            # イベントの伝播を停止
            event.stop()
            await self._handle_submit()
        elif event.button.id == "cancel_button":
            event.stop()
            self.dismiss()
    
    async def on_input_submitted(self, event: Input.Submitted):
        """Enter キー押下時の処理"""
        if event.input == self.url_input:
            # イベントの伝播を停止
            event.stop()
            await self._handle_submit()
    
    async def _handle_submit(self):
        """共通のsubmit処理"""
        # 既に処理中の場合は何もしない
        if self.is_processing:
            return
        
        url = self.url_input.value.strip()
        if not url:
            status_area = self.query_one("#status_area")
            status_area.update("⚠️ URLを入力してください")
            return
        
        self.is_processing = True
        
        try:
            # UI要素を取得
            add_button = self.query_one("#add_button")
            status_area = self.query_one("#status_area")
            
            # ボタンを非活性にして、ステータスエリアに進行状況を表示
            add_button.disabled = True
            add_button.label = "処理中..."
            
            # ステップ1: 処理開始
            status_area.update("🔄 処理を開始しています...")
            await asyncio.sleep(0.3)
            
            # ステップ2: 情報取得中
            status_area.update("🌐 YouTube動画情報を取得中...")
            await asyncio.sleep(0.3)
            
            # ステップ3: データ処理中
            status_area.update("⚙️ 動画データを処理中...")
            await asyncio.sleep(0.3)
            
            # 実際の処理を実行
            await self.callback(url)
            
            # ステップ4: 完了
            status_area.update("✅ 追加が完了しました！")
            await asyncio.sleep(0.5)
            
            # 処理完了後にダイアログを閉じる
            self.dismiss()
            
        except Exception as e:
            # エラー時の処理
            try:
                add_button = self.query_one("#add_button")
                status_area = self.query_one("#status_area")
                add_button.label = "エラー"
                status_area.update("❌ エラーが発生しました")
                await asyncio.sleep(2)
            except:
                pass
            self.dismiss()
        finally:
            self.is_processing = False
    
    def on_key(self, event):
        """ESCキーでキャンセル"""
        if event.key == "escape":
            # 処理中でもキャンセル可能
            self.dismiss() 