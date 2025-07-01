"""
URL入力用のモーダルスクリーン
"""

import asyncio
from typing import Callable, Optional
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
        self.is_processing = False  # 処理中フラグ
        # UI要素への参照を保持
        self._url_input: Optional[Input] = None
        self._add_button: Optional[Button] = None
        self._cancel_button: Optional[Button] = None
        self._status_area: Optional[Static] = None
    
    def compose(self) -> ComposeResult:
        """スクリーンの構成"""
        with Container(id="url_input_dialog"):
            yield Static("YouTube URLを入力してください:", id="title")
            self._url_input = Input(
                placeholder="https://www.youtube.com/watch?v=...",
                id="url_input_field"
            )
            yield self._url_input
            
            # ステータス表示エリアを追加
            self._status_area = Static("", id="status_area")
            yield self._status_area
            
            with Horizontal(id="button_container"):
                self._add_button = Button("追加", variant="primary", id="add_button")
                self._cancel_button = Button("キャンセル", variant="default", id="cancel_button")
                yield self._add_button
                yield self._cancel_button
    
    def on_mount(self):
        """モーダル表示時にフォーカス設定"""
        if self._url_input:
            self._url_input.focus()
    
    async def on_button_pressed(self, event: Button.Pressed):
        """ボタン押下時の処理"""
        if event.button.id == "add_button" and not self.is_processing:
            await self._handle_submit()
        elif event.button.id == "cancel_button" and not self.is_processing:
            self.dismiss()
    
    async def on_input_submitted(self, event: Input.Submitted):
        """Enter キー押下時の処理"""
        if event.input.id == "url_input_field" and not self.is_processing:
            await self._handle_submit()
    
    def _disable_ui(self):
        """UI要素を無効化"""
        if self._add_button:
            self._add_button.disabled = True
            self._add_button.label = "処理中..."
            self._add_button.refresh()
        if self._cancel_button:
            self._cancel_button.disabled = True
            self._cancel_button.refresh()
        if self._url_input:
            self._url_input.disabled = True
            self._url_input.refresh()
    
    def _enable_ui(self):
        """UI要素を有効化"""
        if self._add_button:
            self._add_button.disabled = False
            self._add_button.label = "追加"
            self._add_button.refresh()
        if self._cancel_button:
            self._cancel_button.disabled = False
            self._cancel_button.refresh()
        if self._url_input:
            self._url_input.disabled = False
            self._url_input.refresh()
    
    def _update_status(self, message: str):
        """ステータスメッセージを更新"""
        if self._status_area:
            self._status_area.update(message)
            self._status_area.refresh()
    
    async def _handle_submit(self):
        """共通のsubmit処理"""
        # 既に処理中の場合は何もしない
        if self.is_processing:
            return
        
        # URL取得
        if not self._url_input:
            return
            
        url = self._url_input.value.strip()
        if not url:
            self._update_status("⚠️ URLを入力してください")
            return
        
        self.is_processing = True
        
        try:
            # UI要素を無効化
            self._disable_ui()
            
            # ステップ1: 処理開始
            self._update_status("🔄 処理を開始しています...")
            await asyncio.sleep(0.1)
            
            # ステップ2: 情報取得中
            self._update_status("🌐 YouTube動画情報を取得中...")
            await asyncio.sleep(0.1)
            
            # ステップ3: データ処理中
            self._update_status("⚙️ 動画データを処理中...")
            await asyncio.sleep(0.1)
            
            # 実際の処理を実行
            if self.callback:
                if asyncio.iscoroutinefunction(self.callback):
                    await self.callback(url)
                else:
                    # 同期関数の場合は別スレッドで実行
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(None, self.callback, url)
            
            # ステップ4: 完了
            self._update_status("✅ 追加が完了しました！")
            await asyncio.sleep(1.0)
            
            # 成功した場合はダイアログを閉じる
            self.dismiss()
            
        except ValueError as e:
            # バリデーションエラー
            self._update_status(f"❌ {str(e)}")
            await asyncio.sleep(2.0)
            self._enable_ui()
            self.is_processing = False
            
        except Exception as e:
            # その他のエラー
            error_msg = str(e) if str(e) else "不明なエラーが発生しました"
            self._update_status(f"❌ エラー: {error_msg}")
            await asyncio.sleep(2.0)
            self._enable_ui()
            self.is_processing = False
    
    def on_key(self, event):
        """ESCキーでキャンセル"""
        if event.key == "escape" and not self.is_processing:
            self.dismiss() 