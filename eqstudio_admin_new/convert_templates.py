"""
convert_templates.py
--------------------
Convert HTML template dengan nilai hardcoded kepada placeholders
format [NAMA PENGANTIN LELAKI] — konsisten dengan app.py.

Usage:
  python convert_templates.py              # convert semua FILES
  python convert_templates.py preview      # test dengan PREVIEW_FILES sahaja
"""

import re
from pathlib import Path

Path("templates").mkdir(exist_ok=True)

# ─────────────────────────────────────────────────────────────────────
#  MAP: nilai hardcoded dalam HTML → placeholder [FORMAT] untuk app.py
#
#  SUSUNAN PENTING:
#  • String panjang/spesifik MESTI datang dulu sebelum substring dia
#    (cth: "Sufian bin Salleh" sebelum "Sufian")
#  • URL penuh sebelum URL pendek
# ─────────────────────────────────────────────────────────────────────
REPLACEMENTS = [

    # ── Nama pengantin ────────────────────────────────────────────────
    ("Ahmad Nazmi",             "[NAMA PENGANTIN LELAKI]"),
    ("Nur Farhana",             "[NAMA PENGANTIN PEREMPUAN]"),

    # ── Ibu bapa pengantin lelaki ─────────────────────────────────────
    ("Sufian bin Salleh",       "[NAMA BAPA LELAKI]"),
    ("Sufian Salleh",           "[NAMA BAPA LELAKI]"),   # varian tanpa "bin"
    ("Siti Maimun",             "[NAMA IBU LELAKI]"),

    # ── Tuan rumah ────────────────────────────────────────────────────
    # (tambah nama ibu bapa pengantin perempuan kalau ada)

    # ── Tarikh ────────────────────────────────────────────────────────
    ("10 Ogos 2026",            "[TARIKH]"),
    ("15 Safar 1448H",          "[TARIKH HIJRI]"),
    ("Isnin",                   "[HARI]"),

    # ── ISO tarikh dalam JS countdown ─────────────────────────────────
    ("2026-08-10T12:00:00+08:00", "[YYYY]-[MM]-[DD]T[HH]:00:00"),

    # ── Masa ──────────────────────────────────────────────────────────
    ("12 Tengahari",            "[MASA MULA]"),
    ("12:00 Tengahari",         "[MASA MULA]"),

    # ── Venue ─────────────────────────────────────────────────────────
    # URL-encoded versions DULU, kemudian plain text
    ("Sebening+Embun+Garden+Glass+Hall,+Lot+15,+Jalan+Durian+1,+Kampung+Sungai+Buah,+43800+Dengkil,+Selangor",
                                "[NAMA+VENUE]"),
    ("Sebening+Embun+Garden+Glass+Hall,Lot+15,Jalan+Durian+1,43800+Dengkil,Selangor",
                                "[NAMA+VENUE]"),
    ("Sebening+Embun+Garden+Glass+Hall+Dengkil",
                                "[NAMA+VENUE]"),
    # Alamat penuh plain text DULU (lebih spesifik)
    ("Lot 15, Jalan Durian 1, Kampung Sungai Buah, 43800 Dengkil, Selangor",
                                "[ALAMAT PENUH VENUE]"),
    ("Lot 15, Jalan Durian 1, Kg. Sungai Buah, 43800 Dengkil, Selangor",
                                "[ALAMAT PENUH VENUE]"),
    # Kemudian nama venue pendek
    ("Sebening Embun Garden Glass Hall", "[NAMA VENUE]"),

    # ── No. telefon ───────────────────────────────────────────────────
    # Format panjang/URL dulu
    ("601135623312",            "[NO_TELEFON_TANPA_+]"),
    ("01135623312",             "[NO_TELEFON_TANPA_+]"),
    ("011-3562 3312",           "[NO TELEFON]"),

    # ── WhatsApp URL penuh (dengan text param) — ganti keseluruhan URL ─
    (
        "https://wa.me/601135623312?text=Assalamualaikum%20Encik%20Sufian%2C%20saya%20ingin%20bertanya%20tentang%20majlis%20perkahwinan%20Ahmad%20Nazmi%20%26%20Nur%20Farhana.",
        "https://wa.me/[NO_TELEFON_TANPA_+]?text=Assalamualaikum%2C%20saya%20ingin%20bertanya%20tentang%20majlis."
    ),
    # WhatsApp URL tanpa text param
    ("https://wa.me/601135623312",  "https://wa.me/[NO_TELEFON_TANPA_+]"),

    # ── Waze & Google Maps URL penuh ──────────────────────────────────
    (
        "https://waze.com/ul?q=Sebening+Embun+Garden+Glass+Hall+Dengkil&navigate=yes",
        "https://waze.com/ul?q=[NAMA+VENUE]&navigate=yes"
    ),
    (
        "https://maps.google.com/?q=Sebening+Embun+Garden+Glass+Hall,+Lot+15,+Jalan+Durian+1,+Kampung+Sungai+Buah,+43800+Dengkil,+Selangor",
        "https://maps.google.com/?q=[NAMA+VENUE]"
    ),
    (
        "https://maps.google.com/?q=Sebening+Embun+Garden+Glass+Hall,Lot+15,Jalan+Durian+1,43800+Dengkil,Selangor",
        "https://maps.google.com/?q=[NAMA+VENUE]"
    ),

    # ── Audio ─────────────────────────────────────────────────────────
    ("PLACEHOLDER_AUDIO_URL",   "PLACEHOLDER_AUDIO_URL"),  # kekal sama — app.py handle ni
]

