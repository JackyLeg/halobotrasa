import os
import re

stories_dir = "/Users/imadenovandy/Project/halobotrasa/data/stories"

menus = [
    "MBOutboundNonPT",
    "TAskripsi",
    "cuti",
    "fastTrackAPP",
    "graduationProcess",
    "kartuHasilStudi",
    "kartuPesertaUjian",
    "kartuRencanaStudi",
    "konseling",
    "konversi",
    "majoringApplication",
    "pembayaran",
    "pertukaranMahasiswa",
    "skpi",
    "skpmFK",
    "transkrip",
    "tugasAkhir",
    "wisuda",
]

for target_key in menus:
    dst_path = os.path.join(stories_dir, f"{target_key}_stories.yml")
    if not os.path.exists(dst_path):
        continue

    with open(dst_path, 'r') as f:
        content = f.read()

    # The goal is to find `- action: action_deny_cuti` and add `- checkpoint: check_menu_cuti` after it
    # We use regex to make sure it doesn't already have the checkpoint on the next line.
    
    # Matching: `      - action: action_deny_cuti\n`
    # Replace with: `      - action: action_deny_cuti\n      - checkpoint: check_menu_cuti\n`
    
    search_pattern = rf"(      - action: action_deny_{target_key})\n(?!\s+- checkpoint: check_menu_{target_key})"
    replace_pattern = f"\\1\n      - checkpoint: check_menu_{target_key}\n"
    
    new_content, count = re.subn(search_pattern, replace_pattern, content)

    if count > 0:
        with open(dst_path, 'w') as f:
            f.write(new_content)
        print(f"Updated {dst_path}")

print("Done fixing story loops.")
