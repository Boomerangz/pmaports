#!/bin/zsh
# Flash a boot image and wait for the phone: prints "ssh up", "FASTBOOT (watchdog)" or a timeout.
# usage: cycle.sh <boot.img> [phone-ip] — the phone must be in fastboot, or reachable by ssh/adb.
set -u
IMG=${1:?boot.img}; IP=${2:-172.16.42.1}
if ! fastboot devices | grep -q fastboot; then
  if ~/pmos-share/tools/ph true >/dev/null 2>&1; then
    ~/pmos-share/tools/ph 'sudo /usr/local/bin/rebootmode bootloader' >/dev/null 2>&1 &
  elif adb get-state >/dev/null 2>&1; then
    adb reboot bootloader
  fi
  for i in {1..45}; do fastboot devices | grep -q fastboot && break; sleep 2; done
fi
fastboot devices | grep -q fastboot || { echo "!! no fastboot"; exit 1; }
fastboot flash boot "$IMG" 2>&1 | tail -1
fastboot reboot 2>&1 | tail -1
sleep 8
for i in {1..70}; do
  if ~/pmos-share/tools/ph true >/dev/null 2>&1; then echo "ssh up after ~$((8+i*3))s"; exit 0; fi
  if fastboot devices 2>/dev/null | grep -q fastboot; then echo "FASTBOOT (watchdog) after ~$((8+i*3))s"; exit 3; fi
  sleep 3
done
echo "!! phone neither on USB network nor in fastboot"; exit 2
