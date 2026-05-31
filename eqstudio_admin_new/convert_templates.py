"""
convert_templates.py
--------------------
Convert HTML template yang ada [Square Bracket] placeholders
kepada {{Double Curly}} format untuk dipakai dengan Streamlit app.

Usage: python convert_templates.py
"""

import re
from pathlib import Path

# ─── Buat folder templates ───
Path("templates").mkdir(exist_ok=True)

# ─── Map: [placeholder asal] → {{PLACEHOLDER_BARU}} ───
# Susunan PENTING — yang lebih spesifik kena datang dulu
# supaya "Nama Pengantin Lelaki" di-replace sebelum "Pengantin Lelaki"

BRACKET_REPLACEMENTS = [
    # ── Pengantin ──────────────────────────────────────────────────
    ("[Nama Pengantin Lelaki]",          "{{GROOM_NAME}}"),
    ("[Nama Pengantin Perempuan]",        "{{BRIDE_NAME}}"),

    # ── Ibu bapa pengantin lelaki ───────────────────────────────────
    ("[Nama Bapa Pengantin Lelaki]",      "{{GROOM_FATHER_NAME}}"),
    ("[Nama Ibu Pengantin Lelaki]",       "{{GROOM_MOTHER_NAME}}"),

    # ── Ibu bapa pengantin perempuan ────────────────────────────────
    ("[Nama Bapa Pengantin Perempuan]",   "{{BRIDE_FATHER_NAME}}"),
    ("[Nama Ibu Pengantin Perempuan]",    "{{BRIDE_MOTHER_NAME}}"),

    # ── Tuan rumah & contact ────────────────────────────────────────
    ("[Nama Tuan Rumah]",                "{{HOST_NAME}}"),
    ("[Contact Person 1]",               "{{CONTACT_1_NAME}}"),
    ("[Contact Person 2]",               "{{CONTACT_2_NAME}}"),

    # ── Tarikh ──────────────────────────────────────────────────────
    ("[Hari], [Tarikh Majlis]",          "{{DATE_DAY}}, {{DATE_DISPLAY}}"),
    ("[Tarikh Majlis]",                  "{{DATE_DISPLAY}}"),
    ("[Tarikh Hijri]",                   "{{DATE_HIJRI}}"),
    ("[DD.MM.YYYY]",                     "{{DATE_DOTTED}}"),
    ("[DD]",                             "{{DATE_DD}}"),
    ("[MM]",                             "{{DATE_MM}}"),
    ("[YYYY]",                           "{{DATE_YYYY}}"),
    ("[Hari]",                           "{{DATE_DAY}}"),

    # ── Masa ────────────────────────────────────────────────────────
    ("[Masa Mula — Tamat]",              "{{TIME_RANGE}}"),
    ("[HH:MM] — [HH:MM]",               "{{TIME_START}} — {{TIME_END}}"),

    # ── Venue ───────────────────────────────────────────────────────
    ("[Nama Venue]",                     "{{VENUE_NAME}}"),
    ("[Alamat penuh venue majlis]",      "{{VENUE_ADDRESS}}"),
    ("[Bandar / Negeri]",                "{{VENUE_CITY}}"),
    ("[Lokasi]",                         "{{VENUE_CITY}}"),

    # ── Aturcara masa ───────────────────────────────────────────────
    # Guna lookahead supaya semua [00:00] diganti ikut konteks
    # (handled via regex di bawah)

    # ── Audio ───────────────────────────────────────────────────────
    ("PLACEHOLDER_AUDIO_URL",            "{{MUSIC_URL}}"),
]

# ─── Regex replacements (untuk pattern yang tak boleh exact-match) ───
REGEX_REPLACEMENTS = [
    # Masa dalam aturcara: [00:00] atau [HH:MM]
    (r'\[(?:00:00|HH:MM)\]',             "{{EVENT_TIME}}"),

    # Countdown target date dalam JS
    (r"new Date\('\[YYYY-MM-DD\]T\d{2}:\d{2}:\d{2}'\)",
     "new Date('{{DATE_ISO}}')"),

    # Google Calendar link
    (r'https://calendar\.google\.com/calendar/render\?action=TEMPLATE&text=Walimatul\+Urus\+\[Nama\+Pengantin\][^"]*',
     "https://calendar.google.com/calendar/render?action=TEMPLATE&text=Walimatul+Urus+{{GROOM_NAME}}+%26+{{BRIDE_NAME}}&dates={{DATE_ISO_START}}/{{DATE_ISO_END}}&location={{VENUE_NAME_URL}}"),

    # Apple Calendar .ics
    (r'data:text/calendar;charset=utf8,BEGIN:VCALENDAR.*?VCALENDAR',
     "{{APPLE_CALENDAR_LINK}}"),

    # Waze link dengan [Alamat+Venue]
    (r'https://waze\.com/ul\?q=\[Alamat\+Venue\]',
     "{{WAZE_LINK}}"),

    # Google Maps link dengan [Alamat+Venue]
    (r'https://maps\.google\.com/\?q=\[Alamat\+Venue\]',
     "{{GMAP_LINK}}"),

    # WhatsApp links yang ada 601XXXXXXXXX
    (r'https://wa\.me/601XXXXXXXXX',
     "https://wa.me/{{CONTACT_PHONE_WA}}"),

    # Nombor telefon +601X-XXXXXXX
    (r'\+601X-XXXXXXX',
     "{{CONTACT_PHONE_DISPLAY}}"),

    # Tahun dalam love story [20XX]
    (r'\[20XX\]',
     "{{LOVE_YEAR}}"),

    # Placeholder teks dalam love story
    (r'\[Cerita bagaimana kami mula berkenalan[^\]]*\]',
     "{{LOVE_STORY_1}}"),
    (r'\[Kisah hubungan bermula[^\]]*\]',
     "{{LOVE_STORY_2}}"),
    (r'\[Kisah pertunangan[^\]]*\]',
     "{{LOVE_STORY_3}}"),

    # Mesej tuan rumah
    (r'\[Mesej ikhlas dari tuan rumah[^\]]*\]',
     "{{HOST_MESSAGE}}"),
    (r'\[Heartfelt message from the hosts[^\]]*\]',
     "{{HOST_MESSAGE}}"),
    (r'\[رسالة صادقة من أصحاب البيت[^\]]*\]',
     "{{HOST_MESSAGE}}"),

    # Cal.buildCalendar hardcoded date (Ogos 2026, d===8)
    # Biar je — app.py yang akan update ni via JS injection

    # Audio source
    (r'<source\s+src="[^"]*"\s+type="audio/mpeg">',
     '<source src="{{MUSIC_URL}}" type="audio/mpeg">'),

    # Teks dalam <title>
    (r'<title>Walimatul Urus \| \[Nama Pengantin Lelaki\] &amp; \[Nama Pengantin Perempuan\]</title>',
     '<title>Walimatul Urus | {{GROOM_NAME}} &amp; {{BRIDE_NAME}}</title>'),
]


