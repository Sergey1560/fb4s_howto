# Настройка модема Quectel EP-06 в linux (armbian)

Модем Quectel EP-06 подключается через QMI Interface (Qualcomm MSM Interface). При подключении модем определяется и появляется устройство wwan0:

```
usb 3-1: new high-speed USB device number 3 using ehci-platform
usb 3-1: New USB device found, idVendor=2c7c, idProduct=0306, bcdDevice= 3.10
usb 3-1: New USB device strings: Mfr=1, Product=2, SerialNumber=3
usb 3-1: Product: EP06-E
usb 3-1: Manufacturer: Quectel
usb 3-1: SerialNumber: 0123456789ABCDEF
option 3-1:1.0: GSM modem (1-port) converter detected
usb 3-1: GSM modem (1-port) converter now attached to ttyUSB0
option 3-1:1.1: GSM modem (1-port) converter detected
usb 3-1: GSM modem (1-port) converter now attached to ttyUSB1
option 3-1:1.2: GSM modem (1-port) converter detected
usb 3-1: GSM modem (1-port) converter now attached to ttyUSB2
option 3-1:1.3: GSM modem (1-port) converter detected
usb 3-1: GSM modem (1-port) converter now attached to ttyUSB3
qmi_wwan 3-1:1.4: cdc-wdm0: USB WDM device
qmi_wwan 3-1:1.4 wwan0: register 'qmi_wwan' at usb-1c1b000.usb-1, WWAN/QMI device, 52:62:39:c6:75:24
Using default interface naming scheme 'v247'.
ethtool: autonegotiation is unset or enabled, the speed and duplex are not writable.
Info: Interface "wwan0" enabled.
```

```
root@orangepizero:/home/sergey# lsusb -t
    |__ Port 1: Dev 2, If 4, Class=Vendor Specific Class, Driver=qmi_wwan, 480M
```

## Вариант 1 (QMI Tools)

Для настройки необходимо установить пакеты libqmi-utils и udhcpc. К сожалению dhclient, который идет в составе armbian, не умеет работать с raw ip. Поэтому используется дополнительный пакет udhcpc.

```
apt-get install libqmi-utils udhcpc
```

Проверка режима работы модема:

```
root# qmicli --device=/dev/cdc-wdm0 --device-open-proxy --get-wwan-iface
wwan0

root# qmicli --device=/dev/cdc-wdm0 --get-expected-data-format
802-3

root# qmicli --device=/dev/cdc-wdm0 --device-open-proxy --wda-get-data-format
[/dev/cdc-wdm0] Successfully got data format
                   QoS flow header: no
               Link layer protocol: 'raw-ip'
  Uplink data aggregation protocol: 'disabled'
Downlink data aggregation protocol: 'disabled'
                     NDP signature: '0'
Downlink data aggregation max datagrams: '0'
Downlink data aggregation max size: '0'
```

Изменение режима работы драйвера:

```
root# ip link set dev wwan0 down
root# echo Y > /sys/class/net/wwan0/qmi/raw_ip
root# ip link set dev wwan0 up
```

Подключение к сети:

```
root# qmicli --device=/dev/cdc-wdm0 --device-open-proxy --wds-start-network="ip-type=4,apn=m.tinkoff" --client-no-release-cid
[/dev/cdc-wdm0] Network started
	Packet data handle: '3301379984'
[/dev/cdc-wdm0] Client ID not released:
	Service: 'wds'
	    CID: '20'
```

Получение IP адреса по dhcp:

```
root# udhcpc -q -f -n -i wwan0
udhcpc: started, v1.30.1
/etc/udhcpc/default.script: 60: resolvconf: not found
udhcpc: sending discover
udhcpc: sending select for 100.76.95.8
udhcpc: lease of 100.76.95.8 obtained, lease time 7200
/etc/udhcpc/default.script: 47: resolvconf: not found
root# echo "nameserver 8.8.8.8" > /etc/resolv.conf
```

Дополнительные команды:

```
Производитель:
qmicli --device=/dev/cdc-wdm0 --device-open-proxy --dms-get-manufacturer

Модель:
qmicli --device=/dev/cdc-wdm0 --device-open-proxy --dms-get-model

Версия прошивки:
qmicli --device=/dev/cdc-wdm0 --device-open-proxy --dms-get-revision

IDs (IMEI и т.д.):
qmicli --device=/dev/cdc-wdm0 --device-open-proxy --dms-get-ids

Статус SIM:
qmicli --device=/dev/cdc-wdm0 --device-open-proxy --uim-get-card-status


qmicli -d /dev/cdc-wdm0 --nas-get-signal-info
qmicli -d /dev/cdc-wdm0 --nas-get-signal-strength
qmicli -d /dev/cdc-wdm0 --nas-get-home-network

qmicli -d /dev/cdc-wdm0 --nas-get-serving-system

qmi-network /dev/cdc-wdm0 status
qmicli -d /dev/cdc-wdm0  --wds-get-packet-service-status
```

