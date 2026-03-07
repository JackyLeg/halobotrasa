from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction

# List of all menus mapped to their display name used in options
MENUS = {
    "cuti": "Cuti",
    "MBOutboundNonPT": "MBOutboundNonPT",
    "TAskripsi": "TAskripsi",
    "fastTrackAPP": "FastTrackApp",
    "graduationProcess": "Graduation Process",
    "kartuHasilStudi": "KHS",
    "kartuPesertaUjian": "Kartu Peserta Ujian",
    "kartuRencanaStudi": "KRS",
    "konseling": "Konseling",
    "konversi": "Konversi",
    "majoringApplication": "Majoring Application",
    "pembayaran": "Pembayaran",
    "pertukaranMahasiswa": "Pertukaran Mahasiswa",
    "skpi": "SKPI",
    "skpmFK": "SKPM FK",
    "transkrip": "Transkrip",
    "tugasAkhir": "Tugas Akhir",
    "wisuda": "Wisuda",
}

FAKULTAS = ""  # Set this value when ready

def create_action_answer(menu_key: str, display_name: str):
    class ActionAnswerMenu(Action):
        def name(self) -> Text:
            return f"action_answer_{menu_key}"

        def run(self, dispatcher: CollectingDispatcher,
                tracker: Tracker,
                domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
            
            menu_value = tracker.get_slot(f"menu_{menu_key}")

            dispatcher.utter_message(response=f"utter_menu_{menu_key}_ok")

            menu_to_response = {
                f"Prosedur {display_name}": f"utter_answer_prosedur_{menu_key}",
                f"Persyaratan {display_name}": f"utter_answer_persyaratan_{menu_key}",
                f"Transaksi {display_name}": f"utter_answer_transaksi_{menu_key}",
                f"Hasil {display_name}": f"utter_answer_hasil_{menu_key}",
                f"Status {display_name}": f"utter_answer_status_{menu_key}",
            }

            response = menu_to_response.get(menu_value)

            if response:
                dispatcher.utter_message(response=response)
            else:
                dispatcher.utter_message(response=f"utter_answer_error_{menu_key}")

            return [FollowupAction(f"utter_ask_menu_{menu_key}")]
            
    ActionAnswerMenu.__name__ = f"ActionAnswer_{menu_key}"
    return ActionAnswerMenu


def create_action_ask_confirmation(menu_key: str, display_name: str):
    class ActionAskConfirmationMenu(Action):
        def name(self) -> Text:
            return f"action_ask_confirmation_{menu_key}"

        def run(self, dispatcher: CollectingDispatcher,
                tracker: Tracker,
                domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
            
            intent = tracker.get_intent_of_latest_message()
            intent_lower = intent.lower() if intent else ""

            intent_to_menu = {
                f"prosedur_{menu_key}".lower(): f"Prosedur {display_name}",
                f"persyaratan_{menu_key}".lower(): f"Persyaratan {display_name}",
                f"transaksi_{menu_key}".lower(): f"Transaksi {display_name}",
                f"hasil_{menu_key}".lower(): f"Hasil {display_name}",
                f"status_{menu_key}".lower(): f"Status {display_name}",
            }

            matched_menu = intent_to_menu.get(intent_lower)

            if matched_menu:
                dispatcher.utter_message(
                    text=f"Anda telah memilih opsi: {matched_menu}. Apakah itu benar?",
                    buttons=[
                        {"title": "Ya", "payload": "/affirm"},
                        {"title": "Tidak", "payload": "/deny"},
                    ]
                )

            fakultas_value = FAKULTAS if matched_menu in (f"Prosedur {display_name}", f"Persyaratan {display_name}") else None
            return [SlotSet(f"menu_{menu_key}", matched_menu), SlotSet("fakultas", fakultas_value)]
            
    ActionAskConfirmationMenu.__name__ = f"ActionAskConfirmation_{menu_key}"
    return ActionAskConfirmationMenu


def create_action_deny(menu_key: str):
    class ActionDenyMenu(Action):
        def name(self) -> Text:
            return f"action_deny_{menu_key}"

        def run(self, dispatcher: CollectingDispatcher,
                tracker: Tracker,
                domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

            dispatcher.utter_message(response=f"utter_menu_{menu_key}_cancelled")
            return [FollowupAction(f"utter_ask_menu_{menu_key}")]

    ActionDenyMenu.__name__ = f"ActionDeny_{menu_key}"
    return ActionDenyMenu

# Dynamically instantiate and register all action classes
for key, name in MENUS.items():
    globals()[f"ActionAnswer_{key}"] = create_action_answer(key, name)
    globals()[f"ActionAskConfirmation_{key}"] = create_action_ask_confirmation(key, name)
    globals()[f"ActionDeny_{key}"] = create_action_deny(key)
