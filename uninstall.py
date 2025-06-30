#!/usr/bin/env python3
"""
YouTube Terminal Player - アンインストールスクリプト
"""

import os
import shutil
import sys
from pathlib import Path

def confirm_uninstall():
    """アンインストールの確認"""
    print("YouTube Terminal Player をアンインストールしますか？")
    print("この操作により、以下が削除されます:")
    print("- 仮想環境 (venv/)")
    print("- 全ての依存関係")
    print("- 起動スクリプト")
    print("- 設定ファイル")
    print()
    
    while True:
        response = input("続行しますか？ [y/N]: ").strip().lower()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no', '']:
            return False
        else:
            print("'y' または 'n' を入力してください。")

def remove_virtual_environment():
    """仮想環境を削除"""
    venv_path = Path.cwd() / "venv"
    if venv_path.exists():
        print("仮想環境を削除中...")
        shutil.rmtree(venv_path)
        print("仮想環境が削除されました。")
    else:
        print("仮想環境が見つかりませんでした。")

def remove_launcher_script():
    """起動スクリプトを削除"""
    launcher_path = Path.cwd() / "youtube-player"
    if launcher_path.exists():
        launcher_path.unlink()
        print("起動スクリプトが削除されました。")

def remove_cache_files():
    """キャッシュファイルを削除"""
    cache_patterns = [
        "**/__pycache__",
        "**/*.pyc",
        "**/*.pyo",
        "**/.DS_Store"
    ]
    
    for pattern in cache_patterns:
        for path in Path.cwd().glob(pattern):
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                shutil.rmtree(path)

def show_remaining_files():
    """残存ファイルを表示"""
    remaining_files = []
    for item in Path.cwd().iterdir():
        if item.name not in ['.git', '.gitignore']:
            remaining_files.append(item.name)
    
    if remaining_files:
        print("\n以下のファイルが残っています:")
        for file in remaining_files:
            print(f"  - {file}")
        print("\n完全にアンインストールするには、このディレクトリ全体を削除してください:")
        print(f"  rm -rf {Path.cwd()}")

def main():
    """メインアンインストール関数"""
    print("YouTube Terminal Player アンインストーラー")
    print("=" * 50)
    
    if not confirm_uninstall():
        print("アンインストールをキャンセルしました。")
        return
    
    print("\nアンインストールを開始します...")
    
    # 仮想環境削除
    remove_virtual_environment()
    
    # 起動スクリプト削除
    remove_launcher_script()
    
    # キャッシュファイル削除
    remove_cache_files()
    
    print("\nアンインストールが完了しました。")
    
    # 残存ファイル表示
    show_remaining_files()

if __name__ == "__main__":
    main() 