#!/usr/bin/env bash
# 一键发布在线简历
#   1. 从 Obsidian 的 06 源文件重新生成 index.html
#   2. 提交并推送到 GitHub Pages（token 只在本次命令内使用，不写入磁盘、不进仓库）
#
# 用法（二选一）：
#   GH_TOKEN=ghp_xxxxxxxx bash publish.sh
#   printf '%s' 'ghp_xxxxxxxx' > ~/.gh-token && chmod 600 ~/.gh-token && bash publish.sh
#
set -euo pipefail

REPO="/home/hu/resume-site"
PY="/home/hu/.workbuddy/binaries/python/versions/3.13.12/bin/python3"
REMOTE="https://github.com/jinlaba/hutianxiang-resume.git"

# 取 token：优先环境变量，其次 ~/.gh-token
HOME_DIR="${HOME:-/home/hu}"
if [ -z "${GH_TOKEN:-}" ] && [ -f "$HOME_DIR/.gh-token" ]; then
  GH_TOKEN="$(tr -d ' \t\r\n' < "$HOME_DIR/.gh-token")"
fi
if [ -z "${GH_TOKEN:-}" ]; then
  echo "[x] 缺少 token。请用 GH_TOKEN=xxx bash publish.sh，或把 token 写入 ~/.gh-token"
  exit 1
fi
if [ "${#GH_TOKEN}" -ne 40 ]; then
  echo "[x] token 长度是 ${#GH_TOKEN} 位，GitHub classic PAT 应为 40 位 —— 大概率复制不全，请重新复制。"
  exit 1
fi

cd "$REPO"

echo "[1/4] 生成 index.html"
"$PY" gen_resume.py

echo "[2/4] 提交"
git add index.html gen_resume.py publish.sh 2>/dev/null || git add index.html
if git diff --cached --quiet; then
  echo "      (内容无变化，跳过提交)"
else
  git -c user.name="jinlaba" -c user.email="894102027@qq.com" \
      commit -m "update resume: 凭证口径6万条 + 内部往来核对 + AI实践项目 + 首屏作品集入口"
fi

echo "[3/4] 推送"
git -c credential.helper= push "$REMOTE" main

echo "[4/4] 完成"
echo "      线上地址： https://jinlaba.github.io/hutianxiang-resume/"
echo "      GitHub Pages 构建通常需要 1 分钟左右生效。"
