# Управление подстветкой корпуса

Для подсветки рабочего пространства используется светодиодная лента на 24V. Для возможности включать и отключать подсветку из меню принтера или при помощи g-code, используется небольшая плата, установленная на месте драйвера второго экструдера.

Схема платы, список компонентов, гербера - [на easyeda](https://easyeda.com/sst78rust/fb4s-led-control)

Для управления используется нога En второго экструдера (пин PA3).

## Настройка Marlin

В файле Marlin/src/pins/stm32f1/pins_MKS_ROBIN_NANO.h:

```
#define CASE_LED_INSTEAD_E1
```

```
#ifdef CASE_LED_INSTEAD_E1
  #define LED_CASE_PIN                      PA3
#else
 #define E1_ENABLE_PIN                      PA3
 #define E1_STEP_PIN                        PA6
 #define E1_DIR_PIN                         PA1
#endif
```

В файле Marlin/Configuration_adv.h:

```
#define CASE_LIGHT_ENABLE
#if ENABLED(CASE_LIGHT_ENABLE)
  #define CASE_LIGHT_PIN LED_CASE_PIN         // Override the default pin if needed
  #define INVERT_CASE_LIGHT false             // Set true if Case Light is ON when pin is LOW
  #define CASE_LIGHT_DEFAULT_ON true          // Set default power-up state on
  #define CASE_LIGHT_DEFAULT_BRIGHTNESS 255   // Set default power-up brightness (0-255, requires PWM pin)
  #define CASE_LIGHT_MAX_PWM 255              // Limit pwm
  #define CASE_LIGHT_MENU                   // Add Case Light options to the LCD menu
  #define CASE_LIGHT_NO_BRIGHTNESS          // Disable brightness control. Enable for non-PWM lighting.
  //#define CASE_LIGHT_USE_NEOPIXEL           // Use Neopixel LED as case light, requires NEOPIXEL_LED.
  #if ENABLED(CASE_LIGHT_USE_NEOPIXEL)
    #define CASE_LIGHT_NEOPIXEL_COLOR { 255, 255, 255, 255 } // { Red, Green, Blue, White }
  #endif
#endif
```

Управлять включением и отключением освещения можно из меню принтера или командом [M355](https://marlinfw.org/docs/gcode/M355.html)
