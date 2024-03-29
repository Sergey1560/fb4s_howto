# Стандартная прошивка FB5/4S

В принтеры FB5 и FB4S используются несколько плат: Robin Nano 1.1, Robin Nano-s 1.3, Robin Nano 1.3 Определить, какая плата установлена в принтере можно [тут](../mks_board/readme.md) Прошивка от производителя принтера (стандартная прошивка) для этих плат устроена одинаково.

Прошивка сделана на базе довольно старой версии Marlin v1. Вся часть, которая управляет печатью осталась от Marlin. Добавлен только графический интерфейс и работа с wifi модулем. В связи с этим, управление принтером доступно через Marlin-совместимый G-код. Полное описание команд можно посмотреть на [сайте Marlin](https://marlinfw.org/meta/gcode/), а краткий ликбез [у Дмитрия Соркина](https://k3d.tech/archives/253)

Архив с прошивкой состоит из нескольких папок и файлов:

```
mks_font  - папка с шрифтами
mks_pic - папка с картинками
MksWifi.bin - прошивка WIFI модуля
Robin_nano35.bin - прошивка платы управления принтером
robin_nano35_cfg.txt - файл настроек
╨▐╕──┌╚▌.txt - changelog на китайском
```

На плате установлен МК STM32F103 (для Robin Nano 1.1) или STM32F407 (для плат 1.3), у него всего 512Кб flash памяти. Картинки туда не влезут. Поэтому для картинок на плате установлена дополнительная flash-память W25Q, картинки хранятся в ней. Загружает туда картинки сама прошивка. Если при запуске на SD карте есть папка mks_pic, то из нее будут загружены картинки, а папка будет переименована в bak_pic. Аналогично с папкой mks_font, в которой находятся шрифты.

**MksWifi.bin** - это прошивка для модуля ESP8266, который установлен на плате. Для прошивки принтера или изменения настроек это файл копировать на SD карту не нужно. Он нужен только для прошивки WIFI модуля.

**Robin_nano35.bin** - это прошивка для платы управления. Это программа, которая будет работать внутри МК и управлять печатью. Если при включении принтера на SD карте есть файл Robin_nano35.bin, он будет прошит в микроконтроллер, а сам файл будет переименован в Robin_nano35.cur. Загружает прошивку бутлоадер, который так же находится внутри МК. Прошивка с SD карты абсолютно безопасный процесс. Если прервать процесс или загрузить какой-то мусор вместо прошивки, то плата просто не запустится. В таком случае достаточно снова скопировать на карту памяти файл Robin_nano35.bin и включить принтер. Бутлоадер загрузит прошивку и все исправит.

**robin_nano35_cfg.txt** - файл настроек прошивки. В файле присутствуют "кракозябры" - это комментарии на китайском. Их можно удалить или просто не трогать. Не все настройки дотупны из меню принтера, некоторые можно изменить в этом файле. Это не прошивка, а только настройки. Для применения настроек нужно положить на карту памяти файл robin_nano35_cfg.txt и прошивка при запуске считает оттуда настройки. Если настройки были считаны, файл будет переименован в robin_nano35_cfg.cur. Если понадобится опять что-то изменить, файл снова нужно переименовать в robin_nano35_cfg.txt Для изменения настроек текущей прошивки, прошивать саму прошивку не нужно. Достаточно положить на карту файл robin_nano35_cfg.txt (и не класть Robin_nano35.bin) и настройки будет применены.

## Основные настройки

### Шаговые двигатели

Для движения осей используеются шаговые двигатели. Общий принцип работы можно посмотреть в [видео](https://www.youtube.com/watch?v=r_V8vIuEPws). Для управления двигателем используется специальная микросхема - драйвер. С точки зрения прошивки, двигатель управляется 2-мя сигналами - направление и шаги. Сигнал "направление" может быть или 0 или 1, и в зависимости от этого двигатель будет вращаться в одну или в другую сторону. У разных драйверов направление вращения может отличаться. Кроме того, оно зависит от того, как подключены обмотки двигателя. Настройка этого параметра называется "инвертирование осей". Если после замены драйверов у вас происходит движение не в ту сторону (проверить можно из меню движения принтера), нужно просто инвертировать этот параметр. Если был 1 поставить 0, если был 0, постаивть 1.

В файле robin_nano35_cfg.txt это параметры:

```
>INVERT_X_DIR 	        0	
>INVERT_Y_DIR 	        0
>INVERT_Z_DIR          	0
>INVERT_E0_DIR        	0
>INVERT_E1_DIR         	0 - E1 это для второго экструдера, он не используется.
```

Второй параметр упраления шаговым двигателем - шаги. Плата управления выдает на драйвер импульсы, которые драйвер преобразует в ток на обмотках двигателя. С точки зрения двигателя, есть понятие полного шага и микрошага (подробнее про это в видео). С точки зрения программы управления, шаги это микрошаги. Т.е. сколько сделать импульсов, чтобы двигатель повернулся на нужный угол. На какой конкретно угол драйвер повернет двигатель зависит от настроек деления шагов.
Например возьмем двигатель с шагом 1.8 градуса (полный оборот 200 полных шагов). Если деление шагов стоит 1/1, то на каждый импульс от платы драйвер будет поворачивать двигатель на 1 полный шаг, т.е. 1.8 градуса, а полный оборот сделает за 200 импульсов. Если изменить деление шагов на 1/8, то на каждый импульс от платы драйвер будет делать микрошаг размером в 1/8 полного шага. И за теже 200 импульсов сделает не полный оборот, а повернется на 45 градусов. Таким образом важно установить одинаковые настройки как для драйвера, так и для прошивки.

Для драйвера деление шагов задается перемычками MS1 MS2 на плате под драйвером. Установленная перемычка это 1, снятая 0. Для разных драйверов используются разные комбинации.

Для платы управления нужно задать количество шагов на 1 мм. Это количество меняется в зависимости от деления шагов установленных на драйвере. Стандартное количество шагов для деления 1/16:

```
>DEFAULT_X_STEPS_PER_UNIT	80
>DEFAULT_Y_STEPS_PER_UNIT	80
>DEFAULT_Z_STEPS_PER_UNIT	400
>DEFAULT_E0_STEPS_PER_UNIT	400
```
Значения по осям X,Y,Z в целом не нуждаются в какой-либо калибровке. Они зависят от настроек деления шагов и передаточного отношения привода. Таким образом, в случае изменения деления шагов изменяться эти величины будут кратно 2.

Количество шагов для экструдера - параметр который желательно откалибровать. Подробнее в [видео Дмитрия Соркина](https://www.youtube.com/watch?v=Mga_ezYDTNI) и на [вики](https://fbghost.info/bin/view/Main/%D0%9D%D0%B0%D1%81%D1%82%D1%80%D0%BE%D0%B9%D0%BA%D0%B0/4S%20-%20%D0%9D%D0%B0%D1%81%D1%82%D1%80%D0%BE%D0%B9%D0%BA%D0%B0%20%D1%88%D0%B0%D0%B3%D0%BE%D0%B2%20%D1%8D%D0%BA%D1%81%D1%82%D1%80%D1%83%D0%B4%D0%B5%D1%80%D0%B0/). Для калибровки удобнее вынимать тефлоновую трубку не из головы, а из фидера.

### Настройки скорости перемещения

Основные настройки управления движением - максимальная скорость, максимальное ускорение, рывок (jerk).

Максимальная скорость перемещения задается параметрами:
```
>DEFAULT_X_MAX_FEEDRATE		200	#X��Ĭ���ٶ� (mm/s)		
>DEFAULT_Y_MAX_FEEDRATE		200	#Y��Ĭ���ٶ� (mm/s)		
>DEFAULT_Z_MAX_FEEDRATE		10	#Z��Ĭ���ٶ� (mm/s)		
>DEFAULT_E0_MAX_FEEDRATE	100	#E��Ĭ���ٶ� (mm/s)		
```

Как понятно из комментариев, значение стоит в мм/с. Если в g-коде, который подготовил слайсер, стоит значение выше этого, то будет применено именно это значение. Быстрее чем указано тут, перемещаться не будет.

Максимальное ускорение:

```
>DEFAULT_X_MAX_ACCELERATION	2000	#X��Ĭ�������ٶ� (change/s) change = mm/s
>DEFAULT_Y_MAX_ACCELERATION	2000	#Y��Ĭ�������ٶ� (change/s) change = mm/s
>DEFAULT_Z_MAX_ACCELERATION	50	#Z��Ĭ�������ٶ� (change/s) change = mm/s
>DEFAULT_E0_MAX_ACCELERATION 3000	#E��Ĭ�������ٶ� (change/s) change = mm/s
```

У головы, валов, ротора двигателя и всего, что двигается, есть определенная инерция. Невозможно начать движение сразу с заданной скоростью (если эта скорость достаточно высокая). Из-за инерции двигатель просто пропустит какое-то количество шагов и перемещение будет выполнено на неверное расстояние. Чтобы этого избежать, заданная скорость набирается с определенным ускорение. Это ускорение можно задавать через G-код команды. Данные параметры ограничивают максимальное ускорение, которое можно установить.

Ускорение по умолчанию:

```
>DEFAULT_ACCELERATION		1000	#X,Y,Z,E ��ӡʱ��Ĭ�ϼ��ٶ�		
>DEFAULT_RETRACT_ACCELERATION	2500	#X,Y,Z,E �س�Ĭ�ϼ��ٶ�		
>DEFAULT_TRAVEL_ACCELERATION	1500	#X,Y,Z �Ǵ�ӡʱ��Ĭ�ϼ��ٶ�	
>DEFAULT_MINIMUMFEEDRATE	0.0	#Ĭ����С�ٶ�						
>DEFAULT_MINSEGMENTTIME		20000	#�����ʱ��һ���ƶ��������Сʱ��(��λms). 
>DEFAULT_MINTRAVELFEEDRATE	0.0	#		
```

Это параметры ускорения, которые будут применяться, если не было явной команды установки ускорений. Если вы не включали в слайсере управление ускорением, то будут именно эти значения. 

Рывок (jerk):

```
>DEFAULT_XJERK 			18.0	#Ĭ��X�� Jerk (mm/s)	
>DEFAULT_YJERK 			18.0	#Ĭ��Y�� Jerk (mm/s)	
>DEFAULT_ZJERK 			0.4	#Ĭ��Z�� Jerk (mm/s)	
>DEFAULT_EJERK 			2.0	#Ĭ��E�� Jerk (mm/s)	
```

Это скорость максимальная скорость, которая будет установлена без использования ускорения. На малых величинах скорости использовать управление ускорением не нужно - это будет только замедлять движение. Для примера: XJERK 18, голова стоит на месте. Приходит команда на перемещение со скоростью 100мм/с. Двигатель от нулевой скорости сразу же начнет движение со скоростью 18 мм/с, а дальше с величиной ускорения DEFAULT_ACCELERATION (если не было явно задано другое) будет разгоняться до 100мм/с и продолжит движение на этой сокрости.

### Параметры управления температурой

```
>EXTRUDE_MINTEMP 	170		#��ӡʱ,����������¶�(�𱣻�����)
>HEATER_0_MINTEMP	0		#����0��С�¶�ֵ
>HEATER_0_MAXTEMP 	300		#����0����¶�ֵ
>HEATER_1_MINTEMP	0		#����1��С�¶�ֵ
>HEATER_1_MAXTEMP 	300		#����1����¶�ֵ
>BED_MAXTEMP 		150		#�ȴ�����¶�ֵ
```

**EXTRUDE_MINTEMP** - минимальная температура при которой будет подача пластика. Если температура ниже, подача происходить не будет.

**HEATER_0_MINTEMP** - минимальная температура нагревателя. Если температура ниже, то скорее всего оборван термистор и будет сообщение об ошибки. Это нужно для безопасности, чтобы в случае обрыва термистора не происходит бесконечный нагрев.

**HEATER_0_MAXTEMP** - максимальное значение температуры для нагревателя. Параметр безопасноти, при превышении будет сообщение об ошибке.

**BED_MAXTEMP** - максимальная температура стола.

Настройки защиты от выхода температуры из под контроля:

```
>THERMAL_PROTECTION_PERIOD 		30     #��λ:��
>THERMAL_PROTECTION_HYSTERESIS 		10     	#��λ:��
>WATCH_TEMP_PERIOD 			30	#��λ:��
>WATCH_TEMP_INCREASE 			5	#��λ:��
>THERMAL_PROTECTION_BED_PERIOD 		30    	#��λ:��
>THERMAL_PROTECTION_BED_HYSTERESIS 	4 	#��λ:��
>WATCH_BED_TEMP_PERIOD 			60     #��λ:��
>WATCH_BED_TEMP_INCREASE 		2       #��λ:��
```

Настройки PID:

```
>PIDTEMPE			1	# ģʽѡ��1:PID; 0:bang-bang
>DEFAULT_Kp			11.14	# Pֵ����
>DEFAULT_Ki			0.72	# Iֵ����
>DEFAULT_Kd			43.09	# Dֵ����

>PIDTEMPBED			1	# ģʽѡ��1:PID; 0:bang-bang
>DEFAULT_bedKp			52.63	# Pֵ����
>DEFAULT_bedKi			9.75	# Iֵ����
>DEFAULT_bedKd			71.01	# Dֵ����
```

Параметры PIDTEMPE и PIDTEMPBED задают нужно ли использовать ПИД для управления нагревом экструдера и стола соотвественно. Есть два способа управления нагевом: bang-bang и PID. Bang-bang это режим при котором нагреватель управляется методом включено-выключено, без попытки точного поддержания температуры. Про работу ПИД можно посмотреть в [вики](https://ru.wikipedia.org/wiki/%D0%9F%D0%98%D0%94-%D1%80%D0%B5%D0%B3%D1%83%D0%BB%D1%8F%D1%82%D0%BE%D1%80). Применительно к 3д печати можно посмотреть в видео [Дмитрия Соркина](https://www.youtube.com/watch?v=aizbpcZ7LU0&feature=emb_title).

## Параметры WIFI

Для того, чтобы не вводить параметры WIFI с экрана принтера, их можно установить в конфигурационном файле:

```
>CFG_WIFI_MODE			0			#wifi ģʽ(0:sta;1:ap)
>CFG_WIFI_AP_NAME		         		#wifi ����
>CFG_WIFI_KEY_CODE		         		#wifi ����
```

**CFG_WIFI_MODE** - режим работы. Значение 0 - в режиме клиента, будет подключаться к вашей точке доступа. 1 - сам станет точкой доступа.

**CFG_WIFI_AP_NAME** - Название сети

**CFG_WIFI_KEY_CODE** - Пароль сети.

## Типичные проблемы

* После замены драйверов или замены прошивки голова перемещается в противоположную сторону или на неверное расстояние

Не правильно установлено направление для оси или количество шагов. Как исправить: установите руками голову в центре и опустите немного стол, чтобы при попытке движения ничего никуда не врезалось. Из меню принтера попробуйте двигать каждой осью по 10мм. Если не совпадает направление движения - измените параметр INVERT-?-DIR для соответствующей оси. Перемещение можно измерить обычной линейкой, точность тут не нужна. Если неправильно выставлено количество шагов на мм, то голова будет перемещаться либо в 2,4,8 раз больше или меньше. Если на команду перемещения голова переместилась в 2 раза дальше чем нужно, значение DEFAULT-?-STEPS-PER-UNIT для соответствующей оси нужно сделать в 2 раза меньше. Если голова переместилась в 2 раза меньше, чем нужно, параметр DEFAULT-?-STEPS-PER-UNIT нужно увеличить в 2 раза.

* После прошивки на экране надпись "Booting", "TFT Updating" или просто черный экран. 

Вероятнее всего вы прошили прошивку от другой платы. Возьмите прошивку [для вашей платы](../mks_board/readme.md).

* Прошивка не происходит.

Возьмите прошивку [для вашей платы](../mks_board/readme.md). Возьмите не очень большую карту памяти, до 16Гб, и отформатируйте при помощи [SD Memory Card Formatter](https://www.sdcard.org/downloads/formatter/). Обратите внимание, происходит ли прошивка: есть ли отображение процесса на экране и изменилось ли расширение файла robin_nano35.bin
