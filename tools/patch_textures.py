"""Generate studio-quality localized UI textures for PvZ Hybrid Classic v3.20.1 ([EN] and [VI]),
preserving original stone/wood/icon art and rendering verification contact sheets."""
import math
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAK_DIR = os.path.join(ROOT, "work", "pak_extracted")
WORK = os.path.join(ROOT, "work")
SCRATCH = os.path.join(ROOT, "work", "preview_sheets")

# System & Unicode fonts supporting 100% English + full accented Vietnamese
FONT_BOLD = r"C:\Windows\Fonts\arialbd.ttf"
_PVZ2_FONT = os.path.join(ROOT, "tools", "PvZ2_VH_Bold.ttf")
FONT_BLACK = _PVZ2_FONT if os.path.exists(_PVZ2_FONT) else r"C:\Windows\Fonts\verdanab.ttf"
FONT_COMIC = r"C:\Windows\Fonts\comicbd.ttf" if os.path.exists(r"C:\Windows\Fonts\comicbd.ttf") else FONT_BOLD
FONT_TREB = r"C:\Windows\Fonts\trebucbd.ttf" if os.path.exists(r"C:\Windows\Fonts\trebucbd.ttf") else FONT_BOLD


def get_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, max(8, int(size)))


def fit_font(path: str, text: str, max_w: int, max_h: int, start_size: int, min_size: int = 9) -> ImageFont.FreeTypeFont:
    dummy = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    for sz in range(start_size, min_size - 1, -1):
        f = get_font(path, sz)
        bb = dummy.multiline_textbbox((0, 0), text, font=f, align="center", spacing=2)
        if (bb[2] - bb[0]) <= max_w and (bb[3] - bb[1]) <= max_h:
            return f
    return get_font(path, min_size)


def draw_outlined_text(
    canvas: Image.Image,
    center_xy: tuple[float, float],
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: tuple,
    outline: tuple = (0, 0, 0, 255),
    stroke_w: int = 3,
    glow: tuple | None = None,
    glow_radius: int = 5,
    angle: float = 0.0,
    shadow_offset: tuple[int, int] | None = (0, 2),
    spacing: int = 2,
):
    """Render crisp centered multiline text with optional outer glow, drop shadow, stroke, and rotation."""
    pad = 40
    dummy = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    bb = dummy.multiline_textbbox((0, 0), text, font=font, align="center", spacing=spacing, stroke_width=stroke_w)
    tw, th = int(math.ceil(max(1, bb[2] - bb[0]))), int(math.ceil(max(1, bb[3] - bb[1])))
    layer = Image.new("RGBA", (tw + pad * 2, th + pad * 2), (0, 0, 0, 0))
    tx = pad - bb[0]
    ty = pad - bb[1]

    if glow is not None:
        gl = Image.new("RGBA", layer.size, (0, 0, 0, 0))
        gd = ImageDraw.Draw(gl)
        gd.multiline_text((tx, ty), text, font=font, fill=glow, align="center", spacing=spacing, stroke_width=stroke_w + 2, stroke_fill=glow)
        gl = gl.filter(ImageFilter.GaussianBlur(glow_radius))
        layer.alpha_composite(gl)
        layer.alpha_composite(gl)

    d = ImageDraw.Draw(layer)
    if shadow_offset is not None:
        d.multiline_text(
            (tx + shadow_offset[0], ty + shadow_offset[1]),
            text,
            font=font,
            fill=(0, 0, 0, 190),
            align="center",
            spacing=spacing,
            stroke_width=stroke_w,
            stroke_fill=(0, 0, 0, 190),
        )

    d.multiline_text(
        (tx, ty),
        text,
        font=font,
        fill=fill,
        align="center",
        spacing=spacing,
        stroke_width=stroke_w,
        stroke_fill=outline,
    )

    if abs(angle) > 0.1:
        layer = layer.rotate(angle, resample=Image.BICUBIC, expand=True)

    px = int(round(center_xy[0] - layer.width / 2))
    py = int(round(center_xy[1] - layer.height / 2))
    canvas.alpha_composite(layer, (px, py))


def draw_carved_stone_text(
    canvas: Image.Image,
    center_xy: tuple[float, float],
    text: str,
    font: ImageFont.FreeTypeFont,
    angle: float = 0.0,
    highlight_mode: bool = False,
    spacing: int = 2,
):
    """Render authentic PvZ carved tombstone text (dark engraved groove + bottom-right stone rim highlight, or golden glow on hover)."""
    pad = 36
    dummy = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    bb = dummy.multiline_textbbox((0, 0), text, font=font, align="center", spacing=spacing, stroke_width=2)
    tw, th = int(math.ceil(max(1, bb[2] - bb[0]))), int(math.ceil(max(1, bb[3] - bb[1])))
    layer = Image.new("RGBA", (tw + pad * 2, th + pad * 2), (0, 0, 0, 0))
    tx, ty = pad - bb[0], pad - bb[1]
    d = ImageDraw.Draw(layer)

    if highlight_mode:
        gl = Image.new("RGBA", layer.size, (0, 0, 0, 0))
        gd = ImageDraw.Draw(gl)
        gd.multiline_text((tx, ty), text, font=font, fill=(255, 220, 90, 220), align="center", spacing=spacing, stroke_width=3, stroke_fill=(255, 160, 30, 200))
        gl = gl.filter(ImageFilter.GaussianBlur(4))
        layer.alpha_composite(gl)
        d = ImageDraw.Draw(layer)
        d.multiline_text((tx, ty + 1), text, font=font, fill=(30, 32, 40, 240), align="center", spacing=spacing, stroke_width=2, stroke_fill=(25, 28, 36, 240))
        d.multiline_text((tx, ty), text, font=font, fill=(255, 242, 175, 255), align="center", spacing=spacing, stroke_width=1, stroke_fill=(75, 55, 25, 235))
    else:
        # Bottom-right light rim of carved stone
        d.multiline_text((tx + 1, ty + 2), text, font=font, fill=(165, 172, 190, 175), align="center", spacing=spacing)
        # Top-left inner shadow groove
        d.multiline_text((tx - 1, ty - 1), text, font=font, fill=(24, 27, 36, 235), align="center", spacing=spacing)
        # Core carved dark slate
        d.multiline_text((tx, ty), text, font=font, fill=(40, 44, 58, 245), align="center", spacing=spacing)

    if abs(angle) > 0.1:
        layer = layer.rotate(angle, resample=Image.BICUBIC, expand=True)

    px = int(round(center_xy[0] - layer.width / 2))
    py = int(round(center_xy[1] - layer.height / 2))
    canvas.alpha_composite(layer, (px, py))


def heal_polygon(im: Image.Image, poly: list[tuple[int, int]], blur_r: int = 11, feather: int = 4, brighten: float = 1.0) -> Image.Image:
    """Erase carved/painted characters inside `poly` by replacing with smooth local surface tone + feathered seam."""
    out = im.copy()
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).polygon(poly, fill=255)
    soft_mask = mask.filter(ImageFilter.GaussianBlur(feather))

    # Build a clean background estimate by max-filtering slightly (lifts dark carved grooves back to surrounding stone/wood tone!)
    # followed by Gaussian smoothing, preserving original alpha!
    rgb = im.convert("RGB")
    lifted = rgb.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(blur_r))
    if abs(brighten - 1.0) > 0.01:
        lifted = lifted.point(lambda p: min(255, int(p * brighten)))
    patch = lifted.convert("RGBA")
    patch.putalpha(im.getchannel("A"))
    return Image.composite(patch, out, soft_mask)


def heal_dark_or_bright_in_poly(im: Image.Image, poly: list[tuple[int, int]], mode: str = "median", blur_r: int = 9, feather: int = 4) -> Image.Image:
    """Smooth surface inside `poly` using MedianFilter + GaussianBlur (ideal when text has both light & dark strokes)."""
    out = im.copy()
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).polygon(poly, fill=255)
    soft_mask = mask.filter(ImageFilter.GaussianBlur(feather))
    rgb = im.convert("RGB")
    smoothed = rgb.filter(ImageFilter.MedianFilter(9)).filter(ImageFilter.GaussianBlur(blur_r))
    patch = smoothed.convert("RGBA")
    patch.putalpha(im.getchannel("A"))
    return Image.composite(patch, out, soft_mask)


def heal_horizontal_band(im: Image.Image, x0: int, x1: int, y0: int, y1: int, sample_w: int = 8, feather: int = 3) -> Image.Image:
    """Erase text on a horizontal plank/banner by smoothly interpolating left/right clean margin strips row-by-row."""
    out = im.copy()
    px = out.load()
    for y in range(max(0, y0), min(im.height, y1)):
        ls = [px[x, y][:3] for x in range(max(0, x0 - sample_w), max(1, x0))]
        rs = [px[x, y][:3] for x in range(min(im.width - 1, x1), min(im.width, x1 + sample_w))]
        lc = tuple(sum(c[i] for c in ls) / len(ls) for i in range(3))
        rc = tuple(sum(c[i] for c in rs) / len(rs) for i in range(3))
        span = max(1, x1 - x0)
        for x in range(x0, x1):
            t = (x - x0) / span
            r = int(round(lc[0] * (1 - t) + rc[0] * t))
            g = int(round(lc[1] * (1 - t) + rc[1] * t))
            b = int(round(lc[2] * (1 - t) + rc[2] * t))
            a = px[x, y][3]
            px[x, y] = (r, g, b, a)
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).rectangle([x0 + feather, y0 + feather, x1 - feather, y1 - feather], fill=255)
    return Image.composite(out, im, mask.filter(ImageFilter.GaussianBlur(feather)))


def save_png(im: Image.Image, out_dir: str, rel_path: str):
    dest = os.path.join(out_dir, rel_path.replace("/", os.sep))
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    im.save(dest, "PNG")


def save_jpg(im: Image.Image, out_dir: str, rel_path: str, quality: int = 94):
    dest = os.path.join(out_dir, rel_path.replace("/", os.sep))
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    im.convert("RGB").save(dest, "JPEG", quality=quality)


def save_split_jpg_alpha(rgba: Image.Image, out_dir: str, jpg_rel: str, alpha_rel: str):
    """Save PopCap split RGB (.jpg on black) + grayscale alpha mask (_.png)."""
    black_bg = Image.new("RGBA", rgba.size, (0, 0, 0, 255))
    black_bg.alpha_composite(rgba)
    save_jpg(black_bg, out_dir, jpg_rel, quality=95)
    alpha_l = rgba.getchannel("A")
    alpha_rgb = Image.merge("RGB", (alpha_l, alpha_l, alpha_l))
    dest_a = os.path.join(out_dir, alpha_rel.replace("/", os.sep))
    os.makedirs(os.path.dirname(dest_a), exist_ok=True)
    alpha_rgb.save(dest_a, "PNG")


def load_src(rel_path: str) -> Image.Image:
    return Image.open(os.path.join(PAK_DIR, rel_path.replace("/", os.sep))).convert("RGBA")


