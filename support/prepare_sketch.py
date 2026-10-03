"""Stage the Cardputer sketch without other devices' .ino files."""
from pathlib import Path
import shutil
import re
from platformio.builder.tools.pioino import InoToCPPConverter

Import("env")
root = Path(env.subst("$PROJECT_DIR"))
dest = root / ".cardenza-build" / env["PIOENV"]
env.Replace(PROJECT_SRC_DIR=str(dest))
dest.mkdir(parents=True, exist_ok=True)
shutil.copy2(root / "Evil-Cardputer-v1-5-5.ino", dest / "EvilCardputer.ino")

# PlatformIO's Arduino converter mistakes JavaScript inside raw HTML strings
# for C++ functions. Skip those invented declarations, leaving HTML intact.
original_parser = InoToCPPConverter._parse_prototypes
def parse_cpp_prototypes(self, contents):
    # Mask C++ raw strings while finding declarations, preserving every offset.
    masked = re.sub(r'R"([^\s\\()]*)\(.*?\)\1"',
                    lambda m: "".join("\n" if c == "\n" else " " for c in m.group()),
                    contents, flags=re.S)
    return original_parser(self, masked)
InoToCPPConverter._parse_prototypes = parse_cpp_prototypes

# Arduino IDE understands these signatures; PlatformIO's basic regex does not.
declarations = '''
#include <FS.h>
#include <SD.h>
#include <M5Cardputer.h>
#include <map>
#include <vector>
#include <string>
std::string mac_to_string(const uint8_t* mac);
bool isRegularAP(const std::string& mac);
void displayHostOptions(const std::vector<IPAddress>& hostslist);
void afterScanOptions(IPAddress ip, const std::vector<IPAddress>& hostslist);
extern "C" void send_pwnagotchi_beacon_main();
int menuSelectList(const std::vector<String>& items, const char* title);
void displayHostsAndScanPorts(const std::vector<IPAddress>& hostslist, int scanIndex, bool isWebCommand);
void displayResults(int displayStart, int maxLines, const std::vector<String>& scanResults);
void fetchWebsites(const std::vector<IPAddress>& hostslist, const std::map<IPAddress, std::vector<int>>& openPorts, int scanIndex);
'''
sketch = dest / "EvilCardputer.ino"
contents = declarations + sketch.read_text(encoding="utf-8")
for filename in ["cardenza_hal.h", "cardenza_board.h", "cardenza_m5_power.cpp", "cardenza_nvs_guard.cpp", "sdk_compat.h"]:
    shutil.copy2(root / "support" / filename, dest / filename)
contents = '#ifdef CARDENZA_TARGET\n#include "cardenza_board.h"\n#endif\n' + contents
# Test-only variant: keep the untouched upstream sketch on disk, but prevent
# saved configurations and menu selection from activating network functions.
contents = contents.replace("  firstScanWifiNetworks();", "#ifndef EVIL_MENU_ONLY\n  firstScanWifiNetworks();\n#endif", 1)
contents = contents.replace('  if (ssid != "") {', '#ifdef EVIL_MENU_ONLY\n  if (false) {\n#else\n  if (ssid != "") {\n#endif', 1)
contents = contents.replace("void loop() {", "void loop() {\n#ifdef EVIL_MENU_ONLY\n  bootLaunchDone = true;\n  startAtBootFlag = false;\n  inMenu = true;\n  cardUpdate();\n  handleMenuInput();\n  static uint32_t lastMenuBar = 0;\n  if (millis() - lastMenuBar > 1000) { drawTaskBar(); lastMenuBar = millis(); }\n  delay(10);\n  return;\n#endif", 1)
contents = contents.replace("void executeMenuItem(int index) {", 'void executeMenuItem(int index) {\n#ifdef EVIL_MENU_ONLY\n  Serial.println("Menu-only hardware test: item execution disabled");\n  inMenu = true;\n  return;\n#endif', 1)
# Own conversion so SCons cannot load a second unpatched Arduino parser module.
converter = InoToCPPConverter(env)
converter._main_ino = str(sketch)
converted = converter.append_prototypes('#include <Arduino.h>\n' + contents)
(dest / "EvilCardputer.cpp").write_text(converted, encoding="utf-8")
sketch.unlink()
shutil.copy2(root / "support" / "radio_guard.cpp", dest / "radio_guard.cpp")
(dest / "cardenza_pixels.cpp").unlink(missing_ok=True)

# The upstream instructions require their bundled keyboard-layout files.
# Apply only to this group's private framework, never global Arduino installs.
framework = Path(env.PioPlatform().get_package_dir("framework-arduinoespressif32"))
for filename in (root / "utilities" / "Bad_Usb_Lib").iterdir():
    if filename.suffix in (".h", ".cpp"):
        target = framework / "libraries" / "USB" / "src" / filename.name
        if not target.exists() or target.read_bytes() != filename.read_bytes():
            shutil.copy2(filename, target)

# This sketch never references AudioOutputPDM. ESP8266Audio 2.3's optional PDM
# implementation requires IDF5.5 fields absent from the selected Bluedroid SDK.
# Exclude that unused translation unit; I2S/M5 speaker output remains stock.
def skip_unused_pdm(env, node):
    return None
env.AddBuildMiddleware(skip_unused_pdm, "*/ESP8266Audio/src/AudioOutputPDM.cpp")

# Arduino3 moved SDK layouts into keyboardLayout/. Upstream replacement layouts
# are flat files; compile one set so every symbol has exactly one definition.
env.AddBuildMiddleware(skip_unused_pdm, "*/USB/src/keyboardLayout/KeyboardLayout_*.cpp")
