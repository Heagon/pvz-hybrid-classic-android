# Plants vs. Zombies: Hybrid Classic `v3.20.1` — Build `B.0.2` (`[EN]` / `[VI]` / `[CN]`)

> [!TIP]
> **Latest Recommended Build (`B.0.2` — 2026-11-28):**
> Major performance, FPS selector, mobile control, and stability upgrade over **[`v3.20.1-B.0.1`](https://github.com/Heagon/pvz-hybrid-classic-android/releases/tag/v3.20.1-B.0.1)**.
> Install directly over `B.0.1` (**Update — never uninstall**) to keep 100% of your saves intact. Every build has its own dedicated release tag (`B.0.1`, `B.0.2`, ...) so you can always trace fixes or roll back cleanly!

Standalone Android localization & optimization suite for **Plants vs. Zombies: Hybrid Classic v3.20.1** (*植物大战僵尸杂交版经典版* by **[潜艇伟伟迷](https://space.bilibili.com/97213827)** · [pvzhe.com](https://pvzhe.com)), packaged under dedicated package ID `com.pvzh.cls` (`versionCode 3201`) with a shared Release Keystore across **`[VI]` Bản Việt Hóa**, **`[EN]` English**, and **`[CN]` Chinese Raw**.

---

## What Changed Since `B.0.1` (`v3.20.1-B.0.1` → `v3.20.1-B.0.2`)

### 1. Live `30 / 60 / 90 / 120 FPS` Selector + Hard `>= 30 FPS` Non-Combat Floor + `100.00 Hz` Speed Parity
- **Live In-Game FPS Switcher (`PAD → FPS`):** Switch live between **`30`**, **`60`** (default), **`90`**, and **`120 FPS`** with zero restarts via memory-mapped `fps_cap.bin` (`0` syscalls/frame, persisted across restarts).
- **Exact `100.00 Hz` Simulation Parity Across All FPS Caps:** Decoupled rendering from PopCap's `100 Hz` game logic (`UpdateFrames` gate verified at **`-10s / 10.0s`** across `30 FPS`, `60 FPS`, and `120 FPS` in Hero Mode — zero speedup or slowdown!).
- **6 New Binary Engine Optimizations (`OPT 8–13`, `.d3dopt` `16,964 B` + `gdi42` O(1) Glyph Atlas):**
  - `OPT 8`: **1-Quad Baked Seed-Card Texture Atlas** (`4×1024×1024`, 768 cards, exact two-background black/white straight-alpha recovery, live cooldown sweep preserved).
  - `OPT 9`: **Zero-syscall live `30/60/90/120 FPS` pacer** (`aVSync=0` Frame-1 lock) + exact `100.00 Hz` logic gate.
  - `OPT 10`: **Occluded `PoolEffectDraw` cull** behind docked `SeedChooser` (resumes instantaneously on *View Lawn* / Combat).
  - `OPT 11`: **`Board::Draw` occluded quad cull** behind opaque `SeedChooser` (zero SeedBank clipping) + `SeedChooser` off-screen card culling.
  - `OPT 12`: **`D3DInterface::DrawTrianglesTex` Universal 12-Page Sprite Atlas + Zero-SEH `3072`-Vertex Batcher** — collapses 330–2,500/frame Reanimation body-part draws into ~2–5 batched calls.
  - `OPT 13`: **`HasSeedType` 1×/frame recount throttle + O(1) per-frame memo** — eliminates ~957,000 wasted loop iterations/frame in `SeedChooser`, jumping all 5 Survival maps from `~10–31 FPS` to **`62.6–67.1 FPS`**!
  - **`gdi42.dll` O(1) `DrawString` / `StringWidth` + Glyph Atlas** hooks across all 3 editions.

### 2. Bug Fixes & Stability Hardening (`patch_exe_fixes.py` + `ViewLawn` Sync)
- **Fixed `Menu` Button Not Responding on 1st Tap (incl. `I, Zombie`):** Added direct `Board::MouseHitTest` / `MouseDown` / `MouseUp` hit-testing for the `Menu` button rect, prioritized `Shovel` before `SeedBank`, fixed `-0x8c` `GameButton::Update` offset, and added a `CutScene`/`Board` safety net for stuck `CrazyDave LEAVING` state.
- **Fixed `View Lawn` / `Xem Bãi Cỏ` Soft-Lock:** Synced `CancelLawnView` (`0x48660F`), `MouseDown` (`0x4867D7`), and `KeyChar` (`0x486EBF`) timers (`100/250/251 → 20/50/51`) with fast ViewLawn pan so tapping *"Click to Continue"* / *"Nhấn để Tiếp Tục"* immediately returns to `SeedChooser`.
- **Fixed `I, Zombie` Infinite Free-Zombie Spawn Bug:** Clamped seed-cost & free-plant array upper bounds (`0x320 → 0x200`) so Buckethead / zombies deduct sun accurately.
- **Fixed Long-Session `LAA` (`>2 GB` Heap) Crash (`0x472BDD` / `0x472C9A`):** Patched signed `jg` → unsigned `ja` pointer checks in Reanimation atlas-ID checks so high-bit Wine allocations (`>= 0x80000000`) never crash during long or multi-mode sessions.
- **Fixed Hero Mode & Reanimation Fatal Crashes:** Added 30+ null-pointer, divide-by-zero (`HP bar` / `StringWidth`), `ReanimTryToGet`, `AddCoin`/`AddProj`, and Hero portrait index bounds guards.
- **Fixed Almanac Performance & Page-Table Overflow:** Replaced linear lookup with O(1) LUT + off-page culling.
- **Cleaned Up `NewOptionsDialog`:** Removed non-functional PC-only `3D Acceleration` & `Fullscreen` checkboxes and re-centered buttons.

### 3. Floating `PAD` Touch Toolbar & Quick Hotkeys
- Draggable **`PAD`** button expands to toggle **Quick Hotkeys** (`Shovel / R-Cancel / R-Aim / Drag / x2 / 0.25x / Pause / Rules / Shop / Glove / Zombie HP / Plant HP / Hide UI / Esc`), **Hero D-Pad**, **Drag Mode**, **Live `FPS` (`30/60/90/120`)**, **Opacity**, **Keyboard**, and **Menu**.

### 4. Traceable Build Versioning (`B.0.2`)
- Standardized filenames (`PvZ-Hybrid-Classic-3.20.1-<Language>-B.0.2.apk`) and embedded build stamp (`v3.20.1-{VI,EN,CN-Raw}-B.0.2`) inside `assets/pvz_edition.txt` so both upgrades (`B.0.1 → B.0.2`) and rollbacks (`B.0.2 → B.0.1`) cleanly update `pvz_game/` without touching `yourdata/` saves.

---

## Verified Hardware Benchmarks (`TECNO LG8n`, Helio G99, 90 Hz)

| Area / Test | Result (`B.0.2`) |
| :--- | :--- |
| **Non-Combat Screens (`90 FPS` cap)** | **`50.5 – 89.2 FPS`** (Rules `89.2`, Almanac `56.9–89.2`, Simulator `89.2`, Zen Garden `73.2`, SeedChooser all 5 Survival maps `62.6–67.1` & all 7 tabs `56.9–60.7`, Backyard `59.9`, Main Menu `52.9`, Achievements `52.3`, Shop `50.5`) — **100% above `30 FPS` floor** |
| **Game Speed Parity (`30 / 60 / 120 FPS`)** | Hero timer over `10.0s`: `30 FPS` (`47s→37s`), `60 FPS` (`74s→64s`), `120 FPS` active combat (`19s→9s`) — exact **`100.00 Hz` (`-10s/10s`)** |
| **Mode Checks** | `Survival (Day/Night/Pool/Fog/Roof)`, `Hero Mode`, `I, Zombie` (1-tap Menu + sun deduct), `Vasebreaker` (`59.9 FPS`), `Zomboss` (`60.1 FPS`), `SeedChooser` (`ViewLawn` + multi-tab pick + cooldown sweep + Shovel) — **all verified** |
| **7.9-Min Continuous Soak Test** | **`0` crashes, `0` errors**, flat RAM (`2259.6 → 2235.5 MB`), `37–38°C`, live `60→90→120→30→60 FPS` switching mid-Pool combat |

---

## Downloads & Checksums (`v3.20.1-B.0.2`)

| File | Edition | Exact Size | SHA-256 |
| :--- | :---: | :---: | :--- |
| `PvZ-Hybrid-Classic-3.20.1-Vietnamese-B.0.2.apk` | `[VI]` Bản Việt Hóa | `406,718,680` B (`387.88 MiB`) | `f3c00fc4db478ce06c3872cc30ca0b910d5dbf16b53966b030da6aef1c0cedb5` |
| `PvZ-Hybrid-Classic-3.20.1-English-B.0.2.apk` | `[EN]` English | `406,554,840` B (`387.72 MiB`) | `c299cf884bc665fa244455c9a01ea029f237676f8f5b08c80be987d80b0f8098` |
| `PvZ-Hybrid-Classic-3.20.1-Chinese-Raw-B.0.2.apk` | `[CN]` Original Raw | `408,393,944` B (`389.47 MiB`) | `799db80d71d0441073a26cc3a8da03accb87332a6f41e1d9cc70b15b079f110e` |

- **Build ID:** `B.0.2` · **Tag:** `v3.20.1-B.0.2` · **Previous Build (Rollback):** [`v3.20.1-B.0.1`](https://github.com/Heagon/pvz-hybrid-classic-android/releases/tag/v3.20.1-B.0.1) · **Full History:** [`CHANGELOG.md`](https://github.com/Heagon/pvz-hybrid-classic-android/blob/main/CHANGELOG.md)
- **Package ID:** `com.pvzh.cls` · **Version:** `3.20.1` (`versionCode: 3201`)
- **Signing Certificate SHA-256:** `0240760843400889e49e0030ea741eace8e6e97d64b47c560d609438943339f2` (`[v2, v3]`)
- **Golden Rule:** Always install over your existing app (**Update**) — **never uninstall** — to keep 100% of your `yourdata/` saves intact across updates, language switches, or rollbacks!

---

## Tóm Tắt Nhanh (`[VI]`)
1. **Nâng cấp lớn từ `B.0.1` → `B.0.2`:**
   - Thêm nút chọn **`30 / 60 / 90 / 120 FPS`** trực tiếp trong thanh **`PAD`** (mặc định `60 FPS`, tự lưu sau khi tắt mở lại), giữ chuẩn tốc độ game **`100.00 Hz`** ở mọi mức FPS.
   - Tối ưu sâu đồ họa & CPU (`OPT 8–13` + `gdi42` Glyph Atlas O(1)): **mọi màn hình không giao tranh đều đạt `50,5–89,2 FPS`** (Chọn Cây 5 bản đồ Sinh Tồn tăng lên `62,6–67,1 FPS`, Sổ Tay `56,9–89,2 FPS`).
   - **Vá triệt để hàng loạt lỗi:** lỗi bấm nút `Menu` không ăn (kể cả trong `Tôi Là Zombie`), lỗi kẹt mềm nút `Xem Bãi Cỏ`, lỗi thả Zombie miễn phí vô hạn trong `Tôi Là Zombie`, lỗi crash `LAA` khi chơi lâu / chuyển nhiều chế độ, chống crash `Hero Mode` & `Reanimation`, tối ưu Sổ Tay O(1) và dọn gọn hộp thoại Cài đặt.
   - Bổ sung thanh **`PAD`** & phím tắt cảm ứng tiện lợi (`Xẻng, Hủy R, Nhắm R, Kéo, x2, 0.25x, Dừng, Luật, Shop, Găng, HP ZB, HP Cây, Ẩn UI, Esc`, D-Pad Anh Hùng).
2. **Cách cài đặt / nâng cấp:** Tải tệp `...-B.0.2.apk` tương ứng (`[VI]`, `[EN]` hoặc `[CN]`) và bấm **Cài đè / Cập nhật (Update)** trực tiếp — không gỡ bản cũ để giữ nguyên 100% save. Nếu muốn đối chiếu hoặc quay lại bản cũ `B.0.1`, xem [`v3.20.1-B.0.1`](https://github.com/Heagon/pvz-hybrid-classic-android/releases/tag/v3.20.1-B.0.1).

---

## 👥 Credits, Official Sources & Legal Disclaimer
- **Full Credits & Attribution:** **[`CREDITS.md`](https://github.com/Heagon/pvz-hybrid-classic-android/blob/main/CREDITS.md)** ([`[VI] Tiếng Việt`](https://github.com/Heagon/pvz-hybrid-classic-android/blob/main/CREDITS.md#vi-bản-việt-hóa) · [`[EN] English`](https://github.com/Heagon/pvz-hybrid-classic-android/blob/main/CREDITS.md#en-english) · [`[CN] 简体中文`](https://github.com/Heagon/pvz-hybrid-classic-android/blob/main/CREDITS.md#cn-简体中文))
- **Original Mod (*Plants vs. Zombies: Hybrid Classic* / 植物大战僵尸杂交版经典版):** Created by **潜艇伟伟迷 (Qianting Weiweimi)** ([Official Bilibili](https://space.bilibili.com/97213827) · [Official Website `pvzhe.com`](https://pvzhe.com)) with upstream contributors credited in-game: **小小咩MS**, **AXH弦**, **一只吴铭仕哒**, **沉默寡言白河愁**.
- **Original Game Franchise:** *Plants vs. Zombies* is a registered trademark of **Electronic Arts Inc. (EA) / PopCap Games**.
- **Android Port, Localization, Optimization & Packaging:** **Heagon** ([pvz-hybrid-classic-android](https://github.com/Heagon/pvz-hybrid-classic-android)) using open-source components: [Winlator](https://github.com/brunodev85/winlator) (`Box64` · `Wine`), [MinGW-w64 / w64devkit](https://github.com/skeeto/w64devkit), [fontTools](https://github.com/fonttools/fonttools), [Pillow](https://python-pillow.org/), [Liberation Fonts](https://github.com/liberationfonts/liberation-fonts), [Apktool](https://apktool.org/), [uber-apk-signer](https://github.com/patrickfav/uber-apk-signer), and [Zstandard](https://github.com/facebook/zstd).
- **Non-Commercial Notice:** 100% free, ad-free, non-commercial community release. All original copyrights belong to their respective owners.
