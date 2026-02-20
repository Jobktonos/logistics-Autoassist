import sys

# --- ΡΥΘΜΙΣΕΙΣ ΣΤΟΛΟΥ ---
TRUCK_TYPES = {
    '1': {'name': 'Κλασικό (2 θέσεις: Πλατφόρμα + Ψαλίδι)', 'slots': ['platform', 'psalidi']},
    '2': {'name': 'Τριπλό (3 θέσεις: Πατάρι + Καρότσα + Ψαλίδι)', 'slots': ['patari', 'karotsa', 'psalidi']},
    '3': {'name': 'Τετραπλό (4 θέσεις: 2 Πατάρια + 2 Καρότσες)', 'slots': ['patari_1', 'patari_2', 'karotsa_1', 'karotsa_2']}
}

# --- ΚΑΝΟΝΕΣ ΦΟΡΤΩΣΗΣ ---
def can_fit(v_type, weight, slot_type):
    if 'psalidi' in slot_type:
        if v_type == '4x4': return False
        if weight > 2200: return False
    if 'patari' in slot_type:
        if weight > 1700: return False
    return True

def get_user_input():
    print("\n=== ΕΙΣΑΓΩΓΗ ΝΕΩΝ ΟΧΗΜΑΤΩΝ ΠΡΟΣ ΜΕΤΑΦΟΡΑ ===")
    jobs = []
    while True:
        v_id = input("\nΠινακίδα ή ID (ή πατήστε Enter για τέλος): ")
        if not v_id: break
        
        print("Τύπος: 1: Sedan, 2: 4x4, 3: SUV, 4: Moto")
        t_choice = input("Επιλογή τύπου: ")
        v_types = {'1': 'sedan', '2': '4x4', '3': 'suv', '4': 'moto'}
        v_type = v_types.get(t_choice, 'sedan')
        
        try:
            weight = int(input("Βάρος (σε κιλά, π.χ. 1500): "))
        except:
            weight = 1500
            
        origin = input("Από (Πόλη): ")
        destination = input("Προς (Πόλη): ")
        
        jobs.append({
            'id': v_id, 'type': v_type, 'weight': weight, 
            'origin': origin, 'destination': destination
        })
    return jobs

def main():
    print("=== ΣΥΣΤΗΜΑ ΔΡΟΜΟΛΟΓΗΣΗΣ AUTO-ASSIST ===")
    
    # 1. Επιλογή Φορτηγού
    print("\nΔιαθέσιμα Φορτηγά:")
    for k, v in TRUCK_TYPES.items():
        print(f"{k}: {v['name']}")
    
    t_choice = input("\nΕπιλέξτε φορτηγό για το τρέχον δρομολόγιο: ")
    if t_choice not in TRUCK_TYPES:
        print("Μη έγκυρη επιλογή.")
        return

    # 2. Εισαγωγή Οχημάτων
    current_jobs = get_user_input()
    if not current_jobs:
        print("Δεν δόθηκαν οχήματα.")
        return

    # 3. Υπολογισμός Φόρτωσης
    truck = TRUCK_TYPES[t_choice]
    slots = truck['slots']
    loading_plan = []
    remaining = current_jobs.copy()

    for slot in slots:
        for i, job in enumerate(remaining):
            if can_fit(job['type'], job['weight'], slot):
                loading_plan.append((slot, job))
                remaining.pop(i)
                break

    # 4. Εμφάνιση Αποτελεσμάτων
    print(f"\n===== ΠΛΑΝΟ ΦΟΡΤΩΣΗΣ ΓΙΑ: {truck['name']} =====")
    for slot, job in loading_plan:
        print(f"-> ΘΕΣΗ {slot.upper()}: {job['id']} | {job['origin']} >> {job['destination']} ({job['type']})")
    
    if remaining:
        print("\n[!] ΤΑ ΠΑΡΑΚΑΤΩ ΔΕΝ ΧΩΡΕΣΑΝ Η ΕΙΝΑΙ ΑΣΥΜΒΑΤΑ:")
        for r in remaining:
            print(f"- {r['id']} ({r['type']})")

if __name__ == "__main__":
    main()