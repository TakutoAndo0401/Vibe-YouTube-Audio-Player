#!/usr/bin/env python3
"""
YouTube Terminal Player - セットアップスクリプト
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
    print(f"仮想環境が作成されました: {venv_path}")
    return venv_path

def install_dependencies(venv_path):
    """依存関係をインストール"""
    pip_path = venv_path / "bin" / "pip"
    requirements_path = Path.cwd() / "requirements.txt"
    
    if not requirements_path.exists():
        print("requirements.txtが見つかりません。")
        return False
    
    print("依存関係をインストール中...")
    try:
        subprocess.run([str(pip_path), "install", "-r", str(requirements_path)], 
                      check=True, capture_output=True, text=True)
        print("依存関係のインストールが完了しました。")
        return True
    except subprocess.CalledProcessError as e:
        print(f"依存関係のインストールに失敗しました: {e}")
        return False

def check_vlc_installation():
    """VLCのインストールを確認"""
    try:
        import vlc
        print("VLCライブラリが利用可能です。")
        return True
    except ImportError:
        print("警告: VLCライブラリが見つかりません。")
        print("システムにVLCをインストールしてください:")
        print("  brew install vlc  # Homebrewを使用する場合")
        print("  または https://www.videolan.org/vlc/ からダウンロード")
        return False

def create_launcher_script(venv_path):
    """起動スクリプトを作成"""
    launcher_content = f"""#!/bin/bash
# YouTube Terminal Player 起動スクリプト

SCRIPT_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"
VENV_PATH="$SCRIPT_DIR/venv"
PYTHON_PATH="$VENV_PATH/bin/python"

if [ ! -f "$PYTHON_PATH" ]; then
    echo "仮想環境が見つかりません。setup.pyを実行してください。"
    exit 1
fi

"$PYTHON_PATH" "$SCRIPT_DIR/youtube_player.py" "$@"
"""
    
    launcher_path = Path.cwd() / "youtube-player"
    with open(launcher_path, "w") as f:
        f.write(launcher_content)
    
    # 実行権限を付与
    os.chmod(launcher_path, 0o755)
    print(f"起動スクリプトが作成されました: {launcher_path}")

def main():
    """メインセットアップ関数"""
    print("YouTube Terminal Player セットアップを開始します...")
    
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
    print("  ./youtube-player")
    print("\nアンインストール:")
    print("  このディレクトリ全体を削除してください")

if __name__ == "__main__":
    main() 