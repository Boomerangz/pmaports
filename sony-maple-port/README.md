# Sony Xperia XZ Premium (maple) on a mainline kernel

Work-in-progress port of postmarketOS with a mainline-based kernel to the
Sony Xperia XZ Premium (G8141/G8142, MSM8998, platform "yoshino").
Tested on one G8142, booting from a microSD card. Everything here is
experimental: expect rough edges and read the warnings below first.

## Where the pieces are

| Piece | Location |
| --- | --- |
| Kernel | <https://github.com/Boomerangz/linux>, branch `sony-maple-6.18` (on top of `msm8998-mainline/linux` `qcom-msm8998-6.18.y`) |
| Device packages | this repository, branch `sony-maple`: `device/testing/device-sony-maple`, `linux-sony-maple`, `firmware-sony-maple`, `ta-service-yoshino` |
| Lomiri touch fix | <https://github.com/Boomerangz/qtmir>, branch `maple-touch-scale`; packaged in `temp/qtmir` |
| Helper tools | this directory |

Older working branches of the kernel (`archive/maple`, `archive/maple-display`)
are kept in the kernel repository for reference only. They contain debug code
and experiments and are not meant to be used.

## Status

Working (checked on the device):

- display and GPU (freedreno a5xx), touchscreen, Phosh
- Wi-Fi (WCN3990 / ath10k-snoc), Bluetooth controller
- battery, charging, fuel gauge, RTC
- modem, ADSP and SLPI remoteprocs start (no calls/SMS/data testing was done)
- audio: built-in speakers, earpiece, headphones with jack detection, microphone
- vibrator, NFC controller, flash LED, time-of-flight sensor
- suspend to idle
- Lomiri (the Ubuntu Touch shell) from postmarketOS, with the notes below

Not working or not done:

- internal UFS storage is deliberately left disabled (see warnings)
- cameras, fingerprint reader, motion/light sensors, USB Type-C role switching
- headset buttons and headset microphone are untested
- a click and a short rasp from the top speaker when the sound server starts
- `clk_ignore_unused` is still required on the kernel command line; no cpufreq
- GTK4's GPU renderer triggers GPU faults; the device package sets
  `GSK_RENDERER=cairo` as a workaround

## Warnings

- **UFS**: the msm8998 mainline tree warns that enabling UFS can brick
  devices. The device tree here keeps it off. The modem therefore cannot read
  its data from the phone's partitions; `rmtfs` and `ta-service-yoshino` work
  from file copies instead (see "Device-specific data").
- Unlocking the bootloader erases the phone and removes Sony's DRM keys.
- `host-tools/flash-sd.sh` overwrites the whole microSD card.

## Firmware

`firmware-sony-maple` is a recipe only. The firmware files (modem, ADSP,
SLPI, WLAN, Bluetooth, GPU zap shader) are proprietary and are not
distributed here. Copy them from your own phone's firmware partitions into
`device/testing/firmware-sony-maple/files/` using the paths the APKBUILD
expects, then build the package.

## Device-specific data

Two things are unique to each phone and must never be shared or packaged:

- the Trim Area image (contains IMEI and calibration): `/var/lib/ta/TA.img`
- the modem's NV storage files: `/var/lib/rmtfs/*`

Back them up from your own phone before doing anything else and install them
by hand after flashing.

## Building

With pmbootstrap pointed at this branch:

```
pmbootstrap init                      # choose sony-maple
pmbootstrap build ta-service-yoshino firmware-sony-maple linux-sony-maple device-sony-maple
pmbootstrap install --no-fde
```

`linux-sony-maple` fetches the kernel branch from GitHub. So far the kernel
was always built from a local tree (`pmbootstrap build --src=...`); building
from the published tarball has not been verified yet.

## Booting

The bootloader accepts `fastboot boot <image>` to try a kernel from RAM
before flashing it, which makes a safe test loop possible:

- `host-tools/repack.py old.img vmlinuz dtb new.img` - swap kernel and DTB in a boot image
- `host-tools/cycle.sh boot.img` - reboot the phone to fastboot, flash, wait for ssh
- `host-tools/ph` - ssh to the phone over the USB network
- `device-tools/rebootmode.c` - reboot into the bootloader from the running
  system (Alpine's `reboot-mode` package does the same)
- `loop-boot/loop-init` - init wrapper that boots a second system from image
  files on the SD card's root partition (`/fresh-test/{boot,root}.img`) without
  repartitioning; used to test a clean install and Lomiri next to the main system

## Lomiri

Install `postmarketos-ui-lomiri`; the `device-sony-maple-lomiri` subpackage
then adds the missing `lomiri-ui-extras-qt5` and `maliit-keyboard`
dependencies and a lomiri-deviceinfo profile (phone, grid unit 21).

Two more things were needed on the test system and are not packaged:

- `temp/qtmir` must be installed instead of Alpine's qtmir. With an output
  scale other than 1, Mir 2 delivers touchscreen coordinates in physical
  pixels while the shell is laid out in logical pixels, so only the top-left
  part of the screen reacted to touches. The patch divides touch coordinates
  by the screen's device pixel ratio.
- On an image that also has the Phosh audio setup (PulseAudio owns the sound
  card), the Lomiri session does not start PulseAudio. Adding
  `pulseaudio --start` before `superd &` in `/usr/bin/start_lomiri` fixes it.
  The user also had to be in the `audio` and `video` groups.

Note that Lomiri suspends the phone when the screen turns off, which drops
the USB network until the power key is pressed.

## Other files

- `android/EarTest.java` - tiny tone player run with `app_process` under
  Android (LineageOS) to capture the vendor audio HAL's earpiece register
  setup for comparison
- `device-tools/qrtr-trap.c`, `usb-watchdog.c` - debugging helpers used
  during bring-up

## Credits

- msm8998-mainline and SoMainline (Marijn Suijten, Konrad Dybcio and others)
  for the MSM8998 and yoshino groundwork, including the display work this
  port builds on
- Jayden Milne for the WCD9335 jack detection patches (from
  `gts3lwifi-mainline`), ported here with authorship preserved
- postmarketOS and UBports
