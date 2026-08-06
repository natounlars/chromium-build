# macro for el10 minor version
%if 0%{?rhel} == 10
#%global rhel_minor_version %(echo %{dist} | sed -n 's/.*el10_\\([0-9]\\+\\).*/\\1/p')
%endif
%global main_version %(cat %{_sourcedir}/chromium-version.txt)
Name: chromium
Version: %{main_version}
Release: 1%{?dist}

# Fix installation issue caused by the hard link in locales
%define __os_install_post_hardlink %{nil}

%define _lto_cflags %{nil}
%global _default_patch_fuzz 2

# enable|disable system build flags
%global system_build_flags 0

%global numjobs %{_smp_build_ncpus}

# official builds have less debugging and go faster... but we have to shut some things off.
%global official_build 1

# enable|disble use_custom_libcxx
%global use_custom_libcxx 1

# enable|disble bootstrap
%global bootstrap 0
# workaround for old gn on el9, it causes build error: unknown function filter_labels_include()
%if 0%{?rhel} == 9
%global bootstrap 1
%endif

# Fancy build status, so we at least know, where we are..
# %1 where
# %2 what
%global build_target() \
	export NINJA_STATUS="[%2:%f/%t] " ; \
	ninja -j %{numjobs} -C '%1' '%2'

# enable|disable chrome_management_service
%global build_chrome_management_service 1
%if 0%{?flatpak}
%global build_chrome_management_service 0
%endif

# enable|disable chromedriver
%global build_chromedriver 1
%if 0%{?flatpak}
%global build_chromedriver 0
%endif

# enable|disable headless client build
%global build_headless 1
%if 0%{?flatpak}
%global build_headless 0
%endif

%global system_nodejs 1
# RHEL 9 needs newer nodejs
%if 0%{?rhel} == 9
%global system_nodejs 0
%endif

# enable gtk4 for fedora and el>9
%global gtk_version 4
%if 0%{?rhel} == 9
%global gtk_version 3
%endif

%if 0%{?rhel} == 8
%global chromium_pybin /usr/bin/python3.9
%else
%global chromium_pybin %{__python3}
%endif

# va-api only supported in rhel >= 9 and fedora
%global use_vaapi 1

# v4l2_codec only enable for fedora aarch64
%global use_v4l2_codec 0

# libva is too old on el8
%if 0%{?rhel} == 8
%global use_vaapi 0
%endif

# enable v4l2 and disable vaapi for aarch64 platform
%ifarch aarch64
%if 0%{?fedora} >= 36
%global use_vaapi 0
%global use_v4l2_codec 1
%endif
%endif

%if 0%{?fedora} >= 40 || 0%{?rhel} >= 9
%global noopenh264 1
%endif

# Workaround for https://bugzilla.redhat.com/show_bug.cgi?id=2239523
# Disable BTI until this is fixed upstream.
%global disable_bti 0
%ifarch aarch64
%if 0%{?fedora}
%global optflags %(echo %{optflags} | sed 's/-mbranch-protection=standard /-mbranch-protection=pac-ret /')
%global disable_bti 1
%endif
%endif

# Disabled because of Google, starting with Chromium 88.
%global userestrictedapikeys 0

# We can still use the api key though. For now.
%global useapikey 1

# Leave this alone, please.
%global chromebuilddir out/Release
%global headlessbuilddir out/Headless
%global remotingbuilddir out/Remoting

# enable|disable debuginfo
%global enable_debug 0
# disable debuginfo due to a bug in debugedit on el7
# error: canonicalization unexpectedly shrank by one character
# https://bugzilla.redhat.com/show_bug.cgi?id=304121
%if ! %{enable_debug}
%global debug_package %{nil}
%global debug_level 0
%else
%global debug_level 1
# workaround for the error empty file debugsource
%undefine _debugsource_packages
%endif

%global chromium_menu_name Chromium
%global chromium_path %{_libdir}/chromium-browser
%global crd_path %{_libdir}/chrome-remote-desktop

# We don't want any libs in these directories to generate Provides
# Requires is trickier.

# To generate this list, go into %%{buildroot}%%{chromium_path} and run
# for i in `find . -name "*.so" | sort`; do NAME=`basename -s .so $i`; printf "$NAME|"; done
# for RHEL7, append libfontconfig to the end
# make sure there is not a trailing | at the end of the list
# We always filter provides. We only filter Requires when building shared.
%global __provides_exclude_from ^(%{chromium_path}/.*\\.so|%{chromium_path}/.*\\.so.*)$
%global __requires_exclude ^(%{chromium_path}/.*\\.so|%{chromium_path}/.*\\.so.*)$

# enable|disable control flow integrity support
%global cfi 0
%ifarch x86_64 aarch64
%global cfi 1
%endif

# enable qt backend
%global enable_qt 1
%if %{enable_qt}
%if 0%{?rhel} > 9 || 0%{?fedora} > 39
%global use_qt6 1
%global use_qt5 1
%else
%global use_qt6 0
%global use_qt5 1
%endif
%else
%global use_qt6 0
%global use_qt5 0
%endif

# bundle re2, jsoncpp, woff2 - build errors with use_custom_libcxx=true
%global bundlere2 1
%global bundlejsoncpp 1
%global bundlewoff2 1
%global bundlelibaom 1
%global bundlelibavif 1
%global bundlesnappy 1
%global bundlezstd 1
%global bundleicu 1
%global bundledav1d 1
%global bundlebrotli 1
%global bundlelibwebp 1
%global bundlecrc32c 1
%global bundleharfbuzz 1
%global bundlelibpng 1
%global bundlelibjpeg 1
%global bundlefreetype 1
%global bundlelibdrm 1
%global bundlefontconfig 1
%global bundleffmpegfree 1
%global bundlehighway 1
# openjpeg2, need to update to 2.5.x
%global bundlelibopenjpeg2 1
%global bundlelibtiff 1
# libxml2, need to update to 2.14.x for bz#2368923
%global bundlelibxml 1
%global bundlepylibs 1
%global bundlelibxslt 1
%global bundleflac 1
%global bundledoubleconversion 1
%global bundlelibXNVCtrl 1
%global bundlelibusbx 1
%global bundlelibsecret 1
%global bundleopus 1
%global bundlelcms2 1
%global bundlesimdutf 1

# workaround for build error
# disable bundleminizip for Fedora > 39 due to switch to minizip-ng
# disable bundleminizip for epel and Fedora39 due to old minizip version
%global bundleminizip 1

### From 2013 until early 2021, Google permitted distribution builds of
### Chromium to access Google APIs that added significant features to
### Chromium including, but not limited to, Sync and geolocation.
### As of March 15, 2021, any Chromium builds which pass client_id and/or
### client_secret during build will prevent end-users from signing into their
### Google account.

### With Chromium 88, I have removed the calls to "google_default_client_id"
### and "google_default_client_secret" to comply with their changes.

### Honestly, at this point, you might be better off looking for a different
### FOSS browser.

### Google API keys (see http://www.chromium.org/developers/how-tos/api-keys)
### Note: These are for Fedora use ONLY.
### For your own distribution, please get your own set of keys.
### http://lists.debian.org/debian-legal/2013/11/msg00006.html
%if %{useapikey}
%global api_key AIzaSyDUIXvzVrt5OkVsgXhQ6NFfvWlA44by-aw
%else
%global api_key %nil
%endif

