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

def install_dependencies(venv_path, dev=False):
    """依存関係をインストール"""
    if dev:
        print("開発用依存関係をインストール中...")
        requirements_files = ["requirements.txt", "requirements-dev.txt"]
    else:
        print("依存関係をインストール中...")
        requirements_files = ["requirements.txt"]
    
    # 仮想環境のpipパス
    if sys.platform == "win32":
        pip_path = venv_path / "Scripts" / "pip"
    else:
        pip_path = venv_path / "bin" / "pip"
    
    # 各requirements.txtから依存関係をインストール
    for req_file in requirements_files:
        requirements_file = Path.cwd() / req_file
        if requirements_file.exists():
            try:
                subprocess.run([str(pip_path), "install", "-r", str(requirements_file)], 
                             check=True, capture_output=True, text=True)
                print(f"{req_file} からの依存関係のインストールが完了しました。")
            except subprocess.CalledProcessError as e:
                print(f"{req_file} の依存関係のインストールに失敗しました: {e}")
                print(f"エラー出力: {e.stderr}")
                return False
        elif req_file == "requirements.txt":
            print("requirements.txtが見つかりません。")
            return False
    
    return True

def check_vlc_installation(venv_path):
    """VLCがインストールされているかチェック"""
    # 仮想環境のpythonパス
    if sys.platform == "win32":
        python_path = venv_path / "Scripts" / "python"
    else:
        python_path = venv_path / "bin" / "python"
    
    try:
        # 仮想環境でVLCのインポートをテスト
        result = subprocess.run([str(python_path), "-c", "import vlc; print('VLC OK')"], 
                              capture_output=True, text=True, check=True)
        print("VLCライブラリが見つかりました。")
        return True
    except subprocess.CalledProcessError:
        print("警告: VLCライブラリが見つかりません。")
        print("VLC Media Playerをインストールしてください:")
        print("  brew install vlc  # Homebrewを使用する場合")
        print("  または https://www.videolan.org/vlc/ からダウンロード")
        return False

def create_launcher_script(venv_path):
    """起動スクリプトを作成"""
    # YouTube Audio Player 起動スクリプト
    if sys.platform == "win32":
        python_path = venv_path / "Scripts" / "python"
        launcher_content = f"""@echo off
cd /d "%~dp0"
"{python_path}" main.py
"""
        launcher_path = Path.cwd() / "youtube-audio-player.bat"
    else:
        python_path = venv_path / "bin" / "python"
        launcher_content = f"""#!/bin/bash
# YouTube Audio Player 起動スクリプト
cd "$(dirname "$0")"
"{python_path}" main.py
"""
        launcher_path = Path.cwd() / "youtube-audio-player"
    
    with open(launcher_path, "w") as f:
        f.write(launcher_content)
    
    # 実行権限を付与（Unix系のみ）
    if sys.platform != "win32":
        launcher_path.chmod(0o755)
    
    print(f"起動スクリプトが作成されました: {launcher_path}")

def create_dev_launcher_script(venv_path):
    """開発用起動スクリプトを作成"""
    # 開発用起動スクリプト（テスト実行用）
    if sys.platform == "win32":
        python_path = venv_path / "Scripts" / "python"
        dev_launcher_content = f"""@echo off
cd /d "%~dp0"
echo Running tests...
"{python_path}" -m pytest tests/ -v
pause
"""
        dev_launcher_path = Path.cwd() / "run-tests.bat"
    else:
        python_path = venv_path / "bin" / "python"
        dev_launcher_content = f"""#!/bin/bash
# YouTube Audio Player テスト実行スクリプト
cd "$(dirname "$0")"
echo "Running tests..."
"{python_path}" -m pytest tests/ -v
echo "Press Enter to continue..."
read
"""
        dev_launcher_path = Path.cwd() / "run-tests"
    
    with open(dev_launcher_path, "w") as f:
        f.write(dev_launcher_content)
    
    # 実行権限を付与（Unix系のみ）
    if sys.platform != "win32":
        dev_launcher_path.chmod(0o755)
    
    print(f"開発用テストスクリプトが作成されました: {dev_launcher_path}")

def main():
    """メインセットアップ関数"""
    print("YouTube Audio Player セットアップを開始します...")
    
    # オプション解析
    dev_mode = "--dev" in sys.argv
    
    if dev_mode:
        print("開発モードでセットアップします。")
    
    # 仮想環境作成
    venv_path = create_virtual_environment()
    
    # 依存関係インストール
    if not install_dependencies(venv_path, dev=dev_mode):
        sys.exit(1)
    
    # VLC確認
    vlc_ok = check_vlc_installation(venv_path)
    
    # 起動スクリプト作成
    create_launcher_script(venv_path)
    
    if dev_mode:
        create_dev_launcher_script(venv_path)
    
    print("\nセットアップが完了しました！")
    print("使用方法:")
    if sys.platform == "win32":
        print("  youtube-audio-player.bat")
        if dev_mode:
            print("  run-tests.bat  (テスト実行)")
    else:
        print("  ./youtube-audio-player")
        if dev_mode:
            print("  ./run-tests  (テスト実行)")
    
    if not vlc_ok:
        print("\n⚠️  VLCの設定が必要です。上記の指示に従ってVLCをインストールしてください。")
    
    print("\nアンインストール:")
    print("  python3 uninstall.py")
    
    if dev_mode:
        print("\n開発者向け:")
        print("  新しいモジュール構造に基づいたリファクタリングが完了しています。")
        print("  main.py が新しいエントリーポイントです。")
        print("  youtube_player.py は後方互換性のために残されています。")

if __name__ == "__main__":
    main() 