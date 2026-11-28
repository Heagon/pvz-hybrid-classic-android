#!/usr/bin/env python3
"""Performance, animation, SeedChooser culling, and transition patcher for PvZ Hybrid Classic v3.20.1."""
import hashlib
import os
import shutil
import struct
import subprocess
import sys
import tempfile

# Verified assembled machine code from cave_perf.S (VA 0x00b50000..0x00b5019c, 412 bytes).
CAVE_SHA256 = "f2c612899ce9f79a1ede25faab13ef9b7a1d970b4bec29902b2b1676003ef696"
# Verified compiled D3D7 batcher (256q) + state cache + 4-page Glyph Atlas + 12-page Sprite Atlas (MRU)
# + O(1) gdi42 + zero-SEH + always-LINEAR + 1-Quad Baked Seed-Card Atlas (4x1024)
# + Live 30/60/90/120 FPS Pacer + Occluded SeedChooser Culls + DrawTrianglesTex Reanim Atlas + HasSeedType O(1) Cache (VA 0x00b52000, 16964 bytes).
D3D_OPT_VA = 0x00B52000
D3D_OPT_SHA256 = "0c6768b219276a6f45eedfb6fa6df30b273baeb1f9fd0f39282ddfbb8d36ec8e"
CAVE_HEX = (
    "8b430485c0745b8b480885c974548b514883fa187c4cb8f001b5008b0841890889d8c1e80501c183fa3c7c2583fa6e7c"
    "0c83fd037c2abd01000000eb2583fd017e0883c503c1fd02eb18f6c1037511eb1183fd017e0545d1fdeb07f6c1017402"
    "31ed31ff897c241885ed7e07b886725100ffe0b8ad725100ffe090909090909090909090909090909090909090909090"
    "8b47080b470c25ffffff7f752c8b47108b4f1431d289068956048b0789460889560c894e108b4f04894e148956188956"
    "1cc746200000803fc35589e583e4f8b8f6204700ffe09090909090909090909090909090909090909090909090909090"
    "909090909090909090909090909090908b4d0839f17e1d39d17e128b874401000085c0740f83780c007d0989d1b808bb"
    "4300ffe0b839bb4300ffe090909090909090909090909090909090909090909083fe3074168b44242083f8287c0d3d30"
    "0200007f06684d484800c368dd484800c39090909090909090909090909090908b44241883f8f67c143d300200007f0d"
    "8b43206a006a01689f4a4800c3ddd88b74242068d84a4800c3909090"
)


def va2raw(va: int) -> int:
    if va < 0x00794000:
        return va - 0x00400000
    return va - 0x004B7000


def jmp_rel32(from_va: int, to_va: int, nop_pad: int = 0) -> bytes:
    rel = to_va - (from_va + 5)
    return b"\xe9" + struct.pack("<i", rel) + (b"\x90" * nop_pad)


def call_rel32(from_va: int, to_va: int, nop_pad: int = 0) -> bytes:
    rel = to_va - (from_va + 5)
    return b"\xe8" + struct.pack("<i", rel) + (b"\x90" * nop_pad)


def _find_w32_tool(name: str) -> str:
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cand = os.path.join(root, "tools", "w64devkit32", "w64devkit", "bin", name + ".exe")
    if os.path.isfile(cand):
        return cand
    found = shutil.which(name)
    if found:
        return found
    raise RuntimeError(f"Could not locate 32-bit MinGW tool: {name}")


