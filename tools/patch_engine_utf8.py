"""Patch gdi42.dll (CP936 -> CP_UTF8 65001), build Unicode+Vietnamese TrueType fonts, and relocate .exe strings."""
import hashlib
import io
import json
import os
import re
import shutil
import struct
import urllib.request
from fontTools.misc.transform import Transform
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HE_DIR = os.path.join(ROOT, "work", "he_extracted")
FONTS_OUT = os.path.join(ROOT, "work", "unicode_fonts")
LIB_REGULAR = os.environ.get("LIBERATION_REGULAR_TTF", os.path.join(ROOT, "tools", "LiberationSans.ttf"))
LIB_BOLD_CACHE = os.path.join(ROOT, "tools", "LiberationSans-Bold.ttf")

# Exact 4 MultiByteToWideChar(936, ...) pushes in gdi42.dll DrawString & StringWidth
GDI42_CP936_OFFSETS = [0x2150, 0x218B, 0x22C5, 0x2300]


def ensure_liberation_bold() -> str:
    if os.path.isfile(LIB_BOLD_CACHE) and os.path.getsize(LIB_BOLD_CACHE) > 100_000:
        return LIB_BOLD_CACHE
    os.makedirs(os.path.dirname(LIB_BOLD_CACHE), exist_ok=True)
    url = "https://github.com/liberationfonts/liberation-fonts/raw/main/liberation-fonts-ttf-2.1.5/LiberationSans-Bold.ttf"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        data = urllib.request.urlopen(req, timeout=15).read()
        if data[:4] == b"\x00\x01\x00\x00":
            with open(LIB_BOLD_CACHE, "wb") as f:
                f.write(data)
            print(f"Downloaded LiberationSans-Bold.ttf ({len(data):,} bytes)")
            return LIB_BOLD_CACHE
    except Exception as e:
        print(f"Note: LiberationSans-Bold download fallback to LiberationSans Regular ({e})")
    return LIB_REGULAR


def inject_unicode_glyphs(cn_ttf_path: str, lat_ttf_path: str, out_ttf_path: str, keep_digits: bool = False) -> int:
    """Inject full ASCII + Latin-1 + Latin Extended + Vietnamese + General Punctuation from lat_ttf into cn_ttf."""
    f_cn = TTFont(cn_ttf_path)
    f_lat = TTFont(lat_ttf_path)
    scale = f_cn["head"].unitsPerEm / f_lat["head"].unitsPerEm
    t = Transform(scale, 0, 0, scale, 0, 0)
    gset_lat = f_lat.getGlyphSet()
    cmap_lat = f_lat.getBestCmap() or {}
    cmap_cn = f_cn.getBestCmap() or {}

    has_fmt12 = any(sub.isUnicode() and sub.format >= 12 for sub in f_cn["cmap"].tables)
    max_cp = 0x10FFFF if has_fmt12 else 0xFFFF

    target_codes = []
    for code in sorted(cmap_lat.keys()):
        if code > max_cp:
            continue
        if keep_digits and 0x0030 <= code <= 0x0039:
            continue
        if (
            (0x0020 <= code <= 0x024F)
            or (0x1E00 <= code <= 0x1EFF)
            or (0x2000 <= code <= 0x206F)
            or (code not in cmap_cn)
        ):
            target_codes.append(code)

    order = list(f_cn.getGlyphOrder())
    order_set = set(order)
    injected = 0

    for code in target_codes:
        gname_lat = cmap_lat[code]
        gname_new = f"uni{code:04X}" if code <= 0xFFFF else f"u{code:X}"
        rec = DecomposingRecordingPen(gset_lat)
        try:
            gset_lat[gname_lat].draw(rec)
        except Exception:
            continue
        if gname_new not in order_set:
            order.append(gname_new)
            order_set.add(gname_new)
        pen = TTGlyphPen(None)
        tpen = TransformPen(pen, t)
        rec.replay(tpen)
        f_cn["glyf"][gname_new] = pen.glyph()
        adv, lsb = f_lat["hmtx"].metrics.get(gname_lat, (1000, 0))
        f_cn["hmtx"].metrics[gname_new] = (int(round(adv * scale)), int(round(lsb * scale)))
        if "vmtx" in f_cn:
            f_cn["vmtx"].metrics[gname_new] = (f_cn["head"].unitsPerEm, 0)
        for sub in f_cn["cmap"].tables:
            if sub.isUnicode() and (code <= 0xFFFF or sub.format >= 12):
                sub.cmap[code] = gname_new
        injected += 1

    f_cn.setGlyphOrder(order)
    os.makedirs(os.path.dirname(out_ttf_path), exist_ok=True)
    f_cn.save(out_ttf_path)
    return injected


