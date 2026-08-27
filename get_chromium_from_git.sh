#!/bin/bash
# get_chromium_from_git.sh - COPR 自动化 + PGO 支持版
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

echo ">>> [1/7] Cloning depot_tools..."
git clone --depth 1 --branch main https://chromium.googlesource.com/chromium/tools/depot_tools.git
export PATH="$PWD/depot_tools:$PATH"

echo ">>> [2/7] Fetching Chromium src (shallow)..."
fetch --nohooks --no-history chromium

cd src
echo ">>> [3/7] Checking out ${BRANCH}..."
git checkout "$BRANCH"

GIT_HASH=$(git rev-parse --short HEAD)
VERSION="${DATE_VER}-main-${GIT_HASH}"

echo ">>> [4/7] Running gclient sync (downloading DEPS, this takes 20-40 min)..."
gclient sync --with_branch_heads --with_tags

echo ">>> [5/7] Configuring PGO profile download..."
# 创建 .gclient 文件（如果不存在）或修改现有配置
if [ ! -f ".gclient" ]; then
    # 如果 .gclient 不存在，从 src 父目录创建
    cd ..
    cat > .gclient << EOF
solutions = [
  {
    "url": "https://chromium.googlesource.com/chromium/src.git",
    "managed": False,
    "name": "src",
    "custom_deps": {},
    "custom_vars": {
      "checkout_pgo_profiles": True,
    },
  },
]
EOF
    cd src
else
    # 如果已存在，添加 PGO 配置
    # 使用 sed 在 custom_vars 中添加 checkout_pgo_profiles
    sed -i '/"custom_vars": {/a \      "checkout_pgo_profiles": True,' ../.gclient
fi

echo ">>> [6/7] Downloading PGO profiles..."
# 运行 gclient runhooks 下载 PGO 配置
gclient runhooks

# 验证 PGO 文件是否下载成功
PGO_DIR="chrome/build/pgo_profiles"
if [ -d "$PGO_DIR" ] && [ "$(ls -A $PGO_DIR)" ]; then
    echo "PGO profiles downloaded successfully to $PGO_DIR"
    PGO_FILE=$(ls -1 $PGO_DIR/*.profdata 2>/dev/null | head -1)
    if [ -n "$PGO_FILE" ]; then
        echo "   Using PGO: $(basename $PGO_FILE)"
    fi
else
    echo "PGO profiles not found, continuing without PGO"
fi

cd "$OUTDIR/$WORK_DIR"

echo ">>> [7/7] Recording version and cleaning up..."
echo "$VERSION" > "$OUTDIR/chromium-version.txt"

# 删除 .git 节省空间
find src -type d -name ".git" -prune -exec rm -rf {} + 2>/dev/null || true

# 删除不需要的 sysroot（spec 里 use_sysroot=false）
rm -rf src/build/linux/debian_*_sysroot 2>/dev/null || true

# 如果系统已装 Java，可删掉 bundled JDK 再省几百 MB
rm -rf src/third_party/jdk 2>/dev/null || true

echo ">>> Renaming src -> chromium-$VERSION"
cd "$OUTDIR"
mv "$WORK_DIR/src" "chromium-$VERSION"

echo "=== Chromium main ready with PGO support ==="
echo "VERSION=$VERSION"
echo "PATH=$OUTDIR/chromium-$VERSION"
du -sh "chromium-$VERSION"

# 创建 PGO 标记文件，供 spec 文件检测
touch "$OUTDIR/chromium-$VERSION/.pgo_available"
