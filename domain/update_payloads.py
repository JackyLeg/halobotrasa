import os
import yaml

input_dir = "/Users/imadenovandy/Project/halobotrasa/domain"

# List of menus based on what we generated earlier
menus = [
    "MBOutboundNonPT",
    "TAskripsi",
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
    dst_path = os.path.join(input_dir, f"{target_key}_domain.yml")
    
    if not os.path.exists(dst_path):
        print(f"File not found: {dst_path}")
        continue
        
    with open(dst_path, 'r') as f:
        # Read the #MENU_<MENU># header
        content = f.read()
        
    # extract header
    header = ""
    if content.startswith('version: "3.1"\n\n#'):
        header_end = content.find('#\n') + 2
        header = content[:header_end]
        content = content[header_end:]

    try:
        domain_data = yaml.safe_load(content)
    except yaml.YAMLError as exc:
        print(f"Error parsing {dst_path}: {exc}")
        continue

    if domain_data is None:
        continue

    if "responses" in domain_data:
        ask_menu_key = f"utter_ask_menu_{target_key}"
        if ask_menu_key in domain_data["responses"]:
            # Typically a list of dicts, get the first one
            resp_list = domain_data["responses"][ask_menu_key]
            if isinstance(resp_list, list) and len(resp_list) > 0:
                resp = resp_list[0]
                if "buttons" in resp:
                    for button in resp["buttons"]:
                        title = button.get("title", "")
                        # Map title to payload like /prosedur_<menu>
                        if "Prosedur" in title:
                            button["payload"] = f"/prosedur_{target_key}"
                        elif "Persyaratan" in title:
                            button["payload"] = f"/persyaratan_{target_key}"
                        elif "Transaksi" in title:
                            button["payload"] = f"/transaksi_{target_key}"
                        elif "Hasil" in title:
                            button["payload"] = f"/hasil_{target_key}"
                        elif "Status" in title:
                            button["payload"] = f"/status_{target_key}"
                            
        # Also fix the confirmation buttons
        conf_menu_key = f"utter_ask_menu_{target_key}_confirmation"
        if conf_menu_key in domain_data["responses"]:
            resp_list = domain_data["responses"][conf_menu_key]
            if isinstance(resp_list, list) and len(resp_list) > 0:
                resp = resp_list[0]
                if "buttons" in resp:
                    for button in resp["buttons"]:
                        title = button.get("title", "")
                        if "Yes" in title or "Ya" in title:
                            button["payload"] = "/affirm"
                        elif "No" in title or "Tidak" in title:
                            button["payload"] = "/deny"

    # Write back
    with open(dst_path, 'w') as f:
        if header:
            f.write(header)
        yaml.dump(domain_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        
    print(f"Updated {dst_path}")

print("Done updating domain payloads.")
