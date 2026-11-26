"""Compile translated shards (out_1..out_5b) into UTF-8 (NO BOM) PopCap properties/*.txt files
for English [EN] and Vietnamese [VI], with strict 100% coverage, tag, and zero-CJK verification."""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(ROOT, "work")
SHARDS_OUT = os.path.join(WORK, "shards_out")

CJK_RE = re.compile(r"[\u3000-\u303f\u4e00-\u9fff\uff00-\uffef]")
TAG_RE = re.compile(r"\{[A-Za-z0-9_]+\}")

# Canonical punctuation sanitizer just in case any fullwidth char slipped through
FULLWIDTH_MAP = str.maketrans(
    {
        "，": ", ",
        "。": ". ",
        "！": "!",
        "？": "?",
        "：": ": ",
        "；": "; ",
        "（": "(",
        "）": ")",
        "【": "[",
        "】": "]",
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "《": '"',
        "》": '"',
        "、": ", ",
        "　": " ",
    }
)


def clean_punct(s: str) -> str:
    s = s.translate(FULLWIDTH_MAP)
    s = re.sub(r" {2,}", " ", s)
    s = "\n".join(line.rstrip() for line in s.splitlines())
    return s


def compile_all():
    cat = json.load(open(os.path.join(WORK, "strings_catalog.json"), encoding="utf-8"))
    shard_files = ["out_1.json", "out_2.json", "out_3.json", "out_4.json", "out_5a.json", "out_5b.json"]

    trans_map = {}
    for sf in shard_files:
        p = os.path.join(SHARDS_OUT, sf)
        assert os.path.isfile(p), f"Missing shard output: {p}"
        rows = json.load(open(p, encoding="utf-8"))
        for r in rows:
            trans_map[(r["file"], r["key"])] = (clean_punct(r["en"]), clean_punct(r["vi"]))

    print(f"Loaded {len(trans_map):,} translated keys from {len(shard_files)} shards.")

    out_en_dir = os.path.join(WORK, "overrides_en", "properties")
    out_vi_dir = os.path.join(WORK, "overrides_vi", "properties")
    os.makedirs(out_en_dir, exist_ok=True)
    os.makedirs(out_vi_dir, exist_ok=True)

    cjk_leaks = []
    tag_mismatches = []
    total_written = 0

    for fn, items in cat.items():
        en_blocks = []
        vi_blocks = []
        for it in items:
            key = it["key"]
            cn = it["val"]
            assert (fn, key) in trans_map, f"Missing translation for ({fn}, {key})"
            en_v, vi_v = trans_map[(fn, key)]

            if CJK_RE.search(en_v):
                cjk_leaks.append(("EN", fn, key, en_v))
            if CJK_RE.search(vi_v):
                cjk_leaks.append(("VI", fn, key, vi_v))

            # {SHORTLINE} is purely vertical spacing and is intentionally omitted in compact boxes
            # (Achievements, short gear cards); all semantic/color/icon tags must still match 1:1.
            cn_tags = [t for t in TAG_RE.findall(cn) if t != "{SHORTLINE}"]
            for lang_lbl, tv in [("EN", en_v), ("VI", vi_v)]:
                tv_tags = [t for t in TAG_RE.findall(tv) if t != "{SHORTLINE}"]
                if sorted(cn_tags) != sorted(tv_tags):
                    tag_mismatches.append((lang_lbl, fn, key, cn_tags, tv_tags))

            # PopCap format: [KEY]\r\n<val>\r\n\r\n
            en_crlf = en_v.replace("\r\n", "\n").replace("\n", "\r\n")
            vi_crlf = vi_v.replace("\r\n", "\n").replace("\n", "\r\n")
            en_blocks.append(f"[{key}]\r\n{en_crlf}\r\n")
            vi_blocks.append(f"[{key}]\r\n{vi_crlf}\r\n")
            total_written += 1

        # Save strictly as UTF-8 WITHOUT BOM so PopCap EncodingParser keeps UTF-8 bytes 1:1!
        en_bytes = "\r\n".join(en_blocks).encode("utf-8")
        vi_bytes = "\r\n".join(vi_blocks).encode("utf-8")
        assert not en_bytes.startswith(b"\xef\xbb\xbf")
        assert not vi_bytes.startswith(b"\xef\xbb\xbf")

        with open(os.path.join(out_en_dir, fn), "wb") as f:
            f.write(en_bytes)
        with open(os.path.join(out_vi_dir, fn), "wb") as f:
            f.write(vi_bytes)

    print(f"Compiled {total_written:,} entries across {len(cat)} files into overrides_en & overrides_vi.")
    print(f"CJK leaks: {len(cjk_leaks)}, Tag mismatches: {len(tag_mismatches)}")
    if cjk_leaks:
        for leak in cjk_leaks[:15]:
            print("  CJK LEAK:", leak)
    if tag_mismatches:
        for tm in tag_mismatches[:15]:
            print("  TAG MISMATCH:", tm)
    assert not cjk_leaks, f"Found {len(cjk_leaks)} CJK leaks!"
    assert not tag_mismatches, f"Found {len(tag_mismatches)} tag mismatches!"


if __name__ == "__main__":
    compile_all()
