#!/bin/bash
# get_chromium_from_git.sh - COPR 自动化修正版
set -euo pipefail

OUTDIR="${1:-$(pwd)}"
mkdir -p "$OUTDIR"
cd "$OUTDIR"

BRANCH="main"
DATE_VER=$(date +%Y%m%d)
WORK_DIR="chromium-work"

# 清理旧目录
[ -d "$WORK_DIR" ] && rm -rf "$WORK_DIR"
mkdir -p "$WORK_DIR"
cd "$WORK_DIR"

echo ">>> [1/6] Cloning depot_tools..."
git clone --depth 1 --branch main https://chromium.googlesource.com/chromium/tools/depot_tools.git
export PATH="$PWD/depot_tools:$PATH"

echo ">>> [2/6] Fetching Chromium src (shallow)..."
# fetch 会在当前目录创建 src/
fetch --nohooks --no-history chromium

cd src
echo ">>> [3/6] Checking out ${BRANCH}..."
git checkout "$BRANCH"

GIT_HASH=$(git rev-parse --short HEAD)
VERSION="${DATE_VER}-main-${GIT_HASH}"

echo ">>> [4/6] Running gclient sync (downloading DEPS, this takes 20-40 min)..."
gclient sync --with_branch_heads --with_tags

cd "$OUTDIR/$WORK_DIR"

echo ">>> [5/6] Recording version and cleaning up..."
echo "$VERSION" > "$OUTDIR/chromium-version.txt"

# 删除 .git 节省约 3-5GB 空间
find src -type d -name ".git" -prune -exec rm -rf {} + 2>/dev/null || true

# 删除不需要的 sysroot（spec 里 use_sysroot=false）
rm -rf src/build/linux/debian_*_sysroot 2>/dev/null || true

# 如果系统已装 Java，可删掉 bundled JDK 再省几百 MB
rm -rf src/third_party/jdk 2>/dev/null || true

echo ">>> [6/6] Renaming src -> chromium-$VERSION"
cd "$OUTDIR"
mv "$WORK_DIR/src" "chromium-$VERSION"

echo "=== Chromium main ready ==="
echo "VERSION=$VERSION"
echo "PATH=$OUTDIR/chromium-$VERSION"
du -sh "chromium-$VERSION"
