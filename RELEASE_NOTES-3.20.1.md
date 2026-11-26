# Plants vs. Zombies: Hybrid Classic `v3.20.1` — Standalone Android Suite (`[EN]` / `[VI]` / `[CN]`)

First public standalone Android localization release of **Plants vs. Zombies: Hybrid Classic v3.20.1** (*植物大战僵尸杂交版经典版* by **潜艇伟伟迷**), packaged under dedicated package ID `com.pvzh.cls` (`versionCode 3201`) with a shared Release Keystore for 100% save-preserving updates across **`[EN]` English**, **`[VI]` Bản Việt Hóa**, and **`[CN]` Chinese Raw**.

---

## Highlights
- **Single Self-Contained APK (~390 MiB):** Bundles runtime + game assets together — no root, no manual container import, no external OBB, and no conflict with other apps.
- **Native `1080x600` Mobile Widescreen & Instant 1-Tap Touch (`TECNO_LG8n` arm64 verified):** Automatically configures `1080x600` native widescreen (eliminating right-side menu clipping), stretches edge-to-edge to full phone aspect ratio with fixed axis-independent `TouchpadView` coordinates, and moves the X11 cursor on `ACTION_DOWN` with 60 ms click hold for crisp 1-tap responsiveness.
- **Faster Boot & Smoother Gameplay:** Aggressive Wine service startup pruning (`startupSelection=2`), `WineD3D` `csmt=3`, `strict_shader_math=0`, `mesa_glthread=true`, `WaitForVSync=0`, and locked upright `Is3D=0` rendering (~4.7 s warm launch to `PlantsVsZombies.exe`).
- **UTF-8 Engine Shim & Merged Unicode Fonts:** Binary-patched `gdi42.dll` (`CP936` → `CP_UTF8` at 4 `MultiByteToWideChar` sites) + complete Latin/Vietnamese glyphs merged into all 6 runtime `.ttf` fonts.
- **Full Dual-Language Localization (`[EN]` & `[VI]`):**
  - **3,309/3,309** entries across all 9 `properties/*.txt` files (compact Seed Chooser tabs & re-wrapped Patch Notes).
  - **985 unique strings (1,344 references)** safely relocated inside `PlantsVsZombies.exe` + **73 `std::string(ptr, len)` length-push opcodes updated** (eliminating `Prev□□` / `Next□□` / `Mini-Gam` / `□□□□□□`) + Main Menu version prefix (`PvZ Hybrid Cls EN/VI v3.20.1`).
  - **121 localized UI textures** per language (Main Menu wooden signs, trophies pedestal, gravestones, 18 Adventure chapter headers, Hero/Shop/Almanac UI).

---

## Downloads & Checksums

| File | Edition | Exact Size | SHA-256 |
| :--- | :---: | :---: | :--- |
| `PvZ-Hybrid-Classic-3.20.1-English.apk` | `[EN]` English | `408,930,525` B (`389.99 MiB`) | `32b37bbbb1bb3d46c72c42092f12e04e9da951edb3915462499cc6e71acbab3c` |
| `PvZ-Hybrid-Classic-3.20.1-Vietnamese.apk` | `[VI]` Bản Việt Hóa | `409,012,445` B (`390.06 MiB`) | `e529884d03b514641b14576efdc7c803b4f764868fc07ea11bbcc525c1f60feb` |
| `PvZ-Hybrid-Classic-3.20.1-Chinese-Raw.apk` | `[CN]` Original Raw | `408,361,181` B (`389.44 MiB`) | `09344c5b544faaed2eb0738e543093aadd91096fa6b1b651f9f0de7c6c94ef71` |

- **Signing Certificate SHA-256:** `0240760843400889e49e0030ea741eace8e6e97d64b47c560d609438943339f2` (`[v2, v3]`)
- **Golden Rule:** Always install over your existing app (**Update**) — **never uninstall** — when switching languages so all `yourdata/` saves stay 100% intact.

---

## Hướng Dẫn Nhanh (`[VI]`)
1. Tải bản `[VI]`, `[EN]` hoặc `[CN]` bên dưới (`Android 8.0+ arm64-v8a`, trống ~1.8 GB).
2. Cài đặt bình thường (nếu muốn đổi ngôn ngữ chỉ cần **cài đè / cập nhật trực tiếp**, không gỡ bản cũ để giữ nguyên 100% file save).
3. Lần mở đầu tiên chờ ~20–45 giây để trình khởi chạy tự giải nén và tạo sẵn hồ sơ `Player`.
