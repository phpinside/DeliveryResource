#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把当前目录当成静态 HTML 站点启动。

用法:
    python3 serve.py                    # 默认 http://127.0.0.1:8000
    python3 serve.py -p 8080            # 换端口
    python3 serve.py --host 0.0.0.0     # 允许同一局域网的手机/同事访问
    python3 serve.py --no-browser       # 不自动打开浏览器

最简版其实只需要一行:
    python3 -m http.server 8000
"""

from __future__ import annotations

import argparse
import contextlib
import functools
import os
import socket
import sys
import threading
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

# 这些类型的响应统一补上 UTF-8，避免中文页面在某些浏览器里乱码
UTF8_SUFFIX_TYPES = (
    "text/html",
    "text/css",
    "text/plain",
    "text/xml",
    "application/javascript",
    "application/json",
    "image/svg+xml",
)


class Handler(SimpleHTTPRequestHandler):
    """在标准静态文件处理器上补三件事：UTF-8、禁缓存、安静一点的日志。"""

    # 让浏览器走正确的 MIME（.mjs/.webp 等老版本 Python 不认识）
    extensions_map = {
        **SimpleHTTPRequestHandler.extensions_map,
        ".mjs": "application/javascript",
        ".webp": "image/webp",
        ".avif": "image/avif",
        ".woff2": "font/woff2",
        ".json": "application/json",
    }

    def end_headers(self) -> None:
        # 开发期禁缓存：改完 HTML 刷新即可看到效果
        self.send_header("Cache-Control", "no-store, must-revalidate")
        super().end_headers()

    def guess_type(self, path):  # type: ignore[override]
        ctype = super().guess_type(path)
        if ctype in UTF8_SUFFIX_TYPES:
            return ctype + "; charset=utf-8"
        return ctype

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write("[%s] %s\n" % (self.log_date_time_string(), fmt % args))


class Server(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True  # 重启时不会卡在 "Address already in use"


def free_port(host: str, port: int) -> bool:
    """端口是否可用，用于给出更友好的报错。"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind((host, port))
        except OSError:
            return False
    return True


def main() -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser(description="用 Python 启动静态 HTML 站点")
    ap.add_argument("-d", "--dir", default=here, help="站点根目录（默认脚本所在目录）")
    ap.add_argument("-p", "--port", type=int, default=8000, help="端口，默认 8000")
    ap.add_argument("--host", default="127.0.0.1", help="监听地址，默认仅本机；0.0.0.0 表示局域网可访问")
    ap.add_argument("--no-browser", action="store_true", help="启动后不自动打开浏览器")
    args = ap.parse_args()

    root = os.path.abspath(args.dir)
    if not os.path.isdir(root):
        print(f"目录不存在: {root}", file=sys.stderr)
        return 1

    if not free_port(args.host, args.port):
        print(f"端口被占用: {args.host}:{args.port}，换一个试试（-p 8080）", file=sys.stderr)
        return 1

    handler = functools.partial(Handler, directory=root)
    httpd = Server((args.host, args.port), handler)

    shown = "127.0.0.1" if args.host in ("0.0.0.0", "::") else args.host
    url = f"http://{shown}:{args.port}/"
    print(f"站点根目录: {root}")
    print(f"已启动:     {url}   (Ctrl+C 停止)")
    if args.host in ("0.0.0.0", "::"):
        with contextlib.suppress(OSError):
            lan = socket.gethostbyname(socket.gethostname())
            print(f"局域网访问: http://{lan}:{args.port}/")

    if not args.no_browser:
        threading.Timer(0.4, lambda: webbrowser.open(url)).start()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止")
    finally:
        httpd.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
