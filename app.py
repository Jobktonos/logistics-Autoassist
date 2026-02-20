import streamlit as st
import pandas as pd
from logic import TransportSystem

# Ρύθμιση Σελίδας (Wide mode για καλύτερη ορατότητα σε υπολογιστή, προσαρμόσιμο σε κινητό)
st.set_page_config(page_title="Auto-Assist Logistics ERP", layout="wide")

# Αρχικοποίηση Συστήματος - Σύνδεση με τη Βάση Δεδομένων
if 'sys' not in st.session_state:
    st.session_state.sys = TransportSystem()

st.title("🚛 Auto-Assist: Logistics & History Control")

# Δημιουργία των 4 βασικών ενοτήτων (Tabs)
tab_dash, tab_fleet, tab_new, tab_hist = st.tabs([
    "📊 Dashboard", 
    "🚛 Διαχείριση Στόλου", 
    "🚗 Νέα Φορτία", 
    "📁 Ιστορικό"
])

# --- TAB 1: DASHBOARD (ΧΑΡΤΗΣ & ΤΡΕΧΟΥΣΑ ΚΑΤΑΣΤΑΣΗ) ---
with tab_dash:
    db_jobs = st.session_state.sys.get_jobs()
    db_trucks = st.session_state.sys.get_trucks()
    
    col_map, col_status = st.columns([2, 1])
    
    with col_map:
        st.subheader("🗺️ Live Γεωγραφική Απεικόνιση")
        map_points = []
        
        # Προσθήκη Φορτηγών στον χάρτη
        for t in db_trucks:
            lat, lon = st.session_state.sys.get_coords(t[4]) # t[4] είναι η τοποθεσία
            if lat: map_points.append({"lat": lat, "lon": lon, "name": f"🚛 {t[1]}"})
        
        # Προσθήκη Ενεργών Φορτίων στον χάρτη
        for j in db_jobs:
            lat, lon = st.session_state.sys.get_coords(j[5]) # j[5] είναι η θέση του αμαξιού
            if lat: map_points.append({"lat": lat, "lon": lon, "name": f"🚗 {j[0]}"})
            
        if map_points:
            st.map(pd.DataFrame(map_points))
        else:
            st.info("Εισάγετε δεδομένα για να εμφανιστούν στον χάρτη.")

    with col_status:
        st.subheader("🚛 Κατάσταση Οδηγών")
        for t in db_trucks:
            with st.container(border=True):
                st.write(f"**{t[1]}** ({t[0]})")
                st.write(f"📍 Τώρα στο: **{t[4]}**")
                
                if t[5] == 1: # Αν είναι Flexible (Ευέλικτος)
                    new_city = st.text_input("Αλλαγή Πόλης (Ξενοδοχείο)", key=f"t_loc_{t[0]}", label_visibility="collapsed")
                    if st.button("Ενημέρωση Θέσης", key=f"btn_up_{t[0]}"):
                        st.session_state.sys.update_truck_loc(t[0], new_city)
                        st.rerun()
                else: # Αν είναι Σταθερός (Επιστρέφει βάση)
                    if st.button(f"🏠 Επιστροφή {t[3]}", key=f"h_btn_{t[0]}"):
                        st.session_state.sys.update_truck_loc(t[0], t[3])
                        st.rerun()

    st.divider()
    
    st.subheader("📋 Ενεργές Μεταφορές (Προς Παράδοση)")
    if db_jobs:
        df_jobs = pd.DataFrame(db_jobs, columns=["Πινακίδα", "Από", "Προς", "Τύπος", "Κατάσταση", "Θέση"])
        st.dataframe(df_jobs, use_container_width=True)
        
        with st.expander("🔄 Διαχείριση & Ενημέρωση Φορτίου"):
            job_to_mod = st.selectbox("Επιλέξτε Όχημα", [j[0] for j in db_jobs])
            u1, u2 = st.columns(2)
            new_s = u1.selectbox("Νέα Κατάσταση", ["ΣΕ ΑΝΑΜΟΝΗ", "ΦΟΡΤΩΜΕΝΟ", "ΣΕ ΣΤΑΘΜΟ", "ΠΑΡΑΔΟΘΗΚΕ"])
            new_l = u2.text_input("Νέα Τοποθεσία (αν άλλαξε)")
            
            c_up, c_del = st.columns(2)
            if c_up.button("✅ Αποθήκευση Αλλαγών", use_container_width=True):
                st.session_state.sys.update_job(job_to_mod, new_s, new_l)
                if new_s == "ΠΑΡΑΔΟΘΗΚΕ":
                    st.toast(f"Το όχημα {job_to_mod} μεταφέρθηκε στο Ιστορικό!")
                st.rerun()
            
            if c_del.button("❌ Οριστική Διαγραφή", key="del_job", use_container_width=True):
                st.session_state.sys.delete_job(job_to_mod)
                st.rerun()
    else:
        st.write("Δεν υπάρχουν εκκρεμή δρομολόγια.")