%if %{userestrictedapikeys}
%global default_client_id 449907151817.apps.googleusercontent.com
%global default_client_secret miEreAep8nuvTdvLums6qyLK
%global chromoting_client_id 449907151817-8vnlfih032ni8c4jjps9int9t86k546t.apps.googleusercontent.com 
%else
%global default_client_id %nil
%global default_client_secret %nil
%global chromoting_client_id %nil
%endif

Summary: A WebKit (Blink) powered web browser that Google doesn't want you to use
Url: http://www.chromium.org/Home
License: BSD-3-Clause AND LGPL-2.1-or-later AND Apache-2.0 AND IJG AND MIT AND GPL-2.0-or-later AND ISC AND OpenSSL AND (MPL-1.1 OR GPL-2.0-only OR LGPL-2.0-only)

# Use /etc/chromium for initial_prefs
Patch1: chromium-115-initial_prefs-etc-path.patch

# Try to load widevine from other places
Patch8: chromium-117-widevine-other-locations.patch

# Fix link error when building with system libcxx
Patch22: chromium-131-fix-qt-ui.pach

# Workaround for build error: ERROR Unresolved dependencies.
#//chrome/test:captured_sites_interactive_tests(//build/toolchain/linux/unbundle:default)

# revert the patch to fix the build error: "ld.lld: error: undefined symbol: __sanitizer_set_death_callback"
Patch94: chromium-148-v8-sanitize-build-error.patch

# FTBFS - error: cannot find attribute `sanitize` in this scope
#    --> ../../third_party/crabbyavif/src/src/capi/io.rs:210:41
#     |
# 210 |     #[cfg_attr(feature = "disable_cfi", sanitize(cfi = "off"))]
Patch96: chromium-142-crabbyavif-ftbfs-old-rust.patch

# add correct path for Qt6Gui header and libs
Patch150: chromium-124-qt6.patch

# Fix FTBSF with kernel-7.2.0 (fedora 45 and rhel-11)

# flatpak sandbox patches from
# https://github.com/flathub/org.chromium.Chromium/tree/master/patches/chromium
# Darkmode
Patch603: chromium-150-Add-AutoDarkModeSkipImages-flag-to-bypass-image-dark-mode.patch
Patch604: chromium-150-Make-dark-mode-apply-filter-to-images-irrespective-of-layout-zoom.patch
Patch605: chromium-150-Use-64px-css-pixels-absolute-threshold-for-dark-image-classification.patch
Patch606: chromium-150-Add-size-threshold-for-classifying-SVG-documents-for-auto-dark-mode.patch

# Use chromium-latest.py to generate clean tarball from released build tarballs, found here:
# http://build.chromium.org/buildbot/official/
# For Chromium Fedora use chromium-latest.py --stable --ffmpegclean --ffmpegarm
# If you want to include the ffmpeg arm sources append the --ffmpegarm switch
# https://commondatastorage.googleapis.com/chromium-browser-official/chromium-%%{version}.tar.xz
Source0: get_chromium_from_git.sh
Source1: README.fedora
Source2: chromium.conf
Source3: chromium-browser.sh
Source4: chromium-browser.desktop
# Also, only used if you want to reproduce the clean tarball.
Source5: clean_ffmpeg.sh
# Get the names of all tests (gtests) for Linux
# Usage: get_linux_tests_name.py chromium-%%{version} --spec
#Source8: get_linux_tests_names.py
# GNOME stuff
Source9: chromium-browser.xml
Source10: chromium-browser.appdata.xml
Source11: master_preferences
Source12: chromium-version.txt
BuildRequires: clang
BuildRequires: clang-tools-extra
BuildRequires: llvm
BuildRequires: lld

%if ! %{use_custom_libcxx}
BuildRequires: libcxx-devel
%endif

%if 0%{?rhel} && 0%{?rhel} <= 9
BuildRequires: gcc-toolset-14-libatomic-devel
%endif
BuildRequires: rustc
BuildRequires: rustfmt
BuildRequires: bindgen-cli

%if ! %{bundlezstd}
BuildRequires: libzstd-devel
%endif

# build with system ffmpeg-free
%if ! %{bundleffmpegfree}
BuildRequires: pkgconfig(libavcodec)
BuildRequires: pkgconfig(libavfilter)
BuildRequires: pkgconfig(libavformat)
BuildRequires: pkgconfig(libavutil)
%endif

%if 0%{?noopenh264}
BuildRequires: pkgconfig(openh264)
%endif

# build with system libaom
%if ! %{bundlelibaom}
BuildRequires: libaom-devel
%endif

BuildRequires:	alsa-lib-devel
BuildRequires:	atk-devel
BuildRequires:	bison
BuildRequires:	cups-devel
BuildRequires:	dbus-devel
BuildRequires:	desktop-file-utils
BuildRequires:	expat-devel
BuildRequires:	flex
BuildRequires:	fontconfig-devel
BuildRequires:	glib2-devel
BuildRequires:	glibc-devel
BuildRequires:	gperf

%if %{use_qt5}
BuildRequires: pkgconfig(Qt5Core)
BuildRequires: pkgconfig(Qt5Widgets)
%endif

%if %{use_qt6}
BuildRequires: pkgconfig(Qt6Core)
BuildRequires: pkgconfig(Qt6Widgets)
%endif

BuildRequires: compiler-rt

%if ! %{bundleharfbuzz}
BuildRequires:	harfbuzz-devel >= 2.4.0
%endif

BuildRequires: libatomic
BuildRequires:	libcap-devel
BuildRequires:	libcurl-devel

%if ! %{bundlelibdrm}
BuildRequires:	libdrm-devel
%endif

BuildRequires:	libgcrypt-devel
BuildRequires:	libudev-devel
BuildRequires:	libuuid-devel

%if 0%{?fedora} >= 37 || 0%{?rhel} > 9
BuildRequires:	libusb-compat-0.1-devel
%else
BuildRequires:	libusb-devel
%endif

BuildRequires:	libutempter-devel
BuildRequires:	libXdamage-devel
BuildRequires:	libXtst-devel
BuildRequires:	xcb-proto
BuildRequires:	mesa-libgbm-devel

# Old Fedora (before 30) uses the 1.2 minizip by default.
# Newer Fedora needs to use the compat package
# Fedora > 39 uses minizip-ng
%if ! %{bundleminizip}
%if 0%{?fedora} > 39 || 0%{?rhel} > 9
# BuildRequires: minizip-ng-devel
BuildRequires: minizip-compat-devel
%else
BuildRequires: minizip-compat-devel
%endif
%endif

BuildRequires: nodejs, /usr/bin/node

%if ! %{bootstrap}
BuildRequires: gn
%endif

BuildRequires:	nss-devel >= 3.26
BuildRequires:	pciutils-devel
BuildRequires:	pulseaudio-libs-devel

# For screen sharing on Wayland
# pipewire is old on el8, chromium needs new version, disable it temporary
%if 0%{?fedora} || 0%{?rhel} > 8
BuildRequires:	pipewire-devel
%endif

# for /usr/bin/appstream-util
BuildRequires: libappstream-glib

%if %{bootstrap}
# gn needs these
BuildRequires: libstdc++-static
%endif

