# Release & Build History — PvZ Hybrid Classic Android

<p align="center">
  <a href="README.vi.md"><b>← [VI] Trang Chủ</b></a> &nbsp;•&nbsp;
  <a href="README.md"><b>← [EN] English Home</b></a> &nbsp;•&nbsp;
  <a href="README.cn.md"><b>← [CN] 返回中文主页</b></a> &nbsp;•&nbsp;
  <a href="CHANGELOG.md"><b>📋 CHANGELOG</b></a> &nbsp;•&nbsp;
  <a href="CREDITS.md"><b>👥 Credits &amp; Official Sources</b></a>
</p>

> **Build Versioning &amp; Traceability Policy:** Every published build receives an immutable build ID (`B.<major>.<minor>`) embedded in the **APK filename** (`PvZ-Hybrid-Classic-<GameVersion>-<Language>-B.<major>.<minor>.apk`), inside **`assets/pvz_edition.txt`**, and on its **dedicated GitHub Release tag** (`v<GameVersion>-B.<major>.<minor>`). Previous builds are **never overwritten**, so players can tell new vs. old builds at a glance, trace every fix, or roll back in-place with 100% save preservation.

---

## Build Index (`v3.20.1`)

| Release Tag | Date | Status | APK Files &amp; SHA-256 | Summary of Changes / Fixes |
| :--- | :---: | :---: | :--- | :--- |
| **[`v3.20.1-B.0.2`](https://github.com/Heagon/pvz-hybrid-classic-android/releases/tag/v3.20.1-B.0.2)** | `2026-11-28` | 🟢 **Latest** | • `PvZ-Hybrid-Classic-3.20.1-Vietnamese-B.0.2.apk` (`f3c00fc4...`)<br>• `PvZ-Hybrid-Classic-3.20.1-English-B.0.2.apk` (`c299cf88...`)<br>• `PvZ-Hybrid-Classic-3.20.1-Chinese-Raw-B.0.2.apk` (`799db80d...`) | Live **`30 / 60 / 90 / 120 FPS`** selector (`PAD → FPS`) + exact **`100.00 Hz`** game-speed parity; `OPT 8–13` + `gdi42` O(1) Glyph Atlas (**`50.5–89.2 FPS`** across all non-combat screens, **`62.6–67.1 FPS`** across all 5 Survival SeedChoosers); fixed 1-tap `Menu` &amp; `I, Zombie` free-spawn exploit, `ViewLawn` (`Xem Bãi Cỏ`) soft-lock, `LAA (>2 GB)` signed-pointer crash, 30+ `Hero`/`Reanimation` crash guards, Almanac O(1) LUT, cleaned `NewOptionsDialog`, floating `PAD` toolbar &amp; hotkeys, build-stamped `pvz_edition.txt`. ([Notes](RELEASE_NOTES-3.20.1-B.0.2.md)) |
| **[`v3.20.1-B.0.1`](https://github.com/Heagon/pvz-hybrid-classic-android/releases/tag/v3.20.1-B.0.1)** | `2026-11-27` | 📦 Archived (`3f65f8e`) | • `PvZ-Hybrid-Classic-3.20.1-Vietnamese-B.0.1.apk` (`90dc97ef...`)<br>• `PvZ-Hybrid-Classic-3.20.1-English-B.0.1.apk` (`98b0aaef...`)<br>• `PvZ-Hybrid-Classic-3.20.1-Chinese-Raw-B.0.1.apk` (`63f9556e...`) | Baseline standalone Android suite (`com.pvzh.cls`, 1080×600 widescreen, 1-tap touch, clean exit without relaunch, `VirGL + WineD3D GL csmt=0`, dynamic big-core affinity, binary perf caves `~29–34 FPS`, UTF-8 `gdi42.dll`, 3,309 property strings, 1,038 EXE strings, 171 textures per language). ([Notes](RELEASE_NOTES-3.20.1-B.0.1.md)) |

---

## Credits &amp; Official Sources
Full attribution &amp; legal disclaimer: **[`CREDITS.md`](CREDITS.md)**
- **Original Mod (*Plants vs. Zombies: Hybrid Classic* / 植物大战僵尸杂交版经典版):** **潜艇伟伟迷 (Qianting Weiweimi)** ([Official Bilibili](https://space.bilibili.com/97213827) · [Official Website `pvzhe.com`](https://pvzhe.com)) &amp; upstream contributors (**小小咩MS**, **AXH弦**, **一只吴铭仕哒**, **沉默寡言白河愁**).
- **Original Franchise:** *Plants vs. Zombies* is a registered trademark of **Electronic Arts Inc. (EA) / PopCap Games**.
- **Android Port, Localization &amp; Optimization:** **Heagon** ([pvz-hybrid-classic-android](https://github.com/Heagon/pvz-hybrid-classic-android)) — 100% free, ad-free, non-commercial.
