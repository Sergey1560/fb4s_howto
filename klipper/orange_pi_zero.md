# Установка KlipperScreen на Orange Pi Zero с экраном 3.5"

## Используемое железо

Для установки [Klipper](https://github.com/KevinOConnor/klipper) использовалась плата Orange Pi Zero (http://www.orangepi.org/orangepizero/) на процессоре H2+ с 512мб памяти. Операционная система - [Armbian Buster](https://www.armbian.com/orange-pi-zero/) с актуальным ядром 5.10.

В качестве экрана использован 3.5" экран для Raspberry Pi,  подключаемый по SPI.

## Программная часть

Установку самого [Klipper](https://github.com/KevinOConnor/klipper) и [Moonraker](https://github.com/Arksine/moonraker) можно сделать при помощи скрипта [Kiauh](https://github.com/th33xitus/kiauh), каких-то особенностей в установке нет. Есть некоторые особенности только в установке [KlipperScreen](https://github.com/jordanruthe/KlipperScreen).

## Подключение экрана

У платы Orange Pi Zero 40-иновая колодка совпадает с Raspberry Pi, поэтому экран можно подключить прямо к плате. Важно только правильно ориентировать экран.

![Orange Pi Zero pinout](./klipper/img/orange-pi-zero-piout.png)

![TFT pinout](./klipper/img/lcd_pinout.jpg)

Сам экран выполнен на основе микросхемы ILI9486. Эта микросхема умеет работать как по параллельному интерфейсу, так и по последовательному. По какой-то причине разработчики включили параллельный интерфейс, а затем при помощи сдвиговых регистров превратили его в последовательный:

![TFT schematic](./klipper/img/ili9486_shematic.png)

Из распиновки Orange Pi Zero видно, что экран подключается к SPI1. CS сигнал экрана будет подключен на PA13, а CS сигнал для touch-панели будет подключен на PA10. Сигнал IRQ от touch панели подключен к PA1. Сам touch выполнен на микросхеме TP2046 (аналог ADS7846).

В ядре linux уже есть драйвера и для ILI9486 и для ADS7846. Для включения устройств достаточно указать ядру что куда подключено, при помощи device tree.

```
/dts-v1/;
/plugin/;

/ {
    compatible = "allwinner,sun8i-h3";

	fragment@0 {
		target = <&spi1>;
		__overlay__ {
			num-cs = <2>;
			cs-gpios = <&pio 0 10 0>,
					   <&pio 0 13 0>;
			status = "okay";
			#address-cells = <1>;
			#size-cells = <0>;

			ili9486: ili9486@0{
				compatible = "ilitek,ili9486";
				reg = <1>;
				spi-max-frequency = <16000000>;
				txbuflen = <32768>;
				rotate = <90>;
				bgr = <0>;
				fps = <30>;
				buswidth = <8>;
				regwidth = <16>;
				reset-gpios = <&pio 0 2 0>;
				dc-gpios = <&pio 0 18 0>;
				debug = <1>;
				init = <0x10000f1 0x36 0x04 0x00 0x3c 0x0f 0x8f 0x10000f2 0x18 0xa3 0x12 0x02 0xb2 0x12 0xff 0x10 0x00 0x10000f8 0x21 0x04 0x10000f9 0x00 0x08 0x1000036 0x08 0x10000b4 0x00 0x10000c1 0x41 0x10000c5 0x00 0x91 0x80 0x00 0x10000e0 0x0f 0x1f 0x1c 0x0c 0x0f 0x08 0x48 0x98 0x37 0x0a 0x13 0x04 0x11 0x0d 0x00 0x10000e1 0x0f 0x32 0x2e 0x0b 0x0d 0x05 0x47 0x75 0x37 0x06 0x10 0x03 0x24 0x20 0x00 0x100003a 0x55 0x1000011 0x1000036 0x28 0x20000ff 0x1000029>;
			};
		};
	};

	fragment@1 {
	target = <&spi1>;
	__overlay__ {
		#address-cells = <1>;
		#size-cells = <0>;
		status = "okay";
		ads7846@0 {
			compatible = "ti,ads7846";
			reg = <0>; 
			status = "okay";
			spi-max-frequency = <1600000>;
			interrupt-parent = <&pio>;
			interrupts = <0 1 2>; /* PA1 IRQ_TYPE_EDGE_FALLING */
			pendown-gpio = <&pio 0 1 0>; /* PA1 */

			/* driver defaults, optional */
			ti,x-min = /bits/ 16 <0>;
			ti,y-min = /bits/ 16 <0>;
			ti,x-max = /bits/ 16 <0x0FFF>;
			ti,y-max = /bits/ 16 <0x0FFF>;
			ti,pressure-min = /bits/ 16 <0>;
			ti,pressure-max = /bits/ 16 <0xFFFF>;
			ti,x-plate-ohms = /bits/ 16 <400>;
			ti,swap-xy = <1>;
		};
	};
	};


};
```

[Готовый файл](klipper/sun8i-h3-ili9486.dts)

В overlay для SPI1 указаны два cs-gpios, для двух устройств на шине SPI. Выбор конкретного CS - в overlay устройства в параметре reg

## Установка dts

Компиляция и установка overlay в armbian автоматизированы:

```
sudo armbian-add-overlay sun8i-h3-ili9486.dts
```

Overlay будет установлен в папке пользовательских overlay-ев. Для применения достаточно перезагрузить систему. В выводе dmesg должны появится два устройства на SPI шине:

```
sergey@orangepizero:~$ dmesg|grep spi
[   10.377212] ads7846 spi1.0: supply vcc not found, using dummy regulator
[   10.382330] ads7846 spi1.0: touchscreen, irq 70
[   10.385112] input: ADS7846 Touchscreen as /devices/platform/soc/1c69000.spi/spi_master/spi1/spi1.0/input/input0
[   10.427147] [drm] Initialized ili9486 1.0.0 20200118 for spi1.1 on minor 0
[   12.365795] ili9486 spi1.1: [drm] fb0: ili9486drmfb frame buffer device
```

