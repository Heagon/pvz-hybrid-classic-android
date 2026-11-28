# 👥 Credits &amp; Sources · Đội Ngũ Thực Hiện · 致谢与来源

<p align="center">
  <a href="README.vi.md"><b>← [VI] Trang Chủ Tiếng Việt</b></a> &nbsp;•&nbsp;
  <a href="README.md"><b>← [EN] English Home</b></a> &nbsp;•&nbsp;
  <a href="README.cn.md"><b>← [CN] 返回中文主页</b></a> &nbsp;•&nbsp;
  <a href="CHANGELOG.md"><b>📋 Lịch Sử Build (CHANGELOG)</b></a>
</p>

<p align="center">
  <a href="#vi-bản-việt-hóa"><b>Jump to [VI] Tiếng Việt</b></a> &nbsp;|&nbsp;
  <a href="#en-english"><b>Jump to [EN] English</b></a> &nbsp;|&nbsp;
  <a href="#cn-简体中文"><b>Jump to [CN] 简体中文</b></a>
</p>

---

<a id="vi-bản-việt-hóa"></a>
## [VI] Bản Việt Hóa — Vinh Danh Tác Giả &amp; Nguồn Gốc Chính Thống

Bộ cài đặt đa ngôn ngữ **Plants vs. Zombies: Hybrid Classic (Android v3.20.1)** là dự án cộng đồng **100% miễn phí, không quảng cáo, phi thương mại**, giúp người chơi quốc tế &amp; Việt Nam dễ dàng trải nghiệm bản mod kinh điển trên điện thoại chỉ với 1 tệp APK.

