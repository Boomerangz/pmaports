#!/bin/zsh
# Usage: boot-test.sh <boot.img>
# Puts the phone into fastboot (from adb/LineageOS if needed), RAM-boots the image,
# then waits for the USB network gadget and reports the macOS interface + IP.
set -u
IMG=${1:?boot.img}

to_fastboot() {
  if fastboot devices | grep -q fastboot; then return 0; fi
  if adb get-state >/dev/null 2>&1; then adb reboot bootloader; fi
  for i in {1..60}; do fastboot devices | grep -q fastboot && return 0; sleep 1; done
  echo "!! phone not in fastboot"; return 1
}

ifaces_before=$(ifconfig -l)
to_fastboot || exit 1
fastboot boot "$IMG" || exit 1
echo "booted at $(date +%T); waiting for USB network..."
for i in {1..120}; do
  for ifc in $(ifconfig -l); do
    case " $ifaces_before " in *" $ifc "*) continue;; esac
    ip=$(ifconfig $ifc 2>/dev/null | awk '/inet /{print $2}')
    echo "new iface $ifc ip=${ip:-none} after ${i}s"
    if [ -n "$ip" ]; then exit 0; fi
  done
  sleep 1
done
echo "!! no USB network after 120s"
exit 2
