import streamlit as st
import pandas as pd
from logic import TransportSystem

# Ρύθμιση της σελίδας
st.set_page_config(page_title="Auto-Assist Logistics Control", layout="wide")

# Αρχικοποίηση του συστήματος στη μνήμη του browser
if 'sys' not in st.session_state:
    st.session_state.sys = TransportSystem()
    # ΑΥΤΟΜΑΤΗ ΚΑΤΑΧΩΡΗΣΗ ΤΟΥ ΣΤΑΘΕΡΟΥ ΣΟΥ ΣΤΟΛΟΥ
    st.session_state.sys.add_truck("KAB-100", "Οδηγός 1 (Ιωάννινα)", "Τετραπλό", "Ioannina", True)
    st.session_state.sys.add_truck("KAB-200", "Οδηγός 2 (Ιωάννινα)", "Καρότσα-Ψαλίδι", "Ioannina", True)
    st.session_state.sys.add_truck("KAA-300", "Κώστας (Κατερίνη)", "Τριπλό", "Katerini", False)
    st.session_state.sys.add_truck("KAC-400", "Νίκος (Κόρινθος)", "Κλασικό", "Corinth", False)

st.title("🚛 Auto-Assist: Κέντρο Ελέγχου & Προγραμματισμού")

# --- ΕΝΟΤΗΤΑ ΧΑΡΤΗ ---
st.subheader("🗺️ Γεωγραφική Απεικόνιση")
map_points = []

# Προσθήκη Φορτηγών στον χάρτη
for t in st.session_state.sys.trucks:
    lat, lon = st.session_state.sys.get_coords(t['location'])
    if lat:
        map_points.append({"lat": lat, "lon": lon, "name": f"🚛 {t['driver']}"})

# Προσθήκη Οχημάτων Ασφαλιστικής στον χάρτη
for j in st.session_state.sys.jobs:
    if j['status'] != "ΠΑΡΑΔΟΘΗΚΕ":
        lat, lon = st.session_state.sys.get_coords(j['location'])
        if lat:
            map_points.append({"lat": lat, "lon": lon, "name": f"🚗 {j['id']}"})

if map_points:
    st.map(pd.DataFrame(map_points))
else:
    st.info("Εισάγετε οχήματα για να εμφανιστεί ο χάρτης.")

# --- ΚΥΡΙΟΣ ΠΙΝΑΚΑΣ ΕΛΕΓΧΟΥ ---
col_jobs, col_trucks = st.columns([2, 1])

with col_jobs:
    st.subheader("📋 Λίστα Οχημάτων προς Μεταφορά")
    if st.session_state.sys.jobs:
        df_jobs = pd.DataFrame(st.session_state.sys.jobs)
        st.dataframe(df_jobs, use_container_width=True)
        
        # Εργαλείο Γρήγορης Ενημέρωσης
        with st.expander("🔄 Ενημέρωση Κατάστασης Οχήματος"):
            job_idx = st.selectbox("Επιλέξτε Πινακίδα", range(len(st.session_state.sys.jobs)), 
                                   format_func=lambda x: st.session_state.sys.jobs[x]['id'])
            u1, u2 = st.columns(2)
            new_stat = u1.selectbox("Κατάσταση", ["ΣΕ ΑΝΑΜΟΝΗ", "ΦΟΡΤΩΜΕΝΟ", "ΣΕ ΣΤΑΘΜΟ", "ΠΑΡΑΔΟΘΗΚΕ"])
            new_loc = u2.text_input("Νέα Τοποθεσία (Πόλη)")
            if st.button("Ενημέρωση Φορτίου"):
                st.session_state.sys.update_job_status(job_idx, new_stat, new_loc)
                st.rerun()
    else:
        st.info("Δεν υπάρχουν εκκρεμή οχήματα.")

with col_trucks:
    st.subheader("🚚 Κατάσταση Στόλου")
    for i, t in enumerate(st.session_state.sys.trucks):
        with st.container(border=True):
            st.write(f"**{t['driver']}** | {t['plate']}")
            st.write(f"📍 {t['location']}")
            
            if t['flexible']:
                # Για τους ευέλικτους (Ιωάννινα)
                new_city = st.text_input("Νέα Πόλη (Ξενοδοχείο)", key=f"f_{i}")
                if st.button("Ενημέρωση Θέσης", key=f"b_{i}"):
                    t['location'] = new_city
                    st.rerun()
            else:
                # Για τους σταθερούς (Κατερίνη, Κόρινθος)
                if st.button("🏠 Επιστροφή στη Βάση", key=f"h_{i}"):
                    t['location'] = t['base']
                    st.rerun()

# --- ΦΟΡΜΑ ΕΙΣΑΓΩΓΗΣ ---
st.divider()
with st.expander("➕ Καταχώρηση Νέας Παραλαβής"):
    with st.form("new_job"):
        c1, c2, c3, c4 = st.columns(4)
        v_id = c1.text_input("Πινακίδα")
        v_org = c2.text_input("Από")
        v_dest = c3.text_input("Προς")
        v_type = c4.selectbox("Τύπος", ["Sedan", "4x4", "SUV", "Moto"])
        if st.form_submit_button("Προσθήκη στο Πλάνο"):
            st.session_state.sys.add_job(v_id, v_org, v_dest, v_type)
            st.rerun()