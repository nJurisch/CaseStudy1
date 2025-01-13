import os

from tinydb import TinyDB, Query
from datetime import datetime

# Datenbank initialisieren
db = TinyDB('device_management_db.json')
devices_table = db.table('devices')
reservations_table = db.table('reservations')

class Device:
    def __init__(self, device_name, managed_by_user_id, end_of_life, maintenance_interval, first_maintenance):
        self.device_name = device_name
        self.managed_by_user_id = managed_by_user_id
        self.end_of_life = end_of_life
        self.maintenance_interval = maintenance_interval
        self.first_maintenance = first_maintenance

    def store_data(self):
        """Speichert das Gerät in der Datenbank."""
        devices_table.insert(self.__dict__)

    def add_reservation(self, reserver, start_date, end_date):
        """Fügt eine Reservierung für das Gerät hinzu."""
        reservations_table.insert({
            "device_name": self.device_name,
            "reserver": reserver,
            "start_date": str(start_date),
            "end_date": str(end_date)
        })

    @classmethod
    def remove_reservation(cls, device_name, start_date):
        """Entfernt eine Reservierung basierend auf Gerät und Startdatum."""
        ReservationQuery = Query()
        reservations_table.remove((ReservationQuery.device_name == device_name) & (ReservationQuery.start_date == start_date))

    @classmethod
    def find_all(cls):
        """Liest alle Geräte aus der Datenbank und gibt sie als Objekte zurück."""
        devices = []
        for device_data in devices_table.all():
            devices.append(cls(
                device_name=device_data['device_name'],
                managed_by_user_id=device_data['managed_by_user_id'],
                end_of_life=device_data['end_of_life'],
                maintenance_interval=device_data['maintenance_interval'],
                first_maintenance=device_data['first_maintenance']
            ))
        return devices

    @classmethod
    def find_by_attribute(cls, attribute, value):
        """Findet ein Gerät basierend auf einem bestimmten Attribut und Wert."""
        DeviceQuery = Query()
        result = devices_table.search(DeviceQuery[attribute] == value)
        if result:
            device_data = result[0]
            return cls(
                device_name=device_data['device_name'],
                managed_by_user_id=device_data['managed_by_user_id'],
                end_of_life=device_data['end_of_life'],
                maintenance_interval=device_data['maintenance_interval'],
                first_maintenance=device_data['first_maintenance']
            )
        return None

    @classmethod
    def get_reservations(cls):
        """Gibt alle Reservierungen zurück."""
        return reservations_table.all()

    @classmethod
    def get_maintenance_schedule(cls):
        """Erstellt einen Wartungsplan für alle Geräte."""
        schedule = []
        for device in cls.find_all():
            schedule.append({
                "Gerät": device.device_name,
                "Nächste Wartung": device.first_maintenance
            })
        return schedule

    @classmethod
    def calculate_total_maintenance_cost(cls):
        """Berechnet die Gesamtkosten aller Gerätewartungen."""
        total_cost = 0
        for device in cls.find_all():
            total_cost += (365 / device.maintenance_interval) * 100  # Beispielkosten
        return total_cost