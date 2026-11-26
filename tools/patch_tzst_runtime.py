"""Patch hardcoded com.winlator paths inside Winlator .tzst runtime archives to com.pvzh.cls."""

import io
import os
import pathlib
import subprocess
import sys
import tarfile

ZSTD_EXE = os.environ.get("ZSTD_EXE", "zstd")
OLD_BYTES = b"com.winlator"
NEW_BYTES = b"com.pvzh.cls"
OLD_STR = "com.winlator"
NEW_STR = "com.pvzh.cls"


def patch_tzst_file(path: pathlib.Path) -> int:
    """Replace com.winlator paths in a single .tzst archive if present. Returns match count."""
    dec = subprocess.run([ZSTD_EXE, "-dc", str(path)], capture_output=True, check=True)
    raw_tar = dec.stdout
    if OLD_BYTES not in raw_tar:
        return 0

    tf_in = tarfile.open(fileobj=io.BytesIO(raw_tar), mode="r:")
    out_buf = io.BytesIO()
    tf_out = tarfile.open(fileobj=out_buf, mode="w:", format=tarfile.GNU_FORMAT)
    replacements = 0

    for m in tf_in.getmembers():
        ti = tarfile.TarInfo(name=m.name)
        ti.type = m.type
        ti.mode = m.mode
        ti.uid = m.uid
        ti.gid = m.gid
        ti.mtime = m.mtime
        ti.uname = m.uname
        ti.gname = m.gname
        ti.devmajor = m.devmajor
        ti.devminor = m.devminor

        if m.issym() or m.islnk():
            linkname = m.linkname
            if OLD_STR in linkname:
                replacements += linkname.count(OLD_STR)
                linkname = linkname.replace(OLD_STR, NEW_STR)
            ti.linkname = linkname
            tf_out.addfile(ti)
        elif m.isdir():
            ti.size = 0
            tf_out.addfile(ti)
        elif m.isfile():
            f = tf_in.extractfile(m)
            data = f.read() if f is not None else b""
            if OLD_BYTES in data:
                replacements += data.count(OLD_BYTES)
                data = data.replace(OLD_BYTES, NEW_BYTES)
            ti.size = len(data)
            tf_out.addfile(ti, io.BytesIO(data))
        else:
            ti.size = m.size
            tf_out.addfile(ti)

    tf_out.close()
    tf_in.close()

    tmp_tar = path.with_suffix(".tmp.tar")
    tmp_zst = path.with_suffix(".tmp.tzst")
    tmp_tar.write_bytes(out_buf.getvalue())
    try:
        subprocess.run(
            [ZSTD_EXE, "-f", "-T0", "-15", str(tmp_tar), "-o", str(tmp_zst)],
            capture_output=True,
            check=True,
        )
        os.replace(tmp_zst, path)
    finally:
        if tmp_tar.exists():
            tmp_tar.unlink()
        if tmp_zst.exists():
            tmp_zst.unlink()
    return replacements


def patch_assets_dir(assets_dir: pathlib.Path) -> None:
    """Patch all .tzst archives under assets_dir and verify zero com.winlator references remain."""
    total = 0
    for p in sorted(assets_dir.rglob("*.tzst")):
        cnt = patch_tzst_file(p)
        if cnt:
            print(f"  patched {p.relative_to(assets_dir)}: {cnt} replacements")
            total += cnt

    leftovers = []
    for p in sorted(assets_dir.rglob("*.tzst")):
        dec = subprocess.run([ZSTD_EXE, "-dc", str(p)], capture_output=True, check=True)
        if OLD_BYTES in dec.stdout:
            leftovers.append(str(p.relative_to(assets_dir)))
    if leftovers:
        raise RuntimeError(f"Unpatched com.winlator remaining in: {leftovers}")
    print(f"All .tzst assets verified clean (total replacements in this pass: {total}).")


if __name__ == "__main__":
    default_dir = pathlib.Path(__file__).resolve().parent.parent / "work" / "winlator_decoded" / "assets"
    target = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else default_dir
    patch_assets_dir(target)
