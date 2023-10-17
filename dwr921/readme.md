# Прошивка OpenWRT на D-Link DWR 921 C1

Прошитый U-Boot

<details>
<summary>U-Boot 2023</summary>

```
U-Boot SPL 2023.10-00953-g3c3f162691 (Oct 17 2023 - 09:24:30 +0000)
Trying to boot from NOR


U-Boot 2023.10-00953-g3c3f162691 (Oct 17 2023 - 09:24:30 +0000)

CPU:   MediaTek MT7620N ver:2 eco:6
Boot:  DDR, SPI-NOR 3-Byte Addr
Clock: CPU: 580MHz, Bus: 193MHz, XTAL: 20MHz
Model: MediaTek MT7620 RFB (WS2120)
DRAM:  64 MiB
Core:  39 devices, 16 uclasses, devicetree: separate
MMC:   mmc@10130000: 0
Loading Environment from SPIFlash... SF: Detected w25q128 with page size 256 Bytes, erase size 4 KiB, total 16 MiB
OK
In:    uartlite@10000c00
Out:   uartlite@10000c00
Err:   uartlite@10000c00
=> sf probe
SF: Detected w25q128 with page size 256 Bytes, erase size 4 KiB, total 16 MiB
```
</details>

Чтение памяти:

```
=> sf read 0x08000000 0x40000 58D44D
device 0 offset 0x40000, size 0x58d44d
SF: 5821517 bytes @ 0x40000 Read: OK
```

Попытка загрузки:
```
=> bootm 08000000
## Booting kernel from Legacy Image at 08000000 ...
   Image Name:   DWR_921
   Image Type:   MIPS Linux Kernel Image (lzma compressed)
   Data Size:    1728786 Bytes = 1.6 MiB
   Load Address: 80000000
   Entry Point:  80391a80
   Verifying Checksum ... OK
Working FDT set to 0
   Uncompressing Kernel Image
lzma compressed: uncompress error 1
Must RESET board to recover
```