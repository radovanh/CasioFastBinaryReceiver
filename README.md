# VXRECVB - fast binary transfer from a PC to a Casio VX-4 / FX-870P

VXRECVB loads a machine-code program from a PC into a Casio VX-4 or FX-870P pocket
computer over RS-232, as raw binary at 4800 or 9600 baud. A 3.5 KB program takes about
9 seconds at 4800 baud and about 5 seconds at 9600. The receiver itself is a BASIC
program with a 499-byte machine-code part (RXBIN). It checks the header, the target
address and a CRC-16.

Tested on a real Casio VX-4 at 9600 baud, sending with CoolTerm and with Tera Term.

## Files

| File | What it is |
|---|---|
| `vxrecvb.bas` | The receiver (BASIC with the machine code as DATA lines). Load it into the calculator once |
| `xclear.bas` | "Extended CLEAR": reserves memory at `&H1CD0` for the receiver and your program. Load it into the calculator once |
| `bin2vxb.bat`, `bin2vxb.ps1` | PC tool (Windows): makes a `.vxb` file from a `.bin`. The `.bat` runs the PowerShell script; nothing to install |
| `bin2vxb.py` | The same tool in Python 3, for those who prefer Python (any OS) |
| `pc-settings\` | Settings for CoolTerm and Tera Term (sending the `.vxb`) |
| `LICENSE` | MIT License, plus the credits for the third-party parts in `xclear.bas` |

## What you need

- A Casio **VX-4** (any RAM size) or **FX-870P**, and an RS-232 interface with a cable
  to the PC (or a USB-serial adapter).
- On the PC, a terminal program that can send a file **unchanged** (binary/raw) **without
  flow control**: [CoolTerm](https://freeware.the-meiers.org/) or
  [Tera Term](https://teratermproject.github.io/) work.
- To make `.vxb` files, one of:
  - **Windows PowerShell**, built into Windows 7 and later, so nothing to install
    (`bin2vxb.bat` / `bin2vxb.ps1`);
  - **Python 3** on any system (`bin2vxb.py`);
  - on macOS or Linux without Python, PowerShell (`pwsh bin2vxb.ps1 ...`).
- Your program as a `.bin` file, assembled for the address where it will run (see
  "Where programs may go").

## 1. Load the two BASIC programs (once)

`vxrecvb.bas` and `xclear.bas` are ordinary BASIC text. Load each into its own program
area (e.g. P1 and P2) through F.COM:

1. In BASIC, type **`CLEAR`** first. Variables left over from other programs can fill
   memory and make the load fail with `OM error`.
2. **SHIFT + CASL** (F.COM), choose a free P area, press **S** and set
   `6,N,8,1,N,N,N,B,N` (4800 baud, 8N1, XON/XOFF) with **End = ON**, then **E** (Edit)
   → `Load"COM0:`.
3. On the PC: 4800 baud, 8N1, flow control **Xon/Xoff**. Send the `.bas` file as it is
   (binary/raw), then send **Ctrl+Z** (byte `&H1A`), the end code F.COM waits for.

Note: this step uses XON/XOFF, but sending the `.vxb` later must **not**.

## 2. Reserve the memory (once after each reset)

The receiver lives in the 512 bytes at `&H1CD0-&H1ECF`. These must be reserved with
the extended CLEAR. BASIC's `CLEAR n` does **not** do it; it only sets the string area.

1. Switch to the program area with XCLEAR and `RUN` it. It ends with
   `Now: MODE110(&H18F7),1024`.
2. Type **`MODE110(&H18F7),1024`** directly (not in a program). The answer ` 1024` is
   the reserved size.

1024 bytes are enough for the receiver plus a program in low RAM (see below). For a
program that goes into the reserved area, reserve 512 + its size (rounded up). The
reservation stays until the next reset (`MODE110(&H18F7),0` releases it). XCLEAR itself
lives in the CALC buffer: after using the IN/CALC formula keys, run its loader again.

## 3. Make the `.vxb` file

Open a command prompt in this folder and run `bin2vxb.bat` (it starts the PowerShell
script `bin2vxb.ps1`):

```
bin2vxb prog.bin 0 --exec 0
bin2vxb prog.bin 1ED0 --exec 1ED0 -o prog.vxb
```

- The first number is the **load address** in hex, where the program will be stored.
- `--exec` gives the **start address**. With it, VXRECVB offers to run the program after
  loading; without it, VXRECVB only loads it.
- `-o` sets the output name. By default it is the `.bin` name with `.vxb`.
- Write addresses as plain hex (`1ED0`) or `0x1ED0`, not `&H1ED0`: the Windows command
  line treats `&` as a command separator.

**With Python instead** (any OS), the same arguments:

```
python bin2vxb.py prog.bin 1ED0 --exec 1ED0 -o prog.vxb
```

Both tools write exactly the same file.

The tool prints the address range, the CRC and the number of bytes to send, e.g.
`prog.vxb: &H1ED0-&H25C3 (1780 bytes), exec &H1ED0, CRC &H4A2B, 1791 bytes to send`.

### Where programs may go

VXRECVB accepts only these addresses and refuses everything else, which would
overwrite system areas or BASIC:

