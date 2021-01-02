# Описание настройки firmware retract

Описание не очень актуально для Cura, поскольку там это использовать не удобно. Подробности в конце.

## Что такое retract

При печати модели возникают ситуации, когда нужно передвинуть сопло в новую точку, не выдавливая пластик. Если просто прекратить подачу, то из-за остаточного давления в сопле, а так же из-за текучести расплавленного пластка, он будет самопроизвольно вытекать из сопла, оставляя дефекты на модели.

Для борьбы с этим явлением применяется откат пластика (retract) перед холостым движением и возврат обратно, после перемещения. В gcode это выглядит примерно вот так:

```
G1 X107.717 Y87.531 E12.20186  ;движения на предыдущем слое
G1 X108.120 Y86.268 E12.24598  ;движения на предыдущем слое  
G1 X108.745 Y85.184 E12.28761  ;движения на предыдущем слое
G92 E0                         ;обнуление позиции экструдера
G1 E-1.00000 F1800.00000       ;движение на "-1мм", т.е. от сопла, со скоростью 30 мм/с (30*60 мм/мин)
G1 X116.555 Y89.985 F6000.000  ;движение к новой точке
G1 E0.00000 F1800.00000        ;возврат пластика к соплу
;TYPE:Support material interface
G1 F1200.000                   ;движения на новом слое
G1 X116.555 Y88.772 E0.03097   ;движения на новом слое
G1 X116.248 Y88.772 E0.03881   ;движения на новом слое
```
Это код созданный [SuperSlicer](https://github.com/supermerill/SuperSlicer). Cura создает код немного иначе - нет сброса позиции экструдера командой G92, а значения параметра E увеличиваются с каждым слоем. Откат при этом выглядит аналогично.

## firmware retract

В Marlin есть поддержка команд [G10](https://marlinfw.org/docs/gcode/G010.html)/[G11](https://marlinfw.org/docs/gcode/G011.html), которые использутся вместо команд G1 при откате.

Вот тот же кусок кода, с включенным firmware retract:

```
G1 X107.717 Y87.531 E12.20186
G1 X108.120 Y86.268 E12.24598
G1 X108.745 Y85.184 E12.28761
G92 E0
G10 ; retract
G1 X116.555 Y89.985 F6000.000
G11 ; unretract
;TYPE:Support material interface
G1 F1200.000
G1 X116.555 Y88.772 E0.03097
G1 X116.248 Y88.772 E0.03881
```

## Настройка Marlin

Настройка параметров firmware retract производится в файле Marlin/Configuration_adv.h:

```
#define FWRETRACT
#if ENABLED(FWRETRACT)
  //#define FWRETRACT_AUTORETRACT           // Override slicer retractions
  #if ENABLED(FWRETRACT_AUTORETRACT)
    #define MIN_AUTORETRACT 0.1           // (mm) Don't convert E moves under this length
    #define MAX_AUTORETRACT 5.0          // (mm) Don't convert E moves over this length
  #endif
  #define RETRACT_LENGTH 2                // (mm) Default retract length (positive value)
  #define RETRACT_LENGTH_SWAP 13          // (mm) Default swap retract length (positive value)
  #define RETRACT_FEEDRATE 35             // (mm/s) Default feedrate for retracting
  #define RETRACT_ZRAISE 0                // (mm) Default retract Z-raise
  #define RETRACT_RECOVER_LENGTH 0        // (mm) Default additional recover length (added to retract length on recover)
  #define RETRACT_RECOVER_LENGTH_SWAP 0   // (mm) Default additional swap recover length (added to retract length on recover from toolchange)
  #define RETRACT_RECOVER_FEEDRATE 35      // (mm/s) Default feedrate for recovering from retraction
  #define RETRACT_RECOVER_FEEDRATE_SWAP 35 // (mm/s) Default feedrate for recovering from swap retraction
  #if ENABLED(MIXING_EXTRUDER)
    //#define RETRACT_SYNC_MIXING         // Retract and restore all mixing steppers simultaneously
  #endif
#endif
```

Опция FWRETRACT_AUTORETRACT позволяет автоматически определять в файле откаты сделанные командой G1 и заменять их на команды G10/G11. Допустимые границы движений, которые будут распознаваться как откат, заданы параметрами MIN_AUTORETRACT и MAX_AUTORETRACT. По-умолчанию я эту функцию выключаю. Для включения/выключения можно использовать команду [M209](https://marlinfw.org/docs/gcode/M209.html).

Параметры отката заданные в Marlin/Configuration_adv.h используются в том случае, если не заданы никакие другие командами [M207](https://marlinfw.org/docs/gcode/M207.html)/[M208](https://marlinfw.org/docs/gcode/M208.html)

## Настройка SuperSlicer/PrusiaSlicer

Включение функции firmware rectract ("использовать втягивание прошивки") находится в настройках принтера.
Для управления параметрами отката в стартовый код нужно добавить:

```
M207 S[retract_length] F{retract_speed[0]*60}
```

Значение скорости для команды [M207](https://marlinfw.org/docs/gcode/M207.html)/[M208](https://marlinfw.org/docs/gcode/M208.html) используется в мм/мин, а в настройках слайсер стоит мм/сек, поэтому значение умножается на 60.

Следует обратить внимание, что длина возврата, устанавливаемая командой [M208](https://marlinfw.org/docs/gcode/M208.html), добавляется к длине отката. Если командой M207 установлена длина 2мм, а командой M208 1мм, то при возврате пластика будет сделано движение на 3мм.

## Настройка отката во время печати

Изменять параметры отката можно прямо во время печати из меню принтера Menu->Configuraton->Retract

## Cura

В Cura так же есть возможность влкючить firmware retract и использовать команды G10/G11. Но Cura не поддерживает математических функций в стартовом коде. Значение скорости в настройках стоит в мм/сек, и в таком виде оно подставляется в gcode. А прошивка использует значение в мм/мин.
