#!/usr/bin/env python3
"""bin2vxb - make a .vxb file (for VXRECVB on the Casio VX-4 / FX-870P) from a .bin.

The build script (scripts\\run_asm_hd61700.ps1) already writes build\\NAME.vxb next to
every .bin. This is the same conversion as a standalone script, for a .bin from
elsewhere or a different load address. Python 3, nothing to install.

    python bin2vxb.py prog.bin 1CD0                 -> prog.vxb, no start address
    python bin2vxb.py prog.bin 1ED0 --exec 1ED0     -> VXRECVB offers to run &H1ED0
    python bin2vxb.py prog.bin 0 --exec 0 -o snake.vxb

Addresses in hex, with or without &H / 0x. Then send the .vxb as binary without flow
control (see the README).

VXB format (vxrecvb.md; vxsend.py make_vxb and the build script write the same):
  +0  'V' 'X'        marker
  +2  load address   low byte first
  +4  length n       low byte first, 1..65535
  +6  exec address   low byte first, &HFFFF = none
  +8  header check   bytes +2..+8 add up to 0 (mod 256)
  +9  n data bytes
  then the CRC-16/XMODEM of the data, high byte first (lib/misc/crc16.s)

Part of CasioPocketLib (projects/VX-4 Serial Loader/vxrecvb).
Copyright (c) 2026 Radovan Hrebicek. MIT License (see LICENSE).
"""
import argparse
import os
import sys


def crc16_xmodem(data: bytes) -> int:
    crc = 0
    for b in data:
        crc ^= b << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
    return crc


def make_vxb(addr: int, data: bytes, exec_addr=None) -> bytes:
    if not 1 <= len(data) <= 0xFFFF:
        raise ValueError("a .vxb holds 1..65535 bytes")
    if not 0 <= addr <= 0xFFFF or addr + len(data) > 0x10000:
        raise ValueError(f"&H{addr:04X} + {len(data)} bytes runs past &HFFFF")
    ex = 0xFFFF if exec_addr is None else exec_addr
    hdr = bytes([addr & 255, addr >> 8, len(data) & 255, len(data) >> 8, ex & 255, ex >> 8])
    crc = crc16_xmodem(data)
    return b"VX" + hdr + bytes([(-sum(hdr)) & 255]) + data + bytes([crc >> 8, crc & 255])


def hexaddr(s: str) -> int:
    s = s.strip()
    for p in ("&H", "&h", "0x", "0X", "$"):
        if s.startswith(p):
            s = s[len(p):]
    v = int(s, 16)
    if not 0 <= v <= 0xFFFF:
        raise argparse.ArgumentTypeError(f"{s}: not a 16-bit address")
    return v


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="make a .vxb (VXRECVB) from a .bin")
    ap.add_argument("bin", help="the machine-code file")
    ap.add_argument("addr", type=hexaddr, help="load address (hex), e.g. 1ED0")
    ap.add_argument("--exec", dest="exec_addr", type=hexaddr, help="start address (hex); VXRECVB then offers to run it")
    ap.add_argument("-o", "--out", help="output file (default: the .bin name with .vxb)")
    a = ap.parse_args(argv)
    with open(a.bin, "rb") as f:
        data = f.read()
    try:
        vxb = make_vxb(a.addr, data, a.exec_addr)
    except ValueError as e:
        sys.exit(f"bin2vxb: {e}")
    out = a.out or os.path.splitext(a.bin)[0] + ".vxb"
    with open(out, "wb") as f:
        f.write(vxb)
    crc = vxb[-2] << 8 | vxb[-1]
    print(f"{out}: &H{a.addr:04X}-&H{a.addr + len(data) - 1:04X} ({len(data)} bytes), "
          + (f"exec &H{a.exec_addr:04X}, " if a.exec_addr is not None else "no exec, ")
          + f"CRC &H{crc:04X}, {len(vxb)} bytes to send")
    return 0


if __name__ == "__main__":
    sys.exit(main())
