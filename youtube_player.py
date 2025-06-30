#!/usr/bin/env python3
"""
YouTube Audio Player - 後方互換性のためのレガシーエントリーポイント

このファイルは後方互換性のために残されています。
新しいコードは main.py を使用してください。
"""

import sys
import warnings

# 非推奨警告を表示
warnings.warn(
    "youtube_player.py は非推奨です。代わりに main.py を使用してください。",
    DeprecationWarning,
    stacklevel=2
)

# 新しいメインモジュールをインポートして実行
from main import main

if __name__ == "__main__":
    sys.exit(main()) 