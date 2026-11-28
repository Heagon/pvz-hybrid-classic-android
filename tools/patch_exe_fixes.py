#!/usr/bin/env python3
"""Gameplay, UI layout, Almanac optimization, Shovel/Menu input, I-Zombie, and Hero stability patches for PvZ Hybrid Classic v3.20.1."""
import hashlib
import os
import shutil
import struct
import subprocess
import sys
import tempfile

# Verified assembled machine code from cave_fixes.S (VA 0x00b50400..0x00b509d0, 1488 bytes).
CAVE_BASE_VA = 0x00B50400
FIXES_CAVE_SHA256 = "b233700d61f4e5002ef13afb81a89532f24e20d50ec2e1984cbd3cb7cf769ec8"
FIXES_CAVE_HEX = (
    "397c2464720f8b4c245051b89ac16100ffd083c404682dcf4500c3909090909090909090909090909090909090909090"
    "60bb00b0a30031d231c989d7c1e7098b348b81fe00020000731480bc370010b50000750a8d41018884370010b5004183"
    "f95b7cdb81c36c0100004283fa057cc8c605001ab5000161c39090909090909090909090909090909090909090909090"
    "803d001ab500007505e892ffffff81ff000200007335a10010730083f804760231c0c1e0090fb684380010b50085c074"
    "1a48515231d2b90d000000f7f16bf2346bc04e5a5968e9214000c3689c224000c3909090909090909090909090909090"
    "803d001ab500007505e832ffffff81fb000200007333a10010730083f804760231c0c1e0090fb684180010b50085c074"
    "184852b90d00000031d2f7f16bca346bc04e5a68b4394000c368e9394000c39090909090909090909090909090909090"
    "85f67438505131c0b90070a7003b348174484083f8097cf58b0dc09e6a0085c974188b896807000085c9740e3bb14801"
    "00007506837e0400742059588b0dc09e6a008b81200300008b90e00000008b80e40000006844834400c35958608b15c0"
    "9e6a008b922003000083ba940000000075448b0dc09e6a0083b9fc0700000375358b81f807000083f82b742a83f83274"
    "25618b0dc09e6a008b81200300008b90e00000008b80e400000081ea8c0000006844834400c361eb838db42600000000"
    "80bdf155000000742c53578d44241889da89feb940dc4100ffd184c0741589eeb990244100ffd184c074085f5b687c18"
    "4100c35f5b8b85440100006824184100c38db426000000002e8db4260000000081fd00020000730d608b1dc09e6a0068"
    "9cc5ab00c368b8c5ab00c32e8d7426008b86cc00000083f8017d05b80100000089c38b86c800000085c07f0331dbc339"
    "d87206bbf0000000c3baf0000000f7e2f7f33df00000007605b8f000000089c3c38db426000000002e8db42600000000"
    "85db7e0a39ef750668705ab100c368845ab100c385db7e0a39ef75066890298100c368a4298100c32e8db42600000000"
    "8b44240485c0744652518b15c09e6a0085d274338b922008000085d274298b520885d2742289c125ffff00003b420873"
    "168b1285d274108d0480c1e00501d039889c000000740231c0595ac2040031c0c204002e8d7426002e8db42600000000"
    "85f67412837f3c0475066855059a00c368a5059a00c368aa089a00c385c07406f30f2d4038c331c0c331c985c07405f3"
    "0f2d4838c385c0740ac7804402000001000000c385db740668e0394700c3c20800837c240400740668403a4700c3c20c"
    "008db426000000002e8db4260000000085c07407c7405c00000000c3d9eedaa64001000085c07404d95838c3ddd8c351"
    "85c07418f30f2d482c890dc0cc8100f30f2d4838890dc4cc810059c3c705c0cc810000000000c705c4cc810000000000"
    "59c385c0740b83785c0061689e069200c36168c1069200c385c0740d89c668e9728100685c3c9200c3686a3c9200c385"
    "c074038958688b4f046871049a00c3b810cb4000ffd085c07403897068c385c07407c740683f000000c385c07407c740"
    "6840000000c3b920d64000ffd185c07404c64074036822089a00c3b920d64000ffd185c074128b8d4801000089889c00"
    "0000683a009b00c3616864009b00c3b920d64000ffd185c074128b8d4801000089889c000000689c009b00c36168c600"
    "9b00c38b80301c000083f806720231c08b1c854367b100c38b80301c000083f806720231c08b1c8563368100c38d7600"
    "85c0743780781a00753180b8f900000000752880781800751e538b580839d97c1903581039d97d128b580c39da7c0b03"
    "581439da7d045bb001c35b31c0c385c0742151528b4c24348b542438e8afffffff84c05a59740c8b8548010000689b17"
    "4100c368ca174100c385c0741f51528b4d088b550ce886ffffff84c05a59740c8b8748010000689d1f4100c368c81f41"
    "00c385c0742151528b4c24188b54241ce85bffffff84c05a59740c8b864801000068a2254100c368b5264100c38d7600"
    "8b3683be440800000275295789f7b8f0424500ffd0c7864408000000000000c7864008000000000000c78650080000ff"
    "ffffff5fb8b0f64400ffd068aec34300c3608b858c00000085c0745a83b8fc07000003755183b84408000002754883bd"
    "04560000007f3fb940504500ffd18b858c00000083b844080000027529ffb040080000e8a8fcffff85c0751a8b858c00"
    "0000c7804408000000000000c78040080000000000006180bd6401000000740668f95d4100c3682e5e4100c390909090"
)