# Fedora tries to use system libs whenever it can.
BuildRequires:	bzip2-devel
BuildRequires:	dbus-glib-devel
# For eu-strip
BuildRequires:	elfutils
BuildRequires:	elfutils-libelf-devel

%if ! %{bundleflac}
BuildRequires:	flac-devel
%endif

%if ! %{bundlefreetype}
BuildRequires:	freetype-devel
%endif

%if ! %{bundlecrc32c}
BuildRequires: google-crc32c-devel
%endif

%if ! %{bundlewoff2}
BuildRequires: woff2-devel
%endif

%if ! %{bundledav1d}
BuildRequires: libdav1d-devel
%endif

%if ! %{bundlehighway}
BuildRequires: highway-devel
%endif

%if ! %{bundlelibavif}
BuildRequires: libavif-devel
%endif

%if ! %{bundlejsoncpp}
BuildRequires: jsoncpp-devel
%endif

%if ! %{bundlelibsecret}
BuildRequires: libsecret-devel
%endif

%if ! %{bundledoubleconversion}
BuildRequires: double-conversion-devel
%endif

%if ! %{bundlesnappy}
BuildRequires: snappy-devel
%endif

%if ! %{bundlelibXNVCtrl}
BuildRequires: libXNVCtrl-devel
%endif

# One of the python scripts invokes git to look for a hash. So helpful.
BuildRequires:	git-core
BuildRequires:	hwdata
BuildRequires:	kernel-headers
BuildRequires:	libffi-devel

%if ! %{bundleicu}
# If this is true, we're using the bundled icu.
# We'd like to use the system icu every time, but we cannot always do that.
# Not newer than 54 (at least not right now)
BuildRequires:	libicu-devel >= 68
%endif

%if ! %{bundlelibjpeg}
# If this is true, we're using the bundled libjpeg
# which we need to do because the RHEL 7 libjpeg doesn't work for chromium anymore
BuildRequires:	libjpeg-devel
%endif

%if ! %{bundlelibpng}
# If this is true, we're using the bundled libpng
# which we need to do because the RHEL 7 libpng doesn't work right anymore
BuildRequires:	libpng-devel
%endif

%if ! %{bundlelibopenjpeg2}
BuildRequires: openjpeg2-devel
%endif

%if ! %{bundlelcms2}
BuildRequires: lcms2-devel
%endif

%if ! %{bundlelibtiff}
BuildRequires: libtiff-devel
%endif

BuildRequires:	libudev-devel

%if ! %{bundlelibusbx}
Requires: libusbx >= 1.0.21-0.1.git448584a
BuildRequires: libusbx-devel >= 1.0.21-0.1.git448584a
%endif

%if %{use_vaapi}
BuildRequires:	libva-devel
%endif

# We don't use libvpx anymore because Chromium loves to
# use bleeding edge revisions here that break other things
# ... so we just use the bundled libvpx.
%if ! %{bundlelibwebp}
BuildRequires:	libwebp-devel
%endif

%if ! %{bundlelibxslt}
BuildRequires:	libxslt-devel
%endif

BuildRequires:	libxshmfence-devel

# Same here, it seems.
# BuildRequires: libyuv-devel
BuildRequires:	mesa-libGL-devel

%if ! %{bundleopus}
BuildRequires:	opus-devel
%endif

BuildRequires: %{chromium_pybin}
%if %{gtk_version} == 4
BuildRequires: pkgconfig(gtk4)
BuildRequires: pkgconfig(xcursor)
BuildRequires: pkgconfig(xi)
BuildRequires: pkgconfig(xrender)
BuildRequires: pkgconfig(xscrnsaver)
BuildRequires: pkgconfig(xshmfence)
BuildRequires: pkgconfig(xt)
BuildRequires: pkgconfig(xtst)
BuildRequires: pkgconfig(x11)
BuildRequires: pkgconfig(xcb-dri3)
BuildRequires: pkgconfig(xcb-proto)
Requires: gtk4
%else
BuildRequires: pkgconfig(gtk+-3.0)
# GTK modules it expects to find for some reason.
Requires: libcanberra-gtk3%{_isa}
%endif

# Build deps of Chromium proper which are often transitively pulled in by toolkits (GTK, Qt),
# but are still required without them.
BuildRequires: pkgconfig(atspi-2)
BuildRequires: pkgconfig(atk-bridge-2.0)
BuildRequires: pkgconfig(pangocairo)
BuildRequires: pkgconfig(xkbcommon)
BuildRequires: pkgconfig(xcomposite)
BuildRequires: pkgconfig(xrandr)
BuildRequires: wayland-devel

%if ! %{bundlepylibs}
%if 0%{?fedora} || 0%{?rhel} >= 8
BuildRequires: python3-jinja2
%else
BuildRequires: python-jinja2
%endif
%endif

%if ! %{bundlere2}
Requires: re2 >= 20160401
BuildRequires: re2-devel >= 20160401
%endif

%if ! %{bundlebrotli}
BuildRequires: brotli-devel
%endif

BuildRequires: speech-dispatcher-devel
BuildRequires: zlib-devel

# remote desktop needs this
BuildRequires:	pam-devel
BuildRequires:	systemd

# using the built from source version on aarch64
BuildRequires: ninja-build

# Yes, java is needed as well..
%if %{build_headless}
BuildRequires:	java-openjdk-headless
%endif

BuildRequires: libevdev-devel

%if ! %{bundlesimdutf}
BuildRequires: simdutf-devel
%endif

# esbuild is needed
BuildRequires: golang-github-evanw-esbuild

# There is a hardcoded check for nss 3.26 in the chromium code (crypto/nss_util.cc)
Requires: nss%{_isa} >= 3.26
Requires: nss-mdns%{_isa}

%if 0%{?fedora} && %{undefined flatpak}
# This enables support for u2f tokens
Requires: u2f-hidraw-policy
%endif

Requires: chromium-common%{_isa} = %{version}-%{release}

ExclusiveArch: x86_64 aarch64 ppc64le

# Bundled bits (I'm sure I've missed some)
Provides: bundled(bintrees) = 1.0.1
# This is a fork of openssl.
Provides: bundled(boringssl)
%if %{bundlebrotli}
Provides: bundled(brotli) = 222564a95d9ab58865a096b8d9f7324ea5f2e03e
%endif
%if %{bundlesimdutf} 
Provides: bundled(simdutf) = 7.0.0
%endif
Provides: bundled(bspatch) = 465265d0d473d107b76e74d969199eaf2cdc8750
Provides: bundled(colorama) = 0.4.6
Provides: bundled(crashpad) = 8f131016b21d986c38ca4a0f091403dbb822d636
Provides: bundled(expat) = 2.7.1
Provides: bundled(fdmlibm) = c512d6173f33c6b8301d3fba9384edc9fc1f9e45

# Don't get too excited. MPEG and other legally problematic stuff is stripped out.
%if %{bundleffmpegfree}
Provides: bundled(ffmpeg) = 7.1.git
%endif

%if %{bundlelibaom}
Provides: bundled(libaom) = 3.12.1
%endif

%if %{bundlefontconfig}
Provides: bundled(fontconfig) = 8cf0ce700a8abe0d97ace4bf7efc7f9534b729ba
%endif

%if %{bundleharfbuzz}
Provides: bundled(harfbuzz) = 11.0.0-97
%endif

