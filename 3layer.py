from ui_device import display_device_management
from users import User
from devices import Device
from queries import find_devices
import streamlit as st

# Initialisierung des Frontends
st.title("Geräte-Verwaltung System (Drei-Schichten-Architektur)")

menu = st.sidebar.selectbox("Menü", ["Nutzer-Verwaltung", "Geräte-Verwaltung", "Reservierungssystem", "Wartungs-Management"])

if menu == "Nutzer-Verwaltung":
    st.header("Nutzer-Verwaltung")
    action = st.radio("Aktion", ["Nutzer anlegen", "Nutzer anzeigen", "Nutzer entfernen"])

    if action == "Nutzer anlegen":
        name = st.text_input("Name")
        email = st.text_input("E-Mail-Adresse")
        if st.button("Speichern"):
            user = User(id=email, name=name)
            user.store_data()
            st.success("Nutzer wurde erfolgreich angelegt.")

    elif action == "Nutzer anzeigen":
        users = User.find_all()
        if users:
            user_data = [{"E-Mail": u.id, "Name": u.name} for u in users]
            st.table(user_data)
        else:
            st.write("Keine Nutzer gefunden.")

    elif action == "Nutzer entfernen":
        user_id = st.selectbox("Wähle Nutzer zur Entfernung", [u.id for u in User.find_all()])
        if st.button("Entfernen"):
            User.delete(user_id)
            st.success("Nutzer wurde erfolgreich entfernt.")

elif menu == "Geräte-Verwaltung":
    st.header("Geräte-Verwaltung")
    action = st.radio("Aktion", ["Gerät anlegen", "Geräte anzeigen"])

    if action == "Gerät anlegen":
        device_name = st.text_input("Gerätename")
        responsible_person = st.selectbox("Verantwortlicher Nutzer", [u.id for u in User.find_all()])
        end_of_life = st.date_input("End-of-Life Datum", key="end_of_life")
        maintenance_interval = st.number_input("Wartungsintervall (Tage)", min_value=1, step=1, key="maintenance_interval")
        first_maintenance = st.date_input("Erstes Wartungsdatum", key="first_maintenance")
        
        if st.button("Speichern"):
            device = Device(
                device_name=device_name,
                managed_by_user_id=responsible_person,
                end_of_life=str(end_of_life),
                maintenance_interval=maintenance_interval,
                first_maintenance=str(first_maintenance)
            )
            device.store_data()
            st.success("Gerät wurde erfolgreich angelegt.")

    elif action == "Geräte anzeigen":
        devices = Device.find_all()
        if devices:
            device_data = [{"Gerätename": d.device_name, "Verantwortlicher": d.managed_by_user_id, "End-of-Life": d.end_of_life, "Wartungsintervall": d.maintenance_interval, "Erste Wartung": d.first_maintenance} for d in devices]
            st.table(device_data)
        else:
            st.write("Keine Geräte gefunden.")

elif menu == "Reservierungssystem":
    st.header("Reservierungssystem")
    action = st.radio("Aktion", ["Reservierung eintragen", "Reservierungen anzeigen"])

    if action == "Reservierung eintragen":
        devices = find_devices()
        if devices:
            device_name = st.selectbox("Gerät auswählen", devices)
            loaded_device = Device.find_by_attribute("device_name", device_name)
            if loaded_device:
                st.write(loaded_device)
                reserver = st.text_input("Reservierer")
                start_date = st.date_input("Startdatum")
                end_date = st.date_input("Enddatum")
                if st.button("Reservierung speichern"):
                    loaded_device.add_reservation(reserver, start_date, end_date)
                    st.success("Reservierung wurde gespeichert.")
            else:
                st.error("Gerät nicht gefunden.")
        else:
            st.warning("Keine Geräte vorhanden.")

    elif action == "Reservierungen anzeigen":
        reservations = Device.get_reservations()
        if reservations:
            st.table(reservations)
        else:
            st.write("Keine Reservierungen gefunden.")

elif menu == "Wartungs-Management":
    st.header("Wartungs-Management")
    maintenance_action = st.radio("Aktion", ["Wartungen anzeigen", "Wartungskosten berechnen"])

    if maintenance_action == "Wartungen anzeigen":
        maintenance_data = Device.get_maintenance_schedule()
        st.write(maintenance_data)

    elif maintenance_action == "Wartungskosten berechnen":
        total_cost = Device.calculate_total_maintenance_cost()
        st.write(f"Gesamtkosten für Wartungen: {total_cost:.2f} EUR")
