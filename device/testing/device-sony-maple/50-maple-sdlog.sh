#!/bin/sh
# Bring-up aid: periodically save kernel + initramfs logs to the pmOS_boot partition on the SD card.
(
	mkdir -p /sdlog
	for i in $(seq 1 30); do
		dev=$(blkid -L pmOS_boot 2>/dev/null)
		[ -n "$dev" ] && mount "$dev" /sdlog 2>/dev/null && break
		sleep 1
	done
	mountpoint -q /sdlog || exit 0
	for i in $(seq 1 60); do
		dmesg > /sdlog/maple-dmesg.txt
		cp /pmOS_init.log /sdlog/maple-init.log 2>/dev/null
		{ ls /sys/class/udc; cat /sys/kernel/config/usb_gadget/g1/UDC; ip addr; } > /sdlog/maple-usb.txt 2>&1
		sync
		sleep 3
	done
	umount /sdlog
) &
