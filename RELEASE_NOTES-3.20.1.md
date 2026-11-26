# Plants vs. Zombies: Hybrid Classic `v3.20.1` — Standalone Android Suite (`[EN]` / `[VI]` / `[CN]`)

First public standalone Android localization release of **Plants vs. Zombies: Hybrid Classic v3.20.1** (*植物大战僵尸杂交版经典版* by **潜艇伟伟迷**), packaged under dedicated package ID `com.pvzh.cls` (`versionCode 3201`) with a shared Release Keystore for 100% save-preserving updates across **`[EN]` English**, **`[VI]` Bản Việt Hóa**, and **`[CN]` Chinese Raw**.

---

## Highlights
- **Single Self-Contained APK (~390 MiB):** Bundles runtime + game assets together — no root, no manual container import, no external OBB, and no conflict with other apps.
- **Upright Hardware Graphics (`TECNO` arm64 verified):** Uses **`WineD3D` OpenGL FBO (`renderer=gl`)** + **`GLXExtension` (`flipY=false`)** fix for upright 1:1 touch rendering.
- **UTF-8 Engine Shim & Merged Unicode Fonts:** Binary-patched `gdi42.dll` (`CP936` → `CP_UTF8` at 4 `MultiByteToWideChar` sites) + complete Latin/Vietnamese glyphs merged into all 6 runtime `.ttf` fonts.
- **Full Dual-Language Localization (`[EN]` & `[VI]`):**
  - **3,309/3,309** entries across all 9 `properties/*.txt` files.
  - **983 unique strings (1,342 references)** safely relocated inside `PlantsVsZombies.exe` + Main Menu version prefix (`PvZ Hybrid Cls EN/VI v3.20.1`).
  - **121 localized UI textures** per language (Main Menu wooden signs, trophies pedestal, gravestones, 18 Adventure chapter headers, Hero/Shop/Almanac UI).

---

## Downloads & Checksums

| File | Edition | Exact Size | SHA-256 |
| :--- | :---: | :---: | :--- |
| `PvZ-Hybrid-Classic-3.20.1-English.apk` | `[EN]` English | `408,930,525` B (`389.99 MiB`) | `cb6c80a8a7b99b97c7dff908f1ceae90a2a47d853c8c6b8322359d89bcda7845` |
| `PvZ-Hybrid-Classic-3.20.1-Vietnamese.apk` | `[VI]` Bản Việt Hóa | `408,967,389` B (`390.02 MiB`) | `57ba7050979f1753e04dc229f78275a377bd07106e91461f801214f19c51fb38` |
| `PvZ-Hybrid-Classic-3.20.1-Chinese-Raw.apk` | `[CN]` Original Raw | `408,361,181` B (`389.44 MiB`) | `198d6298405f69e536475b65bb85c9c89e88a55283e4162baaac933e00264ec8` |

- **Signing Certificate SHA-256:** `0240760843400889e49e0030ea741eace8e6e97d64b47c560d609438943339f2` (`[v2, v3]`)
- **Golden Rule:** Always install over your existing app (**Update**) — **never uninstall** — when switching languages so all `yourdata/` saves stay 100% intact.

---

## Hướng Dẫn Nhanh (`[VI]`)
1. Tải bản `[VI]`, `[EN]` hoặc `[CN]` bên dưới (`Android 8.0+ arm64-v8a`, trống ~1.8 GB).
2. Cài đặt bình thường (nếu muốn đổi ngôn ngữ chỉ cần **cài đè / cập nhật trực tiếp**, không gỡ bản cũ để giữ nguyên 100% file save).
3. Lần mở đầu tiên chờ ~20–45 giây để trình khởi chạy tự giải nén và tạo sẵn hồ sơ `Player`.
