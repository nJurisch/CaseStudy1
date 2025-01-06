import pandas as pd
import streamlit as st
from tinydb import TinyDB, Query
from datetime import datetime, timedelta, date
import json

# Custom JSON encoder for datetime and date
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)

# Initialize database
db = TinyDB('device_management_db.json')
users_table = db.table('users')
devices_table = db.table('devices')
reservations_table = db.table('reservations')

# User class
class User:
    def __init__(self, id, name):
        self.id = id  # E-Mail-Adresse
        self.name = name  # Name des Nutzers

# Device class
class Device:
    def __init__(self, id, name, responsible_person, end_of_life,
                 first_maintenance=None, next_maintenance=None, 
                 maintenance_interval=0, maintenance_cost=0.0):
        self.id = id
        self.name = name
        self.responsible_person = responsible_person
        self.__creation_date = datetime.now()
        self.__last_update = datetime.now()
        self.end_of_life = end_of_life
        self.first_maintenance = datetime.fromisoformat(first_maintenance) if isinstance(first_maintenance, str) else first_maintenance
        self.next_maintenance = next_maintenance or (self.first_maintenance + timedelta(days=maintenance_interval))
        self.maintenance_interval = maintenance_interval
        self.maintenance_cost = maintenance_cost

    def update_maintenance_schedule(self):
        if not self.next_maintenance:
            self.next_maintenance = self.first_maintenance + timedelta(days=self.maintenance_interval)
        else:
            self.next_maintenance += timedelta(days=self.maintenance_interval)
        self.__last_update = datetime.now()

    def maintenance_cost_per_year(self):
        return (365 / self.maintenance_interval) * self.maintenance_cost

    def reserve_maintenance_dates(self):
        current_date = self.first_maintenance
        while current_date <= datetime.now().date():
            reservations_table.insert({
                "device_id": self.id,
                "reserver": "Maintenance",  # Reserved for maintenance
                "start_date": str(current_date),
                "end_date": str(current_date)
            })
            current_date += timedelta(days=self.maintenance_interval)

    def reserve_next_maintenance(self):
        if self.next_maintenance <= self.end_of_life:
            reservations_table.insert({
                "device_id": self.id,
                "reserver": "Maintenance",
                "start_date": str(self.next_maintenance),
                "end_date": str(self.next_maintenance)
            })

# Streamlit UI
st.title("Geräte-Verwaltung an einer Hochschule")

menu = st.sidebar.selectbox("Menü", ["Nutzer-Verwaltung", "Geräte-Verwaltung", "Reservierungssystem", "Wartungs-Management"])

if menu == "Nutzer-Verwaltung":
    st.header("Nutzer-Verwaltung")
    action = st.radio("Aktion", ["Nutzer anlegen", "Nutzer anzeigen", "Nutzer entfernen"])

    if action == "Nutzer anlegen":
        name = st.text_input("Name")
        email = st.text_input("E-Mail-Adresse")
        if st.button("Speichern"):
            user = User(id=email, name=name)
            users_table.insert(user.__dict__)
            st.success("Nutzer wurde erfolgreich angelegt.")

    elif action == "Nutzer anzeigen":
        users = pd.DataFrame(users_table.all())
        st.dataframe(users)

    elif action == "Nutzer entfernen":
        user_id = st.selectbox("Wähle Nutzer zur Entfernung", [u['id'] for u in users_table.all()])
        if st.button("Entfernen"):
            UserQuery = Query()
            users_table.remove(UserQuery.id == user_id)
            st.success("Nutzer wurde erfolgreich entfernt.")

