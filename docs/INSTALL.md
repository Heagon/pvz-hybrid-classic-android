# 📖 Hướng Dẫn Cài Đặt · Installation Guide · 安装指南 (Android)

<p align="center">
  <a href="../README.vi.md"><b>← [VI] Trang Chủ Tiếng Việt</b></a> &nbsp;•&nbsp;
  <a href="../README.md"><b>← [EN] English Home</b></a> &nbsp;•&nbsp;
  <a href="../README.cn.md"><b>← [CN] 返回中文主页</b></a>
</p>

<p align="center">
  <a href="UPDATE.md">🔄 Cập Nhật &amp; Đổi Ngôn Ngữ (UPDATE)</a> &nbsp;•&nbsp;
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

### 1. Cấu hình thiết bị yêu cầu
- Điện thoại hoặc máy tính bảng chạy **Android 8.0** trở lên.
- Vi xử lý 64-bit kiến trúc **`arm64-v8a`** (hầu hết thiết bị từ năm 2018 trở lại đây đều hỗ trợ).
- Bộ nhớ trống tối thiểu: **~1.8 GB** khả dụng (tệp APK nặng ~390 MiB / ~409 MB; lần mở đầu tiên sẽ tự giải nén môi trường chạy và dữ liệu game vào bộ nhớ trong).