Provides: bundled(hunspell) = 6d7d19f

%if %{bundleicu}
Provides: bundled(icu) = 74-2
%endif

Provides: bundled(leveldb) = 1.23
Provides: bundled(libaddressinput) = 2610f7b104

%if %{bundlelibdrm}
Provides: bundled(libdrm) = 2.4.122
%endif

Provides: bundled(libjingle) = 5493b8a59deb16cf0481e24707a0ed72d19047dc

%if %{bundlelibjpeg}
Provides: bundled(libjpeg-turbo) = 3.1.0
%endif

Provides: bundled(libphonenumber) = 140dfeb81b753388e8a672900fb7a971e9a0d362

%if %{bundlelibpng}
Provides: bundled(libpng) = 1.6.43
%endif

Provides: bundled(libsrtp) = fd08747fa6800b321d53e15feb34da12dc697dee

%if %{bundlelibusbx}
Provides: bundled(libusbx) = 1.0.17
%endif

Provides: bundled(libvpx) = 1.6.0

%if %{bundlelibwebp}
Provides: bundled(libwebp) = 0.6.0
%endif

%if %{bundlelibxml}
Provides: bundled(libxml) = 2.14.2
%endif

%if %{bundlelibXNVCtrl}
Provides: bundled(libXNVCtrl) = 302.17
%endif
Provides: bundled(libyuv) = 1909
Provides: bundled(lzma) = 24.09

%if %{bundleopus}
Provides: bundled(opus) = 55513e81
%endif

Provides: bundled(ots) = 8d70cffebbfa58f67a5c3ed0e9bc84dccdbc5bc0
Provides: bundled(protobuf) = 3.0.0.beta.3
Provides: bundled(qcms) = 4

%if %{bundlere2}
Provides: bundled(re2)
%endif

Provides: bundled(sfntly) = 04740d2600193b14aa3ef24cd9fbb3d5996b9f77
Provides: bundled(skia)
Provides: bundled(SMHasher) = 0
Provides: bundled(snappy) = 1.1.4-head
Provides: bundled(speech-dispatcher) = 0.7.1
Provides: bundled(sqlite) = 3.17patched
Provides: bundled(superfasthash) = 0
Provides: bundled(talloc) = 2.0.1
Provides: bundled(usrsctp) = 0
Provides: bundled(v8) = 5.9.211.31
Provides: bundled(webrtc) = 90usrsctp
Provides: bundled(woff2) = 445f541996fe8376f3976d35692fd2b9a6eedf2d
Provides: bundled(xdg-mime)
Provides: bundled(xdg-user-dirs)
# Provides: bundled(zlib) = 1.2.11

%if %{undefined flatpak}
# For selinux scriptlet
Requires(post): /usr/sbin/semanage
Requires(post): /usr/sbin/restorecon
%endif

%description
Chromium is an open-source web browser, powered by WebKit (Blink).

%package common
Summary: Files needed for both the headless_shell and full Chromium

%description common
%{summary}.

%package -n chromedriver
Summary: WebDriver for Google Chrome/Chromium
Requires: chromium-common%{_isa} = %{version}-%{release}

%description -n chromedriver
WebDriver is an open source tool for automated testing of webapps across many
browsers. It provides capabilities for navigating to web pages, user input,
JavaScript execution, and more. ChromeDriver is a standalone server which
implements WebDriver's wire protocol for Chromium. It is being developed by
members of the Chromium and WebDriver teams.

%package headless
Summary:	A minimal headless shell built from Chromium
Requires: chromium-common%{_isa} = %{version}-%{release}

%description headless
A minimal headless client built from Chromium. headless_shell is built
without support for alsa, cups, dbus, gconf, gio, kerberos, pulseaudio, or 
udev.

%package qt5-ui
Summary: Qt5 UI built from Chromium
Requires: chromium%{_isa} = %{version}-%{release}

%description qt5-ui
Qt5 UI for chromium.

%package qt6-ui
Summary: Qt6 UI built from Chromium
Requires: chromium%{_isa} = %{version}-%{release}

%description qt6-ui
Qt6 UI for chromium.

%prep
bash %{SOURCE0} %{_builddir}
VERSION=$(cat %{_builddir}/chromium-version.txt)
cd %{_builddir}
rm -rf chromium-%{version}
mv chromium-${VERSION} chromium-%{version}
cd chromium-%{version}

### Chromium Fedora Patches ###
%patch -P1 -p1 -b .etc
%patch -P8 -p1 -b .widevine-other-locations

%patch -P20 -p1 -b .disable-font-test
%patch -P21 -p1 -b .screen-ai-service
%if ! %{use_custom_libcxx}
%patch -P22 -p1 -b .fix-qt-ui
%endif

%patch -P92 -p1 -b .nodejs-checkversion
%patch -P93 -p1 -b .ftbfs-csss_style_sheet
%patch -P94 -p1 -R -b .v8-sanitize-build-error
%patch -P96 -p1 -b .crabbyavif-ftbfs-old-rust

%if 0%{?fedora} > 44 || 0%{?rhel} > 10 
%patch -P450 -p1 -b .pt_regs-kernel-7.2.0
%endif

# Change shebang in all relevant files in this directory and all subdirectories
# See `man find` for how the `-exec command {} +` syntax works
find -type f \( -iname "*.py" \) -exec sed -i '1s=^#! */usr/bin/\(python\|env python\)[23]\?=#!%{chromium_pybin}=' {} +


# Add correct path for esbuild binary
mkdir -p third_party/devtools-frontend/src/third_party/esbuild
ln -s $(which esbuild) third_party/devtools-frontend/src/third_party/esbuild/esbuild

# Remove bundle gn and replace it with a system gn or bootstrap gn as it is x86_64 and causes
# FTBFS on other arch like aarch64/ppc64le
mkdir -p buildtools/linux64/
%if %{bootstrap}
ln -sf ../../%{chromebuilddir}/gn buildtools/linux64/gn 
%else
ln -sf $(which gn) buildtools/linux64/gn
%endif

# Remove bundle gperf and replace it with system gperf
mkdir -p third_party/gperf/cipd/bin
ln -fs $(which gperf) third_party/gperf/cipd/bin/gperf

# Remove bundle rustc and replace it with system rustc
mkdir -p third_party/rust-toolchain/bin/
ln -fs $(which rustc) third_party/rust-toolchain/bin/rustc

%if %{bundlelibusbx}
# no hackity hack hack
%else
# hackity hack hack
rm -rf third_party/libusb/src/libusb/libusb.h
# we _shouldn't need to do this, but it looks like we do.
cp -a $(pkg-config --variable=includedir libusb-1.0)/libusb-1.0/libusb.h third_party/libusb/src/libusb/libusb.h
%endif

# Hard code extra version
sed -i 's/getenv("CHROME_VERSION_EXTRA")/"Fedora Project"/' chrome/common/channel_info_posix.cc

# Fix hardcoded path in remoting code
sed -i 's|/opt/google/chrome-remote-desktop|%{crd_path}|g' remoting/host/setup/daemon_controller_delegate_linux_single_process.cc

# bz#2265957, add correct platform
sed -i "s/Linux x86_64/Linux %{_arch}/" components/embedder_support/user_agent_utils.cc

