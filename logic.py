import sqlite3
from geopy.geocoders import Nominatim
from datetime import datetime

class TransportSystem:
    def __init__(self):
        self.db_path = "logistics.db"
        self.geolocator = Nominatim(user_agent="auto_assist_v3")
        self.create_tables()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def create_tables(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        # Πίνακας Φορτηγών
        cursor.execute('''CREATE TABLE IF NOT EXISTS trucks 
                          (plate TEXT PRIMARY KEY, driver TEXT, type TEXT, base TEXT, location TEXT, flexible INTEGER)''')
        # Πίνακας Ενεργών Φορτίων
        cursor.execute('''CREATE TABLE IF NOT EXISTS jobs 
                          (id TEXT PRIMARY KEY, origin TEXT, destination TEXT, v_type TEXT, status TEXT, location TEXT)''')
        # Πίνακας Ιστορικού (Προσθήκη ημερομηνίας παράδοσης)
        cursor.execute('''CREATE TABLE IF NOT EXISTS history 
                          (id TEXT, origin TEXT, destination TEXT, v_type TEXT, delivery_date TEXT)''')
        conn.commit()
        conn.close()

    # --- ΔΙΑΧΕΙΡΙΣΗ ΦΟΡΤΗΓΩΝ ---
    def add_truck(self, plate, driver, t_type, base, flexible):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO trucks VALUES (?, ?, ?, ?, ?, ?)", 
                       (plate, driver, t_type, base, base, 1 if flexible else 0))
        conn.commit()
        conn.close()

    def get_trucks(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM trucks")
        rows = cursor.fetchall()
        conn.close()
        return rows

    def update_truck_loc(self, plate, new_loc):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE trucks SET location = ? WHERE plate = ?", (new_loc, plate))
        conn.commit()
        conn.close()

    def delete_truck(self, plate):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM trucks WHERE plate = ?", (plate,))
        conn.commit()
        conn.close()

    # --- ΔΙΑΧΕΙΡΙΣΗ ΦΟΡΤΙΩΝ & ΙΣΤΟΡΙΚΟΥ ---
    def add_job(self, v_id, origin, dest, v_type):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO jobs VALUES (?, ?, ?, ?, ?, ?)", 
                       (v_id, origin, dest, v_type, "ΣΕ ΑΝΑΜΟΝΗ", origin))
        conn.commit()
        conn.close()

    def get_jobs(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM jobs")
        rows = cursor.fetchall()
        conn.close()
        return rows

    def update_job(self, v_id, status, loc):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if status == "ΠΑΡΑΔΟΘΗΚΕ":
            # 1. Βρίσκουμε τα στοιχεία του οχήματος
            cursor.execute("SELECT id, origin, destination, v_type FROM jobs WHERE id = ?", (v_id,))
            job = cursor.fetchone()
            if job:
                # 2. Το βάζουμε στο ιστορικό με ημερομηνία
                date_now = datetime.now().strftime("%d/%m/%Y %H:%M")
                cursor.execute("INSERT INTO history VALUES (?, ?, ?, ?, ?)", (*job, date_now))
                # 3. Το σβήνουμε από τα ενεργά
                cursor.execute("DELETE FROM jobs WHERE id = ?", (v_id,))
        else:
            cursor.execute("UPDATE jobs SET status = ?, location = ? WHERE id = ?", (status, loc, v_id))
            
        conn.commit()
        conn.close()

    def get_history(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM history ORDER BY delivery_date DESC")
        rows = cursor.fetchall()
        conn.close()
        return rows

    def delete_job(self, v_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM jobs WHERE id = ?", (v_id,))
        conn.commit()
        conn.close()

    def get_coords(self, city):
        try:
            loc = self.geolocator.geocode(city + ", Greece", timeout=5)
            return (loc.latitude, lon.longitude) if loc else (None, None)
        except: return (None, None)