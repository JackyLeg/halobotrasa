from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction

FAKULTAS = ""  # Set this value when ready

class ActionAnswerCuti(Action):
    def name(self) -> Text:
        return "action_answer_cuti"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        menu_cuti = tracker.get_slot("menu_cuti")

        dispatcher.utter_message(response="utter_menu_cuti_ok")
        dispatcher.utter_message(json_message={"context": "cuti"})

        menu_to_response = {
            "Prosedur Cuti": "utter_answer_prosedur_cuti",
            "Persyaratan Cuti": "utter_answer_persyaratan_cuti",
            "Transaksi Cuti": "utter_answer_transaksi_cuti",
            "Hasil Cuti": "utter_answer_hasil_cuti",
        }

        response = menu_to_response.get(menu_cuti)

        if response:
            dispatcher.utter_message(response=response)
        else:
            dispatcher.utter_message(response="utter_answer_error_cuti")

        return [FollowupAction("utter_ask_menu_cuti")]


class ActionAskConfirmationCuti(Action):
    def name(self) -> Text:
        return "action_ask_confirmation_cuti"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        intent = tracker.get_intent_of_latest_message()

        intent_to_menu = {
            "prosedur_cuti": "Prosedur Cuti",
            "persyaratan_cuti": "Persyaratan Cuti",
            "transaksi_cuti": "Transaksi Cuti",
            "hasil_cuti": "Hasil Cuti",
        }

        menu_cuti = intent_to_menu.get(intent)

        dispatcher.utter_message(
            text=f"Anda telah memilih opsi: {menu_cuti}. Apakah itu benar?",
            buttons=[
                {"title": "Ya", "payload": "/affirm"},
                {"title": "Tidak", "payload": "/deny"},
            ]
        )

        fakultas_value = FAKULTAS if menu_cuti in ("Prosedur Cuti", "Persyaratan Cuti") else None
        return [SlotSet("menu_cuti", menu_cuti), SlotSet("fakultas", fakultas_value)]


class ActionDenyCuti(Action):
    def name(self) -> Text:
        return "action_deny_cuti"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(response="utter_menu_cuti_cancelled")

        return [FollowupAction("utter_ask_menu_cuti")]