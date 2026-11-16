#!/usr/bin/env python3
"""Replace the kernel (Image.gz + appended dtb) in an Android v0 boot.img, keeping ramdisk/cmdline.
usage: repack.py old_boot.img Image.gz board.dtb out.img [ramdisk_addr_hex]"""
import struct, sys

old, kpath, dtb, out = sys.argv[1:5]
d = open(old, "rb").read()
assert d[:8] == b"ANDROID!"
ks, ka, rs, ra, ss, sa, ta, ps = struct.unpack_from("<8I", d, 8)
pages = lambda n: (n + ps - 1) // ps
roff = ps * (1 + pages(ks))
ramdisk = d[roff:roff + rs]
kernel = open(kpath, "rb").read() + open(dtb, "rb").read()
hdr = bytearray(d[:ps])
struct.pack_into("<I", hdr, 8, len(kernel))
if len(sys.argv) > 5:
    struct.pack_into("<I", hdr, 20, int(sys.argv[5], 16))
hdr[576:608] = b"\0" * 32  # clear id hash
pad = lambda b: b + b"\0" * (pages(len(b)) * ps - len(b))
open(out, "wb").write(bytes(hdr) + pad(kernel) + pad(ramdisk))
print(f"kernel {len(kernel)} ramdisk {rs} -> {out}")
