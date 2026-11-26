# 💾 Sao Lưu &amp; Chuyển Dữ Liệu Save · Save Data Migration · 存档备份与迁移

<p align="center">
  <a href="../README.vi.md"><b>← [VI] Trang Chủ Tiếng Việt</b></a> &nbsp;•&nbsp;
  <a href="../README.md"><b>← [EN] English Home</b></a> &nbsp;•&nbsp;
  <a href="../README.cn.md"><b>← [CN] 返回中文主页</b></a>
</p>

<p align="center">
  <a href="INSTALL.md">📖 Hướng Dẫn Cài Đặt (INSTALL)</a> &nbsp;•&nbsp;
  <a href="UPDATE.md">🔄 Cập Nhật &amp; Đổi Ngôn Ngữ (UPDATE)</a> &nbsp;•&nbsp;
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

Vì bản **PvZ Hybrid Classic** đóng gói trong gói riêng `com.pvzh.cls` (không trùng mã gói với Winlator thường hay các bản mod khác), bạn có thể cài song song mà không làm ảnh hưởng các ứng dụng khác. Nếu muốn chép file save `yourdata` từ **bản PC** hoặc **container Winlator khác** sang APK này:

### Đường dẫn Save trên PC (Windows)
```text
C:\ProgramData\PopCap Games\PlantsVsZombies\pvzHE\yourdata\
```
### Đường dẫn Save trong APK `com.pvzh.cls`
```text
/data/data/com.pvzh.cls/files/imagefs/home/xuser/.wine/drive_c/ProgramData/PopCap Games/PlantsVsZombies/pvzHE/yourdata/
```

### Cách chuyển Save từ PC sang APK (qua Menu Cài đặt tích hợp)
1. Chép thư mục `yourdata\` từ PC vào bộ nhớ trong điện thoại (ví dụ `/sdcard/Download/yourdata/`).
2. Cài đặt APK và mở game 1 lần để giải nén xong màn hình đầu tiên, rồi thoát game.
3. Mở lại app và bấm nhanh nút **`Engine Settings`** (góc trên phải lúc màn hình chờ) để mở trình quản lý container Winlator, bấm **Run** mở File Explorer (`D:` trỏ về `/sdcard/Download`), rồi sao chép `D:\yourdata\*` dán đè vào:
   `C:\ProgramData\PopCap Games\PlantsVsZombies\pvzHE\yourdata\`.
4. Khởi động lại app — 100% file save từ PC của bạn đã hoạt động ngay trên điện thoại!

*(Nếu điện thoại đã Root hoặc dùng `adb` trên bản debug/gắn PC khác, lưu ý đường dẫn nằm trong `/data/data/com.pvzh.cls/` chứ không nằm ngoài `/sdcard/Android/data/`)*.

---

<a id="en-english"></a>
## [EN] English

Because this standalone release uses its own dedicated package ID (`com.pvzh.cls`), it installs cleanly alongside standalone Winlator or other PvZ mods without replacing them. If you want to import an existing Windows PC save (`yourdata/`) into the Android build:

### Save Locations
- **Windows PC:** `C:\ProgramData\PopCap Games\PlantsVsZombies\pvzHE\yourdata\`
- **Android Container (`com.pvzh.cls`):** `/data/data/com.pvzh.cls/files/imagefs/home/xuser/.wine/drive_c/ProgramData/PopCap Games/PlantsVsZombies/pvzHE/yourdata/`

### Migrating Your PC Save to Android (No Root Required)
1. Copy your PC `yourdata\` folder (`users.dat`, `user1.dat`, etc.) to `/sdcard/Download/yourdata/` on your phone.
2. Launch the APK once until setup finishes and the Main Menu appears, then close it.
3. Re-open the app and tap **`Engine Settings`** (top-right on the splash screen) to open the embedded container manager.
4. Launch the container desktop (`Run`) → open Wine File Manager → copy `D:\yourdata\*` into `C:\ProgramData\PopCap Games\PlantsVsZombies\pvzHE\yourdata\`.
5. Relaunch the app — your full PC progress loads right away!

---

<a id="cn-简体中文"></a>
## [CN] 简体中文

本整合版使用独立包名 `com.pvzh.cls`，可与普通 Winlator 或其他 PvZ 改版共存。如果您希望将 **PC 电脑端存档** 迁移至安卓版：

### 存档路径对比
- **Windows PC 端：** `C:\ProgramData\PopCap Games\PlantsVsZombies\pvzHE\yourdata\`
- **安卓容器内 (`com.pvzh.cls`)：** `/data/data/com.pvzh.cls/files/imagefs/home/xuser/.wine/drive_c/ProgramData/PopCap Games/PlantsVsZombies/pvzHE/yourdata/`

### 免 Root 将电脑存档导入安卓版
1. 将电脑上的 `yourdata\` 文件夹（内含 `users.dat`、`user1.dat` 等）拷贝至手机 `/sdcard/Download/yourdata/`。
2. 安装并启动一次安卓版 APK，待首次初始化完成后进入主界面再退出。
3. 重新打开软件，在加载页右上角点击 **`Engine Settings`** 进入内置容器管理界面，启动容器进入桌面资源管理器，将 `D:\yourdata\` 中的文件复制覆盖到 `C:\ProgramData\PopCap Games\PlantsVsZombies\pvzHE\yourdata\`。
4. 重启游戏，PC 端全部通关记录与图鉴即刻完整继承！
