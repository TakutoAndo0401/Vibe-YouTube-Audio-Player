#!/usr/bin/env python3
"""
YouTube Audio Player - メインエントリーポイント
"""

def main():
    """メイン関数"""
    try:
        import vlc
    except ImportError:
        print("エラー: VLCライブラリが見つかりません。")
        print("システムにVLCをインストールしてください:")
        print("  brew install vlc  # Homebrewを使用する場合")
        print("  または https://www.videolan.org/vlc/ からダウンロード")
        return 1
    
    from src.ui.app import YouTubePlayerApp
    
    app = YouTubePlayerApp()
    try:
        app.run()
    except KeyboardInterrupt:
        print("\nアプリケーションを終了します...")
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 