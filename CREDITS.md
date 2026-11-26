# 👥 Credits &amp; Sources · Đội Ngũ Thực Hiện · 致谢与来源

<p align="center">
  <a href="README.vi.md"><b>← [VI] Trang Chủ Tiếng Việt</b></a> &nbsp;•&nbsp;
  <a href="README.md"><b>← [EN] English Home</b></a> &nbsp;•&nbsp;
  <a href="README.cn.md"><b>← [CN] 返回中文主页</b></a>
</p>

<p align="center">
  <a href="#vi-bản-việt-hóa"><b>Jump to [VI] Tiếng Việt</b></a> &nbsp;|&nbsp;
  <a href="#en-english"><b>Jump to [EN] English</b></a> &nbsp;|&nbsp;
  <a href="#cn-简体中文"><b>Jump to [CN] 简体中文</b></a>
</p>

---

<a id="vi-bản-việt-hóa"></a>
## [VI] Bản Việt Hóa — Vinh Danh &amp; Nguồn Gốc Tài Nguyên

Bộ cài đặt đa ngôn ngữ **Plants vs. Zombies: Hybrid Classic (Android v3.20.1)** là dự án phi lợi nhuận giúp người chơi quốc tế &amp; Việt Nam dễ dàng trải nghiệm phiên bản kinh điển trên điện thoại chỉ với 1 tệp APK.

### 1. Đội Ngũ Tác Giả Game Gốc (*植物大战僵尸杂交版经典版* / *PvZ Hybrid Classic*)
- **Tác giả, Thiết kế &amp; Lập trình chính:** **潜艇伟伟迷 (Qianting Weiweimi)**
- **Thành viên đóng góp &amp; tri ân trên bản gốc:** **小小咩MS**, **AXH弦**, **一只吴铭仕哒**, **沉默寡言白河愁**
- **Phiên bản gốc sử dụng:** *PvZ Hybrid Edition Classic v3.20.1* (gốc Windows &amp; gói tài nguyên HE).

