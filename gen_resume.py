#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简历生成脚本（Linux 版）
从 Obsidian 的对外简历源 Markdown 生成 GitHub Pages 用的 index.html（蓝金主题）。

用法：
    python3 gen_resume.py            # 生成 index.html
    python3 gen_resume.py --stdout   # 只打印，不写文件（用于比对）

样式（CSS）与结构复刻自 2026-09-03 线上版本，未做视觉改动。
"""
import argparse
import datetime
import pathlib
import re
import sys

SRC_MD = pathlib.Path(
    "/media/hu/本地磁盘1/obsidian/胡多多/1projects/求职/06-个人专属画像-对外简历源.md"
)
OUT_HTML = pathlib.Path(__file__).resolve().with_name("index.html")

CSS = """:root{
  --ink:#1f2733; --navy:#16294a; --navy2:#1f3a66;
  --accent:#c8a25a; --accent-soft:#f3ead6; --line:#e6e9ef;
  --muted:#5b6675; --bg:#eef1f6; --card:#ffffff;
}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;
  background:var(--bg);color:var(--ink);line-height:1.75;font-size:16px;-webkit-font-smoothing:antialiased}
.container{max-width:920px;margin:32px auto;padding:0 16px}
.header{background:linear-gradient(135deg,var(--navy) 0%,var(--navy2) 100%);color:#fff;
  border-radius:18px 18px 0 0;padding:48px 44px;display:flex;justify-content:space-between;
  align-items:flex-start;flex-wrap:wrap;position:relative;overflow:hidden}
.header::after{content:'';position:absolute;right:-40px;top:-40px;width:180px;height:180px;
  background:radial-gradient(circle,rgba(200,162,90,.25),transparent 70%)}
.header-left{position:relative;z-index:1}
.header h1{font-size:40px;font-weight:800;letter-spacing:3px;margin-bottom:6px}
.subtitle{font-size:17px;color:var(--accent);font-weight:600;letter-spacing:1px;margin-bottom:10px}
.tagline{font-size:14.5px;opacity:.85;border-top:1px solid rgba(255,255,255,.18);padding-top:10px;margin-top:10px}
.header-right{position:relative;z-index:1;text-align:right;font-size:14.5px;line-height:2;opacity:.95}
.main{background:var(--card);border-radius:0 0 18px 18px;padding:44px;
  box-shadow:0 10px 40px rgba(20,30,50,.08)}
h2{font-size:23px;font-weight:800;color:var(--navy);border-left:5px solid var(--accent);
  padding-left:14px;margin:38px 0 18px;letter-spacing:1px}
