#!/usr/bin/env python3
"""Rewrite the kernel cmdline in an Android boot.img (header v0/v1/v2).
usage: setcmdline.py in.img out.img "new cmdline" """
import sys

src, dst, cmd = sys.argv[1], sys.argv[2], sys.argv[3]
data = bytearray(open(src, "rb").read())
assert data[:8] == b"ANDROID!", "not a boot image"
b = cmd.encode()
assert len(b) < 512 + 1024, "cmdline too long"
main, extra = b[:511], b[511:]
data[64:64 + 512] = main.ljust(512, b"\0")
data[608:608 + 1024] = extra.ljust(1024, b"\0")
open(dst, "wb").write(data)
print("cmdline:", cmd)
