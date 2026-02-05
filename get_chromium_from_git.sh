#! /bin/bash

SRC_DIR="chromium-src"
VERSION="$1"
# clean|remove
FFMPEG_SOURCE="remove"

if [[ -z $VERSION ]]; then
  echo "Version is missing"
  exit 1
fi

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
git fetch origin tag $VERSION
git checkout tags/$VERSION
gclient sync --with_branch_heads --with_tags
popd # src

find src -type d -name ".git" | xargs rm -rf
find src/third_party/jdk/current -type f -delete
rm -rf src/build/linux/debian_bullseye_amd64-sysroot \
       src/build/linux/debian_bullseye_i386-sysroot \
       src/third_party/node/linux/node-linux-x64* \
       src/third_party/rust-toolchain \
       src/third_party/rust-src \
       src/third_party/devtools-frontend/src/third_party/esbuild \
       src/third_party/enterprise_companion/chromium_linux64 \
       src/third_party/enterprise_companion/chromium_mac_amd64 \
       src/third_party/enterprise_companion/chromium_mac_arm64 \
       src/third_party/enterprise_companion/chromium_win_x86 \
       src/third_party/enterprise_companion/chromium_win_x86_64 \
       src/third_party/node/linux/node-linux-x64.tar.gz \
       src/buildtools/third_party/eu-strip/bin/eu-strip \
       src/buildtools/linux64/gn

if [ "$FFMPEG_SOURCE" == "clean" ] ; then
   # clean ffmpeg from proprietary things
   echo "Cleaning ffmpeg from proprietary things..."
   ln -s ../clean_ffmpeg.sh .
   ln -s ../ffmpeg-clean.patch .
   ln -s ../get_free_ffmpeg_source_files.py .
   ./clean_ffmpeg.sh src 1
else
   # remove ffmpeg source
   find src/third_party/ffmpeg/* -type d | xargs rm -rf
fi

# clean openh264
echo "Cleaning openh264 from proprietary things..."
find src/third_party/openh264/src -type f -not -name '*.h' -delete
mv src ../chromium-$VERSION
popd

echo "Compressing cleaned tree, please wait..."
tar -cf - chromium-$VERSION | xz -9 -T 0 -f > chromium-$VERSION-clean.tar.xz

echo "Done!"
