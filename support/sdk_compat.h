// SPDX-License-Identifier: MIT
#pragma once
#include <esp_now.h>
// SDK compatibility: current ESP-NOW passes metadata rather than a bare MAC.
using EvilLegacyRecv = void (*)(const uint8_t*, const uint8_t*, int);
static EvilLegacyRecv evilLegacyRecv = nullptr;
static void evilRecvAdapter(const esp_now_recv_info_t* info, const uint8_t* data, int len) {
  if (evilLegacyRecv) evilLegacyRecv(info->src_addr, data, len);
}
static esp_err_t evilRegisterRecvCallback(EvilLegacyRecv callback) {
  evilLegacyRecv = callback;
  return esp_now_register_recv_cb(evilRecvAdapter);
}
static esp_err_t evilRegisterRecvCallback(esp_now_recv_cb_t callback) {
  evilLegacyRecv = nullptr;
  return esp_now_register_recv_cb(callback);
}
