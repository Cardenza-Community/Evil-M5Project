# SPDX-License-Identifier: MIT
"""Exercise actual build parser, callback adapter and menu radio guard on the host."""
import ast
import os
from pathlib import Path
import re
import subprocess
import tempfile
from platformio.builder.tools.pioino import InoToCPPConverter

root = Path(__file__).resolve().parent
module = ast.parse((root / "prepare_sketch.py").read_text())
parser = next(n for n in module.body if isinstance(n, ast.FunctionDef) and n.name == "parse_cpp_prototypes")
namespace = {"re": re, "original_parser": InoToCPPConverter._parse_prototypes}
exec(compile(ast.Module(body=[parser], type_ignores=[]), str(root / "prepare_sketch.py"), "exec"), namespace)
sample = 'const char* html = R"HTML(function evil() { async run() { })HTML";\nvoid real_setup() { }\n'
prototypes = namespace["parse_cpp_prototypes"](InoToCPPConverter(None), sample)
assert [m.group(3).strip() for m in prototypes] == ["real_setup"]
# Also scan the real 1.9 MB upstream/app sketch: raw JS must not become declarations.
contents = (root.parent / "Evil-Cardputer-v1-5-5.ino").read_text(encoding="utf-8")
prototypes = namespace["parse_cpp_prototypes"](InoToCPPConverter(None), contents)
assert not any(re.match(r"(?:function|async)\b", m.group(1).strip()) for m in prototypes)

with tempfile.TemporaryDirectory() as folder:
    folder = Path(folder)
    (folder / "esp_now.h").write_text("""#include <cstdint>
using esp_err_t=int;
struct esp_now_recv_info_t { const uint8_t* src_addr; };
using esp_now_recv_cb_t = void (*)(const esp_now_recv_info_t*,const uint8_t*,int);
static esp_now_recv_cb_t receiver;
static esp_err_t esp_now_register_recv_cb(esp_now_recv_cb_t cb) {receiver=cb;return 0;}
""")
    (folder / "esp_wifi.h").write_text("""#pragma once
using esp_err_t=int;
using wifi_interface_t=int;
const int ESP_OK=0,ESP_ERR_NOT_SUPPORTED=-1;
""")
    (folder / "test.cpp").write_text("""#include <cassert>
#include "sdk_compat.h"
#define EVIL_MENU_ONLY
#include "radio_guard.cpp"
static int calls;
static const uint8_t* observed;
static void legacy(const uint8_t* mac,const uint8_t* data,int len) {assert(mac[0]==12 && data[0]==24 && len==3);observed=mac;++calls;}
static void modern(const esp_now_recv_info_t* info,const uint8_t*,int) {observed=info->src_addr;++calls;}
int main() {
  uint8_t mac[]={12}, data[]={24}; esp_now_recv_info_t info{mac};
  assert(evilRegisterRecvCallback(legacy)==0); receiver(&info,data,3);
  assert(calls==1 && observed==mac);
  assert(evilRegisterRecvCallback(modern)==0); receiver(&info,data,3);
  assert(calls==2 && observed==mac);
  assert(__wrap_esp_wifi_start()==ESP_ERR_NOT_SUPPORTED);
  assert(__wrap_esp_wifi_set_promiscuous(true)==ESP_ERR_NOT_SUPPORTED);
  assert(__wrap_esp_wifi_set_promiscuous(false)==ESP_OK);
  assert(__wrap_esp_wifi_80211_tx(0,data,1,false)==ESP_ERR_NOT_SUPPORTED);
}
""")
    output = folder / ("test.exe" if os.name == "nt" else "test")
    subprocess.run([os.environ.get("CXX", "g++"), "-std=c++11", "-I"+str(folder), "-I"+str(root), str(folder/"test.cpp"), "-o", str(output)],check=True)
    subprocess.run([str(output)],check=True)
print("PASS: actual raw-string parser, ESP-NOW callback compatibility and menu radio guard")