# ─────────────────────────────────────────────────────────────────────
#  REGEX REPLACEMENTS — untuk pattern yang tak boleh exact-match
# ─────────────────────────────────────────────────────────────────────
REGEX_REPLACEMENTS = [
    # Countdown target date dalam JS:  new Date('2026-08-10T12:00:00+08:00')
    # (kalau exact replacement atas tak catch, regex ni backup)
    (
        r"new Date\('[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}[^']*'\)",
        "new Date('[YYYY]-[MM]-[DD]T[HH]:00:00')"
    ),

    # <source src="..."> — ganti URL audio
    (
        r'(<source\s+src=")[^"]*(")',
        r'\1PLACEHOLDER_AUDIO_URL\2'
    ),

    # Calendar buildCalendar() — hardcoded highlight tarikh (d===8 = 10 Ogos)
    # Biar je, app.py inject via JS
]

# ─────────────────────────────────────────────────────────────────────
#  FILES nak di-convert
#  Format: (source_file, output_file)
# ─────────────────────────────────────────────────────────────────────
FILES = [
    ("../kad-kawin-v2-celestial.html",   "templates/v2_celestial.html"),
    ("../kad-kawin-v3-garden.html",      "templates/v3_garden.html"),
    ("../kad-kawin-v4-arabian.html",     "templates/v4_arabian.html"),
    ("../kad-kawin-portrait-royal.html", "templates/portrait_royal.html"),
]

# Untuk test dengan satu fail sahaja
PREVIEW_FILES = [
    ("template_test.html", "templates/template_test_out.html"),
]


# ─────────────────────────────────────────────────────────────────────
#  CORE FUNCTION
# ─────────────────────────────────────────────────────────────────────
def convert(src: str, dst: str) -> bool:
    path = Path(src)
    if not path.exists():
        print(f"  ⚠️  Skip — fail tidak jumpa: {src}")
        return False

    html = path.read_text(encoding="utf-8")
    original = html

    # Pass 1 — exact string replacements
    exact_hits = []
    for old, new in REPLACEMENTS:
        count = html.count(old)
        if count > 0:
            html = html.replace(old, new)
            exact_hits.append((old, new, count))

    # Pass 2 — regex replacements
    regex_hits = []
    for pattern, replacement in REGEX_REPLACEMENTS:
        new_html, n = re.subn(pattern, replacement, html, flags=re.DOTALL)
        if n > 0:
            html = new_html
            regex_hits.append((pattern[:40], n))

    # Pass 3 — detect sisa placeholder lama {{CURLY}} kalau ada
    curly_leftovers = re.findall(r'\{\{[A-Z_]+\}\}', html)

    Path(dst).write_text(html, encoding="utf-8")

    # ── Report ────────────────────────────────────────────────────────
    print(f"\n  ✅  {src}")
    print(f"      → {dst}")
    print(f"      Exact  : {len(exact_hits)} jenis replacement")
    print(f"      Regex  : {len(regex_hits)} pattern")

    if exact_hits:
        for old, new, n in exact_hits:
            trunc_old = (old[:45] + "…") if len(old) > 45 else old
            print(f"         • \"{trunc_old}\"  →  {new}  ({n}x)")

    if curly_leftovers:
        uniq = sorted(set(curly_leftovers))
        print(f"\n      ⚠️  Ada placeholder format lama {{{{...}}}} yang tertinggal:")
        for c in uniq:
            print(f"         • {c}")

    if html == original:
        print("      ℹ️  Tiada perubahan — semak nama nilai dalam REPLACEMENTS")

    return True


# ─────────────────────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys

    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    target = PREVIEW_FILES if mode == "preview" else FILES

    print("\n🔄 Converting templates...\n")
    print("=" * 60)

    ok = sum(1 for src, dst in target if convert(src, dst))
    skipped = len(target) - ok

    print("\n" + "=" * 60)
    print(f"\n✅  Selesai — {ok} fail diproses, {skipped} fail skip\n")

    if ok:
        print("📁  Template disimpan dalam folder: templates/")
        print("🚀  Seterusnya: streamlit run app.py\n")
    else:
        print("💡  Tip: Pastikan HTML files ada dalam folder yang betul.")
        print("    Edit senarai FILES di atas ikut path sebenar.\n")
