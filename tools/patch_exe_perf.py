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

    # 1. Decouple render pacing to 30 FPS (0x3c -> 0x1e) while keeping 100 Hz DoUpdateFrames logic,
    #    and bypass 0.75 early-wake multiplier at 0x00551d64 (preserving 0x00551d5b mHasPendingDraw check).
    patch_bytes(
        buf, 0x009F0029,
        b"\xb8\x3c\x00\x00\x00",
        b"\xb8\x1e\x00\x00\x00",
        "ProcessSafe 30 FPS draw cap"
    )
    patch_bytes(
        buf, 0x00551D64,
        bytes.fromhex("dd442438"),
        bytes.fromhex("eb179090"),
        "ProcessSafe bypass 0.75 early-wake scale"
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
