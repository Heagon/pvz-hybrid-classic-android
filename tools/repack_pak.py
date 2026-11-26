"""Fast PopCap PAK repacker (0xBAC04AC0, XOR 0xF7) preserving exact original entry order, GBK paths, and timestamps."""
import os
import struct
import time

XOR_TABLE = bytes(b ^ 0xF7 for b in range(256))


def repack_pak_with_overrides(orig_pak_path: str, overrides_dir: str, out_pak_path: str) -> tuple[int, int]:
    """Repack orig_pak_path -> out_pak_path, substituting any matching relative files from overrides_dir.

    Returns (total_entries, replaced_count).
    """
    t0 = time.time()
    with open(orig_pak_path, "rb") as f:
        raw = f.read().translate(XOR_TABLE)

    magic, ver = struct.unpack_from("<II", raw, 0)
    assert magic == 0xBAC04AC0 and ver == 0, f"Invalid PAK header: {hex(magic)}, {ver}"

    # Build case-insensitive map of override files: normalized forward-slash lower -> full disk path
    override_map = {}
    if overrides_dir and os.path.isdir(overrides_dir):
        for root_d, _, files in os.walk(overrides_dir):
            for fn in files:
                full_p = os.path.join(root_d, fn)
                rel = os.path.relpath(full_p, overrides_dir).replace("\\", "/").lower()
                override_map[rel] = full_p

    pos = 8
    entries = []
    while pos < len(raw):
        flag = raw[pos]
        pos += 1
        if flag & 0x80:
            end_flag = flag
            break
        nlen = raw[pos]
        pos += 1
        name_bytes = raw[pos : pos + nlen]
        pos += nlen
        fsize, ftime = struct.unpack_from("<IQ", raw, pos)
        pos += 12
        norm_key = name_bytes.decode("gbk", errors="replace").replace("\\", "/").lower()
        entries.append((flag, name_bytes, fsize, ftime, norm_key))
    else:
        end_flag = 0x80

    header_parts = [struct.pack("<II", magic, ver)]
    data_parts = []
    replaced = 0

    for flag, name_bytes, orig_fsize, ftime, norm_key in entries:
        orig_chunk = raw[pos : pos + orig_fsize]
        pos += orig_fsize
        if norm_key in override_map:
            new_chunk = open(override_map[norm_key], "rb").read()
            replaced += 1
        else:
            new_chunk = orig_chunk
        header_parts.append(struct.pack("<BB", flag, len(name_bytes)))
        header_parts.append(name_bytes)
        header_parts.append(struct.pack("<IQ", len(new_chunk), ftime))
        data_parts.append(new_chunk)

    header_parts.append(struct.pack("<B", end_flag))
    plain_out = b"".join(header_parts) + b"".join(data_parts)
    enc_out = plain_out.translate(XOR_TABLE)

    os.makedirs(os.path.dirname(os.path.abspath(out_pak_path)), exist_ok=True)
    with open(out_pak_path, "wb") as f:
        f.write(enc_out)

    dt = time.time() - t0
    print(
        f"Repacked {out_pak_path}: {len(entries):,} entries ({replaced:,} overridden), "
        f"{len(enc_out):,} bytes in {dt:.2f}s"
    )
    return len(entries), replaced


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 4:
        print("Usage: python repack_pak.py <orig_main.pak> <overrides_dir> <out_main.pak>")
        sys.exit(1)
    repack_pak_with_overrides(sys.argv[1], sys.argv[2], sys.argv[3])