- **`&H0000-&H0FFF`**: free RAM on an FX-870P and on a VX-4 with 32 KB or more.
  Nothing extra to reserve. An 8 KB VX-4 has no RAM there; VXRECVB checks this and
  refuses such files.
- **`&H1ED0` up to the end of the reserved area** (`&H1CD0` + the size given to
  `MODE110(&H18F7),size`). This is where programs for an 8 KB VX-4 go.

## 4. Start the receiver

Switch to the program area with VXRECVB and `RUN` it.

- The **first RUN** after a new extended CLEAR installs the machine code
  (`VXRECVB installs RXBIN...`, about 30 seconds). Later RUNs start at once.
- Without the reserved memory it stops with `Need extended CLEAR, not CLEAR` /
  `RUN XCLEAR+MODE110(&H18F7),1024`.
- Then it shows `VXRECVB 4800 ML &H1ED0-&H....`, `Send .vxb (binary, no XON/XOFF)`,
  `and wait for OK. BRK=stop`.

## 5. Send the file

Settings: **4800 baud** (or 9600, see below), **8 data bits, no parity, 1 stop bit,
no flow control**. Send the `.vxb` file **as binary/raw**, with **no delays**. Start
sending only when the calculator shows its waiting screen: without flow control it
can hold only 256 bytes until the receiver runs.

- **CoolTerm**: open `pc-settings\CoolTerm_VXRECVB_9600.CoolTermSettings`, set your
  serial port (and 4800 if you use 4800), Connect, then send the `.vxb` with CoolTerm's
  file-send command (Connection menu). It uses raw file transfer, no flow control and no delays.
- **Tera Term**: start it with `ttermpro.exe /F=TeraTerm_VXRECVB_9600.INI` (or copy
  the keys into your TERATERM.INI), set your port, then File → Send file → the `.vxb`
  with **Binary** ticked. The important settings: flow control none, transmit delay
  0 / 0, `FileSendHighSpeedMode=off`. With 5 ms delays and high-speed mode on, the first
  attempt failed on the real machine.

The screen does not change during the transfer.

## 6. Done

`OK n bytes at &Hxxxx`, then (if the file has a start address)
`Run &Hxxxx ? (Y/N)`. **Y** starts the program (`MODE110`).

## 9600 baud

The calculator's BASIC cannot open the serial port at 9600 baud: `OPEN` accepts speeds
only up to 4800. VXRECVB therefore opens it at 4800, and its machine code switches the
serial chip to 9600. To use it, change line 25 of `vxrecvb.bas` from `25 B=4800` to
**`25 B=9600`** (edit it on the calculator) and set the PC to 9600 as well. The first
screen line then shows `VXRECVB 9600`.

## Errors

| Message | Meaning / what to do |
|---|---|
| `ERR bad header` | The start of the file is damaged; nothing was stored. Send again |
| `ERR outside ML area` | Load address not allowed (see "Where programs may go"); nothing was stored |
| `ERR CRC - send again` | All bytes are stored but some are damaged: send again. Check that the PC sends the file unchanged (binary, no delays, no flow control) |
| `ERR serial nn -PC 4800 8N1?` | Serial error, usually a wrong speed or format on the PC (`nn`: 32 = framing, 8/16 = parity/overrun) |
| `ERR stopped (BRK)` | Stopped with BRK (BASIC may also show its own `Break`) |
| `ERR buffer full` | More than 256 bytes arrived before the receiver ran: start sending later |
| `ERR RXBIN DATA damaged` | The DATA lines of `vxrecvb.bas` were damaged during loading: load it again |
| `ERR BASIC nn line mm` | Any other BASIC error (1 = OM: out of memory, type `CLEAR` and RUN again) |

## The VXB format

| Offset | Bytes | Content |
|---|---|---|
| 0 | 2 | `VX` (marker; anything before it is skipped) |
| 2 | 2 | load address, low byte first |
| 4 | 2 | length n (1-65535), low byte first |
| 6 | 2 | start address, low byte first; `FFFF` = none |
| 8 | 1 | header check: bytes 2-8 add up to 0 (mod 256) |
| 9 | n | the program |
| 9+n | 2 | CRC-16/XMODEM of the program (polynomial `&H1021`, start 0), high byte first |

The header and the address are checked before anything is stored. The CRC is checked
after the transfer, over the stored bytes.

## How it works, briefly

- The serial port is opened without XON/XOFF. With XON/XOFF, the calculator's ROM
  would swallow every received byte `&H11` and `&H13`, and binary data contains those.
- The machine code runs with interrupts off and reads the serial chip itself. It
  stores each byte at its address as it arrives and keeps up with 9600 baud, so no flow
  control is needed.
- Memory used:
  - the receiver at `&H1CD0-&H1ECF` (extended CLEAR);
  - XCLEAR in the CALC buffer at `&H18F7`;
  - nothing else outside BASIC.

## Not tested

- PB-1000 Data Communicator, and other senders, with binary files.
- BRK during a transfer on the real machine (works in the emulator).

## License and credits

VXRECVB, RXBIN and bin2vxb: Copyright (c) 2026 Radovan Hrebicek, MIT License (see
`LICENSE`). `xclear.bas` contains Ao's and 123's CLEAR-ZERO and the 123/BLUE/Ao quick
loader, published by their authors as free to use and distribute; they are not under
the MIT License.