def build_d3d_opt_blob() -> bytes:
    sdir = os.path.dirname(os.path.abspath(__file__))
    c_src = os.path.join(sdir, "cave_d3d_opt.c")
    s_src = os.path.join(sdir, "cave_d3d_tramp.S")
    ld_scr = os.path.join(sdir, "cave_d3d.ld")
    gcc = _find_w32_tool("gcc")
    ld = _find_w32_tool("ld")
    objcopy = _find_w32_tool("objcopy")
    with tempfile.TemporaryDirectory() as td:
        opt_o = os.path.join(td, "opt.o")
        tramp_o = os.path.join(td, "tramp.o")
        pe_out = os.path.join(td, "d3d_opt.pe")
        bin_out = os.path.join(td, "d3d_opt.bin")
        subprocess.run([
            gcc, "-m32", "-O2", "-ffreestanding", "-fno-builtin", "-fno-pic",
            "-fno-stack-protector", "-fno-exceptions", "-fno-asynchronous-unwind-tables",
            "-fno-tree-loop-distribute-patterns", "-c", c_src, "-o", opt_o
        ], check=True)
        subprocess.run([gcc, "-m32", "-c", s_src, "-o", tramp_o], check=True)
        subprocess.run([
            ld, "-T", ld_scr, "-nostdlib", "--image-base", "0",
            "-e", "_entry_glyph_atlas_draw", tramp_o, opt_o, "-o", pe_out
        ], check=True)
        subprocess.run([objcopy, "-O", "binary", "-j", ".text", "-j", ".data", pe_out, bin_out], check=True)
        blob = open(bin_out, "rb").read()
    got_sha = hashlib.sha256(blob).hexdigest()
    if got_sha != D3D_OPT_SHA256:
        raise RuntimeError(f"cave_d3d_opt blob SHA-256 mismatch: got {got_sha}, expected {D3D_OPT_SHA256}")
    return blob


def load_cave_blob() -> bytes:
    blob = bytes.fromhex(CAVE_HEX)
    if hashlib.sha256(blob).hexdigest() != CAVE_SHA256:
        raise RuntimeError("Embedded cave_perf blob failed SHA-256 verification")
    asm_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cave_perf.S")
    gcc = os.environ.get("MINGW_GCC") or shutil.which("i686-w64-mingw32-gcc")
    objcopy = os.environ.get("MINGW_OBJCOPY") or shutil.which("objcopy")
    if os.path.isfile(asm_path) and gcc and objcopy:
        with tempfile.TemporaryDirectory() as td:
            obj_p = os.path.join(td, "cave.o")
            bin_p = os.path.join(td, "cave.bin")
            subprocess.run([gcc, "-c", asm_path, "-o", obj_p], check=True)
            subprocess.run([objcopy, "-O", "binary", "--only-section=.text", obj_p, bin_p], check=True)
            compiled = open(bin_p, "rb").read()
            if compiled != blob:
                raise RuntimeError("cave_perf.S compiled bytes differ from verified CAVE_HEX")
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


