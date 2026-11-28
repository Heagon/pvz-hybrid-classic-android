# Plants vs. Zombies: Hybrid Classic `v3.20.1` — Build `B.0.1` (`[EN]` / `[VI]` / `[CN]`)

> [!NOTE]
> **Archived Baseline Build (`B.0.1` — 2026-11-27, commit [`3f65f8e`](https://github.com/Heagon/pvz-hybrid-classic-android/commit/3f65f8e)):**
> This is the **initial baseline release (`B.0.1`)** of the standalone Android suite for *PvZ Hybrid Classic v3.20.1*.
> For the newest build with live **`30 / 60 / 90 / 120 FPS`** switching, **`50.5–89.2 FPS`** non-combat screens, `PAD` mobile controls, and all gameplay/crash fixes (`Menu` 1-tap fix, `I, Zombie` fix, `ViewLawn` fix, `Hero`/`LAA` guards), download **[`v3.20.1-B.0.2`](https://github.com/Heagon/pvz-hybrid-classic-android/releases/tag/v3.20.1-B.0.2)**.
> This release remains permanently archived so users can compare builds or **roll back in-place (Update, never uninstall)** with 100% save preservation.

First public standalone Android localization release of **Plants vs. Zombies: Hybrid Classic v3.20.1** (*植物大战僵尸杂交版经典版* by **[潜艇伟伟迷](https://space.bilibili.com/97213827)** · [pvzhe.com](https://pvzhe.com)), packaged under dedicated package ID `com.pvzh.cls` (`versionCode 3201`) with a shared Release Keystore for 100% save-preserving updates across **`[EN]` English**, **`[VI]` Bản Việt Hóa**, and **`[CN]` Chinese Raw**.

---

## Highlights (`B.0.1`)
- **Single Self-Contained APK (387.7–389.4 MiB) & Clean Exit:** Bundles runtime + game assets together — no root, no manual container import, no external OBB, and no conflict with other apps. Quitting in-game or via the Winlator drawer cleanly tears down Wine processes and removes the Android task (`finishAndRemoveTask()`) without relaunching the game.
- **Native `1080x600` Mobile Widescreen & Instant 1-Tap Touch (`TECNO_LG8n` arm64 verified):** Automatically configures `1080x600` native widescreen (eliminating right-side menu clipping), hides the overlay HUD by default (`HUDMode=0`), stretches edge-to-edge to full phone aspect ratio with fixed axis-independent `TouchpadView` coordinates, and moves the X11 cursor on `ACTION_DOWN` with 60 ms click hold for crisp 1-tap responsiveness.
- **Baseline `~29–34 FPS` Performance, Dynamic Big-Core Affinity & Snappy Transitions (`VirGL` + `csmt=0` + Binary Caves):** Defaults to **`VirGL`** + **`WineD3D` GL (`csmt=0`, `OffscreenRenderingMode=fbo`, `strict_shader_math=0`, `VideoMemorySize=512`)**, `WINEESYNC=1`, `mesa_glthread=false`, upright `Is3D=1` 3D acceleration, Box64 fast dynarec, and `detectBigCoreAffinity()` SoC big-core pinning. Enhanced across all 3 editions (`[EN]`, `[VI]`, `[CN]`) with 5 `.newHE` binary optimizations (`30 FPS` render decoupling, off-screen `SeedChooser` card culling, zero-angle `Reanimation::MatrixFromTransform` fast path, heavy particle-spawn throttling, and `4–20x` faster camera/menu transitions).
- **UTF-8 Engine Shim & Merged Unicode Fonts:** Binary-patched `gdi42.dll` (`CP936` → `CP_UTF8` at 4 `MultiByteToWideChar` sites) + complete Latin/Vietnamese glyphs merged into all 6 runtime `.ttf` fonts.
- **Full Dual-Language Localization & UI Layout Refit (`[EN]` & `[VI]`):**
  - **3,309/3,309** entries across all 9 `properties/*.txt` files, with **437 Plant, Zombie & Hero Almanac descriptions refitted** cleanly inside non-scrolling card bounds.
  - **1,038 unique strings (1,421 references)** relocated inside `PlantsVsZombies.exe` + **73 `std::string(ptr, len)` length-push opcodes updated** + Main Menu version prefix (`PvZ Hybrid Cls EN/VI v3.20.1`).
  - **171 localized UI textures** per language.

---

## Downloads & Checksums (`v3.20.1-B.0.1`)

| File | Edition | Exact Size | SHA-256 |
| :--- | :---: | :---: | :--- |
| `PvZ-Hybrid-Classic-3.20.1-Vietnamese-B.0.1.apk` | `[VI]` Bản Việt Hóa | `406,690,009` B (`387.85 MiB`) | `90dc97ef7628b663910812e77f0312b3f8326ffcae663e5569feb481ef5b3baa` |
| `PvZ-Hybrid-Classic-3.20.1-English-B.0.1.apk` | `[EN]` English | `406,526,169` B (`387.69 MiB`) | `98b0aaef91e536b65986c03aaeb10d0cde52b0bc4da35720c135a1d318efc1c9` |
| `PvZ-Hybrid-Classic-3.20.1-Chinese-Raw-B.0.1.apk` | `[CN]` Original Raw | `408,361,177` B (`389.44 MiB`) | `63f9556e36c57fa2d44641aa5579b67166bf240fe8fcecac63cb79eb306b2b72` |

- **Build ID:** `B.0.1` · **Tag:** `v3.20.1-B.0.1` · **Commit:** [`3f65f8e`](https://github.com/Heagon/pvz-hybrid-classic-android/commit/3f65f8e) · **Full Build History:** [`CHANGELOG.md`](https://github.com/Heagon/pvz-hybrid-classic-android/blob/main/CHANGELOG.md)
- **Signing Certificate SHA-256:** `0240760843400889e49e0030ea741eace8e6e97d64b47c560d609438943339f2` (`[v2, v3]`)
- **Golden Rule:** Always install over your existing app (**Update**) — **never uninstall** — when switching languages or switching between `B.0.1` and `B.0.2` so all `yourdata/` saves stay 100% intact.

---

## Tóm Tắt Nhanh (`[VI]`)
- Đây là **bản phát hành nền đầu tiên (`B.0.1` — 27/11/2026)**, được lưu trữ cố định để người dùng dễ đối chiếu lịch sử sửa lỗi hoặc cài đè quay lại khi cần (giữ nguyên 100% save).
- Để dùng bản mới nhất có chọn mức **`30 / 60 / 90 / 120 FPS`**, màn hình không giao tranh đạt **`50,5–89,2 FPS`**, thanh `PAD` và các bản vá lỗi (`Menu 1 chạm`, `Tôi Là Zombie`, `Xem Bãi Cỏ`, chống crash `Hero`/`LAA`), hãy tải **[`v3.20.1-B.0.2`](https://github.com/Heagon/pvz-hybrid-classic-android/releases/tag/v3.20.1-B.0.2)**.

---

## 👥 Credits, Official Sources & Legal Disclaimer
- **Full Credits Page:** **[`CREDITS.md`](https://github.com/Heagon/pvz-hybrid-classic-android/blob/main/CREDITS.md)** ([`[VI] Tiếng Việt`](https://github.com/Heagon/pvz-hybrid-classic-android/blob/main/CREDITS.md#vi-bản-việt-hóa) · [`[EN] English`](https://github.com/Heagon/pvz-hybrid-classic-android/blob/main/CREDITS.md#en-english) · [`[CN] 简体中文`](https://github.com/Heagon/pvz-hybrid-classic-android/blob/main/CREDITS.md#cn-简体中文))
- **Original Mod (*Plants vs. Zombies: Hybrid Classic* / 植物大战僵尸杂交版经典版):** Created by **潜艇伟伟迷 (Qianting Weiweimi)** ([Official Bilibili](https://space.bilibili.com/97213827) · [Official Website `pvzhe.com`](https://pvzhe.com)) with upstream contributors credited in-game: **小小咩MS**, **AXH弦**, **一只吴铭仕哒**, **沉默寡言白河愁**.
- **Original Game Franchise:** *Plants vs. Zombies* is a registered trademark of **Electronic Arts Inc. (EA) / PopCap Games**.
- **Android Port, Localization & Packaging:** **Heagon** ([pvz-hybrid-classic-android](https://github.com/Heagon/pvz-hybrid-classic-android)) using open-source tools: [Winlator](https://github.com/brunodev85/winlator) (`Box64` · `Wine`), [fontTools](https://github.com/fonttools/fonttools), [Pillow](https://python-pillow.org/), [Liberation Fonts](https://github.com/liberationfonts/liberation-fonts), [Apktool](https://apktool.org/), [uber-apk-signer](https://github.com/patrickfav/uber-apk-signer), and [Zstandard](https://github.com/facebook/zstd).
- **Non-Commercial Notice:** 100% free, ad-free, non-commercial community release. All original copyrights belong to their respective owners.
