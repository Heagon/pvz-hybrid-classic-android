"""Relocate hardcoded Chinese UI strings in PlantsVsZombies.exe into .newHE trailing zero space (UTF-8)
and update verified x86 immediate / pointer-table references for English [EN] and Vietnamese [VI]."""
import json
import os
import pathlib
import struct
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SAFE_REF_KINDS = {
    "push_imm32",
    "mov_reg_imm32",
    "lea_reg_mem32",
    "mov_mem32_imm32",
    "mov_regdisp8_imm32",
    "mov_regdisp32_imm32",
    "mov_sibdisp32_imm32",
    "mov_sibdisp8_imm32",
    "mov_regind_imm32",
    "aligned_ptr_table",
    "unaligned_ptr_table",
}


def load_translations(translations_path=None):
    candidates = []
    if translations_path:
        candidates.append(pathlib.Path(translations_path))
    candidates.extend([
        pathlib.Path(ROOT) / "translations" / "strings_exe.json",
        pathlib.Path(ROOT) / "work" / "strings_exe.json",
    ])
    for p in candidates:
        if p.is_file():
            return json.loads(p.read_text(encoding="utf-8"))
    raise FileNotFoundError(f"Could not locate strings_exe.json in {[str(c) for c in candidates]}")


def load_verified_catalog(catalog_path=None):
    candidates = []
    if catalog_path:
        candidates.append(pathlib.Path(catalog_path))
    candidates.extend([
        pathlib.Path(ROOT) / "work" / "exe_verified_all.json",
        pathlib.Path(ROOT) / "work" / "exe_verified_strings.json",
    ])
    for p in candidates:
        if p.is_file():
            return json.loads(p.read_text(encoding="utf-8"))
    raise FileNotFoundError(f"Could not locate verified EXE catalog in {[str(c) for c in candidates]}")


