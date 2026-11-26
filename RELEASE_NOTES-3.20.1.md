# Plants vs. Zombies: Hybrid Classic `v3.20.1` — Standalone Android Suite (`[EN]` / `[VI]` / `[CN]`)

First public standalone Android localization release of **Plants vs. Zombies: Hybrid Classic v3.20.1** (*植物大战僵尸杂交版经典版* by **潜艇伟伟迷**), packaged under dedicated package ID `com.pvzh.cls` (`versionCode 3201`) with a shared Release Keystore for 100% save-preserving updates across **`[EN]` English**, **`[VI]` Bản Việt Hóa**, and **`[CN]` Chinese Raw**.

---

## Highlights
- **Single Self-Contained APK (~389.4 MiB):** Bundles runtime + game assets together — no root, no manual container import, no external OBB, and no conflict with other apps.
- **Native `1080x600` Mobile Widescreen & Instant 1-Tap Touch (`TECNO_LG8n` arm64 verified):** Automatically configures `1080x600` native widescreen (eliminating right-side menu clipping), hides the overlay HUD by default (`HUDMode=0`), stretches edge-to-edge to full phone aspect ratio with fixed axis-independent `TouchpadView` coordinates, and moves the X11 cursor on `ACTION_DOWN` with 60 ms click hold for crisp 1-tap responsiveness.
- **2x Faster Gameplay & Lower Memory (`VirGL` + `WineD3D csmt=0`):** Defaults to **`VirGL`** + **`WineD3D` GL (`csmt=0`, `OffscreenRenderingMode=fbo`, `strict_shader_math=0`, `VideoMemorySize=512`)**, `WINEESYNC=1`, `mesa_glthread=false`, upright `Is3D=1` 3D acceleration, and Box64 fast dynarec (`STRONGMEM=0`, `BIGBLOCK=3`, `CALLRET=1`, `FASTNAN=1`, `FASTROUND=1`, `NATIVEFLAGS=1`, `FORWARD=1024`) — doubling Main Menu FPS from `8.5–12.2` to **`20.4–20.8 FPS`** while cutting CPU load and saving ~200 MB RAM.
- **UTF-8 Engine Shim & Merged Unicode Fonts:** Binary-patched `gdi42.dll` (`CP936` → `CP_UTF8` at 4 `MultiByteToWideChar` sites) + complete Latin/Vietnamese glyphs merged into all 6 runtime `.ttf` fonts.
- **Full Dual-Language Localization & UI Layout Refit (`[EN]` & `[VI]`):**
  - **3,309/3,309** entries across all 9 `properties/*.txt` files, with **437 Plant, Zombie & Hero Almanac descriptions refitted** cleanly inside non-scrolling card bounds plus tightened Seed Chooser tabs (`K.Cương`, `Chọn Lại`, etc.).
  - **1,038 unique strings (1,421 references)** safely relocated inside `PlantsVsZombies.exe` (Console checkboxes, Sandbox, Shop, Challenge titles, Continue dialogs) + **73 `std::string(ptr, len)` length-push opcodes updated** + Main Menu version prefix (`PvZ Hybrid Cls EN/VI v3.20.1`).
  - **133 localized UI textures** per language (Main Menu wooden signs, trophies pedestal, gravestones, 22 stage/chapter headers, Hero/Shop/Almanac/Progress UI).

---

## Downloads & Checksums

| File | Edition | Exact Size | SHA-256 |
| :--- | :---: | :---: | :--- |
| `PvZ-Hybrid-Classic-3.20.1-English.apk` | `[EN]` English | `408,303,833` B (`389.39 MiB`) | `5b282c40a6d24281f25dd178b3c80c377ddfa76f43e4aeff26df5e2825bcafbf` |
| `PvZ-Hybrid-Classic-3.20.1-Vietnamese.apk` | `[VI]` Bản Việt Hóa | `408,242,393` B (`389.33 MiB`) | `0b12a3593fdf8f701b8a7a1a9cb411c154c8bc5c2448087e6a7bfedeaa144078` |
| `PvZ-Hybrid-Classic-3.20.1-Chinese-Raw.apk` | `[CN]` Original Raw | `408,361,177` B (`389.44 MiB`) | `1087a781c7742c63c505e4e24bf9a5bceba2c046201a10b98f2b954fd338ec81` |

- **Signing Certificate SHA-256:** `0240760843400889e49e0030ea741eace8e6e97d64b47c560d609438943339f2` (`[v2, v3]`)
- **Golden Rule:** Always install over your existing app (**Update**) — **never uninstall** — when switching languages so all `yourdata/` saves stay 100% intact.

---

## Hướng Dẫn Nhanh (`[VI]`)
1. Tải bản `[VI]`, `[EN]` hoặc `[CN]` bên dưới (`Android 8.0+ arm64-v8a`, trống ~1.8 GB).
2. Cài đặt bình thường (nếu muốn đổi ngôn ngữ chỉ cần **cài đè / cập nhật trực tiếp**, không gỡ bản cũ để giữ nguyên 100% file save).
3. Lần mở đầu tiên chờ ~20–45 giây để trình khởi chạy tự giải nén và tạo sẵn hồ sơ `Player`.
