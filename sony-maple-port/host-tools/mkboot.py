#!/usr/bin/env python3
"""Build an Android v0 boot.img from an existing one, replacing ramdisk and/or cmdline.
usage: mkboot.py base.img out.img [--ramdisk file] [--cmdline-append "..."] [--cmdline-sub old=new]"""
import struct, sys

base, out = sys.argv[1:3]
args = sys.argv[3:]
d = open(base, "rb").read()
assert d[:8] == b"ANDROID!"
ks, ka, rs, ra, ss, sa, ta, ps = struct.unpack_from("<8I", d, 8)
pages = lambda n: (n + ps - 1) // ps
kernel = d[ps:ps + ks]
roff = ps * (1 + pages(ks))
ramdisk = d[roff:roff + rs]
cmdline = d[64:64 + 512].split(b"\0")[0].decode() + d[608:608 + 1024].split(b"\0")[0].decode()
i = 0
while i < len(args):
    if args[i] == "--ramdisk":
        ramdisk = open(args[i + 1], "rb").read()
    elif args[i] == "--cmdline-append":
        cmdline += " " + args[i + 1]
    elif args[i] == "--cmdline-sub":
        old, new = args[i + 1].split("=>")
        assert old in cmdline, old
        cmdline = cmdline.replace(old, new)
    i += 2
c = cmdline.encode()
assert len(c) < 512 + 1024
hdr = bytearray(d[:ps])
struct.pack_into("<I", hdr, 16, len(ramdisk))
hdr[64:64 + 512] = c[:511].ljust(512, b"\0")
hdr[608:608 + 1024] = c[511:].ljust(1024, b"\0")
hdr[576:608] = b"\0" * 32
pad = lambda b: b + b"\0" * (pages(len(b)) * ps - len(b))
open(out, "wb").write(bytes(hdr) + pad(kernel) + pad(ramdisk))
print(f"kernel {len(kernel)} ramdisk {len(ramdisk)} cmdline[{len(c)}]: {cmdline}")
