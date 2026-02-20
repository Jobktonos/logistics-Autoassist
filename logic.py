from geopy.geocoders import Nominatim

class TransportSystem:
    def __init__(self):
        # Λίστες για αποθήκευση δεδομένων
        self.trucks = [] 
        self.jobs = []
        # user_agent: ένα όνομα για την υπηρεσία χαρτών
        self.geolocator = Nominatim(user_agent="auto_assist_final_v1")

    def add_truck(self, plate, driver, truck_type, base_city, flexible):
        """Προσθήκη φορτηγού στο σύστημα"""
        self.trucks.append({
            "plate": plate,
            "driver": driver,
            "type": truck_type,
            "base": base_city,
            "location": base_city,
            "flexible": flexible 
        })

    def add_job(self, v_id, origin, destination, v_type):
        """Προσθήκη νέου οχήματος από ασφαλιστική"""
        self.jobs.append({
            "id": v_id,
            "origin": origin,
            "destination": destination,
            "type": v_type,
            "status": "ΣΕ ΑΝΑΜΟΝΗ", 
            "location": origin
        })

    def get_coords(self, city):
        """Μετατροπή πόλης σε συντεταγμένες για τον χάρτη"""
        try:
            # Προσθέτουμε ", Greece" για σιγουριά στα αποτελέσματα
            loc = self.geolocator.geocode(city + ", Greece", timeout=10)
            if loc:
                return loc.latitude, loc.longitude
        except:
            return None, None
        return None, None

    def update_job_status(self, job_index, new_status, new_location):
        """Ενημέρωση κατάστασης και θέσης οχήματος"""
        if 0 <= job_index < len(self.jobs):
            self.jobs[job_index]['status'] = new_status
            if new_location:
                self.jobs[job_index]['location'] = new_location