FIXES_SYM_OFFSETS = {
    "_fix_options_draw_skip": 0x000,
    "_almanac_init_lut": 0x030,
    "_fix_almanac_draw_lookup": 0x090,
    "_fix_almanac_hit_lookup": 0x0F0,
    "_fix_gamebutton_update": 0x150,
    "_fix_shovel_before_seedbank": 0x210,
    "_fix_izombie_seed_bound": 0x260,
    "_hero_safe_bar_width": 0x280,
    "_hero_strdiv_b15a68": 0x2D0,
    "_hero_strdiv_812988": 0x2E4,
    "_safe_try_get_reanim": 0x300,
    "_fix_hero_0x3e_reanim_guard": 0x360,
    "_safe_reanim_y_eax": 0x37C,
    "_safe_reanim_y_ecx": 0x389,
    "_safe_set_reanim_244": 0x395,
    "_safe_4739e0_ebx": 0x3A4,
    "_safe_473a40_stack": 0x3B1,
    "_safe_clr_eax5c": 0x3D0,
    "_safe_fstp_sub140_eax38": 0x3DC,
    "_safe_81cc50_reanim_pos": 0x3EF,
    "_safe_920699_cmp": 0x422,
    "_safe_923c55_reanim": 0x438,
    "_safe_9a046b_coin": 0x44F,
    "_safe_9a047b_coin": 0x45F,
    "_safe_set_coin_3f": 0x46E,
    "_safe_set_coin_40": 0x47A,
    "_safe_9a0819_proj": 0x486,
    "_safe_9b0029_proj": 0x49B,
    "_safe_9b008b_proj": 0x4BF,
    "_safe_portrait_b1718b": 0x4E3,
    "_safe_portrait_8140ab": 0x4F8,
    "_fix_menu_hittest": 0x54E,
    "_fix_menu_mousedown": 0x579,
    "_fix_menu_mouseup": 0x5A2,
    "_fix_cutscene_end_crazydave": 0x5D0,
    "_fix_board_crazydave_update": 0x611,
}


def va2raw(va: int) -> int:
    if va < 0x00794000:
        return va - 0x00400000
    return va - 0x004B7000


def sym(name: str) -> int:
    return CAVE_BASE_VA + FIXES_SYM_OFFSETS[name]


def jmp_rel32(from_va: int, to_va: int, nop_pad: int = 0) -> bytes:
    rel = to_va - (from_va + 5)
    return b"\xe9" + struct.pack("<i", rel) + (b"\x90" * nop_pad)


def call_rel32(from_va: int, to_va: int, nop_pad: int = 0) -> bytes:
    rel = to_va - (from_va + 5)
    return b"\xe8" + struct.pack("<i", rel) + (b"\x90" * nop_pad)


def _find_mingw_tool(name: str):
    env_key = "MINGW_" + ("GCC" if "gcc" in name else "OBJCOPY")
    p = os.environ.get(env_key) or shutil.which(name)
    if p:
        return p
    w64 = os.path.join(os.environ.get("W64DEVKIT_BIN", ""), name + ".exe")
    return w64 if os.path.isfile(w64) else None


