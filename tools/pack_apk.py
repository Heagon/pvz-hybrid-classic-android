"""Pack a PvZ Hybrid Classic game folder into Zstandard tar and assemble + sign a standalone APK."""
import os
import shutil
import subprocess
import sys
import tarfile
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(ROOT, "work")
OUTPUT = os.path.join(ROOT, "output")
ZSTD = os.environ.get("ZSTD_BIN", "zstd")
JDK_HOME = os.environ.get("JDK_HOME", "")
JAVA = os.path.join(JDK_HOME, "bin", "java.exe" if os.name == "nt" else "java") if JDK_HOME else "java"
UBER_SIGNER = os.environ.get("UBER_SIGNER", os.path.join(ROOT, "tools", "uber-apk-signer.jar"))
KEYSTORE = os.environ.get("KEYSTORE_PATH", "")
KS_ALIAS = os.environ.get("KS_ALIAS", "release")
KS_PASS = os.environ.get("KS_PASS", "")


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
                    # 30 bytes local header + len(arcname) + len(extra) must be 4-byte aligned
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
            print(f"Embedding {tzst_path} into APK (ZIP_STORED)...")
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
    print(f"Signed APK -> {final_apk_path} ({os.path.getsize(final_apk_path):,} bytes)")


def prepare_clean_cn_folder():
    from patch_exe_perf import patch_exe_perf

    src = os.path.join(WORK, "he_extracted")
    dst = os.path.join(WORK, "game_stage_cn")
    if os.path.exists(dst):
        shutil.rmtree(dst)
    os.makedirs(os.path.join(dst, "fonts"), exist_ok=True)

    for fn in ["PlantsVsZombies.exe", "bass.dll", "gdi42.dll", "main.pak"]:
        shutil.copy2(os.path.join(src, fn), os.path.join(dst, fn))
    exe_dst = os.path.join(dst, "PlantsVsZombies.exe")
    patch_exe_perf(exe_dst, exe_dst)

    fonts_src = os.path.join(src, "fonts")
    for fn in os.listdir(fonts_src):
        if fn.endswith(".py"):
            continue
        shutil.copy2(os.path.join(fonts_src, fn), os.path.join(dst, "fonts", fn))
        # Ensure lowercase .ttf copy exists on case-sensitive Linux rootfs!
        if fn.lower() != fn:
            shutil.copy2(os.path.join(fonts_src, fn), os.path.join(dst, "fonts", fn.lower()))
    return dst


def prepare_localized_stage(lang: str):
    """Build clean localized Windows game stage for EN or VI with repacked PAK & UTF-8 hooks."""
    from patch_exe_perf import patch_exe_perf
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
    shutil.copy2(gdi_src, os.path.join(dst, "gdi42.dll"))
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
    mode = sys.argv[1] if len(sys.argv) > 1 else "cn"
    base_shell = os.path.join(WORK, "base_shell.apk")
    assert os.path.isfile(base_shell), "Run build_base_shell.py first!"

    targets = ["cn", "en", "vi"] if mode == "all" else [mode]
    for t in targets:
        if t == "cn":
            stage = prepare_clean_cn_folder()
            tzst = os.path.join(WORK, "pvz_game_cn.tzst")
            build_game_tzst(stage, tzst)
            unsigned = os.path.join(WORK, "unsigned_cn.apk")
            align_and_pack_apk(base_shell, tzst, "v3.20.1-CN-Raw", unsigned)
            final_apk = os.path.join(OUTPUT, "PvZ-Hybrid-Classic-3.20.1-Chinese-Raw.apk")
            sign_apk(unsigned, final_apk)
        elif t in ("en", "vi"):
            stage = prepare_localized_stage(t)
            tzst = os.path.join(WORK, f"pvz_game_{t}.tzst")
            build_game_tzst(stage, tzst)
            unsigned = os.path.join(WORK, f"unsigned_{t}.apk")
            edition_tag = f"v3.20.1-{t.upper()}"
            align_and_pack_apk(base_shell, tzst, edition_tag, unsigned)
            label = "English" if t == "en" else "Vietnamese"
            final_apk = os.path.join(OUTPUT, f"PvZ-Hybrid-Classic-3.20.1-{label}.apk")
            sign_apk(unsigned, final_apk)
        else:
            raise SystemExit(f"Unknown mode: {t}")


if __name__ == "__main__":
    main()