elif menu == "Geräte-Verwaltung":
    st.header("Geräte-Verwaltung")
    action = st.radio("Aktion", ["Gerät anlegen", "Geräte anzeigen", "Gerät entfernen"])

    if action == "Gerät anlegen":
        device_name = st.text_input("Gerätename")
        responsible_person = st.selectbox("Verantwortlicher Nutzer", [u['id'] for u in users_table.all()])
        end_of_life = st.date_input("End-of-Life Datum")
        maintenance_interval = st.number_input("Wartungsintervall (Tage)", min_value=1, step=1)
        maintenance_cost = st.number_input("Wartungskosten", min_value=0.0, step=0.1)
        first_maintenance = st.date_input("Erstes Wartungsdatum", datetime.now().date())
        auto_reserve = st.checkbox("Automatische Reservierung für alle Wartungstermine")
        if st.button("Speichern"):
            device = Device(
                id=len(devices_table) + 1,
                name=device_name,
                responsible_person=responsible_person,
                end_of_life=str(end_of_life),
                first_maintenance=first_maintenance,
                maintenance_interval=maintenance_interval,
                maintenance_cost=maintenance_cost
            )
            devices_table.insert(json.loads(json.dumps(device.__dict__, cls=DateTimeEncoder)))
            if auto_reserve:
                device.reserve_maintenance_dates()
            else:
                device.reserve_next_maintenance()
            st.success("Gerät wurde erfolgreich angelegt und Wartungen reserviert.")

    elif action == "Geräte anzeigen":
        devices = pd.DataFrame(devices_table.all())
        if not devices.empty:
            devices['maintenance_interval'] = devices['maintenance_interval'].fillna(0).astype(int)
            devices['maintenance_cost'] = devices['maintenance_cost'].fillna(0.0).astype(float)
        st.dataframe(devices)

    elif action == "Gerät entfernen":
        device_id = st.selectbox("Wähle Gerät zur Entfernung", [d.doc_id for d in devices_table.all()])
        if st.button("Entfernen"):
            devices_table.remove(doc_ids=[device_id])
            st.success("Gerät wurde erfolgreich entfernt.")

elif menu == "Reservierungssystem":
    st.header("Reservierungssystem")
    action = st.radio("Aktion", ["Reservierung eintragen", "Reservierungen anzeigen", "Reservierung entfernen"])

    if action == "Reservierung eintragen":
        device_id = st.selectbox("Gerät", [d.doc_id for d in devices_table.all()])
        reserver = st.selectbox("Reservierer", [u['id'] for u in users_table.all()])
        start_date = st.date_input("Reservierungsbeginn")
        end_date = st.date_input("Reservierungsende")
        if st.button("Speichern"):
            reservations_table.insert({
                "device_id": device_id,
                "reserver": reserver,
                "start_date": str(start_date),
                "end_date": str(end_date)
            })
            st.success("Reservierung wurde erfolgreich eingetragen.")

    elif action == "Reservierungen anzeigen":
        reservations = pd.DataFrame(reservations_table.all())
        if not reservations.empty and 'device_id' in reservations.columns:
            reservations['Gerät'] = reservations['device_id'].apply(
                lambda x: devices_table.get(doc_id=x)['name'] if devices_table.get(doc_id=x) else "Unbekannt"
            )
        st.dataframe(reservations)

    elif action == "Reservierung entfernen":
        reservation_id = st.selectbox("Wähle Reservierung zur Entfernung", [r.doc_id for r in reservations_table.all()])
        if st.button("Entfernen"):
            reservations_table.remove(doc_ids=[reservation_id])
            st.success("Reservierung wurde erfolgreich entfernt.")

elif menu == "Wartungs-Management":
    st.header("Wartungs-Management")
    action = st.radio("Aktion", ["Wartungen anzeigen", "Wartungskosten anzeigen"])

    if action == "Wartungen anzeigen":
        reservations = pd.DataFrame(reservations_table.all())
        if not reservations.empty and 'device_id' in reservations.columns:
            maintenance_reservations = reservations[reservations['reserver'] == "Maintenance"]
            maintenance_reservations['Gerät'] = maintenance_reservations['device_id'].apply(
                lambda x: devices_table.get(doc_id=x)['name'] if devices_table.get(doc_id=x) else "Unbekannt"
            )
            st.dataframe(maintenance_reservations)

    elif action == "Wartungskosten anzeigen":
        devices = devices_table.all()
        total_cost = sum(d.get('maintenance_cost', 0.0) for d in devices)
        st.write(f"Gesamtkosten für die nächste Wartung: {total_cost:.2f} EUR")