def load_fixes_cave_blob() -> bytes:
    blob = bytes.fromhex(FIXES_CAVE_HEX)
    if hashlib.sha256(blob).hexdigest() != FIXES_CAVE_SHA256:
        raise RuntimeError("Embedded cave_fixes blob failed SHA-256 verification")
    asm_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cave_fixes.S")
    gcc = _find_mingw_tool("i686-w64-mingw32-gcc")
    objcopy = _find_mingw_tool("i686-w64-mingw32-objcopy") or _find_mingw_tool("objcopy")
    if os.path.isfile(asm_path) and gcc and objcopy:
        with tempfile.TemporaryDirectory() as td:
            obj_p = os.path.join(td, "cave_fixes.o")
            bin_p = os.path.join(td, "cave_fixes.bin")
            subprocess.run([gcc, "-c", asm_path, "-o", obj_p], check=True)
            subprocess.run([objcopy, "-O", "binary", "--only-section=.text", obj_p, bin_p], check=True)
            compiled = open(bin_p, "rb").read()
            if compiled != blob:
                raise RuntimeError("cave_fixes.S compiled bytes differ from verified FIXES_CAVE_HEX")
    return blob


def patch_bytes(buf: bytearray, va: int, expected: bytes, replacement: bytes, label: str):
    assert len(expected) == len(replacement), f"{label}: length mismatch {len(expected)} != {len(replacement)}"
    raw = va2raw(va)
    actual = bytes(buf[raw : raw + len(expected)])
    if actual != expected:
        raise RuntimeError(
            f"{label} @ VA {hex(va)} (raw {hex(raw)}): expected {expected.hex()}, got {actual.hex()}"
        )
    buf[raw : raw + len(replacement)] = replacement


