#! /bin/bash
OUTDIR="${1:-.}"
SRC_DIR="chromium-src"
BRANCH="main"
DATE_VER=$(date +%Y%m%d)
cd $SRC_DIR 2>/dev/null || { echo "Error: $SRC_DIR not found"; exit 1; }
if [ -d $SRC_DIR ] ; then
   rm -rf $SRC_DIR
fi
mkdir -p $SRC_DIR
pushd $SRC_DIR
echo "cloning depot_tools..."
git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git
export PATH+=":$PWD/depot_tools"
echo "Clone chromium-$VERSION..." 
fetch --nohooks --no-history chromium
pushd src
git checkout $BRANCH
GIT_HASH=$(git rev-parse --short HEAD)
VERSION="${DATE_VER}-main-${GIT_HASH}"
gclient sync --with_branch_heads --with_tags
popd # src
echo "$VERSION" > src/chromium-version.txt
find src -type d -name ".git" | xargs rm -rf
find src/third_party/jdk/current -type f -delete
rm -rf src/build/linux/debian_bullseye_amd64-sysroot \
       src/build/linux/debian_bullseye_i386-sysroot \
echo "Compressing cleaned tree, please wait..."
tar -cf - chromium-$VERSION | xz -9 -T 0 -f > chromium-$VERSION-clean.tar.xz
echo "Generated tarball: chromium-${VERSION}-clean.tar.xz"
echo "VERSION=$VERSION"