### 1. Tác Giả &amp; Đội Ngũ Bản Mod Gốc (*植物大战僵尸杂交版经典版* / *PvZ Hybrid Classic*)
- **Tác giả, Thiết kế &amp; Lập trình chính:** **潜艇伟伟迷 (Qianting Weiweimi)**
  - **Kênh Bilibili chính thức:** [https://space.bilibili.com/97213827](https://space.bilibili.com/97213827)
  - **Trang chủ chính thức PvZ Hybrid:** [https://pvzhe.com](https://pvzhe.com)
- **Thành viên đóng góp &amp; tri ân trong game gốc:** **小小咩MS**, **AXH弦**, **一只吴铭仕哒**, **沉默寡言白河愁**
- **Phiên bản nguồn sử dụng:** *PvZ Hybrid Edition Classic v3.20.1* (bản gốc Windows &amp; gói tài nguyên HE).
- **Trò chơi &amp; Thương hiệu gốc:** *Plants vs. Zombies* là thương hiệu đã đăng ký thuộc quyền sở hữu của **Electronic Arts Inc. (EA) / PopCap Games**.

### 2. Dịch Thuật Đa Ngôn Ngữ (`[EN]` English &amp; `[VI]` Việt Hóa), Tối Ưu Hiệu Năng &amp; Đóng Gói Android
- **Thực hiện &amp; duy trì bởi:** **Heagon** ([https://github.com/Heagon/pvz-hybrid-classic-android](https://github.com/Heagon/pvz-hybrid-classic-android))
  - **Biên dịch hoàn chỉnh 100% (`[EN]` + `[VI]`):** Toàn bộ **3.309 chuỗi** văn bản trong `main.pak/properties/` (`LawnStrings`, `NewPlantStrings`, `NewZombieStrings`, `NewLawnStrings`, `NewLevelStrings`, `NewWisdomStrings`, `NewShopStrings`, `NewPropStrings`, `NewAcheesementsStrings`, kèm **437 mô tả Cây/Zombie/Tướng tinh gọn vừa khung**), và **1.038 chuỗi duy nhất (1.421 tham chiếu mã &amp; bảng con trỏ)** bên trong `PlantsVsZombies.exe`.
  - **Việt hóa &amp; Anh hóa Texture giao diện:** Vẽ lại **171 ảnh giao diện, bảng gỗ, bia đá, bìa sách chương, bản đồ Thời Không/Bí Cảnh, thanh tiến độ &amp; nút bấm** cho mỗi ngôn ngữ (`180` mục ghi đè vào `main.pak` tính cả 9 tệp `properties`), tích hợp font **PvZ2-VH Bold** đầy đủ dấu tiếng Việt sắc nét.
  - **Bản vá Engine UTF-8 (`gdi42.dll`), Tối Ưu Hiệu Năng (`OPT 1–13`) &amp; Vá Lỗi Ổn Định:** Vá `MultiByteToWideChar` (`CP936` → `CP_UTF8`) + bộ đệm Glyph Atlas O(1) trên `gdi42.dll`; nhúng đầy đủ Unicode/Tiếng Việt có dấu vào tất cả **6 font `.ttf`**; tối ưu bộ vẽ Direct3D (`Universal Sprite Atlas + 3072-vertex batcher`, `1-Quad Baked Seed-Card Atlas`, `HasSeedType` O(1) memo, chọn nóng **`30 / 60 / 90 / 120 FPS`** giữ nguyên tốc độ game `100.00 Hz`) cùng các bản vá nút `Menu` 1 chạm, `Tôi Là Zombie`, `Xem Bãi Cỏ`, chống crash `Hero`/`LAA`.
  - **Trình khởi chạy Android độc lập (`com.pvzh.cls`):** Kiến trúc hợp nhất Wine/Box64 standalone với `PvZBootstrapActivity`, thanh điều khiển nổi `PAD`, tối ưu **`VirGL` + `WineD3D` OpenGL FBO (`csmt=0`, `VideoMemorySize=512`)** + `GLXExtension` xuôi chiều (`flipY=false`), đánh số bản build `B.x.y` riêng biệt và khóa ký thống nhất giữ nguyên 100% save khi nâng cấp, đổi ngôn ngữ hoặc quay về bản build trước.

### 3. Công Cụ &amp; Thư Viện Mã Nguồn Mở
- **Nền tảng tương thích Windows-trên-Android:** [Winlator](https://github.com/brunodev85/winlator) (`Box64` · `Wine` · `WineD3D OpenGL` · `VirGL` · `Vortek`).
- **Biên dịch &amp; Đóng gói:** [MinGW-w64 / w64devkit](https://github.com/skeeto/w64devkit) · [fontTools](https://github.com/fonttools/fonttools) · [Pillow](https://python-pillow.org/) · [Liberation Fonts](https://github.com/liberationfonts/liberation-fonts) · [Apktool](https://apktool.org/) · [uber-apk-signer](https://github.com/patrickfav/uber-apk-signer) · [Zstandard (`zstd`)](https://github.com/facebook/zstd).
- **Tuyên bố bản quyền:** Mọi bản quyền *Plants vs. Zombies* thuộc **Electronic Arts Inc. (EA) / PopCap Games**; mọi bản quyền *植物大战僵尸杂交版经典版* thuộc **潜艇伟伟迷** và cộng sự. Dự án hoàn toàn miễn phí, không quảng cáo, phi thương mại; nghiêm cấm mua bán hoặc thu phí dưới mọi hình thức. Nếu chủ sở hữu bản quyền có yêu cầu gỡ bỏ hoặc chỉnh sửa, vui lòng mở Issue tại kho lưu trữ để được xử lý ngay.

---

<a id="en-english"></a>
## [EN] English — Full Credits &amp; Official Attribution

This unofficial standalone Android localization suite brings **Plants vs. Zombies: Hybrid Classic v3.20.1** to Android devices in English, Vietnamese, and original Chinese via a single zero-setup APK — **100% free, ad-free, and non-commercial**.

### 1. Original Mod Creator (*植物大战僵尸杂交版经典版* / *PvZ Hybrid Classic*)
- **Creator, Designer &amp; Lead Developer:** **Qianting Weiweimi (潜艇伟伟迷)**
  - **Official Bilibili Channel:** [https://space.bilibili.com/97213827](https://space.bilibili.com/97213827)
  - **Official PvZ Hybrid Website:** [https://pvzhe.com](https://pvzhe.com)
- **Upstream Contributors Credited In-Game:** **XiaoXiaoMieMS (小小咩MS)**, **AXH弦**, **WuMingShi (一只吴铭仕哒)**, **BaiHeChou (沉默寡言白河愁)**
- **Upstream Build:** *PvZ Hybrid Edition Classic v3.20.1*.
- **Original Franchise:** *Plants vs. Zombies* is a registered trademark of **Electronic Arts Inc. (EA) / PopCap Games**.

### 2. Complete `[EN]` + `[VI]` Localization, Engine Optimization &amp; Android Packaging
- **Maintained by:** **Heagon** ([https://github.com/Heagon/pvz-hybrid-classic-android](https://github.com/Heagon/pvz-hybrid-classic-android))
  - **100% Text &amp; Almanac Coverage:** Translated all **3,309 property strings** (`LawnStrings`, `NewPlantStrings`, `NewZombieStrings`, `NewLawnStrings`, `NewLevelStrings`, `NewWisdomStrings`, `NewShopStrings`, `NewPropStrings`, `NewAcheesementsStrings`, with **437 Almanac descriptions refitted** cleanly inside cards) plus **1,038 unique hardcoded strings (1,421 code &amp; pointer-table references)** inside `PlantsVsZombies.exe`.
  - **Localized Artwork:** Redrawn **171 UI textures, wood signs, gravestones, chapter book covers, Space-Time / Secret Realm map nodes, progress meters &amp; buttons** per language (`180` overridden `main.pak` assets including `9` properties files) using bold game typography (`PvZ2-VH Bold` &amp; custom vector-aligned lettering).
  - **Engine UTF-8 Shim, Performance (`OPT 1–13`) &amp; Stability Patches:** Binary-patched `gdi42.dll` (`CP936` GBK → `65001` `CP_UTF8` + O(1) Glyph Atlas), merged complete Latin Extended + Vietnamese diacritics via `fontTools` into all 6 runtime `.ttf` fonts, Direct3D sprite-atlas &amp; `3072`-vertex batching, 1-quad baked seed-card atlas, live **`30 / 60 / 90 / 120 FPS`** selector with exact `100.00 Hz` logic parity, plus 1-tap Menu/Shovel, I-Zombie, ViewLawn, Hero, and LAA crash fixes.
  - **Standalone Launcher (`com.pvzh.cls`):** Custom `PvZBootstrapActivity` shell embedding `Box64/Wine` + **`VirGL` &amp; `WineD3D` OpenGL FBO (`csmt=0`, `VideoMemorySize=512`)** + **`GLXExtension` upright `flipY=false` patch** + floating `PAD` touch/FPS controls + versioned `pvz_edition.txt` (`B.x.y`) + unified release keystore so upgrades, language switches, and rollbacks preserve 100% of saves.

### 3. Open-Source Projects &amp; Legal Notice
- **Compatibility Shell:** [Winlator](https://github.com/brunodev85/winlator) (`Box64` · `Wine` · `WineD3D OpenGL` · `VirGL` · `Vortek`).
- **Build &amp; Compiler Tooling:** [MinGW-w64 / w64devkit](https://github.com/skeeto/w64devkit) · [fontTools](https://github.com/fonttools/fonttools) · [Pillow](https://python-pillow.org/) · [Liberation Fonts](https://github.com/liberationfonts/liberation-fonts) · [Apktool](https://apktool.org/) · [uber-apk-signer](https://github.com/patrickfav/uber-apk-signer) · [Zstandard (`zstd`)](https://github.com/facebook/zstd).
- **Trademarks &amp; Copyright:** *Plants vs. Zombies* is a registered trademark of **Electronic Arts Inc. (EA) / PopCap Games**. All rights to *Plants vs. Zombies: Hybrid Classic* belong to **潜艇伟伟迷** and upstream contributors. This project is **100% free, non-commercial, and ad-free**; resale or monetization is strictly prohibited. Rightsholders may open an issue for prompt compliance or removal requests.

---

<a id="cn-简体中文"></a>
## [CN] 简体中文 — 制作名单与官方版权致谢

本仓库为**100% 免费、无广告、非商业**社区分享项目，旨在为全球玩家提供开箱即用的《植物大战僵尸杂交版经典版 v3.20.1》安卓独立整合包（内置简体中文原版、完整英文版与完整越南语版）。

### 1. 原版模组作者 (*植物大战僵尸杂交版经典版*)
- **模组创作、设计与主程序：** **潜艇伟伟迷**
  - **官方 Bilibili 主页：** [https://space.bilibili.com/97213827](https://space.bilibili.com/97213827)
  - **植物大战僵尸杂交版官方网站：** [https://pvzhe.com](https://pvzhe.com)
- **原版片头致谢成员：** **小小咩MS**、**AXH弦**、**一只吴铭仕哒**、**沉默寡言白河愁**
- **底层版本来源：** *植物大战僵尸杂交版经典版 v3.20.1*。
- **原作版权声明：** 《植物大战僵尸》（*Plants vs. Zombies*）商标及原作版权归 **Electronic Arts Inc. (EA) / PopCap Games** 所有。

### 2. 安卓独立整合包、性能优化与英/越本地化
- **开发与维护：** **Heagon** ([https://github.com/Heagon/pvz-hybrid-classic-android](https://github.com/Heagon/pvz-hybrid-classic-android))
  - **100% 双语本地化与图鉴排版优化：** 完整精翻 `main.pak/properties/` 内全部 **3,309 条**图鉴与关卡文本（含 **437 条植物/僵尸/英雄图鉴描述精简重排**），并补全 `PlantsVsZombies.exe` 硬编码的 **1,038 条独立词条（共 1,421 处引用）**。
  - **171 张界面贴图重绘：** 为英、越双语各重制 171 张界面、木牌、书皮、地图节点、进度条与按钮贴图（连同 9 个属性文件共替换 `main.pak` 内 180 项资源）。
  - **引擎级 UTF-8 补丁、性能优化 (`OPT 1–13`) 与稳定性修复：** 改造 `gdi42.dll` UTF-8 + O(1) 字形图集与 6 套 Unicode `.ttf` 字库；实现 Direct3D 精灵图集批处理、单四边形选卡缓存、`HasSeedType` O(1) 缓存、实时 **`30 / 60 / 90 / 120 FPS`** 帧率切换（保持 `100.00 Hz` 原速逻辑），以及单点菜单、我是僵尸、查看草坪与英雄/大内存防崩溃补丁。
  - **独立单包启动器 (`com.pvzh.cls`)：** 集成 `PvZBootstrapActivity`、`PAD` 悬浮控键与帧率切换栏、**`VirGL` + `WineD3D` OpenGL FBO (`csmt=0`) + `GLXExtension` 正向渲染补丁**、`B.x.y` 独立版本标识与统一发布密钥，支持跨语言与跨构建版本直接覆盖升级或回退且 100% 保留存档。

### 3. 致谢开源项目与免责声明
- **兼容层基础：** [Winlator](https://github.com/brunodev85/winlator) (`Box64` · `Wine` · `WineD3D OpenGL` · `VirGL` · `Vortek`)。
- **编译与构建工具链：** [MinGW-w64 / w64devkit](https://github.com/skeeto/w64devkit) · [fontTools](https://github.com/fonttools/fonttools) · [Pillow](https://python-pillow.org/) · [Liberation Fonts](https://github.com/liberationfonts/liberation-fonts) · [Apktool](https://apktool.org/) · [uber-apk-signer](https://github.com/patrickfav/uber-apk-signer) · [Zstandard](https://github.com/facebook/zstd)。
- **版权声明：** *Plants vs. Zombies* 商标及原作版权归 **Electronic Arts Inc. (EA) / PopCap Games** 所有；《植物大战僵尸杂交版经典版》版权归原作者**潜艇伟伟迷**所有。本项目纯属免费社区非营利分享，严禁任何商用倒卖或付费二次打包；如版权方有任何合规或下架需求，请在仓库提交 Issue，我们将第一时间配合处理。
