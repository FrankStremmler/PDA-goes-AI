'''
Main für den Test für API-Integration von Google.
Als Modulares System aufgebaut mit calendar_google.py als eigenständiges Modul,
welches die Google Calendar API integriert.
calendar_all.py importiert calendar_google.py und ruft die Funktion get_next_event() auf,
um den nächsten Termin aus dem Google Kalender abzurufen und anzuzeigen.
'''
import datetime
from zoneinfo import ZoneInfo
from core.calendar_all import CalendarEvent, CalendarType
from providers.google_parts import drive_google

#from google_parts_FST import google_base

import core.global_functions as global_functions

# print("teste filetype:")
# try:
#     print(global_functions.get_file_type("assets/images/Kassenzettel/Nr0001.jpg"))
#     base64_str = global_functions.encode_file_to_base64("assets/images/Kassenzettel/Nr0001.jpg")
#     print(base64_str[:30] if base64_str else "Failed to encode file to base64")
# except FileNotFoundError as e:
#     print(f"Error: {e}")
drive_google.main()

def create_event_text(event)-> str:
    startzeit_utc = datetime.datetime.fromisoformat(event['start'].get('dateTime', event['start'].get('date')))
    # Umwandeln in lokale Zeit (z.B. MEZ)
    startzeit = startzeit_utc.astimezone(ZoneInfo('Europe/Berlin'))
    return f"Nächster Termin: {event.get('summary') or 'Ohne Titel'} am {startzeit:%d.%m.%y - %H:%M}"


def main():
    calevent = CalendarEvent()
    calendars = calevent.get_all_calendar()
    for calendar in calendars.get('items', []):
        print(f"Kalender: {calendar['summary']} (ID: {calendar['id']})")
    print("\n")
    calendarevents = calevent.get_next_events()
    print("Nächster Termin im Hauptkalender:")
    for event in calendarevents:
        print(create_event_text(event))
    print("\n")
    print("Nächster Termin im Kalender 'MasterSchool':")
    calendarevents = calevent.get_next_events       (calendar_id='tr4ut3foknv2ga14j5121sh0s1cffc5s@import.calendar.google.com')
    for event in calendarevents:
        print(create_event_text(event))
    print("\n")


if __name__ == '__main__':
    main()
