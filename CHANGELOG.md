# 📋 Build History & Release Changelog · Lịch Sử Bản Build (`B.x.y`)

<p align="center">
  <a href="README.vi.md"><b>← [VI] Trang Chủ Tiếng Việt</b></a> &nbsp;•&nbsp;
  <a href="README.md"><b>← [EN] English Home</b></a> &nbsp;•&nbsp;
  <a href="README.cn.md"><b>← [CN] 返回中文主页</b></a> &nbsp;•&nbsp;
  <a href="CREDITS.md"><b>👥 Credits &amp; Sources</b></a>
</p>

## Build Naming & Immutable Release Policy
- **APK Naming Format:** `<GameName>-<GameVersion>-<Language>-<BuildID>.apk`
  - Example: `PvZ-Hybrid-Classic-3.20.1-Vietnamese-B.0.2.apk`
- **GitHub Release Tag Format:** `v<GameVersion>-<BuildID>` (e.g. `v3.20.1-B.0.1`, `v3.20.1-B.0.2`)
- **Immutability & Rollback:** Every build is published as its **own separate GitHub Release** and never overwrites previous builds. All builds share package ID `com.pvzh.cls` (`versionCode: 3201`) and the unified Release Keystore, with the build ID stamped inside `assets/pvz_edition.txt` — so you can **upgrade (`B.0.1 → B.0.2`) OR roll back (`B.0.2 → B.0.1`) in-place (Update, never uninstall)** with 100% save preservation if you ever need to trace or bisect an issue.

---

## Release Timeline (`v3.20.1`)

| Build | GitHub Release | Date | Status | Key Changes / Fixes | Release Notes |
| :---: | :---: | :---: | :---: | :--- | :---: |
| **`B.0.2`** | [`v3.20.1-B.0.2`](https://github.com/Heagon/pvz-hybrid-classic-android/releases/tag/v3.20.1-B.0.2) | `2026-11-28` | **Latest** | Live `30/60/90/120 FPS` selector + `100.00 Hz` speed parity; `OPT 8–13` + `gdi42` Glyph Atlas (`50.5–89.2 FPS` non-combat, `62.6–67.1 FPS` SeedChooser); fixed 1-tap `Menu` & `I, Zombie` free-spawn bug, `ViewLawn` (`Xem Bãi Cỏ`) soft-lock, `LAA` (`>2 GB`) crash, `Hero`/`Reanimation` crash guards, Almanac O(1) LUT, cleaned `NewOptionsDialog`, floating `PAD` toolbar & hotkeys, versioned `pvz_edition.txt`. | [`RELEASE_NOTES-3.20.1-B.0.2.md`](RELEASE_NOTES-3.20.1-B.0.2.md) |
| **`B.0.1`** | [`v3.20.1-B.0.1`](https://github.com/Heagon/pvz-hybrid-classic-android/releases/tag/v3.20.1-B.0.1) | `2026-11-27` | Archived (`3f65f8e`) | Initial standalone Android multi-language suite (`[VI]` / `[EN]` / `[CN]`, `com.pvzh.cls`), `VirGL` + `WineD3D csmt=0` + big-core affinity (`~29–34 FPS`), `1080x600` widescreen, 1-tap touch, 3,309 property strings + 1,038 EXE strings + 171 textures/language, UTF-8 `gdi42.dll` + 6 Unicode fonts, clean exit without auto-restart. | [`RELEASE_NOTES-3.20.1-B.0.1.md`](RELEASE_NOTES-3.20.1-B.0.1.md) |

---

## Credits & Copyright
Full official credits & sources: **[`CREDITS.md`](CREDITS.md)**
- Original mod *PvZ Hybrid Classic* (*植物大战僵尸杂交版经典版*): **潜艇伟伟迷 (Qianting Weiweimi)** ([Bilibili](https://space.bilibili.com/97213827) · [pvzhe.com](https://pvzhe.com)) & upstream contributors (**小小咩MS**, **AXH弦**, **一只吴铭仕哒**, **沉默寡言白河愁**).
- *Plants vs. Zombies* trademark & franchise: **Electronic Arts Inc. (EA) / PopCap Games**.
- Android localization, optimization & packaging: **Heagon** ([pvz-hybrid-classic-android](https://github.com/Heagon/pvz-hybrid-classic-android)) — 100% free, ad-free, non-commercial.
