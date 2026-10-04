# Runtime Cardputer / ADV / Cardenza support

Build `pio run -e cardputer`; `cardenza` is a compatibility alias. The full app uses 3.5 MiB build capacity because the original 3 MiB metadata is insufficient.

The normal default build uses [203Null/M5Unified](https://github.com/203Null/M5Unified/tree/74fe31c6d9a2bd7c04f81eb4f8f0af99262e3bc2) at immutable commit `74fe31c6d9a2bd7c04f81eb4f8f0af99262e3bc2`, M5GFX 0.2.31 and M5Cardputer 1.1.1. One app image selects original Cardputer, Cardputer ADV or Cardenza at runtime. ES8156 identification, codec initialization, GPIO21 LED hold, and Cardenza-only suppression of battery ADC/charging, RGB and IMU are owned by M5Unified. No `CARDENZA_TARGET`, forced board identity, or Power/LED linker wrappers are used by these builds. Original/ADV initialization remains the library's normal path.

Install only the app BIN through Launcher; preserve its bootloader and partition table. The new unified images have been compiled and audited on the host; they have not been flashed or physically tested. Earlier device logs under `../artifacts/` apply only to the older forced Cardenza images.

The app uses M5.begin and M5Cardputer.begin normally, including keyboard selection. GPIO21 is not assigned by the external NeoPixel object until after detection; begin/show skip output on Cardenza. Battery and IMU temperature are N/A there, and all GPS startup/restoration paths skip UART on codec/keyboard connector pins. Original/ADV GPS, battery and LED behavior remains. Explicit SD SPI pins SCK40/MISO39/MOSI14/CS12 are used for this entire family because StampS3's generic aliases are -1; SD SPI2 stays separate from display SPI3.

The upstream sketch still needs SDK/API compatibility fixes: Arduino3.2.0/IDF5.4 Bluedroid, ESP-NOW callback forwarding and BLE String conversion. Raw HTML is masked only during Arduino prototype generation. The unused ESP8266Audio PDM-output translation unit is excluded because that SDK lacks its required fields. The existing Espressif raw-frame validation is retained on all devices; no private SDK library is patched and features requiring a bypass remain unvalidated.

`cardputer-menu-test` / `cardenza-menu-test` retain the saved-autostart/reconnect/menu execution guards and deny WiFi start/TX/promiscuous capture. Normal full application behavior is compiled separately; no radio/security feature is executed during host validation. `python support/test_compatibility.py` exercises the actual parser, callback adapter and radio guards.

The very large sketch uses -mtext-section-literals to keep Xtensa literals within instruction reach; no application feature is removed for the link fix.

Private build core: C:/pio-evil. Old support/cardenza_board.h, HAL and Power wrappers remain historical files; the sketch staging script no longer copies/includes them and removes any stale copies from its build directory. Earlier guarded image SD/codec startup logs do not establish unified runtime behavior.

## Launcher publication protection

The published `cardenza` compatibility target adds `LAUNCHER_NVS_GUARD` and wraps only esp_partition_erase_range to refuse a whole shared NVS erase. This install-context guard is independent of runtime hardware detection and is retained in the guarded test aliases. Normal NVS page garbage collection and app/filesystem erases still pass through. Run `python support/test_nvs_guard.py`. Build/publication CI retains the cardenza alias and its existing app/license asset paths. See docs/LAUNCHER_PUBLISHING.md.