def build_textures_for_lang(lang: str) -> list[str]:
    assert lang in ("en", "vi")
    is_en = lang == "en"
    out_dir = os.path.join(WORK, f"overrides_{lang}")
    generated = []

    # 1. PvZ_Logo.jpg + PvZ_Logo_.png (700x116)
    logo = Image.new("RGBA", (700, 116), (0, 0, 0, 0))
    f_main = fit_font(FONT_BLACK, "PLANTS vs. ZOMBIES", 660, 68, 52)
    draw_outlined_text(
        logo, (350, 42), "PLANTS vs. ZOMBIES", f_main,
        fill=(152, 238, 52, 255), outline=(18, 32, 8, 255), stroke_w=5,
        glow=(40, 90, 10, 180), glow_radius=4, shadow_offset=(0, 4),
    )
    sub_lbl = "HYBRID CLASSIC v3.20.1" if is_en else "BẢN LAI TẠO CLASSIC v3.20.1"
    f_sub = fit_font(FONT_BOLD, sub_lbl, 400, 32, 23)
    # Draw red-gold ribbon pill behind subtitle
    pill = Image.new("RGBA", (700, 116), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pill)
    pd.rounded_rectangle([140, 75, 560, 112], radius=14, fill=(175, 24, 24, 245), outline=(255, 215, 75, 255), width=3)
    logo.alpha_composite(pill)
    draw_outlined_text(
        logo, (350, 93), sub_lbl, f_sub,
        fill=(255, 238, 120, 255), outline=(45, 10, 10, 255), stroke_w=3, shadow_offset=(0, 2),
    )
    save_split_jpg_alpha(logo, out_dir, "images/PvZ_Logo.jpg", "images/PvZ_Logo_.png")
    generated.extend(["images/PvZ_Logo.jpg", "images/PvZ_Logo_.png"])

    # 2. ZombiesWon.jpg + ZombiesWon_.png (564x468)
    zw = Image.new("RGBA", (564, 468), (0, 0, 0, 0))
    zw_txt = "THE ZOMBIES\nATE YOUR\nBRAINS!" if is_en else "LŨ ZOMBIE\nĐÃ ĂN MẤT\nNÃO CỦA BẠN!"
    f_zw = fit_font(FONT_BLACK, zw_txt, 510, 400, 68)
    draw_outlined_text(
        zw, (282, 234), zw_txt, f_zw,
        fill=(145, 255, 55, 255), outline=(12, 35, 6, 255), stroke_w=6,
        glow=(70, 210, 20, 200), glow_radius=8, shadow_offset=(0, 5), spacing=14,
    )
    save_split_jpg_alpha(zw, out_dir, "reanim/ZombiesWon.jpg", "reanim/ZombiesWon_.png")
    generated.extend(["reanim/ZombiesWon.jpg", "reanim/ZombiesWon_.png"])

    # 3. Main Menu Tombstone Buttons (reanim/)
    tombstones = [
        (
            "reanim/SelectorScreen_StartAdventure_Button1.png",
            "reanim/SelectorScreen_StartAdventure_Highlight.png",
            [(26, 48), (305, 68), (298, 125), (22, 108)],
            (164, 88), -4.0,
            "START ADVENTURE" if is_en else "BẮT ĐẦU PHIÊU LƯU", 30,
        ),
        (
            "reanim/SelectorScreen_Adventure_button.png",
            "reanim/SelectorScreen_Adventure_highlight.png",
            [(24, 20), (306, 38), (300, 86), (20, 70)],
            (164, 53), -3.5,
            "ADVENTURE" if is_en else "PHIÊU LƯU", 34,
        ),
        (
            "reanim/SelectorScreen_Survival_button.png",
            "reanim/SelectorScreen_Survival_highlight.png",
            [(48, 58), (318, 42), (324, 134), (54, 148)],
            (185, 95), 3.5,
            "ADVENTURE" if is_en else "PHIÊU LƯU", 34,
        ),
        (
            "reanim/SelectorScreen_Challenges_button.png",
            "reanim/SelectorScreen_Challenges_highlight.png",
            [(22, 34), (290, 56), (282, 134), (16, 112)],
            (153, 84), -4.5,
            "CHALLENGES" if is_en else "THỬ THÁCH", 32,
        ),
        (
            "reanim/SelectorScreen_Vasebreaker_button.png",
            "reanim/SelectorScreen_vasebreaker_highlight.png",
            [(20, 32), (250, 54), (242, 128), (15, 106)],
            (133, 80), -5.0,
            "SURVIVAL" if is_en else "SINH TỒN", 31,
        ),
    ]
    for norm_rel, hi_rel, poly, cxy, ang, label, max_sz in tombstones:
        for rel, is_hi in [(norm_rel, False), (hi_rel, True)]:
            im = load_src(rel)
            healed = heal_polygon(im, poly, blur_r=9, feather=4)
            f = fit_font(FONT_BLACK, label, int((poly[1][0] - poly[0][0]) * 0.88), 54, max_sz)
            draw_carved_stone_text(healed, cxy, label, f, angle=ang, highlight_mode=is_hi)
            save_png(healed, out_dir, rel)
            generated.append(rel)

    # 4. SelectorScreen_WoodSign2.png + _press.png (291x71)
    wood_lbl = "Switch Player Profile!" if is_en else "Đổi Hồ Sơ Người Chơi!"
    for rel, is_press in [("reanim/SelectorScreen_WoodSign2.png", False), ("reanim/SelectorScreen_WoodSign2_press.png", True)]:
        im = load_src(rel)
        healed = heal_dark_or_bright_in_poly(im, [(20, 14), (272, 10), (274, 48), (22, 52)], blur_r=7, feather=4)
        f = fit_font(FONT_BOLD, wood_lbl, 240, 32, 20)
        fill = (255, 248, 175, 255) if is_press else (248, 236, 195, 255)
        draw_outlined_text(healed, (147, 30), wood_lbl, f, fill=fill, outline=(62, 36, 14, 245), stroke_w=2, angle=1.2, shadow_offset=(0, 1))
        save_png(healed, out_dir, rel)
        generated.append(rel)

    # 5. Bottom-right stone text buttons: Options / Help / Quit
    small_menu_btns = [
        ("images/SelectorScreen_Options1.png", "images/SelectorScreen_Options2.png", "Options" if is_en else "Cài đặt", 16),
        ("images/SelectorScreen_Help1.png", "images/SelectorScreen_Help2.png", "Help" if is_en else "Hỗ trợ", 13),
        ("images/SelectorScreen_Quit1.png", "images/SelectorScreen_Quit2.png", "Quit" if is_en else "Thoát", 14),
    ]
    for r1, r2, lbl, sz in small_menu_btns:
        for rel, is_hi in [(r1, False), (r2, True)]:
            src = load_src(rel)
            canvas = Image.new("RGBA", src.size, (0, 0, 0, 0))
            f = fit_font(FONT_BOLD, lbl, src.width - 4, src.height - 2, sz, min_size=8)
            if is_hi:
                draw_outlined_text(canvas, (src.width / 2, src.height / 2), lbl, f, fill=(255, 240, 120, 255), outline=(20, 24, 30, 255), stroke_w=2, shadow_offset=None)
            else:
                draw_outlined_text(canvas, (src.width / 2, src.height / 2), lbl, f, fill=(42, 46, 58, 255), outline=(150, 158, 175, 160), stroke_w=1, shadow_offset=None)
            save_png(canvas, out_dir, rel)
            generated.append(rel)

    # 6. Almanac Book / Store Key / Zen Garden Watering Can on Main Menu
    for rel, is_hi in [("images/SelectorScreen_Almanac.png", False), ("images/SelectorScreen_AlmanacHighlight.png", True)]:
        im = load_src(rel)
        healed = heal_polygon(im, [(22, 34), (78, 46), (68, 76), (14, 62)], blur_r=6, feather=3)
        lbl = "ALMANAC" if is_en else "SỔ TAY"
        f = fit_font(FONT_BOLD, lbl, 54, 22, 13, min_size=8)
        draw_outlined_text(healed, (46, 55), lbl, f, fill=(255, 245, 160, 255) if is_hi else (95, 58, 22, 255), outline=(255, 235, 185, 200) if not is_hi else (70, 40, 10, 240), stroke_w=1, angle=-14.0, shadow_offset=None)
        save_png(healed, out_dir, rel)
        generated.append(rel)

    for rel, is_hi in [("images/SelectorScreen_Store.png", False), ("images/SelectorScreen_StoreHighlight.png", True)]:
        im = load_src(rel)
        healed = heal_polygon(im, [(48, 8), (102, 22), (94, 42), (42, 28)], blur_r=5, feather=2)
        lbl = "SHOP"
        f = fit_font(FONT_BOLD, lbl, 48, 20, 13, min_size=8)
        draw_outlined_text(healed, (72, 25), lbl, f, fill=(165, 32, 24, 255), outline=(255, 245, 225, 220), stroke_w=1, angle=-15.0, shadow_offset=None)
        save_png(healed, out_dir, rel)
        generated.append(rel)

    for rel, is_hi in [("images/SelectorScreen_ZenGarden.png", False), ("images/SelectorScreen_ZenGardenHighlight.png", True)]:
        im = load_src(rel)
        healed = heal_dark_or_bright_in_poly(im, [(54, 62), (150, 62), (150, 144), (54, 144)], blur_r=9, feather=4)
        lbl = "ZEN\nGARDEN" if is_en else "VƯỜN\nTHIỀN"
        f = fit_font(FONT_BOLD, lbl, 84, 62, 18, min_size=9)
        draw_outlined_text(healed, (102, 104), lbl, f, fill=(255, 242, 140, 255), outline=(14, 52, 28, 255), stroke_w=2, shadow_offset=(0, 1), spacing=2)
        save_png(healed, out_dir, rel)
        generated.append(rel)

    # 7. Almanac_IndexBack.jpg (1080x600) & options_menuback.jpg (423x498)
    alm_bg = load_src("images/Almanac_IndexBack.jpg")
    alm_bg = heal_dark_or_bright_in_poly(alm_bg, [(238, 104), (838, 104), (838, 174), (238, 174)], blur_r=10, feather=5)
    alm_bg = heal_dark_or_bright_in_poly(alm_bg, [(500, 522), (600, 522), (600, 566), (500, 566)], blur_r=8, feather=4)
    free_txt = "100% Free Community Mod — Never Pay Scammers!" if is_en else "Bản Mod Miễn Phí 100% — Không Mua Bán Thu Phí!"
    f_free = fit_font(FONT_BOLD, free_txt, 560, 36, 21)
    draw_outlined_text(alm_bg, (540, 140), free_txt, f_free, fill=(255, 240, 185, 255), outline=(95, 38, 12, 255), stroke_w=3, shadow_offset=(0, 2))
    f_tag = get_font(FONT_BOLD, 14)
    draw_outlined_text(alm_bg, (548, 544), "PvZ Hybrid", f_tag, fill=(255, 245, 190, 255), outline=(60, 35, 10, 255), stroke_w=2, shadow_offset=None)
    save_jpg(alm_bg, out_dir, "images/Almanac_IndexBack.jpg", quality=95)
    generated.append("images/Almanac_IndexBack.jpg")

    opt_bg = load_src("images/options_menuback.jpg")
    opt_bg = heal_polygon(opt_bg, [(145, 58), (278, 58), (278, 102), (145, 102)], blur_r=8, feather=4)
    f_opt = fit_font(FONT_BLACK, "MENU", 120, 36, 26)
    draw_carved_stone_text(opt_bg, (212, 80), "MENU", f_opt)
    save_jpg(opt_bg, out_dir, "images/options_menuback.jpg", quality=95)
    generated.append("images/options_menuback.jpg")

    # 8. Battle Wave Banners: StartReady, StartSet, StartPlant, FinalWave
    wave_banners = [
        ("reanim/StartReady.png", "READY..." if is_en else "CHUẨN BỊ...", 46),
        ("reanim/StartSet.png", "SET..." if is_en else "ĐẶT CÂY...", 46),
        ("reanim/StartPlant.png", "PLANT!" if is_en else "TRỒNG!", 58),
        ("reanim/FinalWave.png", "FINAL WAVE!" if is_en else "ĐỢT CUỐI CÙNG!", 42),
    ]
    for rel, lbl, sz in wave_banners:
        src = load_src(rel)
        canvas = Image.new("RGBA", src.size, (0, 0, 0, 0))
        f = fit_font(FONT_BLACK, lbl, src.width - 16, src.height - 12, sz)
        draw_outlined_text(
            canvas, (src.width / 2, src.height / 2), lbl, f,
            fill=(235, 38, 26, 255), outline=(15, 6, 6, 255), stroke_w=5,
            glow=(90, 12, 8, 160), glow_radius=3, shadow_offset=(0, 3),
        )
        save_png(canvas, out_dir, rel)
        generated.append(rel)

    # 9. Pure-text Carved / Neon Pink Mode Buttons in new/ (MiniGame, PuzzleGame, HeroGame)
    neon_btns = [
        ("new/MiniGameButton.png", "new/MiniGameButton2.png", "MINI\nGAMES" if is_en else "MINI\nGAME", 28),
        ("new/PuzzleGame_Button1.png", "new/PuzzleGame_Button2.png", "PUZZLE" if is_en else "GIẢI ĐỐ", 24),
        ("new/HeroGame_Button1.png", "new/HeroGame_Button2.png", "HERO MODE" if is_en else "ANH HÙNG", 26),
    ]
    for r1, r2, lbl, sz in neon_btns:
        for rel, is_hi in [(r1, False), (r2, True)]:
            src = load_src(rel)
            canvas = Image.new("RGBA", src.size, (0, 0, 0, 0))
            f = fit_font(FONT_BLACK, lbl, src.width - 12, src.height - 12, sz)
            if is_hi:
                draw_outlined_text(
                    canvas, (src.width / 2, src.height / 2), lbl, f,
                    fill=(255, 240, 252, 255), outline=(195, 35, 130, 255), stroke_w=3,
                    glow=(255, 75, 185, 235), glow_radius=6, shadow_offset=None,
                )
            else:
                draw_outlined_text(
                    canvas, (src.width / 2, src.height / 2), lbl, f,
                    fill=(32, 36, 46, 235), outline=(165, 175, 190, 210), stroke_w=2, shadow_offset=None,
                )
            save_png(canvas, out_dir, rel)
            generated.append(rel)

    # 10. Icon-on-top + Bottom-text-band Buttons in new/
    # Format: (norm_rel, hi_rel, clear_y_start, label, font_sz, hi_pink_glow)
    bottom_band_btns = [
        ("new/CollectPlantButton.png", "new/CollectPlantButton2.png", 60, "REWARDS" if is_en else "THƯỞNG", 14, False),
        ("new/TreeOfWisdomCollectButton.png", "new/TreeOfWisdomCollectButton2.png", 60, "GIFTS" if is_en else "QUÀ TẶNG", 14, False),
        ("new/HybridTime_Button.png", "new/HybridTime_ButtonHight.png", 84, "RIFTS" if is_en else "THỜI KHÔNG", 14, False),
        ("new/MockBattle_Button.png", "new/MockBattle_Button_HighLight.png", 92, "SANDBOX" if is_en else "MÔ PHỎNG", 18, False),
        ("new/PlantFubenButton.png", "new/PlantFubenButton2.png", 102, "SKINS" if is_en else "TRANG PHỤC", 17, True),
        ("new/PropAlmanac_button.png", "new/PropAlmanac_button2.png", 66, "GEAR" if is_en else "TRANG BỊ", 16, False),
        ("new/TopChallengeButton.png", "new/TopChallengeButton2.png", 60, "APEX TRIAL" if is_en else "ĐỈNH CAO", 21, True),
        ("new/HeroChoice_Button.png", "new/HeroChoice_Button2.png", 0, "HEROES" if is_en else "CHỌN TƯỚNG", 22, True),
    ]
    for r1, r2, y0, lbl, sz, pink_hi in bottom_band_btns:
        for rel, is_hi in [(r1, False), (r2, True)]:
            im = load_src(rel)
            # Clear bottom text band cleanly
            clear_box = Image.new("RGBA", (im.width, im.height - y0), (0, 0, 0, 0))
            im.paste(clear_box, (0, y0))
            cy = 58 if "HeroChoice" in rel else (y0 + (im.height - y0) / 2)
            box_h = 36 if "HeroChoice" in rel else (im.height - y0 - 2)
            f = fit_font(FONT_BLACK, lbl, im.width - 6, box_h, sz, min_size=9)
            if is_hi and pink_hi:
                draw_outlined_text(
                    im, (im.width / 2, cy), lbl, f,
                    fill=(255, 245, 252, 255), outline=(185, 35, 125, 255), stroke_w=2,
                    glow=(255, 75, 185, 220), glow_radius=4, shadow_offset=None,
                )
            elif is_hi:
                draw_outlined_text(
                    im, (im.width / 2, cy), lbl, f,
                    fill=(255, 238, 120, 255), outline=(22, 18, 12, 255), stroke_w=3, shadow_offset=(0, 1),
                )
            else:
                draw_outlined_text(
                    im, (im.width / 2, cy), lbl, f,
                    fill=(250, 248, 240, 255), outline=(20, 22, 28, 255), stroke_w=3, shadow_offset=(0, 1),
                )
            save_png(im, out_dir, rel)
            generated.append(rel)

    # 11. Surface-inlaid Hybrid Buttons in new/
    # MoreGamesButton (97x94 tilted stone sign)
    for rel, is_hi in [("new/MoreGamesButton.png", False), ("new/MoreGamesButton2.png", True)]:
        im = load_src(rel)
        healed = heal_polygon(im, [(16, 20), (84, 8), (88, 72), (20, 82)], blur_r=7, feather=3)
        lbl = "MORE\nMODES" if is_en else "CHẾ ĐỘ\nKHÁC"
        f = fit_font(FONT_BLACK, lbl, 64, 52, 16, min_size=9)
        draw_carved_stone_text(healed, (52, 46), lbl, f, angle=9.0, highlight_mode=is_hi, spacing=1)
        save_png(healed, out_dir, rel)
        generated.append(rel)

    # MoreContent_Button (133x131 green watering can -> "BACKYARD" / "SÂN SAU")
    for rel, is_hi in [("new/MoreContent_Button.png", False), ("new/MoreContent_Button2.png", True)]:
        im = load_src(rel)
        healed = heal_dark_or_bright_in_poly(im, [(46, 86), (108, 86), (108, 118), (46, 118)], blur_r=6, feather=3)
        lbl = "BACKYARD" if is_en else "SÂN SAU"
        f = fit_font(FONT_BOLD, lbl, 58, 24, 12, min_size=8)
        draw_outlined_text(healed, (77, 102), lbl, f, fill=(255, 242, 140, 255) if is_hi else (245, 252, 245, 255), outline=(10, 48, 24, 255), stroke_w=2, shadow_offset=None)
        save_png(healed, out_dir, rel)
        generated.append(rel)

    # CollectPlantBackButton (76x118 money bag -> "GARDEN" / "VƯỜN")
    for rel, is_hi in [("new/CollectPlantBackButton.png", False), ("new/CollectPlantBackButton2.png", True)]:
        im = load_src(rel)
        healed = heal_dark_or_bright_in_poly(im, [(14, 64), (62, 64), (62, 108), (14, 108)], blur_r=6, feather=3)
        lbl = "BACK\nGARDEN" if is_en else "VỀ\nVƯỜN"
        f = fit_font(FONT_BOLD, lbl, 48, 40, 12, min_size=8)
        draw_outlined_text(healed, (38, 86), lbl, f, fill=(255, 240, 130, 255) if is_hi else (105, 65, 24, 255), outline=(255, 248, 225, 220) if not is_hi else (65, 35, 10, 240), stroke_w=1, shadow_offset=None, spacing=1)
        save_png(healed, out_dir, rel)
        generated.append(rel)

    # GameUpdataTip (92x40 wooden sign -> "NEWS" / "TIN MỚI")
    for rel, is_hi in [("new/GameUpdataTip.png", False), ("new/GameUpdataTip_HighLight.png", True)]:
        im = load_src(rel)
        healed = heal_dark_or_bright_in_poly(im, [(14, 10), (78, 10), (78, 34), (14, 34)], blur_r=5, feather=2)
        lbl = "NEWS" if is_en else "TIN MỚI"
        f = fit_font(FONT_BOLD, lbl, 60, 22, 14, min_size=9)
        draw_outlined_text(healed, (46, 22), lbl, f, fill=(255, 245, 140, 255) if is_hi else (245, 242, 230, 255), outline=(38, 30, 20, 255), stroke_w=2, shadow_offset=None)
        save_png(healed, out_dir, rel)
        generated.append(rel)

    # MockBattle_BackGround_Settings (156x42 brown button -> "START!" / "BẮT ĐẦU!")
    for rel, is_hi in [("new/MockBattle_BackGround_Settings.png", False), ("new/MockBattle_BackGround_Settings2.png", True)]:
        im = load_src(rel)
        healed = heal_dark_or_bright_in_poly(im, [(8, 6), (148, 6), (148, 36), (8, 36)], blur_r=7, feather=2)
        lbl = "READY / START!" if is_en else "HOÀN TẤT!"
        f = fit_font(FONT_BOLD, lbl, 134, 26, 17, min_size=10)
        draw_outlined_text(healed, (78, 21), lbl, f, fill=(255, 242, 145, 255) if is_hi else (255, 250, 240, 255), outline=(60, 24, 10, 255), stroke_w=2, shadow_offset=(0, 1))
        save_png(healed, out_dir, rel)
        generated.append(rel)

    # SeedCardAlmanac_Almanac (58x58 scroll -> "INFO" / "MÔ TẢ")
    for rel, is_hi in [("new/SeedCardAlmanac_Almanac.png", False), ("new/SeedCardAlmanac_Almanac2.png", True)]:
        im = load_src(rel)
        healed = heal_dark_or_bright_in_poly(im, [(10, 14), (48, 14), (48, 44), (10, 44)], blur_r=5, feather=2)
        lbl = "INFO" if is_en else "MÔ TẢ"
        f = fit_font(FONT_BOLD, lbl, 42, 22, 12, min_size=8)
        draw_outlined_text(healed, (29, 29), lbl, f, fill=(255, 245, 150, 255) if is_hi else (95, 52, 18, 255), outline=(60, 32, 10, 240) if is_hi else (255, 240, 200, 200), stroke_w=1, shadow_offset=None)
        save_png(healed, out_dir, rel)
        generated.append(rel)

    # ShopChallenge_button (121x126 red brain flag -> bottom label "SHOP TRIAL" / "ẢI SHOP")
    for rel, is_hi in [("new/ShopChallenge_button.png", False), ("new/ShopChallenge_button2.png", True)]:
        im = load_src(rel)
        px = im.load()
        clean_reds = []
        for y in range(70, 118):
            row_reds = [px[x, y][:3] for x in range(10, 118) if px[x, y][3] > 200 and px[x, y][0] > 125 and px[x, y][1] < 45 and px[x, y][2] < 45]
            clean_reds.append(row_reds)
        poly_mask = Image.new("L", im.size, 0)
        ImageDraw.Draw(poly_mask).polygon([(11, 72), (115, 68), (117, 112), (13, 116)], fill=255)
        pm = poly_mask.load()
        for y in range(70, 118):
            row_r = clean_reds[y - 70]
            avg_c = (
                (sum(c[0] for c in row_r) // len(row_r), sum(c[1] for c in row_r) // len(row_r), sum(c[2] for c in row_r) // len(row_r))
                if row_r else (190, 18, 22)
            )
            for x in range(10, 118):
                if pm[x, y] > 0 and px[x, y][3] > 100:
                    r, g, b, a = px[x, y]
                    if not (r > 125 and g < 45 and b < 45):
                        px[x, y] = (avg_c[0], avg_c[1], avg_c[2], a)
        healed = im
        lbl = "SHOP TRIAL" if is_en else "ẢI SHOP"
        f = fit_font(FONT_BOLD, lbl, 84, 24, 13, min_size=8)
        draw_outlined_text(healed, (66, 92), lbl, f, fill=(255, 245, 150, 255) if is_hi else (255, 248, 240, 255), outline=(95, 12, 12, 255), stroke_w=2, angle=6.0, shadow_offset=None)
        save_png(healed, out_dir, rel)
        generated.append(rel)

    # StarsExchange_Button (164x35 star + yellow text -> keep x<34 star, redraw text on x>=34)
    for rel, is_hi in [("new/StarsExchange_Button.png", False), ("new/StarsExchange_Button2.png", True)]:
        im = load_src(rel)
        clear_box = Image.new("RGBA", (im.width - 34, im.height), (0, 0, 0, 0))
        im.paste(clear_box, (34, 0))
        lbl = "STAR SHOP" if is_en else "ĐỔI SAO"
        f = fit_font(FONT_BLACK, lbl, 124, 28, 20, min_size=11)
        draw_outlined_text(
            im, (98, 18), lbl, f,
            fill=(255, 245, 130, 255) if is_hi else (255, 215, 45, 255),
            outline=(45, 28, 8, 255), stroke_w=3,
            glow=(255, 200, 40, 180) if is_hi else None, glow_radius=3, shadow_offset=(0, 1),
        )
        save_png(im, out_dir, rel)
        generated.append(rel)

    # TreeOfWisdomButton (137x154 bonsai pot -> label on pot plaque)
    for rel, is_hi in [("new/TreeOfWisdomButton.png", False), ("new/TreeOfWisdomButton2.png", True)]:
        im = load_src(rel)
        healed = heal_dark_or_bright_in_poly(im, [(20, 102), (116, 100), (116, 142), (20, 144)], blur_r=7, feather=3)
        lbl = "WISDOM" if is_en else "TRÍ TUỆ"
        f = fit_font(FONT_BOLD, lbl, 82, 26, 16, min_size=9)
        draw_outlined_text(healed, (68, 122), lbl, f, fill=(255, 245, 150, 255) if is_hi else (248, 238, 205, 255), outline=(58, 34, 14, 255), stroke_w=2, shadow_offset=None)
        save_png(healed, out_dir, rel)
        generated.append(rel)

    # 12. Remaining Main Menu, Adventure, Hero, Almanac & Shop UI Textures
    ws1 = load_src("reanim/SelectorScreen_WoodSign1.png")
    ws1 = heal_dark_or_bright_in_poly(ws1, [(62, 72), (235, 72), (235, 97), (62, 97)], blur_r=6, feather=3)
    ws1_lbl = "WELCOME BACK!" if is_en else "CHÀO MỪNG TRỞ LẠI!"
    f_ws1 = fit_font(FONT_BOLD, ws1_lbl, 176, 20, 14, min_size=8)
    draw_outlined_text(ws1, (148, 84), ws1_lbl, f_ws1, fill=(235, 245, 165, 255), outline=(52, 30, 10, 245), stroke_w=2, shadow_offset=None)
    save_png(ws1, out_dir, "reanim/SelectorScreen_WoodSign1.png")
    generated.append("reanim/SelectorScreen_WoodSign1.png")

    ws3 = load_src("reanim/SelectorScreen_WoodSign3.png")
    ws3 = heal_dark_or_bright_in_poly(ws3, [(14, 4), (170, 8), (168, 56), (12, 52)], blur_r=7, feather=3)
    ws3 = heal_dark_or_bright_in_poly(ws3, [(30, 66), (156, 70), (154, 114), (28, 110)], blur_r=7, feather=3)
    ws3 = heal_dark_or_bright_in_poly(ws3, [(116, 124), (238, 144), (230, 192), (112, 172)], blur_r=7, feather=3)
    p1_lbl = "CREDITS:\nWeiweimi & XiaoMie" if is_en else "ĐỘI NGŨ:\nWeiweimi & XiaoMie"
    f_p1 = fit_font(FONT_BOLD, p1_lbl, 138, 38, 13, min_size=8)
    draw_outlined_text(ws3, (92, 30), p1_lbl, f_p1, fill=(255, 240, 165, 255), outline=(54, 30, 10, 245), stroke_w=2, angle=-4.0, shadow_offset=None, spacing=1)
    p2_lbl = "AXH · WuMingShi"
    f_p2 = fit_font(FONT_BOLD, p2_lbl, 112, 30, 13, min_size=8)
    draw_outlined_text(ws3, (93, 90), p2_lbl, f_p2, fill=(255, 232, 195, 255), outline=(54, 30, 10, 245), stroke_w=2, angle=-8.0, shadow_offset=None)
    p3_lbl = "THANKS:\nBaiHeChou" if is_en else "CẢM ƠN:\nBaiHeChou"
    f_p3 = fit_font(FONT_BOLD, p3_lbl, 104, 36, 13, min_size=8)
    draw_outlined_text(ws3, (176, 158), p3_lbl, f_p3, fill=(185, 248, 225, 255), outline=(38, 26, 14, 245), stroke_w=2, angle=-22.0, shadow_offset=None, spacing=1)
    save_png(ws3, out_dir, "reanim/SelectorScreen_WoodSign3.png")
    generated.append("reanim/SelectorScreen_WoodSign3.png")

    for rel, is_press in [
        ("NewAcheesements/Achievements_pedestal.png", False),
        ("NewAcheesements/Achievements_pedestal_press.png", True),
    ]:
        im = load_src(rel)
        healed = heal_polygon(im, [(36, 106), (112, 92), (118, 146), (42, 160)], blur_r=8, feather=3)
        lbl = "TROPHIES" if is_en else "THÀNH TỰU"
        f = fit_font(FONT_BLACK, lbl, 68, 28, 14, min_size=8)
        draw_carved_stone_text(healed, (75, 127), lbl, f, angle=14.0, highlight_mode=is_press)
        save_png(healed, out_dir, rel)
        generated.append(rel)

    for rel, is_hi, has_new in [
        ("new/update_icon1.png", False, False),
        ("new/update_icon2.png", True, False),
        ("new/update_icon3.png", False, True),
        ("new/update_icon4.png", True, True),
    ]:
        im = load_src(rel)
        healed = heal_dark_or_bright_in_poly(im, [(4, 14), (96, 26), (92, 54), (2, 42)], blur_r=6, feather=3)
        if has_new:
            healed = heal_dark_or_bright_in_poly(healed, [(86, 14), (123, 18), (120, 52), (84, 48)], blur_r=5, feather=2)
        lbl = "UPDATES" if is_en else "CẬP NHẬT"
        f = fit_font(FONT_BOLD, lbl, 76, 22, 13, min_size=8)
        draw_outlined_text(
            healed, (49, 34), lbl, f,
            fill=(255, 245, 145, 255) if is_hi else (248, 244, 232, 255),
            outline=(45, 28, 14, 255), stroke_w=2, angle=-14.0, shadow_offset=None,
        )
        if has_new:
            n_lbl = "NEW!" if is_en else "MỚI!"
            fn = fit_font(FONT_BLACK, n_lbl, 34, 20, 13, min_size=8)
            draw_outlined_text(
                healed, (104, 34), n_lbl, fn,
                fill=(255, 238, 95, 255), outline=(170, 20, 12, 255), stroke_w=2, angle=-12.0, shadow_offset=None,
            )
        save_png(healed, out_dir, rel)
        generated.append(rel)

    mc = load_src("new/More content.png")
    mc = heal_polygon(mc, [(16, 20), (84, 8), (88, 72), (20, 82)], blur_r=7, feather=3)
    mc_lbl = "MORE\nMODES" if is_en else "CHẾ ĐỘ\nKHÁC"
    f_mc = fit_font(FONT_BLACK, mc_lbl, 64, 52, 16, min_size=9)
    draw_carved_stone_text(mc, (52, 46), mc_lbl, f_mc, angle=9.0, highlight_mode=False, spacing=1)
    save_png(mc, out_dir, "new/More content.png")
    generated.append("new/More content.png")

    for rel, is_hi in [
        ("Hero/Level_up_button.png", False),
        ("Hero/Level_up_buttonHighlight.png", True),
        ("newshop/Hero/Level_up_button.png", False),
        ("newshop/Hero/Level_up_buttonHighlight.png", True),
    ]:
        im = load_src(rel)
        healed = heal_dark_or_bright_in_poly(im, [(5, 5), (64, 5), (64, 28), (5, 28)], blur_r=6, feather=2)
        lbl = "UPGRADE" if is_en else "NÂNG CẤP"
        f = fit_font(FONT_BOLD, lbl, 58, 20, 12, min_size=8)
        draw_outlined_text(
            healed, (34.5, 16.5), lbl, f,
            fill=(255, 245, 150, 255) if is_hi else (255, 248, 230, 255),
            outline=(58, 28, 8, 255), stroke_w=2, shadow_offset=None,
        )
        save_png(healed, out_dir, rel)
        generated.append(rel)

    chapter_titles = {
        "NewAdventure/chapter_background.png": ("CHAPTERS", "CHỌN CHƯƠNG"),
        "NewAdventure/chapter_background1.png": ("FRONT YARD", "SÂN TRƯỚC"),
        "NewAdventure/chapter_background2.png": ("POOL DEFENSE", "HỒ BƠI"),
        "NewAdventure/chapter_background3.png": ("ROOF BATTLE", "MÁI NHÀ"),
        "NewAdventure/chapter_background4.png": ("JOURNEY'S START", "KHỞI HÀNH"),
        "NewAdventure/chapter_background5.png": ("VALLEY CROSSING", "VƯỢT THUNG LŨNG"),
        "NewAdventure/chapter_background6.png": ("FOUR SEAS", "VƯỢT TỨ HẢI"),
        "NewAdventure/chapter_background7.png": ("VILLAGE TALE", "THĂM LÀNG CỔ"),
        "NewAdventure/chapter_background8.png": ("JOURNEY'S END", "HỒI KẾT"),
        "NewAdventure/chapter_background9.png": ("HIDDEN CHAPTERS", "NGOẠI TRUYỆN"),
        "NewAdventure/chapter_background9_1.png": ("BARREN LANDS", "ĐẤT HOANG"),
        "NewAdventure/chapter_background9_2.png": ("COOL SUMMER", "HÈ MÁT LÀNH"),
        "NewAdventure/chapter_background9_3.png": ("TRI-KINGDOMS", "THẾ CHÂN VẠC"),
        "NewAdventure/chapter_background9_4.png": ("SLEEPLESS NIGHT", "ĐÊM KHÔNG NGỦ"),
        "NewAdventure/chapter_background9_5.png": ("SHOP GUARD", "BẢO VỆ TIỆM"),
        "NewAdventure/chapter_background9_6.png": ("FLOWING CREEK", "SUỐI CHẢY"),
        "NewAdventure/chapter_background9_7.png": ("NIGHT PARADE", "BÁCH QUỶ DẠ HÀNH"),
        "NewAdventure/chapter_background9_8.png": ("HARBOR WATCH", "CẢNH BẾN CẢNG"),
    }
    for rel, (en_t, vi_t) in chapter_titles.items():
        im = load_src(rel)
        healed = heal_horizontal_band(im, 64, 316, 66, 108, sample_w=8, feather=1)
        lbl = en_t if is_en else vi_t
        f = fit_font(FONT_BLACK, lbl, 228, 34, 22, min_size=11)
        draw_outlined_text(
            healed, (190, 88), lbl, f,
            fill=(255, 248, 225, 255), outline=(52, 28, 10, 255), stroke_w=3, shadow_offset=(0, 2),
        )
        save_png(healed, out_dir, rel)
        generated.append(rel)

    for rel, is_hi in [
        ("NewAdventure/chapter_button_reset.png", False),
        ("NewAdventure/chapter_button_reset_Highlignt.png", True),
    ]:
        im = load_src(rel)
        healed = heal_dark_or_bright_in_poly(im, [(5, 22), (67, 22), (67, 46), (5, 46)], blur_r=6, feather=2)
        lbl = "RESET" if is_en else "ĐẶT LẠI"
        f = fit_font(FONT_BOLD, lbl, 58, 20, 13, min_size=8)
        draw_outlined_text(
            healed, (36, 34), lbl, f,
            fill=(255, 242, 140, 255) if is_hi else (250, 252, 255, 255),
            outline=(18, 24, 38, 255), stroke_w=2, shadow_offset=None,
        )
        save_png(healed, out_dir, rel)
        generated.append(rel)

    ch_bg = load_src("new/Card_Holder_BG.png")
    ch_bg = heal_horizontal_band(ch_bg, 260, 600, 99, 157, sample_w=10, feather=1)
    ch_lbl = "SELECT DECK" if is_en else "CHỌN BỘ THẺ"
    f_ch = fit_font(FONT_BLACK, ch_lbl, 270, 36, 24, min_size=12)
    draw_outlined_text(
        ch_bg, (429, 128), ch_lbl, f_ch,
        fill=(255, 245, 205, 255), outline=(58, 28, 10, 255), stroke_w=3, shadow_offset=(0, 2),
    )
    save_png(ch_bg, out_dir, "new/Card_Holder_BG.png")
    generated.append("new/Card_Holder_BG.png")

    for rel in [
        "new/Coin_ExperimentalLogNote00.png",
        "new/Coin_ExperimentalLogNote01.png",
        "new/Coin_ExperimentalLogNote02.png",
    ]:
        im = load_src(rel)
        healed = heal_dark_or_bright_in_poly(im, [(6, 52), (99, 52), (99, 64), (6, 64)], blur_r=5, feather=2)
        clear_bot = Image.new("RGBA", (healed.width, healed.height - 60), (0, 0, 0, 0))
        healed.paste(clear_bot, (0, 60))
        lbl = "LAB LOG" if is_en else "NHẬT KÝ"
        f = fit_font(FONT_BLACK, lbl, 92, 26, 15, min_size=9)
        draw_outlined_text(
            healed, (52, 74), lbl, f,
            fill=(252, 250, 245, 255), outline=(14, 14, 18, 255), stroke_w=3, shadow_offset=None,
        )
        save_png(healed, out_dir, rel)
        generated.append(rel)

    alm_ic = load_src("images/Almanac.png")
    alm_ic = heal_dark_or_bright_in_poly(alm_ic, [(20, 32), (58, 32), (58, 62), (20, 62)], blur_r=6, feather=3)
    alm_lbl = "ALMANAC" if is_en else "SỔ TAY"
    f_alm = fit_font(FONT_BOLD, alm_lbl, 40, 22, 10, min_size=8)
    draw_outlined_text(
        alm_ic, (39, 47), alm_lbl, f_alm,
        fill=(88, 52, 18, 255), outline=(245, 228, 180, 190), stroke_w=1, shadow_offset=None,
    )
    save_png(alm_ic, out_dir, "images/Almanac.png")
    generated.append("images/Almanac.png")

    for rel, is_hi in [("images/zenshopbutton.png", False), ("images/zenshopbutton_highlight.png", True)]:
        im = load_src(rel)
        healed = heal_dark_or_bright_in_poly(im, [(44, 6), (103, 6), (103, 36), (44, 36)], blur_r=6, feather=2)
        lbl = "SHOP" if is_en else "TIỆM"
        f = fit_font(FONT_BOLD, lbl, 54, 22, 15, min_size=9)
        draw_outlined_text(
            healed, (74, 21), lbl, f,
            fill=(185, 42, 20, 255) if is_hi else (95, 38, 14, 255),
            outline=(255, 245, 210, 220), stroke_w=1, shadow_offset=None,
        )
        save_png(healed, out_dir, rel)
        generated.append(rel)

    store_nav_btns = [
        ("images/Store_NextButton.png", False, False, [(22, 8), (122, 8), (122, 38), (22, 38)], (72, 23), 86, 24, "NEXT" if is_en else "TIẾP"),
        ("images/Store_NextButtonDisabled.png", False, True, [(22, 8), (122, 8), (122, 38), (22, 38)], (72, 23), 86, 24, "NEXT" if is_en else "TIẾP"),
        ("images/Store_NextButtonHighlight.png", True, False, [(22, 8), (122, 8), (122, 38), (22, 38)], (72, 23), 86, 24, "NEXT" if is_en else "TIẾP"),
        ("images/Store_PrevButton.png", False, False, [(14, 8), (88, 8), (88, 36), (14, 36)], (51, 22), 68, 22, "PREV" if is_en else "TRƯỚC"),
        ("images/Store_PrevButtonDisabled.png", False, True, [(14, 8), (88, 8), (88, 36), (14, 36)], (51, 22), 68, 22, "PREV" if is_en else "TRƯỚC"),
        ("images/Store_PrevButtonHighlight.png", True, False, [(14, 8), (88, 8), (88, 36), (14, 36)], (51, 22), 68, 22, "PREV" if is_en else "TRƯỚC"),
    ]
    for rel, is_hi, is_dis, poly, cxy, mw, mh, lbl in store_nav_btns:
        im = load_src(rel)
        healed = heal_dark_or_bright_in_poly(im, poly, blur_r=7, feather=3)
        f = fit_font(FONT_BLACK, lbl, mw, mh, 16, min_size=9)
        if is_dis:
            fill, outl = (165, 155, 160, 175), (75, 22, 24, 175)
        elif is_hi:
            fill, outl = (255, 248, 170, 255), (120, 18, 16, 255)
        else:
            fill, outl = (242, 236, 236, 235), (110, 18, 18, 245)
        draw_outlined_text(healed, cxy, lbl, f, fill=fill, outline=outl, stroke_w=2, shadow_offset=None)
        save_png(healed, out_dir, rel)
        generated.append(rel)

    st_sign = load_src("images/Store_Sign.png")
    st_sign = heal_dark_or_bright_in_poly(st_sign, [(76, 14), (450, 14), (450, 108), (76, 108)], blur_r=11, feather=5)
    st_lbl = "WEIWEIMI'S\nHYBRID SHOP" if is_en else "TIỆM TẠP HÓA\nLAI TẠO"
    f_st = fit_font(FONT_BLACK, st_lbl, 355, 82, 28, min_size=14)
    draw_outlined_text(
        st_sign, (260, 61), st_lbl, f_st,
        fill=(255, 236, 145, 255), outline=(52, 26, 8, 255), stroke_w=4, shadow_offset=(0, 3), spacing=4,
    )
    save_png(st_sign, out_dir, "images/Store_Sign.png")
    generated.append("images/Store_Sign.png")

    # 12. FlagMeterLevelProgress.png (86x11)
    fm = load_src("images/FlagMeterLevelProgress.png")
    fm_rgb = fm.convert("RGB")
    bar_crop = fm_rgb.crop((5, 2, 81, 9)).filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(1))
    fm_rgb.paste(bar_crop, (5, 2))
    fm = fm_rgb.convert("RGBA")
    fm.putalpha(load_src("images/FlagMeterLevelProgress.png").getchannel("A"))
    fm_lbl = "PROGRESS" if is_en else "TIẾN ĐỘ"
    f_fm = ImageFont.truetype(FONT_BOLD, 7)
    d_fm = ImageDraw.Draw(fm)
    d_fm.text((43, 5), fm_lbl, font=f_fm, fill=(18, 22, 65, 255), anchor="mm")
    save_png(fm, out_dir, "images/FlagMeterLevelProgress.png")
    generated.append("images/FlagMeterLevelProgress.png")

    # 13. new/Icon_Bilibili*.png & Icon_Douyin*.png (171x54)
    for rel, lbl, is_hi in [
        ("new/Icon_Bilibili.png", "BILIBILI", False),
        ("new/Icon_Bilibili_bright.png", "BILIBILI", True),
        ("new/Icon_Douyin.png", "DOUYIN", False),
        ("new/Icon_Douyin_bright.png", "DOUYIN", True),
    ]:
        im = load_src(rel)
        healed = heal_dark_or_bright_in_poly(im, [(32, 9), (139, 9), (139, 45), (32, 45)], blur_r=8, feather=3)
        f_soc = fit_font(FONT_BLACK, lbl, 118, 30, 22, min_size=12)
        draw_outlined_text(
            healed, (85, 27), lbl, f_soc,
            fill=(255, 255, 255, 255),
            outline=(38, 52, 132, 255),
            stroke_w=2,
            glow=(95, 135, 255, 210) if is_hi else (45, 65, 165, 140),
            glow_radius=4 if is_hi else 2,
            shadow_offset=None,
        )
        save_png(healed, out_dir, rel)
        generated.append(rel)

    # 14. images/ZombieNote.jpg (964x427: Help hotkeys left + Credits header top-right)
    zn = load_src("images/ZombieNote.jpg")
    zn_rgb = zn.convert("RGB")
    zn_src_rgb = zn_rgb.copy()
    # Build clean warm-parchment fill via Row-wise 90th-percentile brightness so ALL dark/colored ink disappears completely without black edge bleed
    for box in [(35, 32, 496, 396), (512, 24, 918, 146)]:
        c = zn_src_rgb.crop(box)
        healed_c = c.filter(ImageFilter.MaxFilter(17)).filter(ImageFilter.GaussianBlur(6))
        zn_rgb.paste(healed_c, box[:2])
    # Also clean small lingering "!" bottom-center around (460..500, 360..405) inside parchment
    zn_rgb.paste(zn_src_rgb.crop((440, 358, 502, 404)).filter(ImageFilter.MaxFilter(11)).filter(ImageFilter.GaussianBlur(4)), (440, 358))
    zn = zn_rgb.convert("RGBA")
    dz = ImageDraw.Draw(zn)
    f_h_title = get_font(FONT_BLACK, 24)
    f_h_key = get_font(FONT_BLACK, 18)
    f_h_txt = get_font(FONT_BOLD, 17)
    dz.text((135, 64), "GAME HOTKEYS" if is_en else "PHÍM TẮT", font=f_h_title, fill=(24, 22, 18), anchor="mm")
    hotkeys = [
        ("1", "→ Shovel" if is_en else "→ Dùng Xẻng", 82, 128),
        ("2", "→ Zombie HP" if is_en else "→ Máu Zombie", 272, 128),
        ("3", "→ Pin Slots" if is_en else "→ Ghim khay thẻ", 82, 182),
        ("4", "→ Plant HP" if is_en else "→ Máu Cây", 272, 182),
        ("5", "→ Speed Boost" if is_en else "→ Tăng tốc", 82, 236),
        ("6", "→ Use Item" if is_en else "→ Đạo cụ", 272, 236),
        ("7", "→ Time Slow" if is_en else "→ Làm chậm", 82, 290),
    ]
    for kch, desc, hx, hy in hotkeys:
        dz.text((hx, hy), kch, font=f_h_key, fill=(215, 24, 20), anchor="lm")
        dz.text((hx + 15, hy), desc, font=f_h_txt, fill=(25, 22, 18), anchor="lm")
    dz.text((82, 342), "ESC", font=f_h_key, fill=(24, 52, 225), anchor="lm")
    dz.text((124, 342), "→ Main Menu" if is_en else "→ Menu Chính", font=f_h_txt, fill=(25, 22, 18), anchor="lm")
    dz.text((262, 342), "SPACE", font=f_h_key, fill=(24, 52, 225), anchor="lm")
    dz.text((330, 342), "→ Pause" if is_en else "→ Tạm dừng", font=f_h_txt, fill=(25, 22, 18), anchor="lm")
    cap_p1 = "No response? Turn on " if is_en else "Không bấm được? Bật "
    cap_p2 = "CAPS LOCK!" if is_en else "CAPS LOCK!"
    w1 = dz.textlength(cap_p1, font=f_h_txt)
    w2 = dz.textlength(cap_p2, font=f_h_txt)
    cx0 = 260 - (w1 + w2) / 2
    dz.text((cx0, 386), cap_p1, font=f_h_txt, fill=(25, 22, 18), anchor="lm")
    dz.text((cx0 + w1, 386), cap_p2, font=f_h_txt, fill=(210, 24, 20), anchor="lm")
    f_cred = ImageFont.truetype(FONT_BOLD, 12)
    cred_lines = (
        [
            "Credits (PvZ Hybrid Mod)",
            "Lead Design: Qianting Weiweimi | Art: Weiweimi, Wumingshi",
            "Code: XiaoxiaomieMS | Community/Tech: AXH Xuan, Lingshazhu",
            "Trailer: Shitu | Manager: COOL | QA Lead: Tongyan",
            "Special Thanks:",
        ]
        if is_en else
        [
            "Nhóm Tác Giả (PvZ Hybrid Mod)",
            "Thiết kế chính: Qianting Weiweimi | Mỹ thuật: Weiweimi, Wumingshi",
            "Lập trình: XiaoxiaomieMS | Hỗ trợ kỹ thuật: AXH Xuan, Lingshazhu",
            "Trailer: Shitu | Quản lý: COOL | Trưởng test: Tongyan",
            "Đặc biệt cảm ơn:",
        ]
    )
    for idx_c, cline in enumerate(cred_lines):
        dz.text((516, 36 + idx_c * 22), cline, font=f_cred, fill=(28, 25, 20), anchor="lm")
    save_jpg(zn, out_dir, "images/ZombieNote.jpg", quality=94)
    generated.append("images/ZombieNote.jpg")

    # 15. White-on-black alpha masks: Credits_ZombieNote, ZombieNote1..4, Zombiefinalnote
    segoe = r"C:\Windows\Fonts\segoeprb.ttf"
    note_font = segoe if os.path.exists(segoe) else FONT_COMIC
    white_notes = [
        ("images/Credits_ZombieNote.png", (
            "All right, you win. We won't\neat your brains. Right now we\njust wanna make a music video\nwith you.\n\nSincerely,\nThe Zombies"
            if is_en else
            "Được rồi, bạn thắng. Tụi tôi\nsẽ không ăn não nữa. Giờ tụi\ntôi chỉ muốn quay MV nhạc với\nbạn thôi.\n\nThân ái,\nLũ Zombie"
        )),
        ("images/ZombieNote1.png", (
            "Hello,\n\nWe are about to launch an\nall-out attack on your house.\n\nSincerely,\nThe Zombies"
            if is_en else
            "Xin chào,\n\nChúng tôi sắp mở cuộc tổng\ntấn công vào nhà bạn đấy.\n\nThân ái,\nLũ Zombie"
        )),
        ("images/ZombieNote2.png", (
            "Hello,\n\nWe'd love to drop by for a\nmidnight snack. How does\nice cream & brains sound?\n\nSincerely,\nThe Zombies"
            if is_en else
            "Xin chào,\n\nTụi tôi muốn ghé nhà bạn ăn\nkhuya chút. Món kem trộn não\nnghe cũng ổn phết nhỉ?\n\nThân ái,\nLũ Zombie"
        )),
        ("images/ZombieNote3.png", (
            "Hello,\n\nWe heard you're throwing a\npool party. Sounds super fun!\nWe'll be right over.\n\nSincerely,\nThe Zombies"
            if is_en else
            "Xin chào,\n\nNghe đồn bạn đang mở tiệc hồ\nbơi. Nghe vui đấy!\nChúng tôi tới ngay đây.\n\nThân ái,\nLũ Zombie"
        )),
        ("images/ZombieNote4.png", (
            "Hello,\n\nThis is your Mom. Please unlock\nthe front door, clear the lawn,\nand come try some meatloaf.\n\nSincerely,\nMom (not the Zombies)"
            if is_en else
            "Xin chào,\n\nMẹ đây. Con mở cửa trước, dọn\nhết cây trên sân rồi ra thử\nmón thịt cuộn nướng nhé.\n\nThương con,\nMẹ (không phải Zombie đâu)"
        )),
    ]
    for rel, txt in white_notes:
        src = load_src(rel)
        mask = Image.new("RGB", src.size, (0, 0, 0))
        dm = ImageDraw.Draw(mask)
        f_nt = fit_font(note_font, txt, src.width - 36, src.height - 28, 25, min_size=14)
        dm.multiline_text((src.width // 2, src.height // 2), txt, font=f_nt, fill=(255, 255, 255), anchor="mm", align="left", spacing=5)
        dest = os.path.join(out_dir, rel.replace("/", os.sep))
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        mask.save(dest, "PNG")
        generated.append(rel)

    zfn_src = Image.open(os.path.join(PAK_DIR, "images/Zombiefinalnote.png")).convert("RGB")
    zfn_mask = Image.new("RGB", zfn_src.size, (0, 0, 0))
    zfn_sig = zfn_src.crop((335, 222, zfn_src.width, 282))
    zfn_mask.paste(zfn_sig, (335, 222))
    dzfn = ImageDraw.Draw(zfn_mask)
    zfn_body = (
        "Homeowner,\nYou rejected our reasonable terms.\nReconsider, or we'll take extreme measures.\nHand over your house & brains now.\n                                    Sincerely,"
        if is_en else
        "Chủ nhà thân mến,\nBạn đã từ chối đề nghị hợp lý của ta.\nHãy nghĩ lại trước khi quá muộn!\nMau giao nộp ngôi nhà và bộ não ngay.\n                                    Kính bút,"
    )
    f_zfn = fit_font(note_font, zfn_body, zfn_src.width - 28, 208, 20, min_size=12)
    dzfn.multiline_text((18, 12), zfn_body, font=f_zfn, fill=(255, 255, 255), spacing=4)
    f_ed = get_font(note_font, 17)
    dzfn.text((438, 298), "Dr. Edgar" if is_en else "Tiến Sĩ Edgar", font=f_ed, fill=(255, 255, 255), anchor="mm")
    dest_zfn = os.path.join(out_dir, "images", "Zombiefinalnote.png")
    zfn_mask.save(dest_zfn, "PNG")
    generated.append("images/Zombiefinalnote.png")

    # 16. Achievements selector rocks & buttons, Shop Card Slot icon, Shop Trial cards (37x), & Adventure Experimental Logs (01..09)
    # 16a. Achievements_selectorscreen_bg + _snow
    for rel, left_y, left_cy, cent_y, cent_cy in [
        ("NewAcheesements/Achievements_selectorscreen_bg.png", 46, 74, 54, 84),
        ("NewAcheesements/Achievements_selectorscreen_bg_snow.png", 56, 85, 52, 80),
    ]:
        im = load_src(rel)
        healed = heal_polygon(im, [(250, left_y), (344, left_y - 8), (348, left_y + 48), (254, left_y + 54)], blur_r=8, feather=3)
        hx = healed.load()
        cmask = Image.new("L", healed.size, 0)
        ImageDraw.Draw(cmask).polygon([(476, cent_y), (590, cent_y), (590, cent_y + 56), (476, cent_y + 56)], fill=255)
        cm = cmask.load()
        for yy in range(cent_y, cent_y + 57):
            rocks = [hx[xx, yy][:3] for xx in range(470, 596) if not (hx[xx, yy][0] > 140 and hx[xx, yy][1] > 125 and hx[xx, yy][2] < 135) and hx[xx, yy][0] > 80]
            rc = (sum(c[0] for c in rocks) // len(rocks), sum(c[1] for c in rocks) // len(rocks), sum(c[2] for c in rocks) // len(rocks)) if rocks else (138, 128, 122)
            for xx in range(476, 591):
                if cm[xx, yy] > 0:
                    r, g, b, a = hx[xx, yy]
                    if (r > 138 and g > 122 and b < 135) or (r < 98):
                        hx[xx, yy] = (rc[0], rc[1], rc[2], a)
        back_lbl = "BACK" if is_en else "TRỞ VỀ"
        fb = fit_font(FONT_BLACK, back_lbl, 74, 28, 17, min_size=10)
        draw_carved_stone_text(healed, (296, left_cy), back_lbl, fb, angle=11.0, highlight_mode=False)
        ach_lbl = "ACHIEVEMENTS" if is_en else "THÀNH TỰU"
        fa = fit_font(FONT_BLACK, ach_lbl, 176, 36, 26, min_size=12)
        draw_outlined_text(
            healed, (533, cent_cy), ach_lbl, fa,
            fill=(252, 212, 82, 255), outline=(42, 34, 18, 255), stroke_w=3, shadow_offset=(0, 2),
        )
        save_png(healed, out_dir, rel)
        generated.append(rel)

    # 16b. acheesements_back_highlight (93x39)
    bh_src = load_src("NewAcheesements/acheesements_back_highlight.png")
    bh_canvas = Image.new("RGBA", bh_src.size, (0, 0, 0, 0))
    back_lbl = "BACK" if is_en else "TRỞ VỀ"
    fbh = fit_font(FONT_BLACK, back_lbl, 74, 28, 17, min_size=10)
    draw_outlined_text(
        bh_canvas, (bh_src.width / 2, bh_src.height / 2), back_lbl, fbh,
        fill=(45, 255, 50, 255), outline=(16, 105, 16, 230), stroke_w=2,
        glow=(130, 255, 85, 220), glow_radius=3, angle=11.0, shadow_offset=None,
    )
    save_png(bh_canvas, out_dir, "NewAcheesements/acheesements_back_highlight.png")
    generated.append("NewAcheesements/acheesements_back_highlight.png")

    # 16c. acheesements_more_button / _top_button (92x120)
    for rel, is_hi in [("NewAcheesements/acheesements_more_button.png", False), ("NewAcheesements/acheesements_more_button_highlight.png", True)]:
        im = load_src(rel)
        im.paste(Image.new("RGBA", (im.width, 56), (0, 0, 0, 0)), (0, 0))
        mlbl = "MORE" if is_en else "THÊM"
        fm = fit_font(FONT_BLACK, mlbl, 70, 22, 16, min_size=10)
        draw_outlined_text(
            im, (45, 41), mlbl, fm,
            fill=(255, 200, 12, 255) if is_hi else (12, 12, 14, 255),
            outline=(155, 88, 5, 230) if is_hi else (130, 130, 135, 170),
            stroke_w=2 if is_hi else 1, shadow_offset=(1, 2),
        )
        save_png(im, out_dir, rel)
        generated.append(rel)

    for rel, is_hi in [("NewAcheesements/acheesements_top_button.png", False), ("NewAcheesements/acheesements_top_button_highlight.png", True)]:
        im = load_src(rel)
        im.paste(Image.new("RGBA", (im.width, im.height - 61), (0, 0, 0, 0)), (0, 61))
        tlbl = "TOP" if is_en else "ĐẦU"
        ft = fit_font(FONT_BLACK, tlbl, 70, 22, 16, min_size=10)
        draw_outlined_text(
            im, (45, 74), tlbl, ft,
            fill=(255, 200, 12, 255) if is_hi else (12, 12, 14, 255),
            outline=(155, 88, 5, 230) if is_hi else (130, 130, 135, 170),
            stroke_w=2 if is_hi else 1, shadow_offset=(1, 2),
        )
        save_png(im, out_dir, rel)
        generated.append(rel)

    # 16d. Remove "卡槽+1" from newshop/SHOP_UI_1.png slot 9 & newshop/Shop_icon.png idx 2
    ui1 = load_src("newshop/SHOP_UI_1.png")
    ui1_px = ui1.load()
    slate = ui1_px[1179 + 96, 40]
    for yy in range(54, 92):
        t_g = max(0.0, min(1.0, (yy - 54) / 24.0))
        card_c = (int(196 + 22 * t_g), int(232 - 6 * t_g), int(186 - 14 * t_g), 255)
        for xx in range(48, 115):
            lx = 1179 + xx
            if yy >= 80 or xx >= 91:
                ui1_px[lx, yy] = slate
            elif yy == 79 and 50 <= xx < 91:
                ui1_px[lx, yy] = (52, 62, 48, 255)
            elif xx == 90:
                ui1_px[lx, yy] = (52, 62, 48, 255)
            else:
                ui1_px[lx, yy] = card_c
    save_png(ui1, out_dir, "newshop/SHOP_UI_1.png")
    generated.append("newshop/SHOP_UI_1.png")

    si = load_src("newshop/Shop_icon.png")
    si_px = si.load()
    for yy in range(26, 59):
        t_g = max(0.0, min(1.0, (yy - 26) / 17.0))
        card_c = (int(196 + 22 * t_g), int(232 - 6 * t_g), int(186 - 14 * t_g), 255)
        for xx in range(21, 59):
            lx = 120 + xx
            if yy >= 44 or xx >= 45:
                si_px[lx, yy] = (0, 0, 0, 0)
            elif yy == 43 or xx == 44:
                si_px[lx, yy] = (52, 62, 48, 255)
            else:
                si_px[lx, yy] = card_c
    save_png(si, out_dir, "newshop/Shop_icon.png")
    generated.append("newshop/Shop_icon.png")

    # 16e. newshop/Shop_Challenge_Window.png (4366x120 = 37 Shop Trial cards x 118px wide)
    scw_labels = [
        ("Silver Trial", "Thử Thách Bạc"),
        ("Gold Trial", "Thử Thách Vàng"),
        ("Gem Trial", "Thử Thách Gem"),
        ("Claw Machine", "Máy Gắp Quà"),
        ("Fortune Cat", "Mèo Thần Tài"),
        ("Crystal Snail", "Ốc Pha Lê"),
        ("Nut Bank", "Heo Đất Hạt"),
        ("Gold Shooter", "Xạ Thủ Vàng"),
        ("Gem Seed", "Hạt Kim Cương"),
        ("Deluxe Gacha", "Hộp Quà VIP"),
        ("Landlord 1", "Địa Chủ 1"),
        ("Landlord 2", "Địa Chủ 2"),
        ("Landlord 3", "Địa Chủ 3"),
        ("Diamond-nut", "Óc Kim Cương"),
        ("Tall-nut Bag", "Túi Phân Cao"),
        ("Snail Chomper", "Răng Hổ Ốc"),
        ("Choco-nut", "Óc Chó Sôcôla"),
        ("Barrow Pot", "Chậu Xe Rùa"),
        ("Wealth Stump", "Gốc Tài Lộc"),
        ("Spray Fume", "Phun Diệt Sâu"),
        ("Gold Sunflwr", "H.Dương Vàng"),
        ("Phono Puff", "Nấm Nhỏ Nhạc"),
        ("Glove Bean", "Đậu Găng Tay"),
        ("Treasure Pot", "Tụ Bảo Bồn"),
        ("Can-pult", "Bình Tưới Hất"),
        ("Custom 1", "Tự Chọn 1"),
        ("Custom 2", "Tự Chọn 2"),
        ("Custom 3", "Tự Chọn 3"),
        ("Custom 4", "Tự Chọn 4"),
        ("Custom 5", "Tự Chọn 5"),
        ("Custom 6", "Tự Chọn 6"),
        ("Custom 7", "Tự Chọn 7"),
        ("Custom 8", "Tự Chọn 8"),
        ("Chili Spray", "Xịt Ớt Cay"),
        ("Reset Bag", "Phân Tái Tạo"),
        ("Key Coffee", "Cà Phê Chìa"),
        ("Mystery Trial", "Biến Hóa Khôn"),
    ]
    scw = load_src("newshop/Shop_Challenge_Window.png")
    scw_px = scw.load()
    d_scw = ImageDraw.Draw(scw)
    ribbon_rows = [(scw_px[12, yy], scw_px[104, yy]) for yy in range(85, 109)]
    for idx_c, (en_lbl, vi_lbl) in enumerate(scw_labels):
        x0 = idx_c * 118
        for idx_y, yy in enumerate(range(85, 109)):
            lc, rc = ribbon_rows[idx_y]
            for xx in range(x0 + 12, x0 + 105):
                t = (xx - (x0 + 12)) / 92.0
                scw_px[xx, yy] = (
                    int(round(lc[0] * (1 - t) + rc[0] * t)),
                    int(round(lc[1] * (1 - t) + rc[1] * t)),
                    int(round(lc[2] * (1 - t) + rc[2] * t)),
                    255,
                )
        lbl = en_lbl if is_en else vi_lbl
        f_c = fit_font(FONT_BOLD, lbl, 86, 18, 12, min_size=8)
        d_scw.text((x0 + 58, 97), lbl, font=f_c, fill=(38, 38, 46, 255), anchor="mm")
    save_png(scw, out_dir, "newshop/Shop_Challenge_Window.png")
    generated.append("newshop/Shop_Challenge_Window.png")

    # 16f. NewAdventure/ExperimentalLogNote01..09.png (654x427 Dr. Edgar story logs)
    palai_p = r"C:\Windows\Fonts\palai.ttf"
    timesi_p = r"C:\Windows\Fonts\timesi.ttf"
    log_font = note_font if is_en else (palai_p if os.path.exists(palai_p) else (timesi_p if os.path.exists(timesi_p) else FONT_BOLD))
    exp_logs = [
        ("ExperimentalLogNote01.png", True,
         "Log 023",
         "Successfully isolated activated Peashooter\ngenes. Less stable than expected, yet they\nsuppress Zombie DNA mutations during fusion\n— boosting mass Peashooter-Zombie output!\nNow I can send more Plant-Zombies ahead.\nTruly, I am the greatest genius alive!",
         "Nhật Ký 023",
         "Đã chiết xuất thành công gen Đậu Bắn Đạn\nhoạt hóa. Dù kém ổn định, nó kìm hãm hiệu\nquả đột biến gen Zombie khi dung hợp — tăng\nmạnh sản lượng Zombie Đậu!\nGiờ ta có thể tung thêm Cây-Zombie ra tiền\ntuyến. Quả nhiên ta là thiên tài xuất chúng!"),
        ("ExperimentalLogNote02.png", True,
         "Log 036",
         "Intelligence enhancement tests succeeded!\nSubject IQ has risen noticeably — they are\nalready learning to wield tools and gear.\n\nA promising start. I see a bright future ahead!",
         "Nhật Ký 036",
         "Thí nghiệm nâng cao trí tuệ đã thành công!\nIQ của các mẫu vật tăng rõ rệt — chúng bắt\nđầu học cách dùng nhiều công cụ và trang bị.\n\nKhởi đầu thuận lợi, ta thấy tương lai rạng rỡ!"),
        ("ExperimentalLogNote03.png", True,
         "Log 048",
         "A breakthrough on Gargantuars! Our new\ngene-enhancement serum reliably triggers the\nonce-rare [Red-Eye Berserk] state while boosting\nstability and obedience.\nWith these giants ready, the plan advances!",
         "Nhật Ký 048",
         "Thuốc cải tiến gen mới đã đột phá trên\nGargantuar, tái hiện ổn định trạng thái\n[Mắt Đỏ Cuồng Nộ] vốn hiếm gặp, đồng thời\ntăng mạnh độ ổn định và phục tùng.\nCó những gã khổng lồ này, kế hoạch tiến xa hơn!"),
        ("ExperimentalLogNote04.png", True,
         "Log 063",
         "Building aerosol dispensers to pilot-spray Gen-\nXII Gene Serum across Zombie clusters. It\nshould spark mass evolution among the horde.\n\nJust wait — one day I'll claim his brains!",
         "Nhật Ký 063",
         "Đang lắp đặt dàn phun sương thí điểm Thuốc\nCải Gen Thế Hệ XII tại các ổ Zombie. Dự kiến\nsẽ kích hoạt đợt tiến hóa quy mô lớn.\n\nCứ chờ xem — rồi ta sẽ đoạt bộ não của hắn!"),
        ("ExperimentalLogNote05.png", True,
         "Log 079",
         "The aerosol worked wonders! IQ surged —\nBobsled Drivers are teaching Gargantuars to\ndrive, and they're learning fast... Need bigger\nZombonis! Can't wait to see that fool's\nface when he meets them, haha!",
         "Nhật Ký 079",
         "Khí cải gen thật kỳ diệu: Zombie khôn ra hẳn,\ntài xế Xe Tuyết còn dạy Gargantuar lái xe và\ntụi nó sắp biết lái rồi... Chắc phải đóng xe\nlớn hơn. Sẽ hả hê lắm khi thấy mặt tên kia!"),
        ("ExperimentalLogNote06.png", True,
         "Log 095",
         "Due to unknown interference, the serum gas\nhas begun drifting slightly from its formula.\nNo abnormal Zombie effects observed yet —\nfurther monitoring required.",
         "Nhật Ký 095",
         "Do tác nhân chưa rõ, tính chất khí cải gen\nbắt đầu hơi lệch khỏi thiết kế ban đầu.\nHiện chưa ghi nhận bất thường trên Zombie,\ncần tiếp tục theo dõi thêm."),
        ("ExperimentalLogNote07.png", False,
         "Log 098",
         "05:47 today: abnormal vibrations struck the\ngas array from flow instability.\nRepairs underway; status stable for—",
         "Nhật Ký 098",
         "05:47 hôm nay: dàn phun khí rung bất thường\ndo biến đổi lưu lượng khí.\nĐang sửa chữa, trạng thái tạm ổn—"),
        ("ExperimentalLogNote08.png", True,
         "Log 099",
         "Though the blast wrecked my lab, our main\nZombie army is intact — enough to crush that\ngarden. Ignore the drifting gas for now.\nHe reached out again with some mad plot.\nI'll grant his visit — and end him for good!",
         "Nhật Ký 099",
         "Dù vụ nổ phá hủy phòng thí nghiệm, đội quân\nZombie chính vẫn an toàn — đủ san phẳng khu\nvườn. Kệ đám khí đang trôi nổi ngoài kia.\nHắn lại tìm gặp ta. Ta sẽ tiếp đón — và nhân\ncơ hội tiễn hắn biến mất vĩnh viễn!"),
        ("ExperimentalLogNote09.png", True,
         "Log 001",
         "Theme: [Deep Plant-Zombie Genetic Research].\nUnlocking cross-species traits to breed elite\nZombies and potent Plant-Zombies.\nNamed: [PROJECT HYBRID].\nMay this mark a great beginning!",
         "Nhật Ký 001",
         "Đề tài: [Nghiên Cứu Gen Cây & Zombie].\nKhai phá đặc tính dung hợp đa gen để tạo\nZombie tinh nhuệ & Cây-Zombie hùng mạnh.\nĐặt tên: [KẾ HOẠCH LAI TẠO].\nHy vọng đây là khởi đầu tốt đẹp!"),
    ]
    for fname, has_sig, h_en, b_en, h_vi, b_vi in exp_logs:
        rel = f"NewAdventure/{fname}"
        im = load_src(rel)
        rgb = im.convert("RGB")
        src_rgb = rgb.copy()
        healed_c = src_rgb.filter(ImageFilter.MaxFilter(19)).filter(ImageFilter.GaussianBlur(5))
        r_arr = rgb.load()
        h_arr = healed_c.load()
        s_arr = src_rgb.load()
        y_lim = 236 if not has_sig else 288
        for yy in range(28, y_lim):
            for xx in range(26, 608):
                sr, sg, sb = s_arr[xx, yy]
                hr, hg, hb = h_arr[xx, yy]
                if hr > 145 and hg > 130 and (hr - hb) > 20 and ((hr - sr > 16) or (hg - sg > 16) or (hb - sb > 14)):
                    r_arr[xx, yy] = (hr, hg, hb)
        if has_sig:
            for yy in range(334, 376):
                for xx in range(400, 565):
                    sr, sg, sb = s_arr[xx, yy]
                    hr, hg, hb = h_arr[xx, yy]
                    if hr > 155 and hg > 140 and (hr - hb) > 20 and ((hr - sr > 16) or (hg - sg > 16) or (hb - sb > 14)):
                        r_arr[xx, yy] = (hr, hg, hb)
        note_rgba = rgb.convert("RGBA")
        note_rgba.putalpha(im.getchannel("A"))
        dn = ImageDraw.Draw(note_rgba)
        hdr = h_en if is_en else h_vi
        body = b_en if is_en else b_vi
        fh = get_font(log_font, 23 if is_en else 22)
        dn.text((48, 48), hdr, font=fh, fill=(24, 22, 18, 255))
        fb = fit_font(log_font, body, 520 if has_sig else 505, 185 if has_sig else 108, 17 if is_en else 18, min_size=12)
        dn.multiline_text((48, 92 if has_sig else 88), body, font=fb, fill=(28, 24, 18, 255), spacing=5 if has_sig else 4)
        if has_sig:
            fs = get_font(log_font, 17)
            dn.text((480, 355), "Dr. Edgar" if is_en else "Tiến Sĩ Edgar", font=fs, fill=(24, 22, 18, 255), anchor="mm")
        save_png(note_rgba, out_dir, rel)
        generated.append(rel)

    # 17. NewAdventure chapter cover books (chapter_book01..09_8.png) & HybridTime Space-Time maps
    import json
    import numpy as np

    wryh_path = os.path.join(WORK, "unicode_fonts", "wryh.ttf")
    ui_font = wryh_path if os.path.exists(wryh_path) else FONT_BOLD

    chapter_books = [
        ("NewAdventure/chapter_book01.png", "Chapter 1", "Yard Alert", "Chương 1", "Sân Trước"),
        ("NewAdventure/chapter_book02.png", "Chapter 2", "Pool Defense", "Chương 2", "Hồ Bơi"),
        ("NewAdventure/chapter_book03.png", "Chapter 3", "Roof Battle", "Chương 3", "Mái Nhà"),
        ("NewAdventure/chapter_book04.png", "Chapter 4", "Journey Begins", "Chương 4", "Khởi Hành"),
        ("NewAdventure/chapter_book05.png", "Chapter 5", "Mystic Valley", "Chương 5", "Thung Lũng"),
        ("NewAdventure/chapter_book06.png", "Chapter 6", "Four Seas", "Chương 6", "Bốn Bể"),
        ("NewAdventure/chapter_book07.png", "Chapter 7", "Village Quest", "Chương 7", "Thôn Làng"),
        ("NewAdventure/chapter_book08.png", "Chapter 8", "Journey's End", "Chương 8", "Trận Cuối"),
        ("NewAdventure/chapter_book09.png", "Extra Chapters", "Hidden Campaign", "Ngoại Truyện", "Chiến Dịch Ẩn"),
        ("NewAdventure/chapter_book09_1.png", "Extra 1", "Barren Land", "Ngoại 1", "Hoang Địa"),
        ("NewAdventure/chapter_book09_2.png", "Extra 2", "Cool Summer", "Ngoại 2", "Hè Mát Lành"),
        ("NewAdventure/chapter_book09_3.png", "Extra 3", "Three Realms", "Ngoại 3", "Chân Vạc"),
        ("NewAdventure/chapter_book09_4.png", "Extra 4", "Sleepless Night", "Ngoại 4", "Đêm Thức"),
        ("NewAdventure/chapter_book09_5.png", "Extra 5", "Shop Guard", "Ngoại 5", "Giữ Tiệm"),
        ("NewAdventure/chapter_book09_6.png", "Extra 6", "Flowing Creek", "Ngoại 6", "Suối Nhỏ"),
        ("NewAdventure/chapter_book09_7.png", "Extra 7", "Night Parade", "Ngoại 7", "Bách Quỷ Đêm"),
        ("NewAdventure/chapter_book09_8.png", "Extra 8", "Harbor Probe", "Ngoại 8", "Bến Cảng"),
    ]
    for rel, h_en, s_en, h_vi, s_vi in chapter_books:
        im = load_src(rel)
        dr = ImageDraw.Draw(im)
        hdr = h_en if is_en else h_vi
        sub = s_en if is_en else s_vi
        dr.rounded_rectangle([72, 20, 308, 76], radius=12, fill=(22, 34, 18, 228), outline=(170, 225, 85, 235), width=2)
        fh = fit_font(ui_font, hdr, 216, 48, 30, min_size=18)
        dr.text((190, 48), hdr, font=fh, fill=(198, 255, 92, 255), stroke_width=2, stroke_fill=(10, 18, 8, 255), anchor="mm")
        dr.rounded_rectangle([148, 174, 456, 248], radius=12, fill=(18, 28, 22, 228), outline=(145, 220, 165, 235), width=2)
        fs = fit_font(ui_font, sub, 286, 56, 28, min_size=16)
        dr.text((302, 211), sub, font=fs, fill=(195, 255, 200, 255), stroke_width=2, stroke_fill=(10, 18, 12, 255), anchor="mm")
        save_png(im, out_dir, rel)
        generated.append(rel)

    # Space-Time Trial maps (new/HybridTime_BG.png & new/HybridTime_BG2.png)
    exe_tr_path = os.path.join(ROOT, "translations", "strings_exe.json")
    if not os.path.isfile(exe_tr_path):
        exe_tr_path = os.path.join(WORK, "strings_exe.json")
    exe_tr = {k.strip(): v for k, v in json.load(open(exe_tr_path, encoding="utf-8")).items()}

    def node_label(cn: str) -> str:
        ent = exe_tr.get(cn)
        if not ent:
            return cn
        return ent["en"] if is_en else ent["vi"]

    ht1_cards = [
        (76, 151, "初始时光"), (76, 409, "水生植物"), (76, 653, "海洋时光"), (76, 911, "大海归途"), (76, 1170, "错乱记忆"), (76, 1432, "滚瓜烂熟"), (76, 1690, "黄金瓜子"),
        (419, 151, "投手时光"), (419, 409, "冰天雪地"), (419, 653, "大嘴领地"), (419, 911, "溜冰场"), (419, 1170, "恐惧僵尸"), (419, 1431, "南瓜派"), (419, 1690, "雪地战役"),
        (762, 150, "玉米大嘴"), (764, 409, "冬眠配方"), (762, 653, "冻结阳光"), (764, 912, "阳光梦想"), (764, 1170, "胆小回忆"), (763, 1428, "葵花宝典"), (762, 1690, "枪林弹雨"),
        (1105, 150, "大嘴派对"), (1105, 408, "多重抉择"), (1105, 652, "蓝色梦想"), (1105, 911, "光明黑暗"), (1105, 1170, "乘风破浪"), (1105, 1429, "风力发电"), (1105, 1690, "狂野之路"),
        (1450, 23, "圣诞之夜"), (1448, 220, "地刺空间"), (1450, 416, "三线入口"), (1448, 579, "土豆泥"), (1448, 817, "阳光道路"), (1448, 996, "禁忌力量"), (1448, 1257, "骷髅巨人"), (1450, 1512, "黑暗巢穴"), (1450, 1767, "黑暗尽头"),
        (1791, 23, "促销风暴"), (1791, 220, "僵尸之主"), (1791, 400, "土豆爆炸"), (1791, 579, "毁灭之路"), (1791, 816, "光明使者"), (1791, 996, "禁忌任务"), (1791, 1257, "僵尸墓地"), (1791, 1512, "暗影之力"), (1791, 1767, "毁灭阳光"),
        (2134, 23, "促销汉堡"), (2134, 219, "魅惑秀场"), (2134, 400, "三重反转"), (2134, 579, "天坑"), (2134, 816, "星星之火"), (2134, 996, "废弃花园"), (2134, 1257, "园艺危机"), (2134, 1512, "重见光明"), (2134, 1767, "南瓜基地"),
        (2478, 78, "促销之旅"), (2477, 324, "光之信仰"), (2477, 571, "太阳能量"), (2477, 816, "阳光火炬"), (2477, 996, "空中花园"), (2477, 1257, "高山流水"), (2477, 1512, "窝瓜时空"), (2477, 1767, "夜晚基地"),
        (2820, 19, "狂野之城"), (2820, 264, "狂野之门"), (2820, 571, "阳光炸弹"), (2820, 817, "阳光征途"), (2820, 996, "巨人飞艇"), (2820, 1257, "细水长流"), (2820, 1512, "生命之源"),
        (3163, 19, "狂野之境"), (3164, 264, "回归自然"), (3164, 507, "天鹅之乱"), (3164, 750, "空中漫步"), (3163, 996, "星空灿烂"), (3163, 1247, "浪漫山谷"), (3163, 1495, "浪漫夜空"), (3163, 1749, "浪漫结局"),
    ]
    ht2_cards = [
        (419, 151, "整装待发"), (762, 151, "精英对决"), (1105, 151, "乱象丛生"), (1448, 151, "巨人之城"), (1791, 151, "天下无双"), (2134, 151, "仙人之掌"),
        (76, 422, "超级汉堡"), (419, 422, "南征北调"), (762, 422, "超级僵尸"), (1105, 422, "极限生存"), (1448, 422, "天空之城"), (1791, 422, "超级葵花"), (2134, 422, "仙人之道"),
        (76, 693, "美味佳肴"), (419, 693, "超级寒冰"), (762, 694, "暗影空间"), (1105, 694, "炼狱之门"), (1448, 693, "无尽能源"), (1791, 693, "钻石剧场"), (2134, 694, "仙人之门"), (2477, 693, "天使之战"), (2820, 693, "天空之战"), (3163, 693, "终极轮盘"),
        (76, 965, "炙手可热"), (419, 965, "冰霜行者"), (762, 965, "兵临城下"), (1105, 965, "熔岩炼狱"), (1448, 965, "坚果魔力"), (1791, 965, "坚不可摧"), (2134, 965, "仙人指路"), (2477, 965, "八仙过海"), (2820, 965, "狗尾池塘"), (3163, 965, "狐尾池塘"),
        (76, 1236, "僵尸实验"), (419, 1236, "千里冰封"), (762, 1236, "火焰女王"), (1105, 1236, "盖世英雄"), (1448, 1236, "阳光魅力"), (1791, 1236, "狂热狙击"), (2134, 1236, "终极猎手"), (2477, 1236, "幽灵之战"), (2820, 1236, "未来科技"), (3163, 1236, "激光装备"),
        (76, 1508, "植物实验"), (419, 1508, "终极实验"), (762, 1508, "阳光危机"), (1105, 1508, "植物危机"), (1448, 1508, "至尊坚果"), (1791, 1508, "狂野狙击"), (2134, 1508, "幽灵之路"), (2477, 1508, "幽灵之城"), (2820, 1508, "夏日决战"), (3163, 1508, "终极武器"),
        (76, 1772, "烈焰行者"), (419, 1772, "火焰使者"), (762, 1772, "美味火锅"), (1105, 1772, "菠萝果屋"), (1448, 1772, "菠萝泳池"), (1791, 1772, "菠萝草坪"), (2134, 1772, "夏日之火"), (2477, 1772, "夏日之水"), (2820, 1772, "清凉一夏"), (3163, 1772, "实验末路"),
    ]

    ht_specs = [
        ("new/HybridTime_BG.png", "HYBRID ERA" if is_en else "THỜI KHÔNG", ht1_cards, (2820, 1749, "Secret Realm" if is_en else "Vào Bí Cảnh")),
        ("new/HybridTime_BG2.png", "SECRET REALM" if is_en else "BÍ CẢNH", ht2_cards, (76, 151, "Hybrid Era" if is_en else "Thời Không")),
    ]
    for rel, rib_txt, card_list, portal in ht_specs:
        im = load_src(rel)
        arr = np.array(im)
        rgb = arr[:, :, :3].copy()
        # Erase baked text in top gold ribbon (x=425..655, y=10..56) via horizontal gold sample
        col = rgb[10:56, 420:425].mean(axis=1, keepdims=True).astype(np.uint8)
        rgb[10:56, 425:655] = np.repeat(col, 655 - 425, axis=1)
        out_ht = Image.fromarray(np.dstack([rgb, arr[:, :, 3]]), "RGBA")
        hd = ImageDraw.Draw(out_ht)
        f_rib = fit_font(ui_font, rib_txt, 240, 40, 28, min_size=16)
        hd.text((540, 32), rib_txt, font=f_rib, fill=(255, 252, 235, 255), stroke_width=3, stroke_fill=(95, 50, 10, 255), anchor="mm")
        for cx, cy, cn in card_list:
            lbl = node_label(cn)
            fc = fit_font(ui_font, lbl, 144, 22, 14, min_size=9)
            hd.rounded_rectangle([cx + 10, cy + 2, cx + 166, cy + 31], radius=5, fill=(22, 26, 32, 235), outline=(235, 195, 95, 230), width=1)
            hd.text((cx + 88, cy + 16), lbl, font=fc, fill=(255, 236, 130, 255), anchor="mm")
        px_p, py_p, p_lbl = portal
        fp = fit_font(ui_font, p_lbl, 134, 28, 16, min_size=10)
        hd.rounded_rectangle([px_p + 14, py_p + 43, px_p + 160, py_p + 83], radius=8, fill=(18, 28, 22, 232), outline=(255, 215, 95, 240), width=2)
        hd.text((px_p + 87, py_p + 63), p_lbl, font=fp, fill=(255, 240, 150, 255), stroke_width=2, stroke_fill=(12, 16, 12, 255), anchor="mm")
        save_png(out_ht, out_dir, rel)
        generated.append(rel)

    return generated


def render_verification_sheet(lang: str, rel_list: list[str]):
    os.makedirs(SCRATCH, exist_ok=True)
    out_dir = os.path.join(WORK, f"overrides_{lang}")
    cols = 5
    cw, ch = 300, 145
    rows = (len(rel_list) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * cw, rows * ch), (22, 26, 32, 255))
    dr = ImageDraw.Draw(sheet)
    f_lbl = get_font(FONT_BOLD, 11)
    for i, rel in enumerate(rel_list):
        cx, cy = (i % cols) * cw, (i // cols) * ch
        dr.rectangle([cx + 2, cy + 2, cx + cw - 3, cy + ch - 3], outline=(65, 78, 92, 255))
        p = os.path.join(out_dir, rel.replace("/", os.sep))
        im = Image.open(p).convert("RGBA")
        im.thumbnail((cw - 16, ch - 30), Image.LANCZOS)
        sheet.alpha_composite(im, (cx + 8, cy + 24))
        dr.text((cx + 6, cy + 5), os.path.basename(rel), font=f_lbl, fill=(175, 235, 185, 255))
    out_p = os.path.join(SCRATCH, f"localized_textures_{lang}.png")
    sheet.save(out_p, "PNG")
    print(f"Saved [{lang.upper()}] texture verification sheet ({len(rel_list)} files) -> {out_p}")


if __name__ == "__main__":
    for lg in ("en", "vi"):
        files = build_textures_for_lang(lg)
        render_verification_sheet(lg, files)