def convert(src: str, dst: str):
    path = Path(src)
    if not path.exists():
        print(f"  ⚠️  Skip — fail tidak jumpa: {src}")
        return

    html = path.read_text(encoding="utf-8")
    original = html

    # ── Pass 1: Exact string replacements ───────────────────────────
    exact_count = 0
    for old, new in BRACKET_REPLACEMENTS:
        if old in html:
            html = html.replace(old, new)
            exact_count += 1

    # ── Pass 2: Regex replacements ───────────────────────────────────
    regex_count = 0
    for pattern, replacement in REGEX_REPLACEMENTS:
        new_html, n = re.subn(pattern, replacement, html, flags=re.DOTALL)
        if n > 0:
            html = new_html
            regex_count += n

    # ── Pass 3: Cari & warn kalau ada [Bracket] yang tertinggal ─────
    leftover = re.findall(r'\[[A-Za-z][^\]]{2,60}\]', html)
    # Tapis keluar yang bukan placeholder (e.g. CSS attribute selectors)
    leftover = [
        l for l in leftover
        if not any(skip in l for skip in [
            'onclick', 'class', 'id', 'data-', 'href', 'src',
            '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
        ])
    ]
    leftover_unique = sorted(set(leftover))

    Path(dst).write_text(html, encoding="utf-8")

    changed = html != original
    print(f"\n  ✅  {src}")
    print(f"      → {dst}")
    print(f"      Exact replacements : {exact_count}")
    print(f"      Regex replacements : {regex_count}")

    if leftover_unique:
        print(f"\n      ⚠️  {len(leftover_unique)} kemungkinan placeholder tertinggal:")
        for item in leftover_unique[:15]:  # tunjuk max 15
            print(f"         • {item}")
        if len(leftover_unique) > 15:
            print(f"         ... dan {len(leftover_unique)-15} lagi")
    else:
        print(f"      ✨ Tiada bracket placeholder yang tertinggal!")

    if not changed:
        print(f"      ℹ️  Tiada perubahan dibuat — semak semula source file")


# ─── Files nak convert ───────────────────────────────────────────────
# (source_file, output_template_file)
# Tukar path ikut struktur folder kau
FILES = [
    ("kad-kawin-v2-celestial.html",    "templates/v2_celestial.html"),
    ("kad-kawin-v3-garden.html",       "templates/v3_garden.html"),
    ("kad-kawin-v4-arabian.html",      "templates/v4_arabian.html"),
    ("kad-kawin-portrait-royal.html",  "templates/portrait_royal.html"),
]

# ─── Preview mode: convert satu file untuk test ──────────────────────
PREVIEW_FILES = [
    ("template_test.html",             "templates/template_test_out.html"),
]


if __name__ == "__main__":
    import sys

    mode = sys.argv[1] if len(sys.argv) > 1 else "all"

    print("\n🔄 Converting templates...\n")
    print("=" * 55)

    target_files = PREVIEW_FILES if mode == "preview" else FILES

    converted = 0
    skipped = 0
    for src, dst in target_files:
        result = convert(src, dst)
        if Path(src).exists():
            converted += 1
        else:
            skipped += 1

    print("\n" + "=" * 55)
    print(f"\n✅ Selesai! {converted} fail diproses, {skipped} fail skip.")

    if converted > 0:
        print("\n📁 Template disimpan dalam folder: templates/")
        print("🚀 Seterusnya jalankan: streamlit run app.py\n")
    else:
        print("\n💡 Tip: Letakkan HTML files dalam folder yang sama dengan script ini.")
        print("   Atau edit senarai FILES di atas ikut path yang betul.\n")
