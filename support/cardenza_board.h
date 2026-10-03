// SPDX-License-Identifier: MIT
#pragma once
#ifdef CARDENZA_TARGET
#include "cardenza_hal.h"
#include <FS.h>
#include <SD.h>
#include <M5Cardputer.h>
static inline void evilCardenzaBegin() {
  const bool ready = cardenza_hal_init(32,16);
  auto cfg = M5.config();
  cfg.fallback_board = m5::board_t::board_M5Cardputer;
  cfg.internal_imu = cfg.internal_rtc = false;
  cfg.internal_spk = cfg.internal_mic = false;
  cfg.output_power = false;
  M5.begin(cfg);
  pinMode(46, INPUT);
  if (!ready) {
    M5.Display.fillScreen(TFT_BLACK);
    M5.Display.drawString("Audio initialization failed",6,55);
    Serial.println("Cardenza ES8156 setup failed");
    for (;;) delay(1000);
  }
  auto mic = M5.Mic.config();
  mic.pin_ws = 43; mic.pin_data_in = 46;
  mic.pin_bck = mic.pin_mck = -1;
  mic.use_adc = false; mic.i2s_port = I2S_NUM_0;
  M5.Mic.config(mic);
  auto spk = M5.Speaker.config();
  spk.pin_bck = 41; spk.pin_ws = 43; spk.pin_data_out = 42;
  spk.pin_mck = -1; spk.stereo = true;
  spk.use_dac = spk.buzzer = false; spk.i2s_port = I2S_NUM_0;
  M5.Speaker.config(spk);
  Serial.println("Cardenza ES8156 ready; PDM46/43; battery ADC/RGB disabled");
}
#endif
