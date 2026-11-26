# 🔄 Cập Nhật &amp; Đổi Ngôn Ngữ Không Mất Save · Safe Updates · 无损更新指南

<p align="center">
  <a href="../README.vi.md"><b>← [VI] Trang Chủ Tiếng Việt</b></a> &nbsp;•&nbsp;
  <a href="../README.md"><b>← [EN] English Home</b></a> &nbsp;•&nbsp;
  <a href="../README.cn.md"><b>← [CN] 返回中文主页</b></a>
</p>

<p align="center">
  <a href="INSTALL.md">📖 Hướng Dẫn Cài Đặt (INSTALL)</a> &nbsp;•&nbsp;
  <a href="MIGRATION.md">💾 Sao Lưu &amp; Chuyển Save (MIGRATION)</a> &nbsp;•&nbsp;
  <a href="../CREDITS.md">👥 Đội Ngũ (CREDITS)</a>
</p>

<p align="center">
  <a href="#vi-bản-việt-hóa"><b>[VI] Bản Việt Hóa</b></a> &nbsp;|&nbsp;
  <a href="#en-english"><b>[EN] English</b></a> &nbsp;|&nbsp;
  <a href="#cn-简体中文"><b>[CN] 简体中文</b></a>
</p>

---

<a id="vi-bản-việt-hóa"></a>
## [VI] Bản Việt Hóa

> [!IMPORTANT]
> **Quy Tắc Vàng:** Luôn bấm **Cài đặt đè / Cập nhật (Install / Update)** — **TUYỆT ĐỐI KHÔNG bấm Gỡ cài đặt (Uninstall)**.

### Vị trí lưu Save của `com.pvzh.cls`
Tiến trình chơi (*PopCap `users.dat` + `user1.dat`...*) được lưu bên trong thư mục riêng của container Wine tại:
```text
/data/data/com.pvzh.cls/files/imagefs/home/xuser/.wine/drive_c/ProgramData/PopCap Games/PlantsVsZombies/pvzHE/yourdata/
```
Trên Android, chỉ khi bạn **Gỡ cài đặt (Uninstall)** hoặc tự tay xóa dữ liệu ứng dụng thì hệ điều hành mới xóa thư mục dữ liệu nội bộ này.

### Cơ chế giữ Save 100% khi nâng cấp hoặc đổi ngôn ngữ
- **Đồng nhất chữ ký số (Unified Release Keystore):** Cả 3 bản APK (**`[VI] Bản Việt Hóa`**, **`[EN] English`**, **`[CN] Trung Gốc`**) đều dùng chung mã gói `com.pvzh.cls` và cùng một khóa ký phát hành chính thức.
- **Tự động cập nhật tài nguyên qua `pvz_edition.txt`:** Khi bạn cài đè một ngôn ngữ khác (ví dụ đổi từ `[CN]` → `[VI]` hoặc `[VI]` → `[EN]`), launcher phát hiện `pvz_edition.txt` trong APK khác với bản đang giải nén trên máy và chỉ giải nén đè lại thư mục `files/pvz_game/` — **hoàn toàn không đụng tới thư mục `yourdata/` chứa save**!
- **Chuyển ngôn ngữ mọi lúc:** Mở file APK ngôn ngữ bạn muốn → bấm **Cập nhật** → vào lại đúng màn đang chơi với ngôn ngữ mới trong vài giây.

---

<a id="en-english"></a>
## [EN] English

> [!IMPORTANT]
> **The Golden Rule:** Always **install over the top (in-place Update)** — **NEVER tap Uninstall**.

### Where Save Data Lives (`com.pvzh.cls`)
All player profiles and progress (*PopCap `users.dat`, `user1.dat`, etc.*) reside inside the Wine prefix in internal app storage:
```text
/data/data/com.pvzh.cls/files/imagefs/home/xuser/.wine/drive_c/ProgramData/PopCap Games/PlantsVsZombies/pvzHE/yourdata/
```
Android only deletes this folder if you manually clear App Data or tap **Uninstall**.

### How Lossless Updates &amp; Language Switching Work
- **Unified Release Keystore:** All three editions (**`[EN] English`**, **`[VI] Bản Việt Hóa`**, and **`[CN] Chinese Raw`**) share package ID `com.pvzh.cls` and the exact same release signing certificate.
- **Edition Stamp (`pvz_edition.txt`):** Whenever you install another language or newer build over the existing app, `PvZBootstrapActivity` compares `pvz_edition.txt` (`v3.20.1-EN`, `v3.20.1-VI`, `v3.20.1-CN-Raw`), cleanly swaps only `files/pvz_game/` (`PlantsVsZombies.exe`, `gdi42.dll`, `main.pak`, Unicode fonts), and leaves your Wine prefix + `yourdata/` saves completely untouched!

---

<a id="cn-简体中文"></a>
## [CN] 简体中文

> [!IMPORTANT]
> **黄金准则：** 升级版本或切换语言时，请始终**直接覆盖安装（点击更新）**——**切勿卸载旧版本**。

### 存档位置说明 (`com.pvzh.cls`)
游戏的全部关卡进度与植物收集存档（PopCap `users.dat`、`user1.dat` 等）保存在容器内置目录中：
```text
/data/data/com.pvzh.cls/files/imagefs/home/xuser/.wine/drive_c/ProgramData/PopCap Games/PlantsVsZombies/pvzHE/yourdata/
```
在安卓系统中，**只有执行“卸载”或手动“清除应用数据”才会清除此目录**。

### 无损更新与跨语言切换机制
- **统一签名证书 (Unified Release Keystore)：** **`[CN] 中文原版`**、**`[VI] 越化版`** 与 **`[EN] 英文版`** 共享包名 `com.pvzh.cls` 及同一项目发布密钥。
- **独立版本标识 (`pvz_edition.txt`)：** 覆盖安装新语言 APK 时，启动器会检测 `pvz_edition.txt` 变化并仅重新释放 `files/pvz_game/` 游戏本体与字库目录，完全不触碰容器内的 `yourdata/` 存档文件！
- **随时无缝互切语言：** 下载任意语言版本 APK 直接点击覆盖更新，即可无缝切回中文原版、英文版或越南语版，存档 100% 完整保留。