def build_all_unicode_fonts() -> str:
    os.makedirs(FONTS_OUT, exist_ok=True)
    src_fdir = os.path.join(HE_DIR, "fonts")
    bold_ttf = ensure_liberation_bold()
    reg_ttf = LIB_REGULAR

    # Copy non-TTF bitmap assets (DwarvenTodcraft18.png / .txt)
    for fn in ["DwarvenTodcraft18.png", "DwarvenTodcraft18.txt"]:
        shutil.copy2(os.path.join(src_fdir, fn), os.path.join(FONTS_OUT, fn))

    # Note: fzkt.TTF and fzyh.ttf are identical bytes in Classic v3.20.1; check MD5 to avoid duplicate work
    built_by_md5 = {}
    font_specs = [
        ("fzcq.ttf", bold_ttf, False),
        ("fzjz.ttf", bold_ttf, False),
        ("fzkt.TTF", bold_ttf, False),
        ("fzyh.ttf", bold_ttf, False),
        ("wryh.ttf", reg_ttf, False),
        ("wryh+pico12num.ttf", bold_ttf, True),  # keep pico12num 0-9 pixel digits!
    ]

    for fn, donor_ttf, keep_digits in font_specs:
        in_p = os.path.join(src_fdir, fn)
        out_p = os.path.join(FONTS_OUT, fn.lower())
        if os.path.exists(out_p) and os.path.getsize(out_p) > 100_000:
            # Remove any stale uppercase-named entry first
            pass
        key = (hashlib.md5(open(in_p, "rb").read()).hexdigest(), donor_ttf, keep_digits)
        if key in built_by_md5:
            if os.path.normcase(built_by_md5[key]) != os.path.normcase(out_p):
                shutil.copy2(built_by_md5[key], out_p)
            print(f"  [Font] Reused identical build -> {os.path.basename(out_p)}")
        else:
            cnt = inject_unicode_glyphs(in_p, donor_ttf, out_p, keep_digits=keep_digits)
            built_by_md5[key] = out_p
            print(f"  [Font] Built {os.path.basename(out_p)}: +{cnt} Unicode/VI glyphs ({os.path.getsize(out_p):,} bytes)")

    # Verify Vietnamese diacritics in every built .ttf
    vi_req = "ăâđêôơưĂÂĐÊÔƠƯắằẳẵặấầẩẫậếềểễệốồổỗộớờởỡợứừửữựỳỷỹỵ"
    for fn in os.listdir(FONTS_OUT):
        if fn.lower().endswith(".ttf"):
            cmap = TTFont(os.path.join(FONTS_OUT, fn)).getBestCmap() or {}
            missing = [c for c in vi_req if ord(c) not in cmap]
            assert not missing, f"{fn} missing VI chars: {missing}"
    print(f"All Unicode fonts verified 100% in {FONTS_OUT}")
    return FONTS_OUT


