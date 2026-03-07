import os
import yaml
import re

menus = {
    "MBOutboundNonPT": "MBoutboundNonPT",
    "TAskripsi": "TAskripsi",
    "fastTrackAPP": "fastTrackApp",
    "graduationProcess": "graduationProcess",
    "kartuHasilStudi": "kartuHasilStudi",
    "kartuPesertaUjian": "kartuPesertaUjian",
    "kartuRencanaStudi": "kartuRencanaStudi",
    "konseling": "konseling",
    "konversi": "konversi",
    "majoringApplication": "majoringApplication",
    "pembayaran": "pembayaran",
    "pertukaranMahasiswa": "pertukaranMahasiswa",
    "skpi": "skpi",
    "skpmFK": "skpmFK",
    "transkrip": "transkrip",
    "tugasAkhir": "tugasAkhir",
    "wisuda": "wisuda",
}

input_dir = "/Users/imadenovandy/Project/chatbot-sis-trisakti/domain"
output_dir = "/Users/imadenovandy/Project/halobotrasa/domain"

os.makedirs(output_dir, exist_ok=True)

def remove_translations(data):
    if isinstance(data, dict):
        if 'translation' in data:
            del data['translation']
        for key, value in data.items():
            remove_translations(value)
    elif isinstance(data, list):
        for item in data:
            remove_translations(item)
    return data

for target_key, src_file_key in menus.items():
    src_path = os.path.join(input_dir, f"menu_{src_file_key}.yml")
    dst_path = os.path.join(output_dir, f"{target_key}_domain.yml")
    
    if not os.path.exists(src_path):
        print(f"File not found: {src_path}")
        continue
        
    with open(src_path, 'r') as f:
        try:
            domain_data = yaml.safe_load(f)
        except yaml.YAMLError as exc:
            print(f"Error parsing {src_path}: {exc}")
            continue

    if domain_data is None:
        continue
        
    # Set up basic domain structure
    processed_domain = {
        "version": "3.1",
        "intents": [
            f"{target_key}_menu",
            f"prosedur_{target_key}",
            f"persyaratan_{target_key}",
            f"transaksi_{target_key}",
            f"hasil_{target_key}",
            f"status_{target_key}"
        ],
        "slots": {},
        "responses": {},
        "actions": [
            f"action_answer_{target_key}",
            f"action_ask_confirmation_{target_key}",
            f"action_deny_{target_key}"
        ]
    }
    
    # Process Slots
    if "slots" in domain_data:
        for slot_name, slot_def in domain_data["slots"].items():
            # Rename if necessary based on our target_key
            new_slot_name = slot_name
            if src_file_key in slot_name:
                new_slot_name = slot_name.replace(src_file_key, target_key)
            
            # Map mappings to type custom
            if "mappings" in slot_def:
                slot_def["mappings"] = [{"type": "custom"}]
            if "influence_conversation" not in slot_def:
                slot_def["influence_conversation"] = False
                
            processed_domain["slots"][new_slot_name] = slot_def

    # Add confirmation slot just in case
    conf_slot = f"menu_{target_key}_confirmation"
    if conf_slot not in processed_domain["slots"]:
        processed_domain["slots"][conf_slot] = {
            "type": "bool",
            "influence_conversation": False,
            "mappings": [{"type": "custom"}]
        }

    # Process Responses
    if "responses" in domain_data:
        responses = domain_data["responses"]
        remove_translations(responses)
        
        for resp_name, resp_list in responses.items():
            new_resp_name = resp_name
            # Fix response name if there's casing differences
            if src_file_key in resp_name:
                new_resp_name = resp_name.replace(src_file_key, target_key)

            # Process conditions format
            new_resp_list = []
            if isinstance(resp_list, list):
                for item in resp_list:
                    new_item = item.copy()
                    if "condition" in new_item:
                        cond_str = new_item["condition"]
                        # expected "slots.fakultas = 'Fakultas Hukum'"
                        match = re.search(r"slots\.(\w+)\s*=\s*'([^']+)'", cond_str)
                        if match:
                            slot_name = match.group(1)
                            slot_val = match.group(2)
                            new_item["condition"] = [
                                {
                                    "type": "slot",
                                    "name": slot_name,
                                    "value": slot_val
                                }
                            ]
                    new_resp_list.append(new_item)
            
            processed_domain["responses"][new_resp_name] = new_resp_list
            
    # Add utter_ask_menu_confirmation and utter_menu_cancelled based on target_key
    # (Since these might exist but we want to ensure they match our stories and actions exactly)
    
    with open(dst_path, 'w') as f:
        yaml.dump(processed_domain, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    # Adding #MENU_XXX# comment header
    with open(dst_path, 'r') as f:
        content = f.read()
    
    with open(dst_path, 'w') as f:
        f.write("version: \"3.1\"\n\n")
        f.write(content.replace("version: '3.1'\n", ""))
        
    print(f"Generated {dst_path}")

print("Done converting domains.")