%if ! %{bundlesimdutf}
ln -sf %{_includedir}/simdutf.h third_party/simdutf/simdutf.h
%endif

%build
# reduce warnings
FLAGS=' -Wno-deprecated-declarations -Wno-unknown-warning-option -Wno-unused-command-line-argument'
FLAGS+=' -Wno-unused-but-set-variable -Wno-unused-result -Wno-unused-function -Wno-unused-variable'
FLAGS+=' -Wno-unused-const-variable -Wno-unneeded-internal-declaration -Wno-unknown-attributes -Wno-unknown-pragmas'

%if %{system_build_flags}
CFLAGS=${CFLAGS/-fexceptions}
CFLAGS=${CFLAGS/-Wp,-D_GLIBCXX_ASSERTIONS}
CFLAGS="$CFLAGS $FLAGS"
CXXFLAGS="$CFLAGS"
%else
# override system build flags
CFLAGS="$FLAGS"
CXXFLAGS="$FLAGS"
%endif

%ifarch ppc64le
CXXFLAGS+=' -faltivec-src-compat=mixed -Wno-deprecated-altivec-src-compat'
%endif

%if ! %{use_custom_libcxx}
LDFLAGS="${LDFLAGS} -stdlib=libc++"
CXXFLAGS="${CXXFLAGS} -stdlib=libc++"
%endif

export CC=clang
export CXX=clang++
export AR=llvm-ar
export NM=llvm-nm
export READELF=llvm-readelf
export CFLAGS
export CXXFLAGS
export LDFLAGS

# need for error: the option `Z` is only accepted on the nightly compiler
export RUSTC_BOOTSTRAP=1

# set rustc version
# Fix error: multiple input filenames provided, caused by rustc_wrapper
rustc_version="$(rustc -V | cut -d' ' -f-2 | sed 's/ /-/')"
# set rust bindgen root
rust_bindgen_root="$(which bindgen | sed 's#/s\?bin/.*##')"
rust_sysroot_absolute="$(rustc --print sysroot)"

# set clang version
clang_version="$(clang --version | sed -n 's/clang version //p' | cut -d. -f1)"
%if 0%{?fedora} > 41 || 0%{?rhel} > 9
clang_base_path="$(PATH=/usr/bin:/usr/sbin which clang | sed 's#/bin/.*##')"
%else
clang_base_path="$(clang --version | grep InstalledDir | cut -d' ' -f2 | sed 's#/bin##')"
%endif

# Core defines are flags that are true for both the browser and headless.
CHROMIUM_CORE_GN_DEFINES=""
CHROMIUM_CORE_GN_DEFINES+=' use_thin_lto=true'   
CHROMIUM_CORE_GN_DEFINES+=' symbol_level=0'        
CHROMIUM_CORE_GN_DEFINES+=' blink_symbol_level=0' 
CHROMIUM_BROWSER_GN_DEFINES+=' ffmpeg_branding="Chrome" proprietary_codecs=true is_component_ffmpeg=false media_use_ffmpeg=true'
CHROMIUM_BROWSER_GN_DEFINES+=' enable_ffmpeg_video_decoders=true'
CHROMIUM_BROWSER_GN_DEFINES+=' media_use_openh264=true rtc_use_h264=true'
CHROMIUM_BROWSER_GN_DEFINES+=' use_vaapi=true use_v4l2_codec=true'
CHROMIUM_BROWSER_GN_DEFINES+=' enable_vr=true safe_browsing_use_unrar=true'
CHROMIUM_CORE_GN_DEFINES+=' enable_enterprise_companion=true' 
# using system toolchain
CHROMIUM_CORE_GN_DEFINES+=' custom_toolchain="//build/toolchain/linux/unbundle:default"'
CHROMIUM_CORE_GN_DEFINES+=' host_toolchain="//build/toolchain/linux/unbundle:default"'
%if ! %{use_custom_libcxx}
CHROMIUM_BROWSER_GN_DEFINES+=' use_custom_libcxx=false'
%endif
CHROMIUM_CORE_GN_DEFINES+=' is_debug=false dcheck_always_on=false dcheck_is_configurable=false'
CHROMIUM_CORE_GN_DEFINES+=' system_libdir="%{_lib}"'

%if %{official_build}
CHROMIUM_CORE_GN_DEFINES+=' is_official_build=true'
sed -i 's|OFFICIAL_BUILD|GOOGLE_CHROME_BUILD|g' tools/generate_shim_headers/generate_shim_headers.py
%endif

CHROMIUM_CORE_GN_DEFINES+=' chrome_pgo_phase=0'

%if ! %{cfi}
CHROMIUM_CORE_GN_DEFINES+=' is_cfi=false use_thin_lto=false'
%endif

%if %{useapikey}
CHROMIUM_CORE_GN_DEFINES+=' google_api_key="%{api_key}"'
%endif

%if %{userestrictedapikeys}
CHROMIUM_CORE_GN_DEFINES+=' google_default_client_id="%{default_client_id}"'
CHROMIUM_CORE_GN_DEFINES+=' google_default_client_secret="%{default_client_secret}"'
%endif

CHROMIUM_CORE_GN_DEFINES+=' is_clang=true'
CHROMIUM_CORE_GN_DEFINES+=" clang_base_path=\"$clang_base_path\""
CHROMIUM_CORE_GN_DEFINES+=" clang_version=$clang_version"
CHROMIUM_CORE_GN_DEFINES+=' clang_use_chrome_plugins=false'
CHROMIUM_CORE_GN_DEFINES+=' use_lld=true'

# enable system rust
CHROMIUM_CORE_GN_DEFINES+=" rust_sysroot_absolute=\"$rust_sysroot_absolute\""
CHROMIUM_CORE_GN_DEFINES+=" rust_bindgen_root=\"$rust_bindgen_root\""
CHROMIUM_CORE_GN_DEFINES+=" rustc_version=\"$rustc_version\""

CHROMIUM_CORE_GN_DEFINES+=' use_sysroot=false'

%ifarch aarch64
CHROMIUM_CORE_GN_DEFINES+=' target_cpu="arm64"'
%endif

%ifarch ppc64le
CHROMIUM_CORE_GN_DEFINES+=' target_cpu="ppc64"'
%endif

CHROMIUM_CORE_GN_DEFINES+=' icu_use_data_file=true'
CHROMIUM_CORE_GN_DEFINES+=' target_os="linux"'
CHROMIUM_CORE_GN_DEFINES+=' current_os="linux"'
CHROMIUM_CORE_GN_DEFINES+=' treat_warnings_as_errors=false'
CHROMIUM_CORE_GN_DEFINES+=' enable_iterator_debugging=false'
CHROMIUM_CORE_GN_DEFINES+=' build_dawn_tests=false enable_perfetto_unittests=false'
CHROMIUM_CORE_GN_DEFINES+=' disable_fieldtrial_testing_config=true'
CHROMIUM_CORE_GN_DEFINES+=' symbol_level=0 blink_symbol_level=0'
CHROMIUM_CORE_GN_DEFINES+=' angle_has_histograms=false'
# drop unrar
CHROMIUM_CORE_GN_DEFINES+=' v8_enable_backtrace=true'
# disable devtools buildle
CHROMIUM_CORE_GN_DEFINES+=' devtools_bundle=false'
export CHROMIUM_CORE_GN_DEFINES

