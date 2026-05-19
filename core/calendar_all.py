'''
CalendarEventClass wrappt die Funktionalität der verschiedenen Kalender-APIs
und bietet eine einheitliche Schnittstelle für den Zugriff auf Kalenderdaten.
Im Moment nur Google Calendar.
Die Struktur ermöglicht die einfache Erweiterung um weitere Kalender-APIs in der Zukunft.
Dazu wird die Enum CalendarType verwendet, um verschiedene Kalender-Typen zu definieren,
und die CalendarEvent-Klasse delegiert die Aufrufe an die entsprechenden Methoden der Kalender-API
basierend auf dem angegebenen Kalender-Typ.
'''

from enum import Enum
import providers.google_parts.calendar_google as calendar_google

class CalendarType(Enum):
    '''
    CalendarType Enum definiert die unterstützten Kalender-Typen.
    '''
    GOOGLE = 'google'
    MICROSOFT = 'microsoft'


class CalendarEvent:
    '''
    CalendarEventClass wrappt die Funktionalität der verschiedenen Kalender-APIs
    und bietet eine einheitliche Schnittstelle für den Zugriff auf Kalenderdaten.
    '''
    def __init__(self, calendertype=CalendarType.GOOGLE.value):
        '''
        Initialisiert die CalendarEvent-Klasse mit dem angegebenen Kalender-Typ.
        :param calendertype: Der Typ des Kalenders, auf den zugegriffen werden soll (Standard ist 'google').
        '''
        match calendertype:
            case CalendarType.GOOGLE.value:
                self.calendarevent = calendar_google.GoogleCalendar()
            case _:
                raise ValueError("Unsupported calendar type")


    def get_all_calendar(self):
        '''
        Ruft alle Kalender ab.
        Delegiert den Aufruf an die entsprechende Methode der Kalender-API basierend auf dem Kalender-Typ.
        '''
        return self.calendarevent.get_all_calendar()


    def get_next_events(self, calendar_id='primary', max_results=3)->list:
        '''
        Ruft die nächsten Ereignisse eines bestimmten Kalenders ab.
        Delegiert den Aufruf an die entsprechende Methode der Kalender-API basierend auf dem Kalender-Typ.
        :param calendar_id: Die ID des Kalenders, von dem die nächsten Ereignisse abgerufen werden sollen.   (Standard ist 'primary' für den Hauptkalender).
        :param max_results: Die maximale Anzahl an Ergebnissen, die zurückgegeben werden sollen.
        :return: Gibt eine Liste der nächsten Ereignisse mit Zusammenfassung und Startzeit zurück.
        '''
        return self.calendarevent.get_next_events(calendar_id=calendar_id, max_results=max_results)


if __name__ == '__main__':
    pass

