"""Pack a PvZ Hybrid Classic game folder into Zstandard tar and assemble + sign a versioned standalone APK.

Naming standard:
    <GameName>-<GameVersion>-<Language>-<BuildID>.apk
    Example: PvZ-Hybrid-Classic-3.20.1-Vietnamese-B.0.2.apk
"""
import argparse
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(ROOT, "work")
OUTPUT = os.path.join(ROOT, "output")
BUILD_VERSION_FILE = os.path.join(ROOT, "build_version.json")

ZSTD = os.environ.get("ZSTD_BIN", "zstd")
JDK_HOME = os.environ.get("JDK_HOME", "")
JAVA = os.path.join(JDK_HOME, "bin", "java.exe" if os.name == "nt" else "java") if JDK_HOME else "java"
UBER_SIGNER = os.environ.get("UBER_SIGNER", os.path.join(ROOT, "tools", "uber-apk-signer.jar"))
KEYSTORE = os.environ.get("KEYSTORE_PATH", "")
KS_ALIAS = os.environ.get("KS_ALIAS", "release")
KS_PASS = os.environ.get("KS_PASS", "")

BUILD_ID_RE = re.compile(r"^B\.\d+\.\d+$")


def load_build_meta():
    if os.path.isfile(BUILD_VERSION_FILE):
        with open(BUILD_VERSION_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {
        "game_name": "PvZ-Hybrid-Classic",
        "game_version": "3.20.1",
        "package_id": "com.pvzh.cls",
        "version_code": 3201,
        "github_repo": "Heagon/pvz-hybrid-classic-android",
        "current_build": "B.0.2",
        "history": [],
    }


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def build_game_tzst(game_folder, tzst_out):
    tar_tmp = tzst_out + ".tar"
    if os.path.exists(tar_tmp):
        os.remove(tar_tmp)
    if os.path.exists(tzst_out):
        os.remove(tzst_out)

    print(f"Creating tar from {game_folder}...")
    with tarfile.open(tar_tmp, "w") as tf:
        for root_d, dirs, files in os.walk(game_folder):
            dirs.sort()
            rel_d = os.path.relpath(root_d, game_folder)
            if rel_d != ".":
                ti_dir = tarfile.TarInfo(name=rel_d.replace(os.sep, "/"))
                ti_dir.type = tarfile.DIRTYPE
                ti_dir.mode = 0o755
                tf.addfile(ti_dir)
            for fn in sorted(files):
                full_p = os.path.join(root_d, fn)
                arc_p = fn if rel_d == "." else f"{rel_d.replace(os.sep, '/')}/{fn}"
                tf.add(full_p, arcname=arc_p, recursive=False)
    subprocess.run([ZSTD, "-3", "-T0", "-f", tar_tmp, "-o", tzst_out], check=True)
    os.remove(tar_tmp)
    print(f"Created {tzst_out} ({os.path.getsize(tzst_out):,} bytes)")


def align_and_pack_apk(base_shell_apk, tzst_path, edition_id, unsigned_apk):
    """Copy entries from base_shell_apk + add assets/pvz_game.tzst & assets/pvz_edition.txt with 4-byte alignment for STORED entries."""
    if os.path.exists(unsigned_apk):
        os.remove(unsigned_apk)

    with zipfile.ZipFile(base_shell_apk, "r") as zin, open(unsigned_apk, "wb") as raw_out:
        with zipfile.ZipFile(raw_out, "w") as zout:
            def write_entry(arcname, data, compress_type):
                zi = zipfile.ZipInfo(arcname)
                zi.compress_type = compress_type
                zi.create_system = 3
                zi.external_attr = 0o100644 << 16
                if compress_type == zipfile.ZIP_STORED:
                    header_len = 30 + len(arcname.encode("utf-8"))
                    pad = (4 - ((raw_out.tell() + header_len) % 4)) % 4
                    zi.extra = b"\x00" * pad
                zout.writestr(zi, data)

            for info in zin.infolist():
                if info.filename in ("assets/pvz_game.tzst", "assets/pvz_edition.txt"):
                    continue
                data = zin.read(info.filename)
                write_entry(info.filename, data, info.compress_type)

            write_entry("assets/pvz_edition.txt", (edition_id + "\n").encode("utf-8"), zipfile.ZIP_DEFLATED)
            print(f"Embedding {tzst_path} into APK (ZIP_STORED, stamp={edition_id})...")
            write_entry("assets/pvz_game.tzst", open(tzst_path, "rb").read(), zipfile.ZIP_STORED)

    print(f"Unsigned APK ready: {unsigned_apk} ({os.path.getsize(unsigned_apk):,} bytes)")


def sign_apk(unsigned_apk, final_apk_path):
    os.makedirs(os.path.dirname(final_apk_path), exist_ok=True)
    sign_tmp = os.path.join(WORK, "sign_tmp")
    if os.path.exists(sign_tmp):
        shutil.rmtree(sign_tmp)
    os.makedirs(sign_tmp, exist_ok=True)

    subprocess.run(
        [
            JAVA, "-jar", UBER_SIGNER,
            "-a", unsigned_apk,
            "--ks", KEYSTORE,
            "--ksAlias", KS_ALIAS,
            "--ksPass", KS_PASS,
            "--ksKeyPass", KS_PASS,
            "--skipZipAlign",
            "-o", sign_tmp,
        ],
        check=True,
    )
    signed_files = [f for f in os.listdir(sign_tmp) if f.endswith(".apk")]
    assert signed_files, "uber-apk-signer did not output a signed APK"
    shutil.move(os.path.join(sign_tmp, signed_files[0]), final_apk_path)
    sz = os.path.getsize(final_apk_path)
    h = sha256_file(final_apk_path)
    print(f"Signed APK -> {final_apk_path} ({sz:,} bytes, SHA-256={h})")
    return sz, h


def prepare_clean_cn_folder():
    from patch_exe_perf import patch_exe_perf
    from patch_exe_fixes import patch_exe_fixes
    from patch_engine_utf8 import patch_gdi42_atlas_hook

    src = os.path.join(WORK, "he_extracted")
    dst = os.path.join(WORK, "game_stage_cn")
    if os.path.exists(dst):
        shutil.rmtree(dst)
    os.makedirs(os.path.join(dst, "fonts"), exist_ok=True)

    for fn in ["PlantsVsZombies.exe", "bass.dll", "gdi42.dll", "main.pak"]:
        shutil.copy2(os.path.join(src, fn), os.path.join(dst, fn))
    exe_dst = os.path.join(dst, "PlantsVsZombies.exe")
    patch_exe_perf(exe_dst, exe_dst)
    patch_exe_fixes(exe_dst, exe_dst)
    patch_gdi42_atlas_hook(os.path.join(dst, "gdi42.dll"))

    fonts_src = os.path.join(src, "fonts")
    for fn in os.listdir(fonts_src):
        if fn.endswith(".py"):
            continue
        shutil.copy2(os.path.join(fonts_src, fn), os.path.join(dst, "fonts", fn))
        if fn.lower() != fn:
            shutil.copy2(os.path.join(fonts_src, fn), os.path.join(dst, "fonts", fn.lower()))
    return dst


def prepare_localized_stage(lang: str):
    """Build clean localized Windows game stage for EN or VI with repacked PAK & UTF-8 hooks."""
    from patch_exe_perf import patch_exe_perf
    from patch_exe_fixes import patch_exe_fixes
    from patch_engine_utf8 import patch_gdi42_atlas_hook
    from repack_pak import repack_pak_with_overrides

    src = os.path.join(WORK, "he_extracted")
    dst = os.path.join(WORK, f"game_stage_{lang}")
    if os.path.exists(dst):
        shutil.rmtree(dst)
    os.makedirs(os.path.join(dst, "fonts"), exist_ok=True)

    exe_src = os.path.join(WORK, f"PlantsVsZombies_{lang}.exe")
    gdi_src = os.path.join(WORK, "gdi42_utf8.dll")
    bass_src = os.path.join(src, "bass.dll")
    assert os.path.isfile(exe_src), f"Missing patched exe: {exe_src}"
    assert os.path.isfile(gdi_src), f"Missing UTF-8 shim: {gdi_src}"
    exe_dst = os.path.join(dst, "PlantsVsZombies.exe")
    shutil.copy2(exe_src, exe_dst)
    patch_exe_perf(exe_dst, exe_dst)
    patch_exe_fixes(exe_dst, exe_dst)
    gdi_dst = os.path.join(dst, "gdi42.dll")
    shutil.copy2(gdi_src, gdi_dst)
    patch_gdi42_atlas_hook(gdi_dst)
    shutil.copy2(bass_src, os.path.join(dst, "bass.dll"))

    overrides_dir = os.path.join(WORK, f"overrides_{lang}")
    assert os.path.isdir(overrides_dir), f"Missing overrides dir: {overrides_dir}"
    repack_pak_with_overrides(
        os.path.join(src, "main.pak"),
        overrides_dir,
        os.path.join(dst, "main.pak"),
    )

    fonts_src = os.path.join(WORK, "unicode_fonts")
    for fn in os.listdir(fonts_src):
        if fn.endswith(".py"):
            continue
        shutil.copy2(os.path.join(fonts_src, fn), os.path.join(dst, "fonts", fn))
        if fn.lower() != fn:
            shutil.copy2(os.path.join(fonts_src, fn), os.path.join(dst, "fonts", fn.lower()))
    return dst


def main():
    meta = load_build_meta()
    ap = argparse.ArgumentParser(description="Build & sign versioned PvZ Hybrid Classic Android APKs")
    ap.add_argument("mode", nargs="?", default="cn", choices=["cn", "en", "vi", "all"], help="Language target(s)")
    ap.add_argument("--build", default=meta["current_build"], help="Build ID in B.X.Y format (e.g. B.0.2)")
    ap.add_argument("--reuse-tzst", action="store_true", help="Reuse existing work/pvz_game_<lang>.tzst")
    args = ap.parse_args()

    build_id = args.build.strip()
    if not BUILD_ID_RE.match(build_id):
        raise SystemExit(f"Invalid --build '{build_id}': expected format B.X.Y (e.g. B.0.1, B.0.2)")

    game_name = meta["game_name"]
    game_ver = meta["game_version"]
    base_shell = os.path.join(WORK, "base_shell.apk")
    assert os.path.isfile(base_shell), "Run build_base_shell.py first!"

    targets = ["cn", "en", "vi"] if args.mode == "all" else [args.mode]
    lang_map = {
        "cn": ("Chinese-Raw", f"v{game_ver}-CN-Raw-{build_id}"),
        "en": ("English", f"v{game_ver}-EN-{build_id}"),
        "vi": ("Vietnamese", f"v{game_ver}-VI-{build_id}"),
    }

    for t in targets:
        label, edition_tag = lang_map[t]
        tzst = os.path.join(WORK, f"pvz_game_{t}.tzst")
        if args.reuse_tzst:
            assert os.path.isfile(tzst), f"--reuse-tzst requested but missing {tzst}"
        else:
            stage = prepare_clean_cn_folder() if t == "cn" else prepare_localized_stage(t)
            build_game_tzst(stage, tzst)

        unsigned = os.path.join(WORK, f"unsigned_{t}.apk")
        align_and_pack_apk(base_shell, tzst, edition_tag, unsigned)
        final_apk = os.path.join(OUTPUT, f"{game_name}-{game_ver}-{label}-{build_id}.apk")
        sign_apk(unsigned, final_apk)


if __name__ == "__main__":
    main()
