#!/usr/bin/env python3
"""个人主页的静态服务。

发布平台会把整个工作区目录（包括 .workbuddy/ 内部笔记、.genie 标记文件等）
上传到沙箱，而默认的静态托管会把目录里所有文件都对外提供——那些文件不该被
访问到。这里用白名单的方式只暴露站点自身需要的文件，其余一律 404。

约定：只有 PUBLIC_FILES 里列出的文件，以及 PUBLIC_DIRS 里的目录，才可访问。
新增样式表 / 图片 / 脚本时，把所在目录加进 PUBLIC_DIRS 即可。
"""

import os
import posixpath
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

PORT = int(os.environ.get("PORT", "3000"))
ROOT = os.path.dirname(os.path.abspath(__file__))

# 允许公开访问的单个文件（相对站点根目录）
PUBLIC_FILES = {
    "index.html",
    "favicon.ico",
    "robots.txt",
    "sitemap.xml",
}

# 允许公开访问的目录（相对站点根目录的第一个路径片段）
PUBLIC_DIRS = {
    "assets",
    "css",
    "js",
    "images",
    "img",
    "fonts",
}


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def translate_path(self, path):
        raw = path.split("?", 1)[0].split("#", 1)[0]
        parts = [p for p in raw.split("/") if p and p not in (".", "..")]
        if not parts:
            parts = ["index.html"]

        rel = posixpath.join(*parts)
        allowed = rel in PUBLIC_FILES or parts[0] in PUBLIC_DIRS
        if not allowed:
            # 指向一个不存在的路径，由上层统一返回 404，不泄露目录结构
            return os.path.join(ROOT, "__not_public__")
        return os.path.join(ROOT, *parts)

    def end_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        super().end_headers()

    def log_message(self, fmt, *args):
        pass


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