# link against noopenh264 library
%if 0%{?noopenh264}
CHROMIUM_BROWSER_GN_DEFINES+=' media_use_openh264=true'
CHROMIUM_BROWSER_GN_DEFINES+=' rtc_use_h264=true'
%else
CHROMIUM_BROWSER_GN_DEFINES+=' media_use_openh264=false'
CHROMIUM_BROWSER_GN_DEFINES+=' rtc_use_h264=false'
%endif
CHROMIUM_BROWSER_GN_DEFINES+=' use_kerberos=true'
# Workaround for FTBFS, error: no member named 'bPsnrY' in 'Source_Picture_s'
CHROMIUM_BROWSER_GN_DEFINES+=' rtc_video_psnr=false'

%if %{use_qt5}
CHROMIUM_BROWSER_GN_DEFINES+=" use_qt5=true moc_qt5_path=\"$(%{_qt5_qmake} -query QT_HOST_BINS)\""
%else
CHROMIUM_BROWSER_GN_DEFINES+=' use_qt5=false'
%endif

%if %{use_qt6}
CHROMIUM_BROWSER_GN_DEFINES+=" use_qt6=true moc_qt6_path=\"$(%{_qt6_qmake} -query QT_HOST_LIBEXECS)\""
%else
CHROMIUM_BROWSER_GN_DEFINES+=' use_qt6=false'
%endif
CHROMIUM_BROWSER_GN_DEFINES+=' use_gtk=true gtk_version=%{gtk_version}'

CHROMIUM_BROWSER_GN_DEFINES+=' use_gio=true use_pulseaudio=true'
CHROMIUM_BROWSER_GN_DEFINES+=' enable_hangout_services_extension=true'
CHROMIUM_BROWSER_GN_DEFINES+=' enable_widevine=true'

%if %{use_vaapi}
CHROMIUM_BROWSER_GN_DEFINES+=' use_vaapi=true'
%else
CHROMIUM_BROWSER_GN_DEFINES+=' use_vaapi=false'
%endif

%if %{use_v4l2_codec} 
CHROMIUM_BROWSER_GN_DEFINES+=' use_v4l2_codec=true'
%endif

%if 0%{?fedora} || 0%{?rhel} > 8
CHROMIUM_BROWSER_GN_DEFINES+=' rtc_use_pipewire=true rtc_link_pipewire=true'
%else
CHROMIUM_BROWSER_GN_DEFINES+=' rtc_use_pipewire=false rtc_link_pipewire=false'
%endif

%if ! %{bundlelibjpeg}
CHROMIUM_BROWSER_GN_DEFINES+=' use_system_libjpeg=true'
%endif

%if ! %{bundlelibpng}
CHROMIUM_BROWSER_GN_DEFINES+=' use_system_libpng=true'
%endif

%if ! %{bundleharfbuzz}
CHROMIUM_BROWSER_GN_DEFINES+=' use_system_harfbuzz=true'
%endif 

%if ! %{bundlelibopenjpeg2}
CHROMIUM_BROWSER_GN_DEFINES+=' use_system_libopenjpeg2=true'
%endif

%if ! %{bundlelcms2}
CHROMIUM_BROWSER_GN_DEFINES+=' use_system_lcms2=true'
%endif

%if ! %{bundlelibtiff}
CHROMIUM_BROWSER_GN_DEFINES+=' use_system_libtiff=true'
%endif
 
CHROMIUM_BROWSER_GN_DEFINES+=' use_system_libffi=true'

export CHROMIUM_BROWSER_GN_DEFINES

# headless gn defines
CHROMIUM_HEADLESS_GN_DEFINES=""
CHROMIUM_HEADLESS_GN_DEFINES+=' use_ozone=true ozone_auto_platforms=false ozone_platform="headless" ozone_platform_headless=true'
CHROMIUM_HEADLESS_GN_DEFINES+=' angle_enable_vulkan=true angle_enable_swiftshader=true headless_use_embedded_resources=false'
CHROMIUM_HEADLESS_GN_DEFINES+=' headless_use_prefs=false headless_use_policy=false'
CHROMIUM_HEADLESS_GN_DEFINES+=' v8_use_external_startup_data=false enable_print_preview=false enable_remoting=false'
CHROMIUM_HEADLESS_GN_DEFINES+=' use_alsa=false use_bluez=false use_cups=false use_dbus=false use_gio=false use_kerberos=false'
CHROMIUM_HEADLESS_GN_DEFINES+=' use_libpci=false use_pulseaudio=false use_udev=false rtc_use_pipewire=false'
CHROMIUM_HEADLESS_GN_DEFINES+=' v8_enable_lazy_source_positions=false use_glib=false use_gtk=false use_pangocairo=false'
CHROMIUM_HEADLESS_GN_DEFINES+=' use_qt5=false use_qt6=false is_component_build=false enable_ffmpeg_video_decoders=false media_use_ffmpeg=false'
CHROMIUM_HEADLESS_GN_DEFINES+=' media_use_libvpx=false proprietary_codecs=false'
export CHROMIUM_HEADLESS_GN_DEFINES

# use system libraries
system_libs=()
%if ! %{bundlelibaom}
	system_libs+=(libaom)
%endif
%if ! %{bundlelibavif}
	system_libs+=(libavif)
%endif
%if ! %{bundlebrotli}
	system_libs+=(brotli)
%endif
%if ! %{bundlecrc32c}
	system_libs+=(crc32c)
%endif
%if ! %{bundledav1d}
	system_libs+=(dav1d)
%endif
%if ! %{bundlehighway}
	system_libs+=(highway)
%endif
%if ! %{bundlefontconfig}
	system_libs+=(fontconfig)
%endif
%if ! %{bundleffmpegfree}
	system_libs+=(ffmpeg)
%endif
%if ! %{bundlefreetype}
	system_libs+=(freetype)
%endif
%if ! %{bundleharfbuzz}
	system_libs+=(harfbuzz)
%endif
%if ! %{bundleicu}
	system_libs+=(icu)
%endif
%if ! %{bundlelibdrm}
	system_libs+=(libdrm)
%endif
%if ! %{bundlelibjpeg}
	system_libs+=(libjpeg)
%endif
%if ! %{bundlelibpng}
	system_libs+=(libpng)
%endif
%if ! %{bundlelibusbx}
	system_libs+=(libusb)
%endif
%if ! %{bundlelibwebp}
	system_libs+=(libwebp)
%endif
%if ! %{bundlelibxml}
	system_libs+=(libxml)
%endif
%if ! %{bundlelibxslt}
	system_libs+=(libxslt)
%endif
%if ! %{bundleopus}
	system_libs+=(opus)
%endif
%if ! %{bundlere2}
	system_libs+=(re2)
%endif
%if ! %{bundlewoff2}
	system_libs+=(woff2)
%endif
%if ! %{bundleminizip}
	system_libs+=(zlib)
%endif
%if ! %{bundlejsoncpp}
	system_libs+=(jsoncpp)
%endif
%if ! %{bundledoubleconversion}
	system_libs+=(double-conversion)
%endif
%if ! %{bundlelibsecret}
	system_libs+=(libsecret)
%endif
%if ! %{bundlesnappy}
	system_libs+=(snappy)
%endif
%if ! %{bundlelibXNVCtrl}
	system_libs+=(libXNVCtrl)