### 2. Dịch Thuật Đa Ngôn Ngữ (`[EN]` English &amp; `[VI]` Việt Hóa) &amp; Đóng Gói Android
- **Thực hiện &amp; duy trì bởi:** **Heagon** (https://github.com/Heagon/pvz-hybrid-classic-android)
  - **Biên dịch hoàn chỉnh 100% (`[EN]` + `[VI]`):** Toàn bộ **3.309 chuỗi** văn bản trong `main.pak/properties/` (`LawnStrings`, `NewPlantStrings`, `NewZombieStrings`, `NewLawnStrings`, `NewLevelStrings`, `NewWisdomStrings`, `NewShopStrings`, `NewPropStrings`, `NewAcheesementsStrings`), kèm **983 chuỗi duy nhất (1.342 tham chiếu mã &amp; bảng con trỏ)** cứng bên trong file thực thi `PlantsVsZombies.exe`.
  - **Việt hóa &amp; Anh hóa Texture giao diện:** Vẽ lại **121 ảnh giao diện, bảng gỗ, bia đá &amp; nút bấm** cho mỗi ngôn ngữ (`130` mục ghi đè vào `main.pak` tính cả 9 tệp `properties`), tích hợp font tiêu đề **PvZ2-VH Bold** đầy đủ dấu tiếng Việt sắc nét (khắc phục hoàn toàn lỗi ô vuông).
  - **Bản vá Engine UTF-8 (`gdi42.dll`):** Vá trực tiếp 4 điểm gọi `MultiByteToWideChar` từ mã trang `CP936` (GBK) sang `CP_UTF8` (`65001`), kết hợp nhúng đủ bộ ký tự Unicode/Tiếng Việt có dấu vào tất cả **6 font hệ thống** trong game (`fzcq`, `fzjz`, `fzkt`, `fzyh`, `wryh`, `wryh+pico12num`).
  - **Trình khởi chạy Android độc lập (`com.pvzh.cls`):** Đóng gói theo kiến trúc hợp nhất Wine/Box64 standalone với `PvZBootstrapActivity`, kết xuất qua **`WineD3D` OpenGL FBO (`renderer=gl`)** kèm bản vá **`GLXExtension` (`flipY=false`)** giúp hình ảnh hiển thị xuôi chiều 100%, tự động khởi tạo profile `Player`, đổi ngôn ngữ cài đè giữ nguyên 100% save bằng khóa ký thống nhất.

### 3. Công Cụ &amp; Thư Viện Mã Nguồn Mở
- **Nền tảng tương thích Windows-trên-Android:** [Winlator](https://github.com/brunodev85/winlator) (`Box64` · `Wine` · `WineD3D OpenGL` · `Vortek/VirGL`).
- **Thư viện Python &amp; Xử lý Font/Ảnh/APK:** [fontTools](https://github.com/fonttools/fonttools) · [Pillow](https://python-pillow.org/) · [Liberation Fonts](https://github.com/liberationfonts/liberation-fonts) · [Apktool](https://apktool.org/) · [uber-apk-signer](https://github.com/patrickfav/uber-apk-signer) · [Zstandard (`zstd`)](https://github.com/facebook/zstd).
- **Thương hiệu gốc:** *Plants vs. Zombies* là nhãn hiệu đã đăng ký của **Electronic Arts Inc. (EA) / PopCap Games**. Dự án hoàn toàn miễn phí, phi thương mại, không quảng cáo.

---

<a id="en-english"></a>
## [EN] English — Full Credits &amp; Attribution

This unofficial standalone Android localization suite brings **Plants vs. Zombies: Hybrid Classic v3.20.1** to Android devices in English, Vietnamese, and original Chinese via a single zero-setup APK.

### 1. Original Mod Creator (*植物大战僵尸杂交版经典版* / *PvZ Hybrid Classic*)
- **Creator &amp; Lead Developer:** **Qianting Weiweimi (潜艇伟伟迷)**
- **Upstream Contributors Credited In-Game:** **XiaoXiaoMieMS (小小咩MS)**, **AXH弦**, **WuMingShi (一只吴铭仕哒)**, **BaiHeChou (沉默寡言白河愁)**
- **Upstream Build:** *PvZ Hybrid Edition Classic v3.20.1*.

### 2. Complete `[EN]` + `[VI]` Localization, UTF-8 Engine Patch &amp; Android Packaging
- **Maintained by:** **Heagon** (https://github.com/Heagon/pvz-hybrid-classic-android)
  - **100% Text &amp; Almanac Coverage:** Translated all **3,309 property strings** (`LawnStrings`, `NewPlantStrings`, `NewZombieStrings`, `NewLawnStrings`, `NewLevelStrings`, `NewWisdomStrings`, `NewShopStrings`, `NewPropStrings`, `NewAcheesementsStrings`) plus **983 unique hardcoded strings (1,342 code &amp; pointer-table references)** inside `PlantsVsZombies.exe`.
  - **Localized Artwork:** Redrawn **121 UI textures, wood signs, gravestones &amp; buttons** per language (`130` overridden `main.pak` assets including `9` properties files) in English and Vietnamese using bold game typography (`PvZ2-VH Bold` &amp; custom vector-aligned lettering).
  - **Engine-Level UTF-8 Shim &amp; Unicode Fonts:** Binary-patched `gdi42.dll` (`CP936` GBK → `65001` `CP_UTF8` at all 4 `MultiByteToWideChar` call sites) and merged complete Latin Extended + Vietnamese diacritics via `fontTools` into all 6 runtime `.ttf` fonts.
  - **Standalone Launcher (`com.pvzh.cls`):** Custom `PvZBootstrapActivity` shell embedding `Box64/Wine` + **`WineD3D` OpenGL FBO (`renderer=gl`)** &amp; **`GLXExtension` upright `flipY=false` patch** + `pvz_edition.txt` edition stamping + pre-seeded `Player` profile + unified release keystore so language switching and updates never wipe saves.

### 3. Open-Source Projects &amp; Legal Notice
- **Compatibility Shell:** [Winlator](https://github.com/brunodev85/winlator) (`Box64` · `Wine` · `WineD3D OpenGL` · `Vortek`).
- **Build Tooling:** [fontTools](https://github.com/fonttools/fonttools) · [Pillow](https://python-pillow.org/) · [Liberation Fonts](https://github.com/liberationfonts/liberation-fonts) · [Apktool](https://apktool.org/) · [uber-apk-signer](https://github.com/patrickfav/uber-apk-signer) · [Zstandard (`zstd`)](https://github.com/facebook/zstd).
- **Trademarks:** *Plants vs. Zombies* is a registered trademark of **Electronic Arts Inc. (EA) / PopCap Games**. This project is 100% free, non-commercial, and ad-free. All original mod assets belong to **潜艇伟伟迷**.

---

<a id="cn-简体中文"></a>
## [CN] 简体中文 — 制作名单与版权致谢

本仓库旨在为全球玩家提供开箱即用的《植物大战僵尸杂交版经典版 v3.20.1》安卓独立整合包（内置简体中文原版、完整英文版与完整越南语版）。

### 1. 原版模组作者 (*植物大战僵尸杂交版经典版*)
- **模组创作与开发：** **潜艇伟伟迷**
- **原版片头致谢成员：** **小小咩MS**、**AXH弦**、**一只吴铭仕哒**、**沉默寡言白河愁**
- **底层版本来源：** *植物大战僵尸杂交版经典版 v3.20.1*。

### 2. 安卓独立整合包与英/越全文本本地化
- **开发与维护：** **Heagon** (https://github.com/Heagon/pvz-hybrid-classic-android)
  - **100% 双语本地化：** 完整精翻 `main.pak/properties/` 内全部 **3,309 条**图鉴与关卡文本，并补全 `PlantsVsZombies.exe` 硬编码的 **983 条独立词条（共 1,342 处代码与指针表引用）**。
  - **121 张界面贴图重绘：** 为英、越双语各重制 121 张主菜单牌匾、章节横幅、图鉴按钮及商店贴图（连同 9 个属性文件共替换 `main.pak` 内 130 项资源），彻底解决字库缺字问题。
  - **引擎级 UTF-8 补丁与 Unicode 字库：** 将 `gdi42.dll` 中 4 处 `MultiByteToWideChar` 从 `CP936` 改造为 `CP_UTF8 (65001)`，并用 `fontTools` 为游戏内置全部 6 套 `.ttf` 字体注入完整拉丁扩展与越南语声调字形。
  - **独立单包启动器 (`com.pvzh.cls`)：** 集成 `PvZBootstrapActivity` 自动初始化、**`WineD3D` OpenGL FBO (`renderer=gl`) + `GLXExtension` 正向渲染补丁 (`flipY=false`)**、预生成 `Player` 存档及 `pvz_edition.txt` 差异更新机制，配合统一发布密钥实现免配置、不断档的跨语言直接覆盖安装。

### 3. 致谢开源项目与免责声明
- **兼容层基础：** [Winlator](https://github.com/brunodev85/winlator) (`Box64` · `Wine` · `WineD3D OpenGL` · `Vortek`)。
- **构建工具链：** [fontTools](https://github.com/fonttools/fonttools) · [Pillow](https://python-pillow.org/) · [Liberation Fonts](https://github.com/liberationfonts/liberation-fonts) · [Apktool](https://apktool.org/) · [uber-apk-signer](https://github.com/patrickfav/uber-apk-signer) · [Zstandard](https://github.com/facebook/zstd)。
- **版权声明：** *Plants vs. Zombies* 商标及原作版权归 **Electronic Arts Inc. (EA) / PopCap Games** 所有；《杂交版经典版》版权与创作归属**潜艇伟伟迷**。本项目为纯免费社区非营利分享，严禁任何商用倒卖或广告二次打包。