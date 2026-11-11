import json
import urllib.request
import urllib.error
from typing import Any, Text, Dict, List

try:
    import requests
except ImportError:
    requests = None

try:
    from rasa_sdk import Action, Tracker
    from rasa_sdk.executor import CollectingDispatcher
    from rasa_sdk.events import SlotSet, FollowupAction
except ImportError:
    class Action:
        pass
    class Tracker:
        pass
    class CollectingDispatcher:
        pass
    def SlotSet(*args, **kwargs):
        return {}
    def FollowupAction(*args, **kwargs):
        return {}

# API Helpers
def fetch_role_api(sender_id: str) -> str:
    url = "https://sismob.trisakti.ac.id/api/get-role"
    try:
        if requests:
            resp = requests.post(url, json={"IdLogin": sender_id}, timeout=10)
            if resp.status_code == 200:
                role = resp.json().get("role")
                if role and role != "No Role":
                    return role
        else:
            payload = json.dumps({"IdLogin": sender_id}).encode("utf-8")
            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    role = data.get("role")
                    if role and role != "No Role":
                        return role
    except Exception as e:
        print(f"API Error get-role: {e}")
    return "STD"

def fetch_peraturan_api(dispatcher: CollectingDispatcher, sender_id: str, context_name: str) -> bool:
    url = "https://sismob.trisakti.ac.id/api/get-peraturan"
    payload_data = {"IdLogin": sender_id, "context": context_name}
    try:
        if requests:
            resp = requests.post(url, json=payload_data, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == 200 and "body" in data and "data" in data["body"] and data["body"]["data"]:
                    aturan = data["body"]["data"].get("aturan")
                    if aturan:
                        dispatcher.utter_message(text=aturan)
                        return True
        else:
            payload = json.dumps(payload_data).encode("utf-8")
            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    if data.get("status") == 200 and "body" in data and "data" in data["body"] and data["body"]["data"]:
                        aturan = data["body"]["data"].get("aturan")
                        if aturan:
                            dispatcher.utter_message(text=aturan)
                            return True
    except Exception as e:
        print(f"API Error get-peraturan: {e}")
    return False

# Base Shared Actions
class ActionCheckUserRole(Action):
    def name(self) -> Text:
        return "action_check_user_role"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        role = tracker.get_slot("user_role")
        if not role:
            role = fetch_role_api(tracker.sender_id)
        return [SlotSet("user_role", role)]

class ActionDetectLanguage(Action):
    def name(self) -> Text:
        return "action_detect_language"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_text = tracker.latest_message.get("text", "")
        if not user_text:
            return [SlotSet("language", "id")]
        text_lower = user_text.lower().strip()
        english_keywords = ["hi", "hello", "hey", "good", "morning", "afternoon", "evening", "please", "help"]
        indonesian_keywords = ["halo", "hai", "selamat", "pagi", "siang", "sore", "malam", "tolong", "bantu"]
        words = text_lower.split()
        en_score = sum(1 for w in words if w in english_keywords)
        id_score = sum(1 for w in words if w in indonesian_keywords)
        detected = "en" if en_score > id_score else "id"
        return [SlotSet("language", detected)]

class ActionHelloWorld(Action):
    def name(self) -> Text:
        return "hello_world"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        name_val = tracker.get_slot("name") or "Mahasiswa/Dosen"
        dispatcher.utter_message(response="utter_greet", name=name_val)
        return []

class ActionShowListMenu(Action):
    def name(self) -> Text:
        return "action_show_list_menu"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        role = tracker.get_slot("user_role")
        if not role:
            role = fetch_role_api(tracker.sender_id)
        
        if role == "DSNWALI":
            dispatcher.utter_message(response="utter_ask_list_menu_dosenwali")
        elif role == "DSN":
            dispatcher.utter_message(response="utter_ask_list_menu_dosen")
        else:
            dispatcher.utter_message(response="utter_ask_list_menu_mahasiswa")
            
        return [SlotSet("user_role", role)]

# Menu Action Factories
def create_action_ask_confirmation(menu_key: str, display_name: str):
    class ActionAskConfirmation(Action):
        def name(self) -> Text:
            return f"action_ask_confirmation_{menu_key}"

        def run(self, dispatcher: CollectingDispatcher,
                tracker: Tracker,
                domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
            intent = tracker.get_intent_of_latest_message() or ""
            intent_lower = intent.lower()
            
            matched = f"Menu {display_name}"
            if "prosedur" in intent_lower:
                matched = f"Prosedur {display_name}"
            elif "persyaratan" in intent_lower:
                matched = f"Persyaratan {display_name}"
            elif "transaksi" in intent_lower:
                matched = f"Transaksi {display_name}"
            elif "hasil" in intent_lower:
                matched = f"Hasil {display_name}"
            elif "status" in intent_lower:
                matched = f"Status {display_name}"
            elif "ganti_password" in intent_lower:
                matched = "Ganti Password"
            elif "keluar" in intent_lower:
                matched = "Keluar"

            dispatcher.utter_message(
                text=f"Anda telah memilih opsi: {matched}. Apakah itu benar?",
                buttons=[
                    {"title": "Ya", "payload": "/affirm"},
                    {"title": "Tidak", "payload": "/deny"},
                ]
            )
            return [SlotSet(f"menu_{menu_key}", matched)]

    ActionAskConfirmation.__name__ = f"ActionAskConfirmation_{menu_key}"
    return ActionAskConfirmation

def create_action_answer(menu_key: str, display_name: str):
    class ActionAnswer(Action):
        def name(self) -> Text:
            return f"action_answer_{menu_key}"

        def run(self, dispatcher: CollectingDispatcher,
                tracker: Tracker,
                domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
            menu_value = tracker.get_slot(f"menu_{menu_key}") or ""
            
            dispatcher.utter_message(response=f"utter_menu_{menu_key}_ok")
            dispatcher.utter_message(json_message={"context": menu_key})

            handled = False
            if "Prosedur" in menu_value or "prosedur" in menu_value.lower():
                if fetch_peraturan_api(dispatcher, tracker.sender_id, f"{menu_key}_prosedur"):
                    handled = True
                else:
                    dispatcher.utter_message(response=f"utter_answer_prosedur_{menu_key}")
                    handled = True
            elif "Persyaratan" in menu_value or "persyaratan" in menu_value.lower():
                if fetch_peraturan_api(dispatcher, tracker.sender_id, f"{menu_key}_persyaratan"):
                    handled = True
                else:
                    dispatcher.utter_message(response=f"utter_answer_persyaratan_{menu_key}")
                    handled = True
            elif "Transaksi" in menu_value or "transaksi" in menu_value.lower():
                dispatcher.utter_message(response=f"utter_answer_transaksi_{menu_key}")
                handled = True
            elif "Hasil" in menu_value or "hasil" in menu_value.lower():
                dispatcher.utter_message(response=f"utter_answer_hasil_{menu_key}")
                handled = True
            elif "Status" in menu_value or "status" in menu_value.lower():
                dispatcher.utter_message(response=f"utter_answer_status_{menu_key}")
                handled = True
            elif "Ganti Password" in menu_value:
                dispatcher.utter_message(response="utter_answer_ganti_password")
                handled = True
            elif "Keluar" in menu_value:
                dispatcher.utter_message(response="utter_answer_keluar")
                handled = True

            if not handled:
                err_resp = f"utter_answer_error_{menu_key}"
                if err_resp in domain.get("responses", {}):
                    dispatcher.utter_message(response=err_resp)
                else:
                    dispatcher.utter_message(text="Maaf, pilihan tidak dikenali. Silakan pilih opsi lain.")

            return [FollowupAction(f"utter_ask_menu_{menu_key}")]

    ActionAnswer.__name__ = f"ActionAnswer_{menu_key}"
    return ActionAnswer

def create_action_deny(menu_key: str):
    class ActionDeny(Action):
        def name(self) -> Text:
            return f"action_deny_{menu_key}"

        def run(self, dispatcher: CollectingDispatcher,
                tracker: Tracker,
                domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
            dispatcher.utter_message(response=f"utter_menu_{menu_key}_cancelled")
            return [FollowupAction(f"utter_ask_menu_{menu_key}")]

    ActionDeny.__name__ = f"ActionDeny_{menu_key}"
    return ActionDeny

# Register all menu actions
MENUS = {
    'MBoutboundNonPT': 'MB Outbound Non PT',
    'cuti': 'Cuti',
    'fastTrackApp': 'Fast Track App',
    'graduationProcess': 'Graduation Process',
    'kartuHasilStudi': 'Kartu Hasil Studi',
    'kartuPesertaUjian': 'Kartu Peserta Ujian',
    'kartuRencanaStudi': 'Kartu Rencana Studi',
    'konseling': 'Konseling',
    'pembayaran': 'Pembayaran',
    'pertukaranMahasiswa': 'Pertukaran Mahasiswa',
    'profil': 'Profil',
    'skpi': 'SKPI',
    'transkrip': 'Transkrip',
    'tugasAkhir': 'Tugas Akhir',
    'wisuda': 'Wisuda',
    'absensiKelas': 'Absensi Kelas',
    'absensiUjian': 'Absensi Ujian',
    'bimbinganDiktisaintekBerdampak': 'Bimbingan Diktisaintek Berdampak',
    'bimbinganKerjaPraktek': 'Bimbingan Kerja Praktek',
    'bimbinganSkripsi': 'Bimbingan Skripsi',
    'bkd': 'BKD',
    'daftarMahasiswaPerKelas': 'Daftar Mahasiswa Per Kelas',
    'evaluasiKelas': 'Evaluasi Kelas',
    'melihatHonor': 'Melihat Honor',
    'membuatSoalUjian': 'Membuat Soal Ujian',
    'mentoringDosen': 'Mentoring Dosen',
    'pelaporanPdpt': 'Pelaporan PDPT',
    'pengisianNilai': 'Pengisian Nilai',
    'portofolio': 'Portofolio',
    'rps': 'RPS',
    'bimbinganAkademik': 'Bimbingan Akademik',
    'biodataMahasiswa': 'Biodata Mahasiswa',
    'persetujuanPengambilanKrs': 'Persetujuan Pengambilan KRS',
    'persetujuanPengisianKrs': 'Persetujuan Pengisian KRS',
}

for menu_key, display_name in MENUS.items():
    cls_ask = create_action_ask_confirmation(menu_key, display_name)
    globals()[cls_ask.__name__] = cls_ask

    cls_answer = create_action_answer(menu_key, display_name)
    globals()[cls_answer.__name__] = cls_answer

    cls_deny = create_action_deny(menu_key)
    globals()[cls_deny.__name__] = cls_deny