def patch_pvz_exe(
    lang: str,
    out_exe_path: str,
    src_exe_path: str = None,
    catalog_path: str = None,
    translations_path: str = None,
):
    assert lang in ("en", "vi")
    src_exe = src_exe_path or os.path.join(ROOT, "work", "he_extracted", "PlantsVsZombies.exe")
    buf = bytearray(open(src_exe, "rb").read())
    verified = load_verified_catalog(catalog_path)
    translations = load_translations(translations_path)

    spans = sorted((int(it["off"], 16), int(it["off"], 16) + it["len_bytes"] + 1) for it in verified)
    for (s1, e1), (s2, e2) in zip(spans, spans[1:]):
        assert e1 <= s2, f"Overlapping string slots: (0x{s1:x}..0x{e1:x}) vs (0x{s2:x}..0x{e2:x})"

    pe_off = struct.unpack_from("<I", buf, 0x3C)[0]
    nsec = struct.unpack_from("<H", buf, pe_off + 6)[0]
    opt_sz = struct.unpack_from("<H", buf, pe_off + 20)[0]
    img_base = struct.unpack_from("<I", buf, pe_off + 52)[0]
    sec_off = pe_off + 24 + opt_sz

    newhe_va = newhe_rptr = newhe_rsz = None
    for i in range(nsec):
        s = buf[sec_off + i * 40 : sec_off + (i + 1) * 40]
        nm = s[:8].rstrip(b"\x00").decode("ascii", "ignore")
        vsz, rva, rsz, rptr = struct.unpack_from("<IIII", s, 8)
        if nm == ".newHE":
            newhe_va = img_base + rva
            newhe_rptr = rptr
            newhe_rsz = rsz
            break
    assert newhe_va is not None

    pool_off = 0xA60000
    pool_limit = newhe_rptr + newhe_rsz - 256
    assert all(b == 0 for b in buf[pool_off : pool_off + 0x35000]), "Expected zero pool in .newHE!"

    allocated_va = {}
    patched_strings = 0
    patched_refs = 0
    patched_len_pushes = 0
    inplace_strings = 0

    # Non-adjacent `push <orig_len>; ...; push <va>` std::string(ptr, len) sites in PlantsVsZombies.exe
    # Value is byte delta backwards from <va> ref_off (so 0x68 is at roff-1, 0x6a at roff-1-delta, len byte at roff-delta)
    NONADJ_PUSH_DELTAS = {
        0x330FD: 9,
        0x50347: 7,
        0x52E11: 7,
        0x1A70E1: 3,
    }
    orig_buf = bytes(buf)

    for item in verified:
        cn_txt = item["text"]
        if cn_txt not in translations:
            continue
        new_txt = translations[cn_txt][lang]
        new_bytes = new_txt.encode("utf-8")

        orig_off = int(item["off"], 16)
        orig_len = item["len_bytes"]
        safe_refs = [r for r in item["refs"] if r["kind"] in SAFE_REF_KINDS]

        def patch_std_string_length_pushes():
            nonlocal patched_len_pushes
            for r in safe_refs:
                roff = int(r["ref_off"], 16)
                if orig_len <= 0 or roff < 3 or orig_buf[roff - 1] != 0x68:
                    continue
                len_byte_off = None
                if orig_buf[roff - 3] == 0x6A and orig_buf[roff - 2] == orig_len:
                    len_byte_off = roff - 2
                elif roff in NONADJ_PUSH_DELTAS:
                    d = NONADJ_PUSH_DELTAS[roff]
                    if orig_buf[roff - 1 - d] == 0x6A and orig_buf[roff - d] == orig_len:
                        len_byte_off = roff - d
                if len_byte_off is not None:
                    assert len(new_bytes) <= 127, (
                        f"String {cn_txt!r} -> {new_txt!r} ({len(new_bytes)}B) exceeds signed imm8 push limit (127B) at 0x{roff:x}"
                    )
                    buf[len_byte_off] = len(new_bytes)
                    patched_len_pushes += 1

        if len(new_bytes) <= orig_len:
            buf[orig_off : orig_off + orig_len + 1] = new_bytes + b"\x00" * (orig_len + 1 - len(new_bytes))
            patch_std_string_length_pushes()
            inplace_strings += 1
            patched_strings += 1
            continue

        if not safe_refs:
            continue

        if new_bytes not in allocated_va:
            assert pool_off + len(new_bytes) + 4 < pool_limit, "String pool overflow!"
            new_va = newhe_va + (pool_off - newhe_rptr)
            buf[pool_off : pool_off + len(new_bytes) + 1] = new_bytes + b"\x00"
            allocated_va[new_bytes] = new_va
            pool_off = (pool_off + len(new_bytes) + 4) & ~3
        else:
            new_va = allocated_va[new_bytes]

        old_va_bytes = struct.pack("<I", int(item["va"], 16))
        new_va_bytes = struct.pack("<I", new_va)
        for r in safe_refs:
            roff = int(r["ref_off"], 16)
            assert bytes(buf[roff : roff + 4]) == old_va_bytes, f"Mismatch at {r['ref_off']} for {cn_txt!r}"
            buf[roff : roff + 4] = new_va_bytes
            patched_refs += 1
        patch_std_string_length_pushes()
        patched_strings += 1

    # Patch 18-byte GBK prefix at 0x251540 ("植物大战僵尸杂交版v3.20.1" + "st1105125000")
    # Preserves 0x251552 ("v3.20.1st1105125000") referenced by debug overlay 0x5c9c86
    orig_banner_prefix = "植物大战僵尸杂交版v3.20.1".encode("gb18030")
    assert bytes(buf[0x251540:0x251559]) == orig_banner_prefix, "Unexpected banner bytes at 0x251540!"
    assert bytes(buf[0x251552:0x251566]) == b"v3.20.1st1105125000\x00", "Unexpected version tail at 0x251552!"
    ascii_prefix = b"PvZ Hybrid Cls EN " if lang == "en" else b"PvZ Hybrid Cls VI "
    assert len(ascii_prefix) == 18
    buf[0x251540:0x251552] = ascii_prefix
    assert bytes(buf[0x251552:0x251566]) == b"v3.20.1st1105125000\x00"

    # UI geometry & button-overlap fixes in PlantsVsZombies.exe (.text VA 0x401000 == file off 0x1000)
    # 1. ContinueDialog::Resize (0x4334b6): reduce stone button middle repeat from 3*w to 2*w (8d 34 40 -> 8d 34 00)
    #    so "Continue" & "New Game" / "Tiếp tục" & "Chơi mới" sit cleanly side-by-side without overlapping.
    assert bytes(buf[0x334B6:0x334B9]) == b"\x8d\x34\x40", f"Unexpected ContinueDialog bytes at 0x334b6: {buf[0x334B6:0x334B9].hex()}"
    buf[0x334B6:0x334B9] = b"\x8d\x34\x00"

    # 2. Plant & Zombie Almanac description rects: slightly expand vertical margins to eliminate bottom crowding.
    assert bytes(buf[0x2600:0x2608]) == b"\xc7\x44\x24\x40\x35\x01\x00\x00", "Unexpected Plant Almanac Y instruction"
    assert bytes(buf[0x2610:0x2618]) == b"\xc7\x44\x24\x48\xe6\x00\x00\x00", "Unexpected Plant Almanac H instruction"
    buf[0x2604:0x2608] = struct.pack("<I", 305)
    buf[0x2614:0x2618] = struct.pack("<I", 234)

    assert bytes(buf[0x3761:0x3769]) == b"\xc7\x44\x24\x28\x79\x01\x00\x00", "Unexpected Zombie Almanac Y instruction"
    assert bytes(buf[0x3771:0x3779]) == b"\xc7\x44\x24\x30\xaa\x00\x00\x00", "Unexpected Zombie Almanac H instruction"
    buf[0x3765:0x3769] = struct.pack("<I", 373)
    buf[0x3775:0x3779] = struct.pack("<I", 178)

    os.makedirs(os.path.dirname(os.path.abspath(out_exe_path)), exist_ok=True)
    with open(out_exe_path, "wb") as f:
        f.write(buf)
    print(
        f"Patched PlantsVsZombies.exe [{lang.upper()}]: {patched_strings} items "
        f"({inplace_strings} in-place, {patched_refs} relocated refs, {patched_len_pushes} len pushes, pool used {pool_off - 0xA60000:,} bytes) -> {out_exe_path}"
    )


if __name__ == "__main__":
    if len(sys.argv) >= 4:
        patch_pvz_exe(
            sys.argv[1],
            sys.argv[2],
            src_exe_path=sys.argv[3],
            catalog_path=sys.argv[4] if len(sys.argv) > 4 else None,
            translations_path=sys.argv[5] if len(sys.argv) > 5 else None,
        )
    else:
        patch_pvz_exe("en", os.path.join(ROOT, "work", "PlantsVsZombies_en.exe"))
        patch_pvz_exe("vi", os.path.join(ROOT, "work", "PlantsVsZombies_vi.exe"))
