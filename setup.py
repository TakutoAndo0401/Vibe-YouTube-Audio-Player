#!/usr/bin/env python3
"""
YouTube Audio Player - セットアップスクリプト
"""

import os
import sys
import subprocess
import venv
from pathlib import Path

def create_virtual_environment():
    """仮想環境を作成"""
    venv_path = Path.cwd() / "venv"
    
    if venv_path.exists():
        print("仮想環境は既に存在します。")
        return venv_path
    
    print("仮想環境を作成中...")
    venv.create(venv_path, with_pip=True)
    print("仮想環境が作成されました。")
    
    return venv_path

def install_dependencies(venv_path):
    """依存関係をインストール"""
    print("依存関係をインストール中...")
    
    # 仮想環境のpipパス
    if sys.platform == "win32":
        pip_path = venv_path / "Scripts" / "pip"
    else:
        pip_path = venv_path / "bin" / "pip"
    
    # requirements.txtから依存関係をインストール
    requirements_file = Path.cwd() / "requirements.txt"
    if requirements_file.exists():
        try:
            subprocess.run([str(pip_path), "install", "-r", str(requirements_file)], 
                         check=True, capture_output=True, text=True)
            print("依存関係のインストールが完了しました。")
            return True
        except subprocess.CalledProcessError as e:
            print(f"依存関係のインストールに失敗しました: {e}")
            print(f"エラー出力: {e.stderr}")
            return False
    else:
        print("requirements.txtが見つかりません。")
        return False

def check_vlc_installation():
    """VLCがインストールされているかチェック"""
    try:
        import vlc
        print("VLCライブラリが見つかりました。")
    except ImportError:
        print("警告: VLCライブラリが見つかりません。")
        print("VLC Media Playerをインストールしてください:")
        print("  brew install vlc  # Homebrewを使用する場合")
        print("  または https://www.videolan.org/vlc/ からダウンロード")

def create_launcher_script(venv_path):
    """起動スクリプトを作成"""
    # YouTube Audio Player 起動スクリプト
    if sys.platform == "win32":
        python_path = venv_path / "Scripts" / "python"
        launcher_content = f"""@echo off
"{python_path}" youtube_player.py
"""
        launcher_path = Path.cwd() / "youtube-audio-player.bat"
    else:
        python_path = venv_path / "bin" / "python"
        launcher_content = f"""#!/bin/bash
# YouTube Audio Player 起動スクリプト
cd "$(dirname "$0")"
"{python_path}" youtube_player.py
"""
        launcher_path = Path.cwd() / "youtube-audio-player"
    
    with open(launcher_path, "w") as f:
        f.write(launcher_content)
    
    # 実行権限を付与（Unix系のみ）
    if sys.platform != "win32":
        launcher_path.chmod(0o755)
    
    print(f"起動スクリプトが作成されました: {launcher_path}")

def main():
    """メインセットアップ関数"""
    print("YouTube Audio Player セットアップを開始します...")
    
    # 仮想環境作成
    venv_path = create_virtual_environment()
    
    # 依存関係インストール
    if not install_dependencies(venv_path):
        sys.exit(1)
    
    # VLC確認
    check_vlc_installation()
    
    # 起動スクリプト作成
    create_launcher_script(venv_path)
    
    print("\nセットアップが完了しました！")
    print("使用方法:")
    if sys.platform == "win32":
        print("  youtube-audio-player.bat")
    else:
        print("  ./youtube-audio-player")
    print("\nアンインストール:")
    print("  このディレクトリ全体を削除してください")

if __name__ == "__main__":
    main() 