# --- TAB 2: ΔΙΑΧΕΙΡΙΣΗ ΣΤΟΛΟΥ ---
with tab_fleet:
    st.subheader("🚛 Τα Φορτηγά μου")
    current_trucks = st.session_state.sys.get_trucks()
    
    if current_trucks:
        for t in current_trucks:
            col_info, col_del = st.columns([4, 1])
            with col_info.container(border=True):
                st.write(f"**Οδηγός:** {t[1]} | **Πινακίδα:** {t[0]} | **Τύπος:** {t[2]}")
                st.write(f"🏠 Βάση: {t[3]} | {'🟢 Ευέλικτος' if t[5] else '🏠 Σταθερός'}")
            if col_del.button("🗑️ Διαγραφή", key=f"del_tr_{t[0]}", use_container_width=True):
                st.session_state.sys.delete_truck(t[0])
                st.rerun()
    
    st.divider()
    st.subheader("➕ Προσθήκη Νέου Φορτηγού στο Στόλο")
    with st.form("truck_form"):
        c1, c2, c3 = st.columns(3)
        plate = c1.text_input("Πινακίδα")
        driver = c2.text_input("Όνομα Οδηγού")
        t_type = c3.selectbox("Τύπος Φορτηγού", ["Τετραπλό (2+2)", "Τριπλό (2+1)", "Κλασικό (1+1)", "Καρότσα-Ψαλίδι"])
        
        base_city = c1.text_input("Πόλη Βάσης (π.χ. Ioannina)")
        is_flex = c2.checkbox("Δυνατότητα Διανυκτέρευσης εκτός έδρας")
        
        if st.form_submit_button("Καταχώρηση Φορτηγού"):
            if plate and driver and base_city:
                st.session_state.sys.add_truck(plate, driver, t_type, base_city, is_flex)
                st.success("Το φορτηγό προστέθηκε στη βάση δεδομένων!")
                st.rerun()
            else:
                st.error("Παρακαλώ συμπληρώστε όλα τα πεδία.")

# --- TAB 3: ΝΕΑ ΦΟΡΤΙΑ (ΕΙΣΑΓΩΓΗ ΑΠΟ ΑΣΦΑΛΙΣΤΙΚΗ) ---
with tab_new:
    st.subheader("🚗 Καταχώρηση Νέων Οχημάτων")
    with st.form("job_form"):
        col1, col2 = st.columns(2)
        v_id = col1.text_input("Πινακίδα Οχήματος")
        v_type = col2.selectbox("Τύπος", ["Sedan", "4x4", "SUV", "Moto", "Ελαφρύ Φορτηγό"])
        orig = col1.text_input("Από (Πόλη Παραλαβής)")
        dest = col2.text_input("Προς (Πόλη Παράδοσης)")
        
        if st.form_submit_button("Προσθήκη στο Πλάνο Μεταφορών"):
            if v_id and orig and dest:
                st.session_state.sys.add_job(v_id, orig, dest, v_type)
                st.success(f"Το όχημα {v_id} καταγράφηκε!")
                st.rerun()
            else:
                st.error("Συμπληρώστε τουλάχιστον Πινακίδα και Διαδρομή.")

# --- TAB 4: ΙΣΤΟΡΙΚΟ (ΑΡΧΕΙΟ ΠΑΡΑΔΟΣΕΩΝ) ---
with tab_hist:
    st.subheader("📁 Αρχείο Ολοκληρωμένων Μεταφορών")
    history_data = st.session_state.sys.get_history()
    
    if history_data:
        df_hist = pd.DataFrame(history_data, columns=["Πινακίδα", "Από", "Προς", "Τύπος", "Ημ/νία Παράδοσης"])
        st.dataframe(df_hist, use_container_width=True)
        
        st.divider()
        if st.button("🗑️ Καθαρισμός Όλου του Ιστορικού", type="primary"):
            conn = st.session_state.sys.get_connection()
            conn.cursor().execute("DELETE FROM history")
            conn.commit()
            st.warning("Το ιστορικό διαγράφηκε οριστικά.")
            st.rerun()
    else:
        st.info("Το αρχείο είναι προς το παρόν κενό. Οι παραδόσεις θα εμφανίζονται εδώ αυτόματα.")