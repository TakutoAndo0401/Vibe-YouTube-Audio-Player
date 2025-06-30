#!/usr/bin/env python3
"""
YouTube Audio Player - アンインストールスクリプト
"""

import os
import shutil
import sys
from pathlib import Path

def confirm_uninstall():
    """アンインストールの確認"""
    print("YouTube Audio Player をアンインストールしますか？")
    print("この操作により以下が削除されます:")
    print("  - 仮想環境 (venv/)")
    print("  - 起動スクリプト (youtube-audio-player)")
    print("  - キャッシュファイル")
    print()
    
    while True:
        response = input("続行しますか？ [y/N]: ").lower().strip()
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
        try:
            shutil.rmtree(venv_path)
            print("✓ 仮想環境を削除しました")
            return True
        except Exception as e:
            print(f"✗ 仮想環境の削除に失敗しました: {e}")
            return False
    else:
        print("仮想環境が見つかりません")
        return True

def remove_launcher_script():
    """起動スクリプトを削除"""
    scripts_to_remove = []
    
    if sys.platform == "win32":
        scripts_to_remove = [
            Path.cwd() / "youtube-audio-player.bat",
            Path.cwd() / "run-tests.bat"
        ]
    else:
        scripts_to_remove = [
            Path.cwd() / "youtube-audio-player",
            Path.cwd() / "run-tests"
        ]
    
    success = True
    found_any = False
    
    for script_path in scripts_to_remove:
        if script_path.exists():
            found_any = True
            print(f"起動スクリプトを削除中: {script_path.name}")
            try:
                script_path.unlink()
                print(f"✓ {script_path.name} を削除しました")
            except Exception as e:
                print(f"✗ {script_path.name} の削除に失敗しました: {e}")
                success = False
    
    if not found_any:
        print("起動スクリプトが見つかりません")
    
    return success

def remove_cache_files():
    """キャッシュファイルを削除"""
    cache_patterns = ["__pycache__", "*.pyc", "*.pyo"]
    removed_count = 0
    
    print("キャッシュファイルを削除中...")
    
    # __pycache__ディレクトリを削除
    for pycache_dir in Path.cwd().rglob("__pycache__"):
        try:
            shutil.rmtree(pycache_dir)
            removed_count += 1
            print(f"✓ {pycache_dir} を削除しました")
        except Exception as e:
            print(f"✗ {pycache_dir} の削除に失敗しました: {e}")
    
    # .pyc, .pyoファイルを削除
    for pattern in ["*.pyc", "*.pyo"]:
        for file_path in Path.cwd().rglob(pattern):
            try:
                file_path.unlink()
                removed_count += 1
                print(f"✓ {file_path} を削除しました")
            except Exception as e:
                print(f"✗ {file_path} の削除に失敗しました: {e}")
    
    if removed_count == 0:
        print("削除するキャッシュファイルが見つかりませんでした")
    
    return True

def show_remaining_files():
    """残存ファイルを表示"""
    print("\n残存ファイル:")
    remaining_files = []
    
    for item in Path.cwd().iterdir():
        if item.name not in ['.git', '.gitignore']:
            remaining_files.append(item)
    
    if remaining_files:
        for file_path in sorted(remaining_files):
            if file_path.is_dir():
                print(f"  📁 {file_path.name}/")
            else:
                print(f"  📄 {file_path.name}")
        
        print(f"\n完全な削除には、このディレクトリ全体を削除してください:")
        print(f"  rm -rf {Path.cwd()}")
    else:
        print("  なし")

def main():
    """メインアンインストール関数"""
    print("YouTube Audio Player アンインストーラー")
    print("=" * 50)
    
    if not confirm_uninstall():
        print("アンインストールをキャンセルしました。")
        return 0
    
    print("\nアンインストールを開始します...")
    
    success = True
    
    # 仮想環境を削除
    if not remove_virtual_environment():
        success = False
    
    # 起動スクリプトを削除
    if not remove_launcher_script():
        success = False
    
    # キャッシュファイルを削除
    if not remove_cache_files():
        success = False
    
    # 残存ファイルを表示
    show_remaining_files()
    
    if success:
        print("\n✓ アンインストールが完了しました！")
        return 0
    else:
        print("\n⚠ アンインストール中にエラーが発生しました。")
        print("手動で残りのファイルを削除してください。")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 