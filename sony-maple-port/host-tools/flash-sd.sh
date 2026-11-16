#!/bin/zsh
# Writes ~/pmos-share/out/sony-maple.raw to the phone's microSD via LineageOS (adb root).
set -eu
IMG=~/pmos-share/out/sony-maple.raw
if ! adb get-state >/dev/null 2>&1; then
  if fastboot devices | grep -q fastboot; then fastboot reboot >/dev/null; fi
  adb wait-for-device
fi
for i in {1..90}; do [ "$(adb shell getprop sys.boot_completed 2>/dev/null | tr -d '\r')" = 1 ] && break; sleep 2; done
adb root >/dev/null; sleep 3; adb wait-for-device
for i in {1..30}; do [ "$(adb shell getprop sys.boot_completed 2>/dev/null | tr -d '\r')" = 1 ] && break; sleep 1; done
adb shell 'for v in $(sm list-volumes public | awk "{print \$1}"); do sm unmount $v; done; sleep 1' || true
adb push $IMG /data/local/tmp/pmos.img | tail -1
adb shell "dd if=/data/local/tmp/pmos.img of=/dev/block/mmcblk0 bs=4M 2>&1 | tail -1; sync; rm /data/local/tmp/pmos.img"
echo "SD written"
