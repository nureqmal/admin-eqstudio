"""
convert_templates.py
--------------------
Jalankan script ni sekali untuk convert HTML asal kepada template dengan placeholders.
Usage: python convert_templates.py
"""

import re
from pathlib import Path

# ─── Buat folder templates ───
Path("templates").mkdir(exist_ok=True)

# ─── Map: teks asal → placeholder ───
# Edit ikut HTML template kau yang sebenar
REPLACEMENTS = [
    # Nama pengantin
    ("Ahmad Nazmi",         "{{GROOM_NAME}}"),
    ("Nur Farhana",         "{{BRIDE_NAME}}"),

    # Ibu bapa
    ("Sufian bin Salleh",   "{{FATHER_NAME}}"),
    ("Siti Maimun",         "{{MOTHER_NAME}}"),
    ("Sufian Salleh",       "{{FATHER_NAME}}"),

    # Tarikh
    ("10 Ogos 2026",        "{{DATE_DISPLAY}}"),
    ("Isnin",               "{{DATE_DAY}}"),
    ("15 Safar 1448H",      "{{DATE_HIJRI}}"),
    ("2026-08-10T12:00:00+08:00", "{{DATE_ISO}}"),
    ("12 Tengahari",        "{{TIME_DISPLAY}}"),
    ("12:00 Tengahari",     "{{TIME_DISPLAY}}"),

    # Lokasi
    ("Sebening Embun Garden Glass Hall", "{{VENUE_NAME}}"),
    ("Lot 15, Jalan Durian 1, Kg. Sungai Buah, 43800 Dengkil, Selangor", "{{VENUE_ADDRESS}}"),
    ("Lot 15, Jalan Durian 1, Kampung Sungai Buah, 43800 Dengkil, Selangor", "{{VENUE_ADDRESS}}"),

    # Contact
    ("011-3562 3312",       "{{CONTACT_PHONE}}"),
    ("01135623312",         "{{CONTACT_PHONE_WA}}"),
    ("601135623312",        "{{CONTACT_PHONE_WA}}"),

    # Waze & Maps — replace URL terus
    (
        "https://waze.com/ul?q=Sebening+Embun+Garden+Glass+Hall+Dengkil&navigate=yes",
        "{{WAZE_LINK}}"
    ),
    (
        "https://maps.google.com/?q=Sebening+Embun+Garden+Glass+Hall,Lot+15,Jalan+Durian+1,43800+Dengkil,Selangor",
        "{{GMAP_LINK}}"
    ),
    (
        "https://maps.google.com/?q=Sebening+Embun+Garden+Glass+Hall,+Lot+15,+Jalan+Durian+1,+Kampung+Sungai+Buah,+43800+Dengkil,+Selangor",
        "{{GMAP_LINK}}"
    ),

    # WhatsApp text dalam URL (encode version)
    (
        "https://wa.me/601135623312?text=Assalamualaikum%20Encik%20Sufian%2C%20saya%20ingin%20bertanya%20tentang%20majlis%20perkahwinan%20Ahmad%20Nazmi%20%26%20Nur%20Farhana.",
        "https://wa.me/{{CONTACT_PHONE_WA}}?text=Assalamualaikum%20{{CONTACT_NAME}}%2C%20saya%20ingin%20bertanya%20tentang%20majlis."
    ),
]

# ─── Files nak convert ───
# (source_file, output_file)
FILES = [
    ("../kad-kawin-v2-celestial.html",    "templates/v2_celestial.html"),
    ("../kad-kawin-v3-garden.html",        "templates/v3_garden.html"),
    ("../kad-kawin-v4-arabian.html",       "templates/v4_arabian.html"),
    ("../kad-kawin-portrait-royal.html",   "templates/portrait_royal.html"),
]

def convert(src: str, dst: str):
    path = Path(src)
    if not path.exists():
        print(f"  ⚠️  Skip — fail tidak jumpa: {src}")
        return

    html = path.read_text(encoding="utf-8")
    count = 0
    for old, new in REPLACEMENTS:
        if old in html:
            html = html.replace(old, new)
            count += 1

    # Handle music section — replace src URL
    html = re.sub(
        r'(<source\s+src=")[^"]*(")',
        r'\1{{MUSIC_URL}}\2',
        html
    )

    # Replace music label
    html = re.sub(
        r'(<b>)[^<]*(</b>\s*Sedang bermain)',
        r'\1{{MUSIC_LABEL}}\2',
        html
    )
    html = re.sub(
        r'(<b>)[^<]*(</b>\s*Klik untuk main)',
        r'\1{{MUSIC_LABEL}}\2',
        html
    )

    Path(dst).write_text(html, encoding="utf-8")
    print(f"  ✅  {src} → {dst} ({count} replacements)")

if __name__ == "__main__":
    print("\n🔄 Converting templates...\n")
    for src, dst in FILES:
        convert(src, dst)
    print("\n✅ Done! Semua template dalam folder templates/\n")
    print("Sekarang jalankan: streamlit run app.py")