Настройка автоматического запуска:

```
echo "APN=m.tinkoff" > /etc/qmi-network.conf 
```

В /etc/network/interfaces:

```
allow-hotplug wwan0
auto wwan0
iface wwan0 inet manual
pre-up ifconfig wwan0 down
pre-up echo Y > /sys/class/net/wwan0/qmi/raw_ip
pre-up for _ in $(seq 1 10); do /usr/bin/test -c /dev/cdc-wdm0 && break; /bin/sleep 1; done
pre-up for _ in $(seq 1 10); do /usr/bin/qmicli -d /dev/cdc-wdm0 --nas-get-signal-strength && break; /bin/sleep 1; done
pre-up /usr/bin/qmi-network /dev/cdc-wdm0 start
pre-up udhcpc -i wwan0
post-down /usr/bin/qmi-network /dev/cdc-wdm0 stop
```

## Вариант 2 (Modem manager)

Установка ModemManager:

```
apt-get install modemmanager
```

После установки необходимо перезагрузить. Просмотр доступных модемов:

```
root# mmcli --list-modems
    /org/freedesktop/ModemManager1/Modem/0 [Quectel] EP06-E
```

Получение информации о модеме:

```
root# mmcli --modem=0
  -----------------------------------
  General  |               dbus path: /org/freedesktop/ModemManager1/Modem/0
           |               device id: 8f3f39de34fc745b912b2f40095c4a6bcea64fbb
  -----------------------------------
  Hardware |            manufacturer: Quectel
           |                   model: EP06-E
           |       firmware revision: EP06ELAR04A03M4G
           |          carrier config: ROW_Generic_3GPP
           | carrier config revision: 06010821
           |            h/w revision: 20000
           |               supported: gsm-umts, lte
           |                 current: gsm-umts, lte
           |            equipment id: 861486022026011
  -----------------------------------
  System   |                  device: /sys/devices/platform/soc/1c1b000.usb/usb3/3-1
           |                 drivers: option1, qmi_wwan
           |                  plugin: quectel
           |            primary port: cdc-wdm0
           |                   ports: cdc-wdm0 (qmi), ttyUSB0 (qcdm), ttyUSB1 (gps), 
           |                          ttyUSB2 (at), ttyUSB3 (at), wwx069f0d4a9fcd (net)
  -----------------------------------
  Status   |                    lock: sim-pin2
           |          unlock retries: sim-pin (3), sim-puk (10), sim-pin2 (3), sim-puk2 (10)
           |                   state: registered
           |             power state: on
           |             access tech: lte
           |          signal quality: 100% (recent)
  -----------------------------------
  Modes    |               supported: allowed: 3g; preferred: none
           |                          allowed: 4g; preferred: none
           |                          allowed: 3g, 4g; preferred: 4g
           |                          allowed: 3g, 4g; preferred: 3g
           |                 current: allowed: 2g, 3g, 4g; preferred: 4g
  -----------------------------------
  Bands    |               supported: utran-1, utran-3, utran-5, utran-8, eutran-1, eutran-3, 
           |                          eutran-5, eutran-7, eutran-8, eutran-20, eutran-28, eutran-32, 
           |                          eutran-38, eutran-40, eutran-41
           |                 current: utran-1, utran-3, utran-5, utran-8, eutran-1, eutran-3, 
           |                          eutran-5, eutran-7, eutran-8, eutran-20, eutran-28, eutran-32, 
           |                          eutran-38, eutran-40, eutran-41
  -----------------------------------
  IP       |               supported: ipv4, ipv6, ipv4v6
  -----------------------------------
  3GPP     |                    imei: 364185042021011
           |             operator id: 25020
           |           operator name: Tinkoff
           |            registration: home
  -----------------------------------
  3GPP EPS |    ue mode of operation: csps-2
  -----------------------------------
  SIM      |               dbus path: /org/freedesktop/ModemManager1/SIM/0

```

Просмотр дотупных модемов в Network Manager (появился cdc-wdm0):

```
root# nmcli device status
DEVICE         TYPE      STATE         CONNECTION         
eth0           ethernet  connected     Wired connection 1 
cdc-wdm0       gsm       disconnected  --                 
wlan0          wifi      disconnected  --                 
p2p-dev-wlan0  wifi-p2p  disconnected  --                 
lo             loopback  unmanaged     --       
```

Создание профиля подключения:

```
root# nmcli connection add type gsm ifname '*' con-name 'Tinkoff' apn 'm.tinkoff' connection.autoconnect yes
Connection 'Tinkoff' (ba3fdc29-1714-4a55-9dd9-143fe0f7279c) successfully added.
```
