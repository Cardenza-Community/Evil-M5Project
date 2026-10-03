// SPDX-License-Identifier: MIT
// Menu-only hardware test guard; no radio start, capture or raw transmission.
#ifdef EVIL_MENU_ONLY
#include <esp_wifi.h>
extern "C" esp_err_t __wrap_esp_wifi_start(void) { return ESP_ERR_NOT_SUPPORTED; }
extern "C" esp_err_t __wrap_esp_wifi_set_promiscuous(bool enabled) { return enabled ? ESP_ERR_NOT_SUPPORTED : ESP_OK; }
extern "C" esp_err_t __wrap_esp_wifi_80211_tx(wifi_interface_t, const void*, int, bool) { return ESP_ERR_NOT_SUPPORTED; }
#endif
