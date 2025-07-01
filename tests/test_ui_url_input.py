"""
URL入力スクリーンのテスト
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from textual.widgets import Input, Button, Static
from src.ui.screens.url_input_screen import URLInputScreen


class TestURLInputScreen:
    """URL入力スクリーンのテストクラス"""
    
    def test_init(self):
        """初期化テスト"""
        callback = Mock()
        screen = URLInputScreen(callback)
        
        assert screen.callback == callback
        assert screen.is_processing is False
        assert screen._url_input is None
        assert screen._add_button is None
        assert screen._cancel_button is None
        assert screen._status_area is None
    
    @pytest.mark.asyncio
    async def test_compose(self):
        """compose メソッドのテスト"""
        callback = Mock()
        screen = URLInputScreen(callback)
        
        # composeメソッドが存在し、呼び出し可能であることを確認
        assert hasattr(screen, 'compose')
        assert callable(screen.compose)
    
    @pytest.mark.asyncio
    async def test_disable_ui(self):
        """UI無効化テスト"""
        callback = Mock()
        screen = URLInputScreen(callback)
        
        # UI要素を手動で設定
        screen._url_input = Mock(spec=Input)
        screen._add_button = Mock(spec=Button)
        screen._cancel_button = Mock(spec=Button)
        screen._status_area = Mock(spec=Static)
        
        screen._disable_ui()
        
        # ボタンが無効化されることを確認
        assert screen._add_button.disabled is True
        assert screen._add_button.label == "処理中..."
        assert screen._cancel_button.disabled is True
        assert screen._url_input.disabled is True
        
        # refresh が呼ばれることを確認
        screen._add_button.refresh.assert_called_once()
        screen._cancel_button.refresh.assert_called_once()
        screen._url_input.refresh.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_enable_ui(self):
        """UI有効化テスト"""
        callback = Mock()
        screen = URLInputScreen(callback)
        
        # UI要素を手動で設定
        screen._url_input = Mock(spec=Input)
        screen._add_button = Mock(spec=Button)
        screen._cancel_button = Mock(spec=Button)
        screen._status_area = Mock(spec=Static)
        
        screen._enable_ui()
        
        # ボタンが有効化されることを確認
        assert screen._add_button.disabled is False
        assert screen._add_button.label == "追加"
        assert screen._cancel_button.disabled is False
        assert screen._url_input.disabled is False
        
        # refresh が呼ばれることを確認
        screen._add_button.refresh.assert_called_once()
        screen._cancel_button.refresh.assert_called_once()
        screen._url_input.refresh.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_status(self):
        """ステータス更新テスト"""
        callback = Mock()
        screen = URLInputScreen(callback)
        
        # UI要素を手動で設定
        screen._status_area = Mock(spec=Static)
        
        screen._update_status("テストメッセージ")
        
        screen._status_area.update.assert_called_once_with("テストメッセージ")
        screen._status_area.refresh.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_submit_empty_url(self):
        """空URLの処理テスト"""
        callback = Mock()
        screen = URLInputScreen(callback)
        
        # UI要素を手動で設定
        screen._url_input = Mock(spec=Input)
        screen._url_input.value = "  "  # 空白のURL
        screen._status_area = Mock(spec=Static)
        
        await screen._handle_submit()
        
        # エラーメッセージが表示されることを確認
        screen._status_area.update.assert_called_with("⚠️ URLを入力してください")
        callback.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_handle_submit_processing_flag(self):
        """処理中フラグのテスト"""
        callback = Mock()
        screen = URLInputScreen(callback)
        screen.is_processing = True
        
        await screen._handle_submit()
        
        # 処理中の場合は何もしない
        callback.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_handle_submit_success(self):
        """正常処理のテスト"""
        callback = AsyncMock()
        screen = URLInputScreen(callback)
        
        # UI要素を手動で設定
        screen._url_input = Mock(spec=Input)
        screen._url_input.value = "https://www.youtube.com/watch?v=test"
        screen._add_button = Mock(spec=Button)
        screen._cancel_button = Mock(spec=Button)
        screen._status_area = Mock(spec=Static)
        screen.dismiss = Mock()
        
        with patch('asyncio.sleep', return_value=None):
            await screen._handle_submit()
        
        # UI無効化が行われることを確認
        assert screen._add_button.disabled is True
        assert screen._add_button.label == "処理中..."
        
        # ステータス更新が呼ばれることを確認
        status_calls = [call[0][0] for call in screen._status_area.update.call_args_list]
        assert "🔄 処理を開始しています..." in status_calls
        assert "🌐 YouTube動画情報を取得中..." in status_calls
        assert "⚙️ 動画データを処理中..." in status_calls
        assert "✅ 追加が完了しました！" in status_calls
        
        # コールバックが呼ばれることを確認
        callback.assert_called_once_with("https://www.youtube.com/watch?v=test")
        
        # ダイアログが閉じられることを確認
        screen.dismiss.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_submit_validation_error(self):
        """バリデーションエラーの処理テスト"""
        callback = Mock(side_effect=ValueError("無効なURLです"))
        screen = URLInputScreen(callback)
        
        # UI要素を手動で設定
        screen._url_input = Mock(spec=Input)
        screen._url_input.value = "https://www.youtube.com/watch?v=test"
        screen._add_button = Mock(spec=Button)
        screen._cancel_button = Mock(spec=Button)
        screen._status_area = Mock(spec=Static)
        screen.dismiss = Mock()
        
        with patch('asyncio.sleep', return_value=None):
            await screen._handle_submit()
        
        # エラーメッセージが表示される
        error_calls = [call[0][0] for call in screen._status_area.update.call_args_list if "❌" in call[0][0]]
        assert len(error_calls) > 0
        assert "無効なURLです" in error_calls[0]
        
        # UI要素が再有効化される
        assert screen._add_button.disabled is False
        assert screen._add_button.label == "追加"
        
        # エラー時はダイアログを閉じない
        screen.dismiss.assert_not_called()
        
        # 処理フラグがリセットされる
        assert screen.is_processing is False
    
    @pytest.mark.asyncio
    async def test_handle_submit_general_error(self):
        """一般的なエラーの処理テスト"""
        callback = Mock(side_effect=Exception("不明なエラー"))
        screen = URLInputScreen(callback)
        
        # UI要素を手動で設定
        screen._url_input = Mock(spec=Input)
        screen._url_input.value = "https://www.youtube.com/watch?v=test"
        screen._add_button = Mock(spec=Button)
        screen._cancel_button = Mock(spec=Button)
        screen._status_area = Mock(spec=Static)
        screen.dismiss = Mock()
        
        with patch('asyncio.sleep', return_value=None):
            await screen._handle_submit()
        
        # エラーメッセージが表示される
        error_calls = [call[0][0] for call in screen._status_area.update.call_args_list if "❌" in call[0][0]]
        assert len(error_calls) > 0
        assert "不明なエラー" in error_calls[0]
        
        # エラー時はダイアログを閉じない
        screen.dismiss.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_button_pressed_add(self):
        """追加ボタン押下テスト"""
        callback = Mock()
        screen = URLInputScreen(callback)
        screen.is_processing = False
        
        # モックイベントを作成
        mock_event = Mock()
        mock_event.button.id = "add_button"
        
        with patch.object(screen, '_handle_submit', new_callable=AsyncMock) as mock_handle:
            await screen.on_button_pressed(mock_event)
            
            mock_handle.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_button_pressed_cancel(self):
        """キャンセルボタン押下テスト"""
        callback = Mock()
        screen = URLInputScreen(callback)
        screen.is_processing = False
        
        # モックイベントを作成
        mock_event = Mock()
        mock_event.button.id = "cancel_button"
        
        screen.dismiss = Mock()
        
        await screen.on_button_pressed(mock_event)
        
        screen.dismiss.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_button_pressed_while_processing(self):
        """処理中のボタン押下テスト"""
        callback = Mock()
        screen = URLInputScreen(callback)
        screen.is_processing = True
        
        # モックイベントを作成
        mock_event = Mock()
        mock_event.button.id = "add_button"
        
        with patch.object(screen, '_handle_submit', new_callable=AsyncMock) as mock_handle:
            await screen.on_button_pressed(mock_event)
            
            # 処理中の場合は何もしない
            mock_handle.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_input_submitted(self):
        """Enterキー押下テスト"""
        callback = Mock()
        screen = URLInputScreen(callback)
        screen.is_processing = False
        
        # モックイベントを作成
        mock_event = Mock()
        mock_event.input.id = "url_input_field"
        
        with patch.object(screen, '_handle_submit', new_callable=AsyncMock) as mock_handle:
            await screen.on_input_submitted(mock_event)
            
            mock_handle.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_duplicate_processing_prevention(self):
        """重複処理防止テスト"""
        callback = AsyncMock()
        screen = URLInputScreen(callback)
        
        # UI要素を手動で設定
        screen._url_input = Mock(spec=Input)
        screen._url_input.value = "https://www.youtube.com/watch?v=test"
        screen._add_button = Mock(spec=Button)
        screen._cancel_button = Mock(spec=Button)
        screen._status_area = Mock(spec=Static)
        screen.dismiss = Mock()
        
        # 最初の処理を開始
        task1 = asyncio.create_task(screen._handle_submit())
        await asyncio.sleep(0.01)  # 少し待つ
        
        # 2回目の処理を試行（処理中なので無視される）
        await screen._handle_submit()
        
        # 最初のタスクを完了
        await task1
        
        # コールバックは1回だけ呼ばれる
        callback.assert_called_once() 