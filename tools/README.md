# 🛠️ Standalone Android Localization, Optimization & Release Tools

<p>
  <a href="../README.vi.md"><b>← [VI] Trang Chủ</b></a> &nbsp;•&nbsp;
  <a href="../README.md"><b>← [EN] Main README</b></a> &nbsp;•&nbsp;
  <a href="../README.cn.md"><b>← [CN] 返回主页</b></a> &nbsp;•&nbsp;
  <a href="../CHANGELOG.md"><b>📋 CHANGELOG</b></a> &nbsp;•&nbsp;
  <a href="../CREDITS.md"><b>👥 Credits</b></a>
</p>

Reference build, optimization, localization &amp; release scripts used to assemble the versioned standalone multi-language Android APKs (**`[EN]` English**, **`[VI]` Bản Việt Hóa**, **`[CN]` Chinese Raw**) for **Plants vs. Zombies: Hybrid Classic v3.20.1**.

> [!NOTE]
> Players do **not** need any tools from this folder — download ready-to-install versioned APKs directly from **[Releases](https://github.com/Heagon/pvz-hybrid-classic-android/releases)**.

## Requirements to Reproduce From Scratch
- **Python 3.10+** with `Pillow` and `fonttools`:
  ```bash
  pip install pillow fonttools
  ```
- **MinGW-w64 (`i686-w64-mingw32-gcc` / `objcopy`)** for compiling C/ASM code caves (`cave_d3d_opt.c`, `cave_fixes.S`, `cave_perf.S`)
- **JDK 17/21+** (`java`, `javac`, `jar`) &amp; **Android SDK Build-Tools** (`android.jar`, `d8`)
- **Zstandard CLI** (`zstd`) + [`apktool.jar`](https://apktool.org/) + [`uber-apk-signer.jar`](https://github.com/patrickfav/uber-apk-signer/releases)
- Your own legally obtained original *PvZ Hybrid Classic v3.20.1* files (`PlantsVsZombies.exe`, `bass.dll`, `gdi42.dll`, `main.pak`, `fonts/`) + upstream Winlator base APK + an Android signing keystore (provided via environment variables).

## Scripts Included
| Script | Purpose |
| :--- | :--- |
| `patch_engine_utf8.py` | Binary-patches `gdi42.dll` (`CP936` → `CP_UTF8` + O(1) `DrawString`/`StringWidth` Glyph Atlas hooks) and merges Latin Extended + full Vietnamese diacritic glyphs from `LiberationSans` into all 6 runtime `.ttf` fonts. |
| `patch_exe_strings.py` | Loads [`translations/strings_exe.json`](../translations/strings_exe.json) and relocates all **1,038 unique verified Chinese strings** (1,421 code &amp; pointer-table refs) inside `PlantsVsZombies.exe` for clean English &amp; Vietnamese UI. |
| `patch_exe_perf.py` | Injects verified x86/C performance caves ([`cave_perf.S`](cave_perf.S), [`cave_d3d_opt.c`](cave_d3d_opt.c), [`cave_d3d_tramp.S`](cave_d3d_tramp.S), [`cave_d3d.ld`](cave_d3d.ld)) (`OPT 1–13`: live `30/60/90/120 FPS` pacer + `100.00 Hz` speed gate, 1-Quad Baked Seed-Card Atlas, Universal 12-Page `DrawTrianglesTex` Sprite Atlas + `3072`-vertex batcher, `HasSeedType` O(1) memo, occluded culling, and synced `ViewLawn` timers). |
| `patch_exe_fixes.py` | Injects stability &amp; gameplay fixes ([`cave_fixes.S`](cave_fixes.S)): direct 1-tap `Menu`/`Shovel` hit-testing, `I, Zombie` free-spawn bound fix, `LAA` (`>2 GB`) unsigned pointer fixes, 30+ Hero Mode &amp; Reanimation crash guards, Almanac O(1) LUT, and cleaned `NewOptionsDialog`. |
| `patch_textures.py` | Renders **171 localized UI textures** per language into `work/overrides_{en,vi}/`. |
| `compile_properties.py` | Compiles and validates 3,309 translated strings across all 9 `properties/*.txt` files (including 437 refitted Almanac descriptions). |
| `repack_pak.py` | Rebuilds PopCap `main.pak` (XOR `0xF7`) substituting 180 localized properties and UI textures case-insensitively. |
| `patch_tzst_runtime.py` | Rewrites hardcoded container paths inside runtime `.tzst` archives to `com.pvzh.cls`. |
| `pack_apk.py` | Stages `game_stage_{cn,en,vi}`, builds `pvz_game_*.tzst`, embeds 4-byte-aligned `ZIP_STORED` payloads inside `base_shell.apk`, stamps `pvz_edition.txt` with `B.x.y` (e.g. `v3.20.1-VI-B.0.2`), and signs versioned APKs (`PvZ-Hybrid-Classic-3.20.1-<Lang>-B.x.y.apk`). |
| `publish_release.py` | Creates a new **immutable** GitHub Release (`v<Ver>-B.x.y`) with SHA-256 verification and refuses to overwrite any existing release tag. |

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

# 3. Render 171 localized UI textures + compile 3,309 property strings
python tools/patch_textures.py
python tools/compile_properties.py

# 4. Patch runtime .tzst container paths for com.pvzh.cls
python tools/patch_tzst_runtime.py

# 5. Pack & sign all 3 versioned APKs (e.g. Build B.0.2)
python tools/pack_apk.py all --build B.0.2

# 6. Publish as a new immutable GitHub Release (never overwrites old builds)
python tools/publish_release.py --build B.0.2 --notes RELEASE_NOTES-3.20.1-B.0.2.md
```
