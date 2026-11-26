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

    # ShopChallenge_button (121x126 red brain flag -> bottom label "SHOP" / "ẢI SHOP")
    for rel, is_hi in [("new/ShopChallenge_button.png", False), ("new/ShopChallenge_button2.png", True)]:
        im = load_src(rel)
        healed = heal_dark_or_bright_in_poly(im, [(28, 76), (108, 70), (112, 106), (32, 112)], blur_r=6, feather=3)
        lbl = "SHOP TRIAL" if is_en else "ẢI SHOP"
        f = fit_font(FONT_BOLD, lbl, 76, 24, 13, min_size=8)
        draw_outlined_text(healed, (70, 92), lbl, f, fill=(255, 245, 150, 255) if is_hi else (255, 248, 240, 255), outline=(95, 12, 12, 255), stroke_w=2, angle=6.0, shadow_offset=None)
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
