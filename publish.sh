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
# token 只出现在本次命令的 URL 里；credential.helper= 关闭凭据缓存，不落盘、不进 .git/config
PUSH_URL="https://x-access-token:${GH_TOKEN}@github.com/jinlaba/hutianxiang-resume.git"

# 网络（2026-09-14 实测）：本机 shell 里的 http_proxy/https_proxy（45301 或 45777）都是失效的，
# 真正能连 GitHub 的是 Clash 混合端口 7897。探测到就用它，探测不到则直连。
GIT_PROXY_OPTS=()
if timeout 1 bash -c "echo > /dev/tcp/127.0.0.1/7897" 2>/dev/null; then
  GIT_PROXY_OPTS=(-c http.proxy=http://127.0.0.1:7897 -c https.proxy=http://127.0.0.1:7897)
  echo "      代理：http://127.0.0.1:7897"
else
  echo "      代理：未探测到 7897，直连"
fi

if ! env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY \
       git -c credential.helper= -c http.extraheader= "${GIT_PROXY_OPTS[@]}" \
       push "$PUSH_URL" main; then
  echo "[x] 推送失败（commit 已在本地，不会丢）。手动补推："
  echo "    cd $REPO && env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY \\"
  echo "      git -c credential.helper= -c http.proxy=http://127.0.0.1:7897 -c https.proxy=http://127.0.0.1:7897 \\"
  echo "      push \"https://x-access-token:\$GH_TOKEN@github.com/jinlaba/hutianxiang-resume.git\" main"
  exit 1
fi

echo "[4/4] 完成"
echo "      线上地址： https://jinlaba.github.io/hutianxiang-resume/"
echo "      GitHub Pages 构建通常需要 1 分钟左右生效。"
