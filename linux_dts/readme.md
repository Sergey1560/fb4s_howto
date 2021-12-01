# Подключение устройств в Linux через device tree

В качестве платформы используется Armbian Bullsye, с ядром 5.10 В качестве примера приведено поделючени датчика тока и напряжения INA226 и экрана на контроллере SSD1306. Оба устройства подключены по шине I2C.

## Подключение INA226

Для для датчика напряжения и тока [INA226](https://www.ti.com/lit/ds/symlink/ina226.pdf?ts=1638376222123&ref_url=https%253A%252F%252Fwww.google.com%252F) в ядре уже есть драйвер. Достаточно создать dts файл, с описанием к какой шине подключен датчик и какой у него адрес.

Я подключал к плате [NanoPi Neo Air](https://wiki.friendlyarm.com/wiki/index.php/NanoPi_NEO_Air), к шине I2C0.

Для начала, можно включить в armbian-config overlay i2c0 и посмотреть, какие устройства есть на шине:

```
root@nanopiair:~# i2cdetect -y 0
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:                         -- -- -- -- -- -- -- -- 
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
30: -- -- -- -- -- -- -- -- -- -- -- -- UU -- -- -- 
40: UU -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
70: -- -- -- -- -- -- -- --                         
```

Как видно, на шине есть два устройства, с адресом 0x40 и 0x3C. 0x40 - это INA226, 0x3C - экран на SSD1306. Адрес устройства можно посмотреть в datasheet.

Для подключения INA226 я сделал такой dts:

```
/dts-v1/;
/plugin/;

/ {
    compatible = "allwinner,sun8i-h3";

    fragment@1 {
        target = <&i2c0>;
        __overlay__ {
            pinctrl-names = "default";
            pinctrl-0 = <&i2c0_pins>;
            status = "okay";
            
        power-sensor@40 {
            compatible = "ti,ina226";
            reg = <0x40>;
            shunt-resistor = <1000>;
        };
    };
    };    
};
```

В параметре reg указан адрес устройства, в параметре shunt-resistor номинал шунта, на котором измеряется падение напряжения. Описание всех возможных параметров, а также их значений находится в [документации на ядро](https://elixir.bootlin.com/linux/v5.10.60/source/Documentation/devicetree/bindings/hwmon/ina2xx.txt)

Добавление overlay:

```
sudo armbian-add-overlay sun8i-h3-ina226.dts
```

При этом dts файл будет скомпилирован в бинарный вид, скопирован в /boot/overlay-user/ и в armbianEnv.txt будет добавлен в параметр user_overlays.

После перезагрузки можно проверить, что устройство подключено:

```
sergey@nanopiair:~$ dmesg|grep ina2
[   10.403095] ina2xx 0-0040: power monitor ina226 (Rshunt = 1000 uOhm)
```

Посмотреть значения напряжения (в мВ) можно командой:

```
sergey@nanopiair:~$ cat /sys/bus/i2c/devices/0-0040/hwmon/hwmon1/in1_input
5343
```

Значение тока:

```
cat /sys/bus/i2c/devices/0-0040/hwmon/hwmon1/curr1_input 
```

## Подключение экрана на SSD1306

Для экрана на контроллере SSD1306 также есть драйвер в ядре. В [описании dts](https://elixir.bootlin.com/linux/v5.10.60/source/Documentation/devicetree/bindings/display/ssd1307fb.txt) есть пример и указаны несколько типов контроллеров, с которыми работает драйвер. В стандартном armbian есть драйвер ssd1306:

```
sergey@nanopiair:~$ find /lib/modules/$(uname -r)/kernel/drivers/ -iname "*ssd1306*"
/lib/modules/5.10.60-sunxi/kernel/drivers/staging/fbtft/fb_ssd1306.ko
```

Но это не тот драйвер, про который написано в описании. Если посмотреть [его код](https://elixir.bootlin.com/linux/v5.10.60/source/drivers/staging/fbtft/fb_ssd1306.c), то можно увидеть, что драйвер этот для шины SPI. Для I2C драйвер называется именно [ssd1307](https://elixir.bootlin.com/linux/v5.10.60/source/drivers/video/fbdev/ssd1307fb.c), а конкретный тип контроллера выбирается в параметре compatible.

Поскольку в стандартном ядре armbian нет драйвера ssd1307, его нужно туда добавить. Я собирал ядро по [инструкции от armbian](https://docs.armbian.com/Developer-Guide_Build-Preparation/). В menuconfig ядра нужно включить сборку модуля для SSD1307. Самый простой способ найти нужную опцию, нажать "/" и ввести "ssd1307". Я включил сборку ввиде подключаемого модуля.

После сборки ядра скопировал на nanopi готовые deb пакеты:

```
linux-dtb-current-sunxi_21.11.0-trunk_armhf.deb
linux-headers-current-sunxi_21.11.0-trunk_armhf.deb
linux-image-current-sunxi_21.11.0-trunk_armhf.deb
linux-u-boot-current-nanopiair_21.11.0-trunk_armhf.deb
```

Файл для наложения на device tree:

```
/dts-v1/;
/plugin/;

/ {
    compatible = "allwinner,sun8i-h3";

    fragment@0 {
        target = <&i2c0>;
        __overlay__ {
            pinctrl-names = "default";
            pinctrl-0 = <&i2c0_pins>;
            status = "okay";

ssd1306: oled@3c {
	compatible = "solomon,ssd1306fb-i2c";
	reg = <0x3c>;
	solomon,height = <64>;
    solomon,width = <128>;
	solomon,com-invdir;
    solomon,page-offset = <0>;
	};
	};
};
};
```

В выводе dmesg есть упоминание о загрузке драйвер:

```
sergey@nanopiair:~$ dmesg|grep ssd
[   10.513759] ssd1307fb 0-003c: fb0: Solomon SSD1307 framebuffer device registered, using 1024 bytes of video memory
[   10.968144] systemd[1]: Starting Load/Save Screen Backlight Brightness of backlight:ssd1307fb0...
[   11.054282] systemd[1]: Finished Load/Save Screen Backlight Brightness of backlight:ssd1307fb0.
```

Так же появилось устройство framebuffer - /dev/fb0

После добавления dts и перезагрузки на экран стала выводиться системная консоль. Для экрана размером 128*64 это не лучшее применение. Для того, чтобы отключить вывод консоли, можно назначить ее вывод на не существующий 1-ый framebuffer. Для этого в armbianEnv.txt нужно добавить параметры для ядра:

```
extraargs="fbcon=map:1"
```

После перезагруки экран останется пустым. Для проверки, можно вывести на экран случайные данные:

```
root@nanopiair:~# cat /dev/random > /dev/fb0
```

Экран заполнится случайным мусором. Очистить экран можно заполнив его 0x00:

```
root@nanopiair:~# cat /dev/zero > /dev/fb0 
```

Контроллер экрана умеет включать и отключать подсветку:

```
root@nanopiair:~# echo 0 > /sys/bus/i2c/devices/0-003c/backlight/ssd1307fb0/brightness
root@nanopiair:~# echo 255 > /sys/bus/i2c/devices/0-003c/backlight/ssd1307fb0/brightness
```

Для тестирования вывода на экран через frame buffer можно использовать простой код:

```
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <linux/fb.h>
#include <sys/mman.h>


int main(int argc, char* argv[])
{
  int fbfd = 0;
  struct fb_var_screeninfo vinfo;
  struct fb_fix_screeninfo finfo;
  long int screensize = 0;
  char *fbp = 0;

  // Open the file for reading and writing
  fbfd = open("/dev/fb0", O_RDWR);
  if (!fbfd) {
    printf("Error: cannot open framebuffer device.\n");
    return(1);
  }
  printf("The framebuffer device was opened successfully.\n");

  // Get fixed screen information
  if (ioctl(fbfd, FBIOGET_FSCREENINFO, &finfo)) {
    printf("Error reading fixed information.\n");
  }

  // Get variable screen information
  if (ioctl(fbfd, FBIOGET_VSCREENINFO, &vinfo)) {
    printf("Error reading variable information.\n");
  }
  printf("%dx%d, %d bpp\n", vinfo.xres, vinfo.yres, vinfo.bits_per_pixel );

  // map framebuffer to user memory 
  screensize = finfo.smem_len;

  fbp = (char*)mmap(0, 
                    screensize, 
                    PROT_READ | PROT_WRITE, 
                    MAP_SHARED, 
                    fbfd, 0);

  if ((int)fbp == -1) {
    printf("Failed to mmap.\n");
  }
  else {
    // draw...
    // just fill upper half of the screen with something
    memset(fbp, 0xff, screensize/2);
    // and lower half with something else
    memset(fbp + screensize/2, 0, screensize/2);
  }

  // cleanup
  munmap(fbp, screensize);
  close(fbfd);
  return 0;
}

```

Для компиляции в исполняемый файл (если файл с исходником называется fbtest1.c) достаточно выполнить "make fbtest1" и можно запустить:
```
sergey@nanopiair:~/fbtest$ ./fbtest1 
The framebuffer device was opened successfully.
128x64, 1 bpp
```

На экран при этом будет выведено тестовое изображение - верхняя половина экрана будет залита, нижняя пустая.
Подробности по программированию framebuffer под Linux можно посмотреть по [ссылке](http://raspberrycompote.blogspot.com/2013/01/low-level-graphics-on-raspberry-pi-part.html)

## Полезное

После добавления overlay можно посмотреть как они применились в итоговое device tree:

```
dtc --sort -I fs -O dts  /sys/firmware/devicetree/base > device_tree.out
```