%endif
%if ! %{bundleflac}
	system_libs+=(flac)
%endif
%if ! %{bundlezstd}
	system_libs+=(zstd)
%endif
%if 0%{?noopenh264}
	system_libs+=(openh264)
%endif
%if ! %{bundlesimdutf}
   system_libs+=(simdutf)
%endif

build/linux/unbundle/replace_gn_files.py --system-libraries ${system_libs[@]}

# Check that there is no system 'google' module, shadowing bundled ones:
if python3 -c 'import google ; print google.__path__' 2> /dev/null ; then \
    echo "Python 3 'google' module is defined, this will shadow modules of this build"; \
    exit 1 ; \
fi

%if %{bootstrap}
tools/gn/bootstrap/bootstrap.py --gn-gen-args="$CHROMIUM_CORE_GN_DEFINES $CHROMIUM_BROWSER_GN_DEFINES"
%else
mkdir -p %{chromebuilddir} && cp -a $(which gn) %{chromebuilddir}/
%endif

%{chromebuilddir}/gn --script-executable=%{chromium_pybin} gen --args="$CHROMIUM_CORE_GN_DEFINES $CHROMIUM_BROWSER_GN_DEFINES" %{chromebuilddir}

%build_target %{chromebuilddir} chrome

%build_target %{chromebuilddir} chrome_sandbox

%if %{build_chromedriver}
%build_target %{chromebuilddir} chromedriver
%endif

%if %{build_headless}
%build_target %{chromebuilddir} headless_shell
%endif

%if %{build_chrome_management_service}
%build_target %{chromebuilddir} chrome_management_service
%endif

%install
rm -rf %{buildroot}

mkdir -p %{buildroot}%{_bindir} \
         %{buildroot}%{chromium_path}/locales \
         %{buildroot}%{_sysconfdir}/%{name}

# install system wide chromium config
cp -a %{SOURCE2} %{buildroot}%{_sysconfdir}/%{name}/%{name}.conf
cp -a %{SOURCE3} %{buildroot}%{chromium_path}/chromium-browser.sh

%if ! %{use_vaapi}
# remove vaapi flags
echo "# system wide chromium flags" > %{buildroot}%{_sysconfdir}/%{name}/%{name}.conf
%endif

export BUILD_TARGET=`cat /etc/redhat-release`

sed -i "s|@@BUILD_TARGET@@|$BUILD_TARGET|g" %{buildroot}%{chromium_path}/chromium-browser.sh
sed -i "s|@@EXTRA_FLAGS@@||g" %{buildroot}%{chromium_path}/chromium-browser.sh

ln -s ../..%{chromium_path}/chromium-browser.sh %{buildroot}%{_bindir}/chromium-browser
mkdir -p %{buildroot}%{_mandir}/man1/

pushd %{chromebuilddir}
%if %{bundleicu}
	cp -a icudtl.dat %{buildroot}%{chromium_path}
