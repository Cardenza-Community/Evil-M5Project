# Cardenza support

This target retains the original Cardputer display and matrix-keyboard layout.
It verifies the ES8156 codec on SDA2/SCL1 and uses stereo Philips I2S,
16-bit samples and 32 BCLK per frame on BCLK41/LRCK43/DOUT42.
GPIO21 is held high to disable the keyboard LED. Cardenza has no battery,
charging detector, IMU or PSRAM; unavailable hardware is not simulated.
The original application license and third-party notices remain in force.

Build the normal application with `pio run -e cardenza`. Install only
`.pio/build/cardenza/firmware.bin` through Software Launcher. Preserve the
existing bootloader, partition table, otadata and shared NVS.
The target refuses whole shared-NVS erasure during Arduino recovery while
allowing normal NVS page garbage collection and unrelated partition writes.
Run `python3 support/test_nvs_guard.py` to verify this forwarding contract.
Successful compilation does not prove physical display, keys, audio or RF.
No wireless/security functionality is executed by these build checks.

This upstream sketch needs the pinned Arduino 3.2.0 / ESP-IDF 5.4 Bluedroid SDK,
pioarduino 55.03.39, M5Unified 0.2.22, M5Cardputer 1.1.1 and ESP8266Audio 2.3.0.
The build stages only the Cardputer sketch and fixes actual SDK/include/prototype
compatibility. The unused PDM audio backend is omitted; the M5 speaker backend remains.
The full app requires a 3.5 MiB app slot. Linker wrappers suppress absent M5 power
and RGB initialization. Automatic GPS initialization on codec GPIO1 is disabled.
`cardenza-menu-test` is a separate radio-disabled startup-test target.
Run `python3 support/test_compatibility.py` with a host C++ compiler to check
raw-string parsing, callback metadata forwarding and guarded menu behavior.
The upstream raw-frame validation bypass is not added or enabled.
The original MIT notice is at the top of `Evil-Cardputer-v1-5-5.ino`;
the HAL license is `support/CARDENZA_HAL_LICENSE`.