def patch_exe_fixes(in_exe: str, out_exe: str, cave_bin: bytes | None = None):
    if cave_bin is None:
        cave_bin = load_fixes_cave_blob()

    with open(in_exe, "rb") as f:
        buf = bytearray(f.read())

    # Inject fixes cave at 0x00b50400..0x00b50fff (runtime LUT at 0x00b51000..0x00b51a04)
    cave_raw = va2raw(CAVE_BASE_VA)
    if len(cave_bin) > 0xC00:
        raise RuntimeError(f"Fixes cave too large ({len(cave_bin)} bytes), overlaps 0x00b51000 LUT!")
    if any(buf[cave_raw : cave_raw + 0x1800]):
        raise RuntimeError("Cave region 0x00b50400..0x00b51c00 is not empty (already fixes-patched?)")

    buf[cave_raw : cave_raw + len(cave_bin)] = cave_bin

    # ------------------------------------------------------------------
    # Fix 1: Remove 3D Acceleration & Fullscreen from NewOptionsDialog
    # ------------------------------------------------------------------
    patch_bytes(
        buf, 0x0045C7ED,
        bytes.fromhex("8b8e6401000085c974088b018b106a01ffd28b8e6801000085c974088b018b106a01ffd2"),
        b"\xeb\x22" + b"\x90" * 34,
        "Options AddedToManager skip 3D/Fullscreen"
    )
    patch_bytes(
        buf, 0x0045C8ED,
        bytes.fromhex("8b8e680100008b068b500c518bceffd28b8e640100008b068b500c518bceffd2"),
        b"\xeb\x1e" + b"\x90" * 30,
        "Options RemovedFromManager skip 3D/Fullscreen"
    )
    patch_bytes(
        buf, 0x0045CA2E,
        bytes.fromhex(
            "8b8e680100008b118b82a00000006a2d6a2e68af000000681b010000ffd0"
            "8b8e640100008b118b82a00000006a2d6a2e68ce000000681c010000ffd0"
        ),
        b"\xeb\x3a" + b"\x90" * 58,
        "Options Resize skip 3D/Fullscreen"
    )
    patch_bytes(
        buf, 0x0045CA7F + 1,
        struct.pack("<I", 0x000000F1),
        struct.pack("<I", 0x000000D4),
        "Options Resize center buttons vertically (base Y=212)"
    )
    patch_bytes(
        buf, 0x00961A1D + 1,
        struct.pack("<I", 0x0000011C),
        struct.pack("<I", 0x000000FF),
        "Options Resize Update button Y=255"
    )
    patch_bytes(
        buf, 0x0045CD72,
        bytes.fromhex("397c2464720d8b4c245051e818f41b0083c404"),
        jmp_rel32(0x0045CD72, sym("_fix_options_draw_skip"), nop_pad=14),
        "Options Draw skip 3D/Fullscreen labels"
    )

    # ------------------------------------------------------------------
    # Fix 2: Almanac O(1) LUT + eliminate page-table overflow & offscreen packets
    # ------------------------------------------------------------------
    patch_bytes(
        buf, 0x0087E700,
        bytes.fromhex("5731c08bf7"),
        jmp_rel32(0x0087E700, sym("_fix_almanac_draw_lookup")),
        "AlmanacDrawPlants O(1) LUT + off-page cull"
    )
    patch_bytes(
        buf, 0x0087EB00,
        bytes.fromhex("8bcb31c083"),
        jmp_rel32(0x0087EB00, sym("_fix_almanac_hit_lookup")),
        "AlmanacMouseHitTest O(1) LUT + off-page cull"
    )

    # ------------------------------------------------------------------
    # Fix 3: Fix Menu/DialogButton -0x8c mouse offset & Menu/Shovel clicks
    # ------------------------------------------------------------------
    patch_bytes(
        buf, 0x00876F00,
        bytes.fromhex("608b15c09e"),
        jmp_rel32(0x00876F00, sym("_fix_gamebutton_update")),
        "GameButton::Update shift custom overlay + parentless Menu"
    )
    patch_bytes(
        buf, 0x00411796,
        bytes.fromhex("385018742f"),
        jmp_rel32(0x00411796, sym("_fix_menu_hittest")),
        "Board::MouseHitTest direct Menu button rect hit-test"
    )
    patch_bytes(
        buf, 0x00411F97,
        bytes.fromhex("80781800742b"),
        jmp_rel32(0x00411F97, sym("_fix_menu_mousedown"), nop_pad=1),
        "Board::MouseDown direct Menu button rect hit-test"
    )
    patch_bytes(
        buf, 0x00412598,
        bytes.fromhex("807818000f8413010000"),
        jmp_rel32(0x00412598, sym("_fix_menu_mouseup"), nop_pad=5),
        "Board::MouseUp direct Menu button rect hit-test"
    )
    patch_bytes(
        buf, 0x0041181E,
        bytes.fromhex("8b8544010000"),
        jmp_rel32(0x0041181E, sym("_fix_shovel_before_seedbank"), nop_pad=1),
        "Board::MouseHitTest check Shovel before SeedBank"
    )
    patch_bytes(
        buf, 0x0043C3A7,
        bytes.fromhex("8b36e802330100"),
        jmp_rel32(0x0043C3A7, sym("_fix_cutscene_end_crazydave"), nop_pad=2),
        "CutScene end finalize stuck CrazyDave LEAVING state"
    )
    patch_bytes(
        buf, 0x00415DF0,
        bytes.fromhex("80bd64010000007435"),
        jmp_rel32(0x00415DF0, sym("_fix_board_crazydave_update"), nop_pad=4),
        "Board::Update safety net for CrazyDave LEAVING state"
    )

    # ------------------------------------------------------------------
    # Fix 4: I, Zombie infinite Buckethead free-plant array bounds (>= 0x200)
    # ------------------------------------------------------------------
    patch_bytes(
        buf, 0x0087C575,
        bytes.fromhex("81fb200300007d05"),
        bytes.fromhex("81fb000200007305"),
        "I-Zombie seed cost bound 0x320 -> 0x200"
    )
    patch_bytes(
        buf, 0x00ABC595,
        bytes.fromhex("608b1dc09e6a00"),
        jmp_rel32(0x00ABC595, sym("_fix_izombie_seed_bound"), nop_pad=2),
        "I-Zombie place check free-plant array bound < 0x200"
    )

    # ------------------------------------------------------------------
    # Fix 5: Hero Mode & Reanimation Fatal Error crash guards
    # ------------------------------------------------------------------
    bar_orig = bytes.fromhex("8b86cc00000031d2bbf0000000f7f38bd88b86c800000031d2f7f38bd8")
    for va in (0x00B16D87, 0x00B16F02, 0x00B17076, 0x00813CA7, 0x00813E22, 0x00813F96):
        patch_bytes(
            buf, va,
            bar_orig,
            call_rel32(va, sym("_hero_safe_bar_width")) + b"\xeb\x16" + b"\x90" * 22,
            f"Safe HP bar width @ {hex(va)}"
        )

    patch_bytes(
        buf, 0x00B15A68,
        bytes.fromhex("39ef0f8514000000"),
        jmp_rel32(0x00B15A68, sym("_hero_strdiv_b15a68"), nop_pad=3),
        "Safe StringWidth idiv @ 0xb15a68"
    )
    patch_bytes(
        buf, 0x00812988,
        bytes.fromhex("39ef0f8514000000"),
        jmp_rel32(0x00812988, sym("_hero_strdiv_812988"), nop_pad=3),
        "Safe StringWidth idiv @ 0x812988"
    )

    patch_bytes(
        buf, 0x00B14BB0,
        bytes.fromhex("8b44240485"),
        jmp_rel32(0x00B14BB0, sym("_safe_try_get_reanim")),
        "Safe ReanimTryToGet @ 0xb14bb0"
    )

    patch_bytes(
        buf, 0x009A054B,
        bytes.fromhex("837f3c040f8550000000"),
        jmp_rel32(0x009A054B, sym("_fix_hero_0x3e_reanim_guard"), nop_pad=5),
        "Hero 0x3e null Reanim guard @ 0x9a054b"
    )

    patch_bytes(
        buf, 0x0081D167,
        bytes.fromhex("f30f2d4038"),
        call_rel32(0x0081D167, sym("_safe_reanim_y_eax")),
        "Safe Reanim Y read @ 0x81d167"
    )
    for va in (0x0081D402, 0x0081D494, 0x0081D526, 0x0081D5B8, 0x0081D64A, 0x0081D6DC, 0x0081D76E):
        patch_bytes(
            buf, va,
            bytes.fromhex("f30f2d4838"),
            call_rel32(va, sym("_safe_reanim_y_ecx")),
            f"Safe Reanim Y read @ {hex(va)}"
        )

    for va in (0x00AAE6CD, 0x00AAE6E3, 0x00AAE6F9, 0x00AAE70F, 0x00AAE725):
        patch_bytes(
            buf, va,
            bytes.fromhex("c7804402000001000000"),
            call_rel32(va, sym("_safe_set_reanim_244"), nop_pad=5),
            f"Safe Reanim +0x244 write @ {hex(va)}"
        )

    reanim_4739e0_sites = [
        (0x008B2C3D, "e89e0dbcff"),
        (0x008B2C49, "e8920dbcff"),
        (0x008B3033, "e8a809bcff"),
        (0x008B303F, "e89c09bcff"),
        (0x008B3283, "e85807bcff"),
        (0x008B328F, "e84c07bcff"),
        (0x008B329B, "e84007bcff"),
        (0x008B32A7, "e83407bcff"),
    ]
    for va, exp_hx in reanim_4739e0_sites:
        patch_bytes(
            buf, va,
            bytes.fromhex(exp_hx),
            call_rel32(va, sym("_safe_4739e0_ebx")),
            f"Safe PlayReanim ebx @ {hex(va)}"
        )

    patch_bytes(
        buf, 0x008B32B4,
        bytes.fromhex("e88707bcff"),
        call_rel32(0x008B32B4, sym("_safe_473a40_stack")),
        "Safe PlayReanim stack @ 0x8b32b4"
    )
    patch_bytes(
        buf, 0x008B3CB2,
        bytes.fromhex("e889fdbbff"),
        call_rel32(0x008B3CB2, sym("_safe_473a40_stack")),
        "Safe PlayReanim stack @ 0x8b3cb2"
    )

    patch_bytes(
        buf, 0x0081B377,
        bytes.fromhex("c7405c00000000"),
        call_rel32(0x0081B377, sym("_safe_clr_eax5c"), nop_pad=2),
        "Safe Reanim +0x5c clr @ 0x81b377"
    )
    patch_bytes(
        buf, 0x0081C423,
        bytes.fromhex("d9eedaa640010000d95838"),
        call_rel32(0x0081C423, sym("_safe_fstp_sub140_eax38"), nop_pad=6),
        "Safe Reanim +0x38 fstp @ 0x81c423"
    )
    patch_bytes(
        buf, 0x0081C522,
        bytes.fromhex("d9eedaa640010000d95838"),
        call_rel32(0x0081C522, sym("_safe_fstp_sub140_eax38"), nop_pad=6),
        "Safe Reanim +0x38 fstp @ 0x81c522"
    )
    patch_bytes(
        buf, 0x0081CC50,
        bytes.fromhex("51f30f2d482c890dc0cc8100f30f2d4838890dc4cc810059"),
        call_rel32(0x0081CC50, sym("_safe_81cc50_reanim_pos"), nop_pad=19),
        "Safe Reanim XY read @ 0x81cc50"
    )
    patch_bytes(
        buf, 0x00920699,
        bytes.fromhex("83785c0061"),
        jmp_rel32(0x00920699, sym("_safe_920699_cmp")),
        "Safe Reanim +0x5c cmp @ 0x920699"
    )
    patch_bytes(
        buf, 0x00923C55,
        bytes.fromhex("8bf068e9728100"),
        jmp_rel32(0x00923C55, sym("_safe_923c55_reanim"), nop_pad=2),
        "Safe Reanim play @ 0x923c55"
    )

    patch_bytes(
        buf, 0x009A046B,
        bytes.fromhex("8958688b4f04"),
        jmp_rel32(0x009A046B, sym("_safe_9a046b_coin"), nop_pad=1),
        "Safe AddCoin deref @ 0x9a046b"
    )
    patch_bytes(
        buf, 0x009A047B,
        bytes.fromhex("e890c6a6ff897068c3"),
        jmp_rel32(0x009A047B, sym("_safe_9a047b_coin"), nop_pad=4),
        "Safe AddCoin deref @ 0x9a047b"
    )
    patch_bytes(
        buf, 0x009A088A,
        bytes.fromhex("c740683f000000"),
        call_rel32(0x009A088A, sym("_safe_set_coin_3f"), nop_pad=2),
        "Safe AddCoin deref 0x3f @ 0x9a088a"
    )
    patch_bytes(
        buf, 0x009A08A3,
        bytes.fromhex("c7406840000000"),
        call_rel32(0x009A08A3, sym("_safe_set_coin_40"), nop_pad=2),
        "Safe AddCoin deref 0x40 @ 0x9a08a3"
    )
    patch_bytes(
        buf, 0x009A0819,
        bytes.fromhex("e802cea6ffc6407403"),
        jmp_rel32(0x009A0819, sym("_safe_9a0819_proj"), nop_pad=4),
        "Safe AddProj deref @ 0x9a0819"
    )
    patch_bytes(
        buf, 0x009B0029,
        bytes.fromhex("e8f2d5a5ff8b8d4801000089889c000000"),
        jmp_rel32(0x009B0029, sym("_safe_9b0029_proj"), nop_pad=12),
        "Safe AddProj deref @ 0x9b0029"
    )
    patch_bytes(
        buf, 0x009B008B,
        bytes.fromhex("e890d5a5ff8b8d4801000089889c000000"),
        jmp_rel32(0x009B008B, sym("_safe_9b008b_proj"), nop_pad=12),
        "Safe AddProj deref @ 0x9b008b"
    )

    patch_bytes(
        buf, 0x00B1718B,
        bytes.fromhex("8b80301c00008b1c854367b100"),
        call_rel32(0x00B1718B, sym("_safe_portrait_b1718b"), nop_pad=8),
        "Hero portrait table clamp @ 0xb1718b"
    )
    patch_bytes(
        buf, 0x008140AB,
        bytes.fromhex("8b80301c00008b1c8563368100"),
        call_rel32(0x008140AB, sym("_safe_portrait_8140ab"), nop_pad=8),
        "Hero portrait table clamp @ 0x8140ab"
    )

    # ------------------------------------------------------------------
    # Fix 6: LAA (>2GB heap) signed-pointer crash in Reanimation atlas-ID checks
    # PlantsVsZombies.exe is LARGE_ADDRESS_AWARE, so Wine allocates MemoryImage*
    # pointers >= 0x80000000 during long/multi-mode sessions. PopCap's `cmp eax, 1000; jg`
    # treats bit-31 pointers as negative (<= 1000) and crashes at 0x00472CAC / 0x00472BEF.
    # Fix both sites to unsigned `ja` (0x7f -> 0x77).
    # ------------------------------------------------------------------
    patch_bytes(
        buf, 0x00472BDD,
        bytes.fromhex("3de80300007f0e"),
        bytes.fromhex("3de8030000770e"),
        "Reanimation LAA unsigned pointer check @ 0x472bdd (jg->ja)"
    )
    patch_bytes(
        buf, 0x00472C9A,
        bytes.fromhex("3de80300007f0e"),
        bytes.fromhex("3de8030000770e"),
        "Reanimation LAA unsigned pointer check @ 0x472c9a (jg->ja)"
    )

    os.makedirs(os.path.dirname(os.path.abspath(out_exe)), exist_ok=True)
    with open(out_exe, "wb") as f:
        f.write(buf)
    print(f"Fixes-patched {out_exe} ({len(buf):,} bytes)")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise SystemExit("Usage: python patch_exe_fixes.py <in_exe> <out_exe>")
    patch_exe_fixes(sys.argv[1], sys.argv[2])