%endif
	cp -a chrom*.pak resources.pak %{buildroot}%{chromium_path}
	cp --remove-destination locales/*.pak %{buildroot}%{chromium_path}/locales/
	cp -a MEIPreload/ PrivacySandboxAttestationsPreloaded/ %{buildroot}%{chromium_path}/
%if %{build_chrome_management_service}
	cp -a chrome_management_service %{buildroot}%{chromium_path}/chrome-management-service
%endif
	%ifarch x86_64 aarch64 ppc64le
		cp -a libvk_swiftshader.so %{buildroot}%{chromium_path}
		cp -a libvulkan.so.1 %{buildroot}%{chromium_path}
		cp -a vk_swiftshader_icd.json %{buildroot}%{chromium_path}
	%endif
	cp -a chrome %{buildroot}%{chromium_path}/chromium-browser
	cp -a chrome_sandbox %{buildroot}%{chromium_path}/chrome-sandbox
	cp -a chrome_crashpad_handler %{buildroot}%{chromium_path}/chrome_crashpad_handler
	cp -a ../../chrome/app/resources/manpage.1.in %{buildroot}%{_mandir}/man1/chromium-browser.1
	sed -i "s|@@PACKAGE|chromium-browser|g" %{buildroot}%{_mandir}/man1/chromium-browser.1
	sed -i "s|@@MENUNAME|%{chromium_menu_name}|g" %{buildroot}%{_mandir}/man1/chromium-browser.1

	# V8 initial snapshots
	# https://code.google.com/p/chromium/issues/detail?id=421063
	cp -a v8_context_snapshot.bin %{buildroot}%{chromium_path}

	# This is ANGLE, not to be confused with the similarly named files under swiftshader/
	cp -a libEGL.so libGLESv2.so %{buildroot}%{chromium_path}

	%if %{use_qt5}
		cp -a libqt5_shim.so %{buildroot}%{chromium_path}
	%endif

	%if %{use_qt6}
		cp -a libqt6_shim.so %{buildroot}%{chromium_path}
	%endif

	%if %{build_chromedriver}
		# chromedriver
		cp -a chromedriver %{buildroot}%{chromium_path}/chromedriver
		ln -s ../..%{chromium_path}/chromedriver %{buildroot}%{_bindir}/chromedriver
	%endif

popd

%if %{build_headless}
	pushd %{chromebuilddir}
		cp -a *.pak headless_shell %{buildroot}%{chromium_path}
	popd
%endif

# need to strip binaries explicitly when debug is disable
%if ! %{enable_debug}
pushd %{buildroot}%{chromium_path}/
for f in *.so *.so.1 chrome_crashpad_handler chrome-sandbox chromium-browser headless_shell chromedriver ; do
   [ -f $f ] && strip $f
done
popd
%endif

# Add directories for policy management
mkdir -p %{buildroot}%{_sysconfdir}/chromium/policies/managed
mkdir -p %{buildroot}%{_sysconfdir}/chromium/policies/recommended

# disable AI
#cp -a %{SOURCE14} %{buildroot}%{_sysconfdir}/chromium/policies/managed/

mkdir -p %{buildroot}%{_datadir}/icons/hicolor/256x256/apps
cp -a chrome/app/theme/chromium/product_logo_256.png %{buildroot}%{_datadir}/icons/hicolor/256x256/apps/chromium-browser.png
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/128x128/apps
cp -a chrome/app/theme/chromium/product_logo_128.png %{buildroot}%{_datadir}/icons/hicolor/128x128/apps/chromium-browser.png
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/64x64/apps
cp -a chrome/app/theme/chromium/product_logo_64.png %{buildroot}%{_datadir}/icons/hicolor/64x64/apps/chromium-browser.png
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/48x48/apps
cp -a chrome/app/theme/chromium/product_logo_48.png %{buildroot}%{_datadir}/icons/hicolor/48x48/apps/chromium-browser.png
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/24x24/apps
cp -a chrome/app/theme/chromium/product_logo_24.png %{buildroot}%{_datadir}/icons/hicolor/24x24/apps/chromium-browser.png

# Install the master_preferences file
install -m 0644 %{SOURCE11} %{buildroot}%{_sysconfdir}/%{name}/

mkdir -p %{buildroot}%{_datadir}/applications/
desktop-file-install --dir %{buildroot}%{_datadir}/applications %{SOURCE4}

install -D -m0644 %{SOURCE10} ${RPM_BUILD_ROOT}%{_datadir}/appdata/chromium-browser.appdata.xml
appstream-util validate-relax --nonet ${RPM_BUILD_ROOT}%{_datadir}/appdata/chromium-browser.appdata.xml

mkdir -p %{buildroot}%{_datadir}/gnome-control-center/default-apps/
cp -a %{SOURCE9} %{buildroot}%{_datadir}/gnome-control-center/default-apps/

# README.fedora
cp %{SOURCE1} .

%if %{undefined flatpak}
%post
# Set SELinux labels - semanage itself will adjust the lib directory naming
# But only do it when selinux is enabled, otherwise, it gets noisy.
if selinuxenabled; then
	semanage fcontext -a -t bin_t /usr/lib/chromium-browser &>/dev/null || :
	semanage fcontext -a -t bin_t /usr/lib/chromium-browser/chromium-browser.sh &>/dev/null || :
	semanage fcontext -a -t chrome_sandbox_exec_t /usr/lib/chrome-sandbox &>/dev/null || :
	restorecon -R -v %{chromium_path}/chromium-browser &>/dev/null || :
fi
%endif

%files
%doc AUTHORS README.fedora
%license LICENSE
%dir %{_sysconfdir}/%{name}/policies/
%dir %{chromium_path}/MEIPreload/
%dir %{chromium_path}/PrivacySandboxAttestationsPreloaded/
%config(noreplace) %{_sysconfdir}/%{name}/chromium.conf
%config %{_sysconfdir}/%{name}/master_preferences
#%config %{_sysconfdir}/%{name}/policies/managed/disable-ai.json
%{_bindir}/chromium-browser
%{chromium_path}/chrome_*.pak
%{chromium_path}/chrome_crashpad_handler
%{chromium_path}/resources.pak
%{chromium_path}/chromium-browser
%{chromium_path}/chromium-browser.sh
%if %{build_chrome_management_service}
%{chromium_path}/chrome-management-service
%endif
%{chromium_path}/MEIPreload/*
%{chromium_path}/PrivacySandboxAttestationsPreloaded/*
%{chromium_path}/chrome-sandbox
%{_mandir}/man1/chromium-browser.*
%{_datadir}/icons/hicolor/*/apps/chromium-browser.png
%{_datadir}/applications/*.desktop
%{_datadir}/appdata/*.appdata.xml
%{_datadir}/gnome-control-center/default-apps/chromium-browser.xml

%if %{use_qt5}
%files qt5-ui
%{chromium_path}/libqt5_shim.so
%endif

%if %{use_qt6}
%files qt6-ui
%{chromium_path}/libqt6_shim.so
%endif

%files common
%{chromium_path}/libvk_swiftshader.so*
%{chromium_path}/libvulkan.so*
%{chromium_path}/vk_swiftshader_icd.json
%{chromium_path}/libEGL.so*
%{chromium_path}/libGLESv2.so*
%{chromium_path}/*.bin
%if %{bundleicu}
%{chromium_path}/icudtl.dat
%endif
%dir %{chromium_path}/
%dir %{chromium_path}/locales/
%lang(af) %{chromium_path}/locales/af*.pak
%lang(am) %{chromium_path}/locales/am*.pak
%lang(ar) %{chromium_path}/locales/ar*.pak
%lang(bg) %{chromium_path}/locales/bg*.pak
%lang(bn) %{chromium_path}/locales/bn*.pak
%lang(ca) %{chromium_path}/locales/ca*.pak
%lang(cs) %{chromium_path}/locales/cs*.pak
%lang(da) %{chromium_path}/locales/da*.pak
%lang(de) %{chromium_path}/locales/de*.pak
%lang(el) %{chromium_path}/locales/el*.pak
%lang(en_GB) %{chromium_path}/locales/en-GB*.pak
# Chromium _ALWAYS_ needs en-US.pak as a fallback
# This means we cannot apply the lang code here.
# Otherwise, it is filtered out on install.
%{chromium_path}/locales/en-US*.pak
%lang(es) %{chromium_path}/locales/es*.pak
%lang(et) %{chromium_path}/locales/et*.pak
%lang(fa) %{chromium_path}/locales/fa*.pak
%lang(fi) %{chromium_path}/locales/fi{.pak,_*.pak}
%lang(fil) %{chromium_path}/locales/fil*.pak
%lang(fr) %{chromium_path}/locales/fr*.pak
%lang(gu) %{chromium_path}/locales/gu*.pak
%lang(he) %{chromium_path}/locales/he*.pak
%lang(hi) %{chromium_path}/locales/hi*.pak
%lang(hr) %{chromium_path}/locales/hr*.pak
%lang(hu) %{chromium_path}/locales/hu*.pak
%lang(id) %{chromium_path}/locales/id*.pak
%lang(it) %{chromium_path}/locales/it*.pak
%lang(ja) %{chromium_path}/locales/ja*.pak
%lang(kn) %{chromium_path}/locales/kn*.pak
%lang(ko) %{chromium_path}/locales/ko*.pak
%lang(lt) %{chromium_path}/locales/lt*.pak
%lang(lv) %{chromium_path}/locales/lv*.pak
%lang(ml) %{chromium_path}/locales/ml*.pak
%lang(mr) %{chromium_path}/locales/mr*.pak
%lang(ms) %{chromium_path}/locales/ms*.pak
%lang(nb) %{chromium_path}/locales/nb*.pak
%lang(nl) %{chromium_path}/locales/nl*.pak
%lang(pl) %{chromium_path}/locales/pl*.pak
%lang(pt_BR) %{chromium_path}/locales/pt-BR*.pak
%lang(pt_PT) %{chromium_path}/locales/pt-PT*.pak
%lang(ro) %{chromium_path}/locales/ro*.pak
%lang(ru) %{chromium_path}/locales/ru*.pak
%lang(sk) %{chromium_path}/locales/sk*.pak
%lang(sl) %{chromium_path}/locales/sl*.pak
%lang(sr) %{chromium_path}/locales/sr*.pak
%lang(sv) %{chromium_path}/locales/sv*.pak
%lang(sw) %{chromium_path}/locales/sw*.pak
%lang(ta) %{chromium_path}/locales/ta*.pak
%lang(te) %{chromium_path}/locales/te*.pak
%lang(th) %{chromium_path}/locales/th*.pak
%lang(tr) %{chromium_path}/locales/tr*.pak
%lang(uk) %{chromium_path}/locales/uk*.pak
%lang(ur) %{chromium_path}/locales/ur*.pak
%lang(vi) %{chromium_path}/locales/vi*.pak
%lang(zh_CN) %{chromium_path}/locales/zh-CN*.pak
%lang(zh_TW) %{chromium_path}/locales/zh-TW*.pak
# These are psuedolocales, not real ones.
# They only get generated when is_official_build=false
%if ! %{official_build}
%{chromium_path}/locales/ar-XB.pak
%{chromium_path}/locales/en-XA.pak
%endif

%if %{build_headless}
%files headless
%{chromium_path}/headless_shell
%{chromium_path}/headless_*.pak
%endif

%if %{build_chromedriver}
%files -n chromedriver
%doc AUTHORS
%license LICENSE
%{_bindir}/chromedriver
%{chromium_path}/chromedriver
%endif

%changelog
* Wed Jul 15 2026 - main