def patch_exe_perf(in_exe: str, out_exe: str, cave_bin: bytes | None = None):
    if cave_bin is None:
        cave_bin = load_cave_blob()

    with open(in_exe, "rb") as f:
        buf = bytearray(f.read())

    # Inject verified code caves at RWX .newHE VA 0x00b50000..0x00b5019c (counter at 0x00b501f0)
    cave_va = 0x00B50000
    cave_raw = va2raw(cave_va)
    if len(cave_bin) > 0x1E0:
        raise RuntimeError(f"Cave blob too big ({len(cave_bin)} bytes), overlaps 0x00b501f0 counter!")
    if any(buf[cave_raw : cave_raw + 0x400]):
        raise RuntimeError("Cave region 0x00b50000..0x00b50400 is not empty (already perf-patched?)")

    buf[cave_raw : cave_raw + len(cave_bin)] = cave_bin

    # Inject D3D7 state cache + hybrid quad batcher + 4-page Glyph Atlas + 12-page Universal Sprite Atlas
    # + O(1) gdi42 + zero-SEH + SeedPacket Display-List Cache + Live 30/60/90/120 FPS Pacer
    # @ VA 0x00b52000 (code < 0x6000, BSS @ 0x00b58000..0x00ca6000)
    d3d_blob = build_d3d_opt_blob()
    d3d_raw = va2raw(D3D_OPT_VA)
    if len(d3d_blob) > 0x6000:
        raise RuntimeError(f"D3D opt blob too big ({len(d3d_blob)} bytes), overlaps 0x00b58000 BSS!")
    if any(buf[d3d_raw : d3d_raw + 0x1B0000]):
        raise RuntimeError("D3D opt region 0x00b52000..0x00d02000 is not empty (already patched?)")
    buf[d3d_raw : d3d_raw + len(d3d_blob)] = d3d_blob

    # 1. Live selectable 30 / 60 / 90 / 120 FPS engine pacer (preserving exact 100 Hz DoUpdateFrames logic!),
    #    and bypass 0.75 early-wake multiplier at 0x00551d64 (preserving 0x00551d5b mHasPendingDraw check).
    patch_bytes(
        buf, 0x009F0029,
        b"\xb8\x3c\x00\x00\x00",
        b"\xb8\x3c\x00\x00\x00",
        "ProcessSafe 60 FPS draw ceiling verify"
    )
    patch_bytes(
        buf, 0x00551AC7,
        bytes.fromhex("80beb8050000007441"),
        jmp_rel32(0x00551AC7, D3D_OPT_VA + 0x98, nop_pad=4),
        "ProcessSafe live 30/60/90/120 FPS target hook"
    )
    patch_bytes(
        buf, 0x00551E18,
        bytes.fromhex("8b168b42248bceffd0"),
        jmp_rel32(0x00551E18, D3D_OPT_VA + 0xA0, nop_pad=4),
        "ProcessSafe exact 100 Hz logic gate for 120 FPS"
    )
    patch_bytes(
        buf, 0x00551D64,
        bytes.fromhex("dd442438"),
        bytes.fromhex("eb179090"),
        "ProcessSafe bypass 0.75 early-wake scale"
    )

    # 1b. Eliminate dummy backbuffer Lock+Unlock GPU readback stall in DDInterface::Redraw @ 0x005630ed
    patch_bytes(
        buf, 0x005630ED,
        bytes.fromhex(
            "8b4768536a118d94240401000052899c2408010000c78424080100006c000000"
            "8b0853508b4164ffd08b47688b088b91800000005350ffd2"
        ),
        b"\xeb\x36" + (b"\x90" * 54),
        "DDInterface::Redraw skip dummy backbuffer Lock+Unlock"
    )

    # 1c. D3D7 SetupDrawMode state cache @ 0x005681a0 -> 0x00b52008
    patch_bytes(
        buf, 0x005681A0,
        bytes.fromhex("837c240400"),
        jmp_rel32(0x005681A0, D3D_OPT_VA + 0x08),
        "D3DInterface::SetupDrawMode state cache"
    )

    # 1d. D3D7 SetTexture(0, tex) cache across all 8 call sites -> 0x00b52010
    settex_sites = [
        (0x00564E2C, "ffd250bf281a6700e8a7f6ffff"),
        (0x00566435, "ffd050bf901a6700e89ee0ffff"),
        (0x00567091, "ffd150bf901a6700e842d4ffff"),
        (0x00567282, "ffd050bf901a6700e851d2ffff"),
        (0x00567BD1, "ffd050bf901a6700e802c9ffff"),
        (0x0056891B, "ffd250bf281a6700e8b8bbffff"),
        (0x00568B94, "ffd050bf281a6700e83fb9ffff"),
        (0x00568C5D, "ffd250bf281a6700e876b8ffff"),
    ]
    for va, exp_hx in settex_sites:
        patch_bytes(
            buf, va,
            bytes.fromhex(exp_hx),
            call_rel32(va, D3D_OPT_VA + 0x10) + b"\x50" + (b"\x90" * 7),
            f"D3D7 SetTexture cache @ {hex(va)}"
        )

    # 1e. D3D7 Quad Batcher across all 3 TRIANGLESTRIP(4) sites -> 0x00b52018
    quad_sites = [
        (0x0056645C, "ffd050bfa41a6700e877e0ffff"),
        (0x005670C1, "ffd150bfd41a6700e812d4ffff"),
        (0x00568BBD, "ffd050bf541b6700e816b9ffff"),
    ]
    for va, exp_hx in quad_sites:
        patch_bytes(
            buf, va,
            bytes.fromhex(exp_hx),
            call_rel32(va, D3D_OPT_VA + 0x18) + b"\x50" + (b"\x90" * 7),
            f"D3D7 Quad Batcher @ {hex(va)}"
        )

    # 1f. Flush quad batch before all 6 non-quad DrawPrimitive sites -> 0x00b52020
    other_draw_sites = [
        (0x00566B27, "ffd150bfbc1a6700e8acd9ffff"),
        (0x005674E3, "ffd250bfec1a6700e8f0cfffff"),
        (0x00567587, "ffd150bf0c1b6700e84ccfffff"),
        (0x00567C03, "ffd050bf241b6700e8d0c8ffff"),
        (0x00568944, "ffd250bf3c1b6700e88fbbffff"),
        (0x00568DE8, "ffd050bf6c1b6700e8ebb6ffff"),
    ]
    for va, exp_hx in other_draw_sites:
        patch_bytes(
            buf, va,
            bytes.fromhex(exp_hx),
            call_rel32(va, D3D_OPT_VA + 0x20) + b"\x50" + (b"\x90" * 7),
            f"D3D7 Flush+DrawPrimitive @ {hex(va)}"
        )

    # 1g. Lock SetLinearFilter always-LINEAR (0x5661b0 -> +0x88) + flush on init (0x5661bb),
    #     DrawPool wrap (0x46a606), D3DInterface::Flush EndScene (0x568ec0), and ReleaseTextures (0x565a10)
    patch_bytes(
        buf, 0x005661B0,
        bytes.fromhex("51381d519f6a00"),
        jmp_rel32(0x005661B0, D3D_OPT_VA + 0x88, nop_pad=2),
        "D3D7 SetLinearFilter always-LINEAR lock"
    )
    patch_bytes(
        buf, 0x005661BB,
        bytes.fromhex("33c084db0f95c0"),
        call_rel32(0x005661BB, D3D_OPT_VA + 0x28, nop_pad=2),
        "D3D7 SetLinFilt flush"
    )
    patch_bytes(
        buf, 0x0046A606,
        bytes.fromhex("8b46208b10"),
        call_rel32(0x0046A606, D3D_OPT_VA + 0x30),
        "D3D7 DrawPool wrap flush"
    )
    patch_bytes(
        buf, 0x00568EC0,
        bytes.fromhex("807e3c00741d"),
        jmp_rel32(0x00568EC0, D3D_OPT_VA + 0x38, nop_pad=1),
        "D3DInterface::Flush EndScene batch flush + cache reset"
    )
    patch_bytes(
        buf, 0x00565A10,
        bytes.fromhex("5356578bf8"),
        jmp_rel32(0x00565A10, D3D_OPT_VA + 0x40),
        "TextureData::ReleaseTextures cache invalidation"
    )
    for va in (0x00565655, 0x00567E89):
        r = va2raw(va)
        s = bytes(buf[r : r + 13])
        if not (s[0] == 0xFF and s[2] == 0x50 and s[3] == 0xBF and s[8] == 0xE8):
            raise RuntimeError(f"Lock Texture @ VA {hex(va)} does not match expected 13-byte CheckDXError site")
        buf[r : r + 13] = call_rel32(va, D3D_OPT_VA + 0x48) + b"\x50" + (b"\x90" * 7)

    # 1h. Universal Sprite Texture Atlas hooks: D3DInterface::Blt, BltTransformed, MemoryImage::~MemoryImage
    patch_bytes(
        buf, 0x005681F0,
        bytes.fromhex("837f54005355"),
        jmp_rel32(0x005681F0, D3D_OPT_VA + 0x50, nop_pad=1),
        "Universal Sprite Atlas D3DInterface::Blt remap"
    )
    patch_bytes(
        buf, 0x00568520,
        bytes.fromhex("558bec83e4f8"),
        jmp_rel32(0x00568520, D3D_OPT_VA + 0x58, nop_pad=1),
        "Universal Sprite Atlas D3DInterface::BltTransformed remap"
    )
    patch_bytes(
        buf, 0x00590430,
        bytes.fromhex("6aff68788c6400"),
        jmp_rel32(0x00590430, D3D_OPT_VA + 0x60, nop_pad=2),
        "Universal Sprite & Glyph Atlas MemoryImage::~MemoryImage eviction"
    )

    # 1i. Zero-SEH fast paths for CreateImageTexture (0x00567cf0 -> +0x68) & D3DCheckError (0x005644e0 -> +0x70)
    patch_bytes(
        buf, 0x00567CF0,
        bytes.fromhex("6aff6883d86400"),
        jmp_rel32(0x00567CF0, D3D_OPT_VA + 0x68, nop_pad=2),
        "D3DInterface::CreateImageTexture zero-SEH fast path"
    )
    patch_bytes(
        buf, 0x005644E0,
        bytes.fromhex("6aff6858a56400"),
        jmp_rel32(0x005644E0, D3D_OPT_VA + 0x70, nop_pad=2),
        "D3DCheckError zero-SEH fast path"
    )

    # 1j. 1-Quad Baked Seed-Card Atlas for DrawSeedPacket (0x004876f0 -> +0x90)
    patch_bytes(
        buf, 0x004876F0,
        bytes.fromhex("6aff687fe86400"),
        jmp_rel32(0x004876F0, D3D_OPT_VA + 0x90, nop_pad=2),
        "DrawSeedPacket 1-Quad Baked Card Atlas"
    )

    # 1k. Zero-visual-loss occluded PoolEffectDraw cull during SeedChooser (0x00469de0 -> +0xa8)
    patch_bytes(
        buf, 0x00469DE0,
        bytes.fromhex("558bec83e4f8"),
        jmp_rel32(0x00469DE0, D3D_OPT_VA + 0xA8, nop_pad=1),
        "PoolEffectDraw occluded SeedChooser cull"
    )

    # 1l. Board::Draw occluded quad cull behind SeedChooser wooden panel (0x00416880 -> +0xb0)
    patch_bytes(
        buf, 0x00416880,
        bytes.fromhex("558bec83e4f8"),
        jmp_rel32(0x00416880, D3D_OPT_VA + 0xB0, nop_pad=1),
        "Board::Draw occluded SeedChooser quad cull"
    )

    # 1m. SeedChooserScreen::Draw Loop-2 early off-screen card cull (0x004849e5 -> +0xb8)
    patch_bytes(
        buf, 0x004849E5,
        bytes.fromhex("8b5424148b7320"),
        jmp_rel32(0x004849E5, D3D_OPT_VA + 0xB8, nop_pad=2),
        "SeedChooser::Draw Loop 2 early off-screen cull"
    )

    # 1n. D3DInterface::DrawTrianglesTex Universal Sprite Atlas + Zero-SEH Batcher (0x00568e30 -> +0xc0)
    patch_bytes(
        buf, 0x00568E30,
        bytes.fromhex("53558b6c240c"),
        jmp_rel32(0x00568E30, D3D_OPT_VA + 0xC0, nop_pad=1),
        "D3DInterface::DrawTrianglesTex Sprite Atlas + Batcher"
    )

    # 1o. HasSeedType 1/frame recount throttle + O(1) memoization (0x00930000 -> +0xc8)
    patch_bytes(
        buf, 0x00930000,
        bytes.fromhex("60bd00080000"),
        jmp_rel32(0x00930000, D3D_OPT_VA + 0xC8, nop_pad=1),
        "HasSeedType 1/frame recount throttle + O(1) cache"
    )

    # 2. Hook TodParticleEmitter::UpdateSpawning @ 0x0051727c -> cave 0x00b50000
    patch_bytes(
        buf, 0x0051727C,
        bytes.fromhex("33ff85ed897c24187e27"),
        jmp_rel32(0x0051727C, 0x00B50000, nop_pad=5),
        "TodParticleEmitter::UpdateSpawning throttle"
    )

    # 3. Hook Reanimation::MatrixFromTransform @ 0x004720f0 -> cave 0x00b50090 (zero-angle fast path)
    patch_bytes(
        buf, 0x004720F0,
        bytes.fromhex("558bec83e4f8"),
        jmp_rel32(0x004720F0, 0x00B50090, nop_pad=1),
        "Reanimation::MatrixFromTransform zero-angle fast path"
    )

    # 3b. Hook CutScene::Update SeedBank slide @ 0x0043bafd -> cave 0x00b50100 (failsafe clamp)
    patch_bytes(
        buf, 0x0043BAFD,
        bytes.fromhex("8b4d083bce7e353bca7f31"),
        jmp_rel32(0x0043BAFD, 0x00B50100, nop_pad=6),
        "CutScene::Update SeedBank slide failsafe"
    )

    # 3c. Hook SeedChooserScreen::Draw Loops 1 & 2 @ 0x00484844 / 0x00484a98 -> off-screen card culling
    patch_bytes(
        buf, 0x00484844,
        bytes.fromhex("83fe300f8490000000"),
        jmp_rel32(0x00484844, 0x00B50140, nop_pad=4),
        "SeedChooser::Draw Loop 1 off-screen cull"
    )
    patch_bytes(
        buf, 0x00484A98,
        bytes.fromhex("8b43206a006a01"),
        jmp_rel32(0x00484A98, 0x00B50170, nop_pad=2),
        "SeedChooser::Draw Loop 2 off-screen cull"
    )

    # 4. Snappy SelectorScreen Adventure zombie-hand transition (4.5s -> 0.20s, laugh 1.25s -> 0.05s)
    patch_bytes(buf, 0x0044B322, b"\x3d\xc2\x01\x00\x00", b"\x3d\x14\x00\x00\x00", "SelectorScreen Adv 450->20")
    patch_bytes(buf, 0x0044B45F, bytes.fromhex("83bdc40000007d"), bytes.fromhex("83bdc400000005"), "SelectorScreen Laugh 125->5")

    # 5. Snappy SeedChooserScreen::Update ViewLawn pan (3.5s -> 0.70s, 1/5 scale keeping curve continuity)
    patch_bytes(buf, 0x00484C6F, b"\x83\xf8\x64", b"\x83\xf8\x14", "SeedChooser cmp 100->20 (1)")
    patch_bytes(buf, 0x00484E05, b"\x3d\xfb\x00\x00\x00", b"\x3d\x33\x00\x00\x00", "SeedChooser cmp 251->51")
    patch_bytes(buf, 0x00484E0C, bytes.fromhex("c7853c0d0000fa000000"), bytes.fromhex("c7853c0d000032000000"), "SeedChooser set 250->50")
    patch_bytes(buf, 0x00484E1C, b"\x83\xf8\x64", b"\x83\xf8\x14", "SeedChooser cmp 100->20 (2)")
    patch_bytes(buf, 0x00484E43, b"\xb9\x64\x00\x00\x00", b"\xb9\x14\x00\x00\x00", "SeedChooser mov ecx 100->20")
    patch_bytes(buf, 0x00484E7E, b"\xb9\x28\x00\x00\x00", b"\xb9\x08\x00\x00\x00", "SeedChooser mov ecx 40->8")
    patch_bytes(buf, 0x00484EAE, b"\x3d\xfa\x00\x00\x00", b"\x3d\x32\x00\x00\x00", "SeedChooser cmp 250->50")
    patch_bytes(buf, 0x00484EEF, b"\x3d\x5e\x01\x00\x00", b"\x3d\x46\x00\x00\x00", "SeedChooser cmp 350->70")
    patch_bytes(buf, 0x00484F2D, bytes.fromhex("b95e010000578d519c"), bytes.fromhex("b946000000578d51ec"), "SeedChooser pan back 350->70 -20")
    patch_bytes(buf, 0x00484F65, bytes.fromhex("b95e01000068040200008d51d8"), bytes.fromhex("b94600000068040200008d51f8"), "SeedChooser fade back 350->70 -8")
    # Sync CancelLawnView (0x48660f), MouseDown (0x4867d7), KeyChar (0x486ebf) with scaled (20, 50, 51) ViewLawn timer!
    patch_bytes(
        buf, 0x0048660F,
        bytes.fromhex("83f8647e113dfa0000007f0ac7813c0d0000fb000000"),
        bytes.fromhex("83f8147e113d320000007f0ac7813c0d000033000000"),
        "SeedChooser CancelLawnView 100/250/251 -> 20/50/51"
    )
    patch_bytes(
        buf, 0x004867D7,
        bytes.fromhex("83f8640f8ee50400003dfa0000000f8fda040000c7863c0d0000fb000000"),
        bytes.fromhex("83f8140f8ee50400003d320000000f8fda040000c7863c0d000033000000"),
        "SeedChooser MouseDown ViewLawn 100/250/251 -> 20/50/51"
    )
    patch_bytes(
        buf, 0x00486EBF,
        bytes.fromhex("83f8647e113dfa0000007f0ac7813c0d0000fb000000"),
        bytes.fromhex("83f8147e113d320000007f0ac7813c0d000033000000"),
        "SeedChooser KeyChar ViewLawn 100/250/251 -> 20/50/51"
    )

    # 6. Snappy CutScene camera pan & pre-roll (~8s -> ~2.6s including 1.4s Ready-Set-Plant)
    patch_bytes(buf, 0x0043B7ED + 2, struct.pack("<i", 1500), struct.pack("<i", 200), "CutScene 0x43b7ed 1500->200")
    patch_bytes(buf, 0x0043C439 + 1, struct.pack("<i", 1500), struct.pack("<i", 200), "CutScene 0x43c439 1500->200")
    patch_bytes(buf, 0x0043C459 + 1, struct.pack("<i", 1500), struct.pack("<i", 200), "CutScene 0x43c459 1500->200")
    patch_bytes(
        buf, 0x006A4FFC,
        struct.pack("<5I", 3500, 2000, 3500, 5500, 5890),
        struct.pack("<5I", 600, 250, 600, 1000, 1000),
        "CutScene base table"
    )
    crt_adders = [
        (0x64FC75 + 1, 750, 50),
        (0x64FC85 + 1, 500, 50),
        (0x64FC95 + 1, 750, 100),
        (0x64FCA5 + 1, 500, 50),
        (0x64FCB5 + 1, 250, 50),
        (0x64FCC5 + 1, 250, 50),
        (0x64FCD5 + 1, 250, 50),
        (0x64FD15 + 1, 1500, 350),
        (0x64FD55 + 1, 2000, 400),
        (0x64FD75 + 1, 1000, 200),
        (0x64FDE5 + 1, 1830, 1400),
        (0x64FE05 + 1, 500, 100),
        (0x64FE15 + 1, 750, 150),
        (0x64FE25 + 1, 500, 100),
        (0x64FE35 + 1, 750, 150),
        (0x64FE55 + 1, 2500, 500),
        (0x64FE65 + 1, 1000, 200),
        (0x64FE75 + 1, 1000, 200),
        (0x64FE85 + 1, 3000, 500),
        (0x64FEA5 + 1, 400, 100),
        (0x64FEB5 + 1, 6000, 1000),
        (0x64FEC5 + 1, 5000, 800),
        (0x64FED5 + 1, 1000, 200),
        (0x64FEE5 + 1, 2000, 400),
    ]
    for addr, orig_v, new_v in crt_adders:
        patch_bytes(buf, addr, struct.pack("<i", orig_v), struct.pack("<i", new_v), f"CutScene CRT {hex(addr)}")

    # 7. Fix scaled subtractive offsets & end-of-cutscene margin so Dave/Sod/SeedBank stay positive
    patch_bytes(buf, 0x0043AF25 + 2, struct.pack("<i", -1500), struct.pack("<i", -200), "CutScene Dave pre-time -1500->-200")
    patch_bytes(buf, 0x0043C0D7 + 2, struct.pack("<i", -2000), struct.pack("<i", -300), "CutScene post-sod -2000->-300")
    patch_bytes(
        buf, 0x0064FE40,
        bytes.fromhex("a164a26a00a380a26a00c3cccccccccc"),
        bytes.fromhex("a164a26a0005c8000000a380a26a00c3"),
        "CutScene CRT 0x6aa280 = 0x6aa264 + 200"
    )

    os.makedirs(os.path.dirname(os.path.abspath(out_exe)), exist_ok=True)
    with open(out_exe, "wb") as f:
        f.write(buf)
    print(f"Perf-patched {out_exe} ({len(buf):,} bytes)")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise SystemExit("Usage: python patch_exe_perf.py <in_exe> <out_exe>")
    patch_exe_perf(sys.argv[1], sys.argv[2])
