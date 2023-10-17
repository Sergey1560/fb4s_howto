# Прошивка OpenWRT на D-Link DWR 921 C1

[Страница устройства](https://openwrt.org/toh/d-link/dwr-921#tab__revisions_c1c3) на сайте OpenWRT.

|             |             |
| ----------- | ----------- |
| SOC      | MediaTek MT7620N | 
| CPU      | 580 Mhz | 
| RAM      | 64 Mb | 
| Flash    | 16 Mb | 
| Ethernet | MT7530 (SoC) 6×10/100 Mbit/s, w/vlan support	 | 

Может быть 2 разных загрузчика:

<details>
<summary>JBoot</summary>
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

<details>
<summary>U-Boot</summary>
```
U-Boot 1.1.3 (Nov 17 2015 - 18:08:01)

Board: Ralink APSoC DRAM:  64 MB
relocate_code Pointer at: 83fb0000
enable ephy clock...done. rf reg 29 = 5
SSC disabled.
spi_wait_nsec: 29 
spi device id: ef 40 18 0 0 (40180000)
find flash: W25Q128BV
raspi_read: from:30000 len:1000 
*** Warning - bad CRC, using default environment

============================================ 
Ralink UBoot Version: 4.1.1.0
-------------------------------------------- 
ASIC 7620_MP (Port5<->None)
DRAM component: 512 Mbits DDR, width 16
DRAM bus: 16 bit
Total memory: 64 MBytes
Flash component: SPI Flash
Date:Nov 17 2015  Time:18:08:01
============================================ 
icache: sets:512, ways:4, linesz:32 ,total:65536
dcache: sets:256, ways:4, linesz:32 ,total:32768 

 ##### The CPU freq = 580 MHZ #### 
 estimate memory size =64 Mbytes
raspi_read: from:40028 len:6 


Please choose the operation: 
   1: Load system code to SDRAM via TFTP. 
   2: Load system code then write to Flash via TFTP. 
   3: Boot system code via Flash (default).
   4: Entr boot command line interface.
   7: Load Boot Loader code then write to Flash via Serial. 
   9: Load Boot Loader code then write to Flash via TFTP. 
 0 
   
3: System Boot system code via Flash.
## Booting image at bc050000 ...
raspi_read: from:50000 len:40 
   Image Name:   DWR_921
   Image Type:   MIPS Linux Kernel Image (lzma compressed)
   Data Size:    1728786 Bytes =  1.6 MB
   Load Address: 80000000
   Entry Point:  80391a80
raspi_read: from:50040 len:1a6112 
   Verifying Checksum ... OK
   Uncompressing Kernel Image ... OK
No initrd
## Transferring control to Linux (at address 80391a80) ...
## Giving linux memsize in MB, 64

Starting kernel ...


LINUX started...

 THIS IS ASIC

SDK 5.0.S.0
Linux version 3.10.108+ (jenkins@jrdslave2) (gcc version 5.5.0 (Buildroot 2018.08-git-00492-g751df64) ) #1 Thu Aug 18 18:02:37 MSK 2022
```
</details>

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

Создание образа uboot:
```
mkimage -A mips -O linux -T kernel -C lzma -a 0 -e 0 -n Linux -d dlink_dwr-921-c1-kernel.bin kernel.bin
```