def patch_gdi42_atlas_hook(dll_path: str):
    """Redirect gdi42.dll DrawString/StringWidth & glyph draw to PlantsVsZombies.exe fast cache + Glyph Atlas."""
    buf = bytearray(open(dll_path, "rb").read())
    # 1. 7-byte absolute jump trampoline in int3 padding at VA 0x10001ea8 (raw 0x12a8) -> 0x00b52000 (fallback draw)
    tramp_raw = 0x12A8
    tramp_target = b"\xb8\x00\x20\xb5\x00\xff\xe0"  # mov eax, 0x00b52000; jmp eax
    if bytes(buf[tramp_raw : tramp_raw + 7]) != tramp_target:
        assert bytes(buf[tramp_raw : tramp_raw + 8]) == b"\xcc" * 8, (
            f"Unexpected padding at gdi42+0x12a8: {buf[tramp_raw:tramp_raw+8].hex()}"
        )
        buf[tramp_raw : tramp_raw + 7] = tramp_target
    # 2. Patch DrawString glyph call at VA 0x10002e45 (raw 0x2245): call 0x10001e80 -> call 0x10001ea8
    call_raw = 0x2245
    call_new = b"\xe8\x5e\xf0\xff\xff"  # rel32 = 0x10001ea8 - 0x10002e4a = -0xFA2
    if bytes(buf[call_raw : call_raw + 5]) != call_new:
        assert bytes(buf[call_raw : call_raw + 5]) == b"\xe8\x36\xf0\xff\xff", (
            f"Unexpected call at gdi42+0x2245: {buf[call_raw:call_raw+5].hex()}"
        )
        buf[call_raw : call_raw + 5] = call_new

    # 3. Relocation-safe 12-byte DrawString trampoline at VA 0x10001f40 (raw 0x1340, 16x int3) -> 0x00b52078
    #    call $+5; mov eax, 0x00b52078; jmp eax  (pushes runtime VA of gdi_base+0x1f45)
    ds_tramp_raw = 0x1340
    ds_tramp = b"\xe8\x00\x00\x00\x00\xb8\x78\x20\xb5\x00\xff\xe0"
    if bytes(buf[ds_tramp_raw : ds_tramp_raw + 12]) != ds_tramp:
        assert bytes(buf[ds_tramp_raw : ds_tramp_raw + 16]) == b"\xcc" * 16 or (
            buf[ds_tramp_raw : ds_tramp_raw + 6] == b"\xe8\x00\x00\x00\x00\xb8"
        ), f"Unexpected padding at gdi42+0x1340: {buf[ds_tramp_raw:ds_tramp_raw+16].hex()}"
        buf[ds_tramp_raw : ds_tramp_raw + 12] = ds_tramp
    #    Hook DrawString prologue @ VA 0x10002d20 (raw 0x2120): 55 8b ec 83 ec 0c -> jmp rel32 0x10001f40; nop
    ds_hook_raw = 0x2120
    ds_hook = b"\xe9" + struct.pack("<i", 0x10001F40 - 0x10002D25) + b"\x90"
    if bytes(buf[ds_hook_raw : ds_hook_raw + 6]) != ds_hook:
        assert bytes(buf[ds_hook_raw : ds_hook_raw + 6]) == bytes.fromhex("558bec83ec0c"), (
            f"Unexpected DrawString prologue at gdi42+0x2120: {buf[ds_hook_raw:ds_hook_raw+6].hex()}"
        )
        buf[ds_hook_raw : ds_hook_raw + 6] = ds_hook

    # 4. Relocation-safe 12-byte StringWidth trampoline at VA 0x10003771 (raw 0x2b71, 15x int3) -> 0x00b52080
    #    call $+5; mov eax, 0x00b52080; jmp eax  (pushes runtime VA of gdi_base+0x3776)
    sw_tramp_raw = 0x2B71
    sw_tramp = b"\xe8\x00\x00\x00\x00\xb8\x80\x20\xb5\x00\xff\xe0"
    if bytes(buf[sw_tramp_raw : sw_tramp_raw + 12]) != sw_tramp:
        assert bytes(buf[sw_tramp_raw : sw_tramp_raw + 15]) == b"\xcc" * 15 or (
            buf[sw_tramp_raw : sw_tramp_raw + 6] == b"\xe8\x00\x00\x00\x00\xb8"
        ), f"Unexpected padding at gdi42+0x2b71: {buf[sw_tramp_raw:sw_tramp_raw+15].hex()}"
        buf[sw_tramp_raw : sw_tramp_raw + 12] = sw_tramp
    #    Hook StringWidth prologue @ VA 0x10002e90 (raw 0x2290): 55 8b ec 83 ec 0c -> jmp rel32 0x10003771; nop
    sw_hook_raw = 0x2290
    sw_hook = b"\xe9" + struct.pack("<i", 0x10003771 - 0x10002E95) + b"\x90"
    if bytes(buf[sw_hook_raw : sw_hook_raw + 6]) != sw_hook:
        assert bytes(buf[sw_hook_raw : sw_hook_raw + 6]) == bytes.fromhex("558bec83ec0c"), (
            f"Unexpected StringWidth prologue at gdi42+0x2290: {buf[sw_hook_raw:sw_hook_raw+6].hex()}"
        )
        buf[sw_hook_raw : sw_hook_raw + 6] = sw_hook

    with open(dll_path, "wb") as f:
        f.write(buf)
    print(f"Patched gdi42.dll O(1) DrawString/StringWidth + Glyph Atlas hooks -> {dll_path}")


def patch_gdi42_utf8(out_dll_path: str):
    src_dll = os.path.join(HE_DIR, "gdi42.dll")
    buf = bytearray(open(src_dll, "rb").read())
    for off in GDI42_CP936_OFFSETS:
        orig = bytes(buf[off : off + 5])
        assert orig == b"\x68\xa8\x03\x00\x00", f"Unexpected bytes at gdi42.dll+{hex(off)}: {orig.hex()}"
        # Verify followed by `call dword ptr [MultiByteToWideChar]` (`ff 15 ...`)
        assert buf[off + 5 : off + 7] == b"\xff\x15", f"Expected call [IAT] after {hex(off)}"
        # Patch 936 (0x000003A8) -> 65001 CP_UTF8 (0x0000FDE9)
        buf[off : off + 5] = b"\x68\xe9\xfd\x00\x00"
    os.makedirs(os.path.dirname(os.path.abspath(out_dll_path)), exist_ok=True)
    with open(out_dll_path, "wb") as f:
        f.write(buf)
    print(f"Patched gdi42.dll (4 MultiByteToWideChar CP936 -> CP_UTF8 65001) -> {out_dll_path}")
    patch_gdi42_atlas_hook(out_dll_path)


if __name__ == "__main__":
    build_all_unicode_fonts()
    patch_gdi42_utf8(os.path.join(ROOT, "work", "gdi42_utf8.dll"))
