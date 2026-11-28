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

### Cơ chế giữ Save 100% khi nâng cấp, quay lại bản cũ (`B.x.y`) hoặc đổi ngôn ngữ
- **Đồng nhất chữ ký số &amp; `versionCode` (`3201`):** Cả 3 ngôn ngữ (**`[VI]`**, **`[EN]`**, **`[CN]`**) và mọi bản build (`B.0.1`, `B.0.2`, ...) đều dùng chung mã gói `com.pvzh.cls`, cùng `versionCode` và cùng một khóa ký phát hành chính thức.
- **Tự động cập nhật tài nguyên qua tem `pvz_edition.txt` (`v3.20.1-VI-B.0.2`):** Khi bạn cài đè bản build mới (`B.0.1 → B.0.2`), quay lại bản build trước (`B.0.2 → B.0.1`), hoặc đổi ngôn ngữ (`[VI]` ↔ `[EN]` ↔ `[CN]`), launcher phát hiện `pvz_edition.txt` khác và chỉ giải nén đè lại thư mục `files/pvz_game/` — **hoàn toàn không đụng tới thư mục `yourdata/` chứa save**!
- **Chuyển ngôn ngữ hoặc phiên bản build mọi lúc:** Mở tệp APK tương ứng trong mục [Releases](https://github.com/Heagon/pvz-hybrid-classic-android/releases) (xem bảng lịch sử tại [`CHANGELOG.md`](../CHANGELOG.md)) → bấm **Cập nhật** → vào lại đúng màn đang chơi trong vài giây.

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

### How Lossless Updates, Rollbacks (`B.x.y`) &amp; Language Switching Work
- **Unified Release Keystore &amp; `versionCode` (`3201`):** All three editions (**`[EN]`**, **`[VI]`**, **`[CN]`**) and every `B.x.y` build share package ID `com.pvzh.cls`, the same `versionCode`, and the exact same release signing certificate.
- **Build-Stamped `pvz_edition.txt` (`v3.20.1-EN-B.0.2`):** Whenever you upgrade (`B.0.1 → B.0.2`), roll back (`B.0.2 → B.0.1`), or switch languages over the existing app, `PvZBootstrapActivity` compares `pvz_edition.txt`, cleanly swaps only `files/pvz_game/` (`PlantsVsZombies.exe`, `gdi42.dll`, `main.pak`, Unicode fonts), and leaves your Wine prefix + `yourdata/` saves completely untouched! See [`CHANGELOG.md`](../CHANGELOG.md) for all releases.

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

### 无损更新、版本回退 (`B.x.y`) 与跨语言切换机制
- **统一签名证书与 `versionCode` (`3201`)：** **`[CN]`**、**`[VI]`**、**`[EN]`** 与所有 `B.x.y` 构建版本共享包名 `com.pvzh.cls`、相同 `versionCode` 及同一项目发布密钥。
- **独立构建标识 (`pvz_edition.txt`，例如 `v3.20.1-CN-Raw-B.0.2`)：** 无论覆盖升级（`B.0.1 → B.0.2`）、回退旧版（`B.0.2 → B.0.1`）还是跨语言切换，启动器均会检测 `pvz_edition.txt` 变化并仅重新释放 `files/pvz_game/`，完全不触碰 `yourdata/` 存档！全部构建记录详见 [`CHANGELOG.md`](../CHANGELOG.md)。