h2:first-child{margin-top:0}
h3{font-size:17.5px;font-weight:700;color:var(--navy);
  background:linear-gradient(90deg,var(--accent-soft),#fff);padding:14px 18px;border-radius:10px;
  border-left:4px solid var(--accent);margin:26px 0 12px;letter-spacing:.5px}
ul{margin:10px 0;padding-left:0;list-style:none}
li{position:relative;padding-left:22px;margin-bottom:9px;font-size:15.5px;color:#374151}
li::before{content:'';position:absolute;left:4px;top:11px;width:7px;height:7px;
  border-radius:50%;background:var(--accent)}
table{width:100%;border-collapse:separate;border-spacing:0;margin:14px 0;font-size:15px;
  border:1px solid var(--line);border-radius:10px;overflow:hidden}
th,td{border-bottom:1px solid var(--line);padding:12px 16px;text-align:left;vertical-align:top}
th{background:var(--navy);color:#fff;font-weight:700}
tr:last-child td{border-bottom:none}
blockquote{background:var(--accent-soft);border-left:4px solid var(--accent);padding:12px 18px;
  margin:10px 0;border-radius:0 8px 8px 0;color:var(--muted);font-size:14.5px}
strong{color:var(--navy);font-weight:700}
a{color:var(--navy2)}
.footer{text-align:center;padding:22px;font-size:13px;color:#9aa3b2}
@media(max-width:768px){.header{flex-direction:column;padding:30px 24px}
  .header-right{text-align:left;margin-top:16px}.main{padding:28px 20px}.container{margin:16px auto}}
@media print{body{background:#fff}.container{margin:0;max-width:100%}.main,.header{box-shadow:none}}"""


def _esc(text: str) -> str:
    """按线上页的实际风格转义：& < > \" 转义；单引号保持原样。"""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def inline(text: str) -> str:
    """Markdown 行内语法 → HTML（先转义，再放行 strong / 链接）。"""
    s = _esc(text)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(
        r"\[([^\]]+)\]\((https?://[^)]+)\)",
        r'<a href="\2" target="_blank">\1</a>',
        s,
    )
    s = re.sub(
        r'(?<![="/>])(https?://[^\s<"]+)',
        r'<a href="\1" target="_blank">\1</a>',
        s,
    )
    return s


def split_row(line: str):
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    return cells


def is_sep_row(line: str) -> bool:
    return bool(re.match(r"^\|[\s\-:|]+\|$", line.strip()))


def parse_basic_info(lines):
    """从「## 一、基本信息」后的表格里取字段。"""
    info = {}
    try:
        start = next(i for i, l in enumerate(lines) if l.startswith("## 一、"))
    except StopIteration:
        return info, 0
    i = start + 1
    while i < len(lines) and not lines[i].strip().startswith("|"):
        i += 1
    while i < len(lines) and lines[i].strip().startswith("|"):
        cells = split_row(lines[i])
        if len(cells) >= 2 and cells[0] not in ("项", "----") and not is_sep_row(lines[i]):
            info[cells[0]] = cells[1]
        i += 1
    # 正文从基本信息表结束处开始（保留「核心标签」「作品集 Demo」等首屏内容）
    return info, i


def render_body(lines):
    out = []
    list_open = False
    table_buf = []
    i = 0

    def close_list():
        nonlocal list_open
        if list_open:
            out.append("</ul>")
            list_open = False

    def flush_table():
        nonlocal table_buf
        if not table_buf:
            return
        rows = [r for r in table_buf if not is_sep_row(r)]
        if rows:
            head = split_row(rows[0])
            out.append("<table>")
            out.append(
                "<thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in head) + "</tr></thead>"
            )
            out.append("<tbody>")
            for r in rows[1:]:
                cells = split_row(r)
                tds = "".join(f"<td>{inline(c)}</td>" for c in cells)
                out.append(f"<tr>{tds}</tr>")
            out.append("</tbody></table>")
        table_buf = []

    while i < len(lines):
        raw = lines[i]
        line = raw.rstrip()
        s = line.strip()

        if s.startswith("|"):
            close_list()
            table_buf.append(s)
            i += 1
            continue
        flush_table()

        # 代码块整体跳过（公开简历页不展示内部脚本）
        if s.startswith("```"):
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                i += 1
            i += 1
            continue

        if not s or s == "---" or s.startswith("# "):
            close_list()
            i += 1
            continue

        if s.startswith("## "):
            close_list()
            out.append(f"<h2>{inline(s[3:].strip())}</h2>")
        elif s.startswith("### "):
            close_list()
            out.append(f"<h3>{inline(s[4:].strip())}</h3>")
        elif s.startswith("- "):
            if not list_open:
                out.append("<ul>")
                list_open = True
            out.append(f"<li>{inline(s[2:].strip())}</li>")
        elif s.startswith("> "):
            close_list()
            out.append(f"<blockquote><p>{inline(s[2:].strip())}</p></blockquote>")
        else:
            close_list()
            out.append(f"<p>{inline(s)}</p>")
        i += 1

    flush_table()
    close_list()
    return out


# 正文截止标记：出现这些二级标题之后的内容属于"内部操作说明"，不上公开简历页
STOP_HEADINGS = ("🔄", "简历部署", "关联笔记", "部署与同步")


def cut_at_internal_sections(lines, start):
    """从 start 起渲染，遇到内部说明章节就截断。"""
    for k in range(start, len(lines)):
        s = lines[k].strip()
        if s.startswith("## ") and any(t in s for t in STOP_HEADINGS):
            return lines[:k]
    return lines


def build(md_text: str) -> str:
    lines = md_text.splitlines()
    info, body_start = parse_basic_info(lines)
    lines = cut_at_internal_sections(lines, body_start)

    name = info.get("姓名", "")
    intent = info.get("求职意向", "")
    age = info.get("年龄", "")
    exp = info.get("经验", "")
    phone = info.get("电话", "")
    mail = info.get("邮箱", "")
    city = info.get("期望城市", "")

    tagline = " ｜ ".join(x for x in (age, exp) if x)

    parts = []
    parts.append("<!DOCTYPE html>")
    parts.append("<html lang='zh-CN'>")
    parts.append("<head>")
    parts.append("<meta charset='UTF-8'>")
    parts.append("<meta name='viewport' content='width=device-width, initial-scale=1.0'>")
    parts.append(f"<title>{name} - {intent} - 个人简历</title>")
    parts.append("<style>")
    parts.append(CSS)
    parts.append("</style>")
    parts.append("</head>")
    parts.append("<body>")
    parts.append("<div class='container'>")
    parts.append("<div class='header'>")
    parts.append("<div class='header-left'>")
    parts.append(f"<h1>{name}</h1>")
    parts.append(f"<div class='subtitle'>{intent}</div>")
    parts.append(f"<div class='tagline'>{tagline}</div>")
    parts.append("</div>")
    parts.append("<div class='header-right'>")
    parts.append(f"📱 {phone}<br>")
    parts.append(f"✉️ {mail}<br>")
    parts.append(f"📍 {city}")
    parts.append("</div>")
    parts.append("</div>")
    parts.append("<div class='main'>")
    parts.extend(render_body(lines[body_start:]))
    parts.append("</div>")
    today = datetime.date.today().isoformat()
    parts.append(
        f"<div class='footer'>最后更新：{today} ｜ 由「个人专属画像」自动生成</div>"
    )
    parts.append("</div>")
    parts.append("</body>")
    parts.append("</html>")
    return "\n".join(parts) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=str(SRC_MD))
    ap.add_argument("--out", default=str(OUT_HTML))
    ap.add_argument("--stdout", action="store_true")
    args = ap.parse_args()

    src = pathlib.Path(args.src)
    if not src.exists():
        sys.exit(f"[x] 源文件不存在：{src}")
    md = src.read_text(encoding="utf-8")
    result = build(md)

    if args.stdout:
        sys.stdout.write(result)
        return
    pathlib.Path(args.out).write_text(result, encoding="utf-8")
    print(f"[√] 已生成 {args.out}")
    print(f"    源文件：{src}")


if __name__ == "__main__":
    main()