### 2. Các bước cài đặt chuẩn (Chỉ 1 APK duy nhất)
> Khác với các bản giả lập rời yêu cầu tải riêng container hay tự chép file, bộ cài đặt này đóng gói toàn bộ thành **1 tệp APK độc lập (`com.pvzh.cls`)**:
1. **Tải tệp APK:** Chọn phiên bản mong muốn (**`[VI] Bản Việt Hóa`**, **`[EN] English`**, hoặc **`[CN] Trung Gốc`**) từ [Trang Chủ Tiếng Việt](../README.vi.md#downloads) hoặc mục [Releases](https://github.com/Heagon/pvz-hybrid-classic-android/releases).
2. **Cấp quyền cài đặt tệp APK (nếu cài lần đầu):**
   - Vào **Cài đặt → Ứng dụng → Trình duyệt / Quản lý tệp** → Bật **Cho phép cài đặt ứng dụng không rõ nguồn gốc**.
3. **Mở tệp APK và bấm Cài đặt (Install):**
   - Nếu đang dùng một bản ngôn ngữ khác từ cùng kho này, chỉ cần bấm **Cập nhật / Cài đặt đè (Update)** (**không gỡ bản cũ**) để giữ nguyên 100% file save.
4. **Chờ giải nén lần đầu (~20–45 giây):**
   - Màn hình khởi động tích hợp sẽ tự giải nén Linux/Wine runtime, bộ nhớ đệm container và dữ liệu game **PvZ Hybrid Classic v3.20.1**, đồng thời tạo sẵn hồ sơ `Player` để vào thẳng menu chính.
5. **Điều khiển trong game trên cảm ứng:**
   - **Chạm màn hình:** Di chuyển chuột tới điểm chạm và nhấp chuột trái.
   - **Bấm nút Quay lại (Back) của điện thoại:** Mở menu điều khiển (bật/tắt bàn phím ảo cho các cây dùng phím `WASD`, phím `Space` tạm dừng, chuột phải thu Thẻ/Mặt trời, chuyển chế độ chạm).
   - **Nút `Engine Settings` (góc trên phải lúc màn hình chờ):** Tùy chỉnh đồ họa (`VirGL` mặc định tối ưu FPS / `Vortek`), độ phân giải hoặc nút điều khiển nếu cần trên một số máy đặc thù.

### 3. Xử lý sự cố thường gặp
> [!NOTE]
> **Cảnh báo Google Play Protect:** Vì APK cộng đồng được ký bằng chứng chỉ phát hành riêng ngoài Google Play, Play Protect có thể nhắc cảnh báo. Bấm **Chi tiết khác (More details) → Vẫn cài đặt (Install anyway)**. Toàn bộ script đóng gói được công khai minh bạch trong [`tools/`](../tools/README.md).

> [!TIP]
> **Màn hình đen hoặc khác biệt theo dòng GPU:** Lần đầu khởi tạo Wine prefix cần 20–45 giây để dựng registry. Bản dựng mặc định đã dùng `VirGL` + `WineD3D csmt=0` để đạt tốc độ cao và tiết kiệm RAM trên Mali/Adreno; nếu gặp lỗi hiển thị hiếm gặp trên một số máy, hãy chạm **`Engine Settings`** ở góc trên phải lúc vừa mở app để thử đổi sang `Vortek`.

---

<a id="en-english"></a>
## [EN] English

### 1. System Requirements
- Android phone or tablet running **Android 8.0+**.
- **`arm64-v8a`** 64-bit CPU architecture.
- Free storage: at least **~1.8 GB** available (~390 MiB / ~409 MB APK + one-time first-launch extraction of runtime & game data).

### 2. Step-by-Step Installation (Single Standalone APK)
> No separate emulator setup, OBB folders, or manual file copying required — everything runs from one self-contained package (**`com.pvzh.cls`**):
1. **Download APK:** Grab your preferred edition (**`[EN] English`**, **`[VI] Bản Việt Hóa`**, or **`[CN] Chinese Raw`**) from the [Main README](../README.md#downloads) or [Releases](https://github.com/Heagon/pvz-hybrid-classic-android/releases).
2. **Allow Unknown Apps (first-time sideloading):**
   - Go to **Settings → Apps → (Your Browser / File Manager)** → Enable **Install unknown apps**.
3. **Open the APK and tap Install:**
   - Already playing another language from this repo? Simply tap **Update / Install over existing app** (**never uninstall**) to preserve 100% of your save data.
4. **Wait for First-Time Extraction (~20–45s):**
   - The built-in launcher automatically sets up the Wine/Box64 runtime, extracts the game archive, pre-seeds a default `"Player"` profile, and launches *PvZ Hybrid Classic v3.20.1* in fullscreen.
5. **Touch Controls & Shortcuts:**
   - **Touchscreen:** Direct cursor-to-touchpoint click.
   - **Device Back Button:** Opens overlay controls (virtual keyboard for `WASD`-controlled plants, `Space` pause, right-click for Shovel/Chili Suns, touch mode toggle).
   - **`Engine Settings` (top-right during boot splash):** Adjust GPU driver (`VirGL` default / `Vortek`), Box64 preset, or resolution if needed.

### 3. Troubleshooting
> [!NOTE]
> **Google Play Protect prompt:** Standard warning for community-signed APKs outside the Play Store. Tap **More details → Install anyway**. Build scripts are fully open in [`tools/`](../tools/README.md).

> [!TIP]
> **GPU driver fallback / slow cold boot:** First-time Wine initialization takes 20–45 seconds. The build defaults to **`VirGL` + `WineD3D csmt=0`** for ~2x higher FPS and lower RAM on Mali/Adreno GPUs; if your GPU has display artifacts, tap **`Engine Settings`** on the launch splash to try `Vortek`.

---

<a id="cn-简体中文"></a>
## [CN] 简体中文

### 1. 系统配置要求
- 运行 **Android 8.0** 及以上系统的手机或平板电脑。
- **`arm64-v8a`** 64 位处理器架构。
- 存储空间：建议预留 **约 1.8 GB** 可用空间（APK 本体约 390 MiB / 409 MB，首次启动时会自动在应用内部释放运行环境与游戏文件）。

### 2. 一键单包安装步骤（无需单独配置模拟器）
> 本项目将游戏本体与运行容器整合为**单一独立 APK（包名 `com.pvzh.cls`）**，免去手动导入容器的繁琐步骤：
1. **下载安装包：** 前往 [中文主页](../README.cn.md#downloads) 或 [Releases](https://github.com/Heagon/pvz-hybrid-classic-android/releases) 下载 **`[CN] 中文原版`**、**`[VI] 越化版`** 或 **`[EN] 英文版`**。
2. **开启未知来源应用安装权限：**
   - **设置 → 应用 → 浏览器 / 文件管理器** → 开启 **允许安装未知应用**。
3. **直接安装或覆盖升级：**
   - 如果设备已安装本仓库任意语言版本，直接**覆盖更新安装（切勿卸载）**即可无损保留全部通关存档。
4. **等待首次初始化（约 20–45 秒）：**
   - 内置引导器会自动释放运行环境并预先创建默认 `Player` 存档档案，随后自动全屏进入《植物大战僵尸杂交版经典版 v3.20.1》。
5. **触屏操作说明：**
   - **屏幕点击：** 自动将指针移至触控点并触发左键点击。
   - **手机返回键 (Back)：** 呼出悬浮菜单（调出 `WASD` 虚拟键盘、`Space` 暂停、右键交互切换等）。
   - **启动界面右上角 `Engine Settings`：** 可根据机型调整图形驱动（默认 **`VirGL` + `csmt=0`** 性能优化 / `Vortek`）或 Box64 预设。

### 3. 常见问题排查
> [!NOTE]
> **Play Protect / 手机管家安全提醒：** 社区重签名包会触发常规未上架提示，点击 **“了解详情 → 仍要安装”** 即可，构建工具完全开源于 [`tools/`](../tools/README.md)。

> [!TIP]
> **部分机型首次黑屏或 GPU 兼容微调：** 首次启动需要创建 Wine 运行环境（约 20–45 秒）。本版默认已启用 **`VirGL` + `WineD3D csmt=0`** 以大幅提升帧率并降低内存占用；若极少数机型出现画面兼容异常，可在启动等待页右上角点击 **`Engine Settings`** 切换至 `Vortek` 渲染驱动。
