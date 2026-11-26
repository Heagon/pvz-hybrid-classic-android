# 🛠️ Standalone Android Localization & Packaging Tools

<p>
  <a href="../README.vi.md"><b>← [VI] Trang Chủ</b></a> &nbsp;•&nbsp;
  <a href="../README.md"><b>← [EN] Main README</b></a> &nbsp;•&nbsp;
  <a href="../README.cn.md"><b>← [CN] 返回主页</b></a> &nbsp;•&nbsp;
  <a href="../CREDITS.md"><b>👥 Credits</b></a>
</p>

Reference build & localization scripts used to assemble the standalone multi-language Android APKs (**`[EN]` English**, **`[VI]` Bản Việt Hóa**, **`[CN]` Chinese Raw**) for **Plants vs. Zombies: Hybrid Classic v3.20.1**.

> [!NOTE]
> Players do **not** need any tools from this folder — download ready-to-install APKs directly from **[Releases](https://github.com/Heagon/pvz-hybrid-classic-android/releases)**.

## Requirements to Reproduce From Scratch
- **Python 3.10+** with `Pillow` and `fonttools`:
  ```bash
  pip install pillow fonttools
  ```
- **JDK 17/21+** (`java`, `javac`, `jar`) & **Android SDK Build-Tools** (`android.jar`, `d8`)
- **Zstandard CLI** (`zstd`) + [`apktool.jar`](https://apktool.org/) + [`uber-apk-signer.jar`](https://github.com/patrickfav/uber-apk-signer/releases)
- Your own legally obtained original *PvZ Hybrid Classic v3.20.1* files (`PlantsVsZombies.exe`, `bass.dll`, `gdi42.dll`, `main.pak`, `fonts/`) + upstream Winlator base APK + an Android signing keystore (provided via environment variables).

## Scripts Included
| Script | Purpose |
| :--- | :--- |
| `patch_engine_utf8.py` | Binary-patches `gdi42.dll` (`MultiByteToWideChar` codepage `936` GBK → `65001` `CP_UTF8` at 4 call sites) and merges Latin Extended + full Vietnamese diacritic glyphs from `LiberationSans` into all 6 runtime `.ttf` fonts. |
| `patch_exe_strings.py` | Loads [`translations/strings_exe.json`](../translations/strings_exe.json) and relocates all **983 unique verified Chinese strings** (1,342 code & pointer-table items across `.rdata`/`.newHE`: dialogs, rules, HUD counters, stage titles, modifiers, and Hero Mode labels, plus the Main Menu ASCII version prefix) inside `PlantsVsZombies.exe` (`GB18030` → UTF-8 in `.newHE` zero slack) for clean English & Vietnamese UI. |
| `patch_textures.py` | Renders **121 localized UI textures** (main menu signs, gravestones, chapter headers, hero/shop/almanac buttons) into `work/overrides_{en,vi}/` using sharp full-diacritic bold typography. |
| `compile_properties.py` | Compiles and validates 3,309 translated strings across all 9 `properties/*.txt` files (UTF-8 without BOM, zero CJK leaks, 1:1 `{TAG}` preservation). |
| `repack_pak.py` | Rebuilds PopCap `main.pak` (XOR `0xF7`) substituting 130 localized properties and UI textures case-insensitively. |
| `patch_tzst_runtime.py` | Rewrites hardcoded `/data/data/com.winlator/...` paths, shell wrappers, and ELF symlink targets inside runtime `.tzst` archives (`rootfs.tzst`, `box64`, `container_pattern`) to `com.pvzh.cls` so Wine/Box64 boots standalone without requiring Winlator installed. |
| `pack_apk.py` | Stages `game_stage_{cn,en,vi}`, compresses into `pvz_game_*.tzst`, embeds 4-byte-aligned `ZIP_STORED` payloads inside `base_shell.apk` (configured with `WineD3D` OpenGL FBO `renderer=gl` and `GLXExtension` top-down `flipY=false` patch so Mali/Adreno GPUs render 100% upright), stamps `pvz_edition.txt`, and signs with your keystore (`KEYSTORE_PATH`, `KS_PASS`, `KS_ALIAS`). |

## Usage Overview
```bash
# Configure signing & toolchain paths via environment variables
export KEYSTORE_PATH=/path/to/your-release.keystore
export KS_PASS="your-keystore-password"
export KS_ALIAS="release"

# 1. Patch gdi42.dll to UTF-8 & build Unicode fonts
python tools/patch_engine_utf8.py

# 2. Relocate hardcoded .exe UI strings for EN / VI
python tools/patch_exe_strings.py

# 3. Render 121 localized UI textures + compile 3,309 property strings
python tools/patch_textures.py
python tools/compile_properties.py

# 4. Patch runtime .tzst container paths for com.pvzh.cls
python tools/patch_tzst_runtime.py

# 5. Pack & sign all 3 APKs with identical certificate (save-preserving install -r)
python tools/pack_apk.py all
```
