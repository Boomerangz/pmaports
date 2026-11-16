/*
 * Bring-up watchdog for the Xperia XZ Premium postmarketOS port.
 *
 * Started from the initramfs (rdinit wrapper) as a static binary, so it keeps
 * running after switch_root. If no USB host has sent any packets to usb0 a
 * while after boot, save the kernel log to the SD card and reboot into the
 * bootloader (fastboot), so the device can be recovered without pressing keys.
 */
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/klog.h>
#include <sys/mount.h>
#include <sys/reboot.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <linux/reboot.h>

static long rx_packets(void)
{
	char buf[32] = "";
	int fd = open("/sys/class/net/usb0/statistics/rx_packets", O_RDONLY);

	if (fd < 0)
		return -1;
	if (read(fd, buf, sizeof(buf) - 1) < 0)
		buf[0] = '\0';
	close(fd);
	return atol(buf);
}

static void save_log(const char *path, const char *note)
{
	static char buf[1 << 20];
	int n, fd = open(path, O_WRONLY | O_CREAT | O_TRUNC, 0644);

	if (fd < 0)
		return;
	if (write(fd, note, strlen(note)) < 0)
		note = NULL;
	n = klogctl(3 /* SYSLOG_ACTION_READ_ALL */, buf, sizeof(buf));
	if (n > 0 && write(fd, buf, n) < 0)
		note = NULL;
	fsync(fd);
	close(fd);
}

int main(int argc, char **argv)
{
	int delay = argc > 1 ? atoi(argv[1]) : 150;
	char note[128];
	long rx;

	if (fork() != 0)
		return 0;
	setsid();

	sleep(delay);

	/* Find the current root (the initramfs is emptied by switch_root) */
	mkdir("/maple-wd", 0700);
	if (mount("proc", "/maple-wd", "proc", 0, NULL) == 0) {
		if (chroot("/maple-wd/1/root") == 0)
			chdir("/");
	}

	rx = rx_packets();
	if (rx >= 3 || access("/etc/maple-no-watchdog2", F_OK) == 0)
		return 0;

	snprintf(note, sizeof(note), "maple-wd: usb0 rx_packets=%ld after %d s, rebooting to bootloader\n",
		 rx, delay);
	save_log("/boot/maple-wd-dmesg.txt", note);
	save_log("/sdlog/maple-wd-dmesg.txt", note);
	sync();

	syscall(SYS_reboot, LINUX_REBOOT_MAGIC1, LINUX_REBOOT_MAGIC2,
		LINUX_REBOOT_CMD_RESTART2, "bootloader");
	reboot(RB_AUTOBOOT);
	return 1;
}
