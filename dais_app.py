import streamlit as st
import pandas as pd
import time

# --- INITIALIZATION ---
FUTURISTIC_NATIONS = [
    "United Mars Colonies", "Neo-Tokyo Megacity", "Europa Ice-Base", 
    "The AI Collective", "Luna Trade Republic", "Ceres Belt Alliance",
    "Amazonia Eco-Dome", "Orion Station", "Titan Refinery"
]

if 'delegates' not in st.session_state: st.session_state.delegates = {} 
if 'suspended' not in st.session_state: st.session_state.suspended = []
if 'gsl_queue' not in st.session_state: st.session_state.gsl_queue = []
if 'agenda' not in st.session_state: st.session_state.agenda = "Accord on Inter-Planetary Resource Sovereignty"
if 'committee_status' not in st.session_state: st.session_state.committee_status = "In Session"

if 't_remaining' not in st.session_state: st.session_state.t_remaining = 60
if 't_running' not in st.session_state: st.session_state.t_running = False
if 't_expiry_msg' not in st.session_state: st.session_state.t_expiry_msg = "TRANSMISSION CONCLUDED: The Floor is Ceded."

# --- PAGE CONFIG ---
st.set_page_config(page_title="FGA Dais Console 2026", layout="wide")

# --- PURE MAROON CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #1a0505; color: #ffcccc; }
    h1, h2, h3 { color: #ff4d4d !important; font-family: 'Segoe UI', sans-serif; text-transform: uppercase; }
    
    .timer-display { 
        font-size: 90px; font-weight: bold; font-family: 'Courier New', monospace;
        text-align: center; color: #ff3333; text-shadow: 0 0 20px #800000;
        border: 2px solid #800000; border-radius: 10px; padding: 25px; 
        background: #2b0808; margin-bottom: 25px;
    }

    .stButton>button { 
        border: 1px solid #ff4d4d; background-color: #4b0015; color: #ffcccc; font-weight: bold;
    }
    .stButton>button:hover { background-color: #800000; color: white; border-color: white; }
    
    section[data-testid="stSidebar"] { background-color: #2b0808; border-right: 1px solid #4b0015; }
    label { color: #ffcccc !important; }
    .stAlert { background-color: #3d0a0a; color: #ffcccc; border: 1px solid #800000; }
    
    /* Success Overlay Style */
    .success-text {
        font-size: 50px; color: #ff4d4d; text-align: center; font-weight: bold;
        border: 5px solid #ff4d4d; padding: 20px; background-color: #4b0015;
        text-shadow: 0 0 10px #ff3333;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
st.sidebar.title("🍷 DAIS AUTHORITY")
st.session_state.agenda = st.sidebar.text_area("Directive:", value=st.session_state.agenda)

st.sidebar.divider()

if st.sidebar.button("🍷 Reset Clock"):
    st.session_state.t_remaining = 60
    st.session_state.t_running = False
    st.rerun()

if st.sidebar.button("🍷 Convene All"):
    for nation in FUTURISTIC_NATIONS:
        if nation not in st.session_state.delegates: st.session_state.delegates[nation] = "Present"
    st.rerun()

# --- NEW FEATURE: COMMITTEE SUCCESS OPTION ---
st.sidebar.subheader("🏁 Final Protocol")
if st.sidebar.button("🏆 GRANT COMMITTEE SUCCESS"):
    st.session_state.committee_status = "SUCCESSFUL"
    st.rerun()

if st.sidebar.button("🚨 Terminate Session"):
    st.session_state.delegates, st.session_state.suspended, st.session_state.gsl_queue = {}, [], []
    st.session_state.committee_status = "In Session"
    st.rerun()

# --- MAIN DASHBOARD ---
if st.session_state.committee_status == "SUCCESSFUL":
    st.balloons()
    st.markdown('<div class="success-text">COMMITTEE ADJOURNED: MISSION SUCCESSFUL</div>', unsafe_allow_html=True)
    if st.button("Return to Control Center"):
        st.session_state.committee_status = "In Session"
        st.rerun()
else:
    st.title("🏛️ MAROON COMMAND (2026)")
    st.info(f"**CURRENT DIRECTIVE:** {st.session_state.agenda}")

    tab1, tab2, tab3 = st.tabs(["📊 Registry", "🎙️ Speakers (GSL)", "🗳️ Voting"])

    # --- TAB 1: REGISTRY ---
    with tab1:
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("Add Entity")
            new_c = st.text_input("Name:")
            if st.button("Add"):
                if new_c and new_c not in st.session_state.delegates:
                    st.session_state.delegates[new_c] = "Present"
                    st.rerun()
            st.divider()
            active_list = [n for n in st.session_state.delegates if n not in st.session_state.suspended]
            for n in active_list:
                c1, c2 = st.columns([3, 1])
                c1.write(f"🍷 {n}")
                if c2.button("RECESS", key=f"sus_{n}"):
                    st.session_state.suspended.append(n)
                    if n in st.session_state.gsl_queue: st.session_state.gsl_queue.remove(n)
                    st.rerun()
        with col_b:
            st.subheader("🚫 Suspended")
            for s in st.session_state.suspended:
                c1, c2 = st.columns([3, 1])
                c1.write(f"🛑 {s}")
                if c2.button("RESTORE", key=f"re_{s}"):
                    st.session_state.suspended.remove(s)
                    st.rerun()

    # --- TAB 2: GSL & TIMER ---
    with tab2:
        col_q, col_timer = st.columns([1, 2])
        with col_q:
            st.subheader("Queue")
            eligible = [n for n in st.session_state.delegates if n not in st.session_state.suspended and n not in st.session_state.gsl_queue]
            to_add = st.selectbox("Assign", eligible if eligible else ["None"])
            if st.button("Grant Floor") and to_add != "None":
                st.session_state.gsl_queue.append(to_add)
                st.rerun()
            if st.button("Clear"):
                st.session_state.gsl_queue = []
                st.rerun()

        with col_timer:
            if st.session_state.gsl_queue:
                speaker = st.session_state.gsl_queue[0]
                st.success(f"**FLOOR:** {speaker}")
                t_placeholder = st.empty()
                mins, secs = divmod(st.session_state.t_remaining, 60)
                t_placeholder.markdown(f'<div class="timer-display">{mins:02d}:{secs:02d}</div>', unsafe_allow_html=True)
                
                c1, c2, c3 = st.columns(3)
                if c1.button("▶️ START"): st.session_state.t_running = True
                if c2.button("⏸️ PAUSE"): st.session_state.t_running = False
                if c3.button("⏭️ NEXT"): 
                    st.session_state.gsl_queue.pop(0)
                    st.session_state.t_remaining = 60
                    st.session_state.t_running = False
                    st.rerun()

                if st.session_state.t_running and st.session_state.t_remaining > 0:
                    while st.session_state.t_running and st.session_state.t_remaining > 0:
                        time.sleep(1)
                        st.session_state.t_remaining -= 1
                        m, s = divmod(st.session_state.t_remaining, 60)
                        t_placeholder.markdown(f'<div class="timer-display">{m:02d}:{s:02d}</div>', unsafe_allow_html=True)
                        if st.session_state.t_remaining <= 0:
                            st.session_state.t_running = False
                            st.error(f"🛑 {st.session_state.t_expiry_msg}")
                            break
            else:
                st.info("Awaiting speakers...")

    # --- TAB 3: VOTING ---
    with tab3:
        active_now = len(st.session_state.delegates) - len(st.session_state.suspended)
        st.subheader("Voting")
        v1, v2, v3 = st.columns(3)
        v_yes = v1.number_input("In Favor", min_value=0, max_value=active_now)
        v_no = v2.number_input("Opposed", min_value=0, max_value=active_now)
        v_abs = v3.number_input("Abstain", min_value=0, max_value=active_now)
        if st.button("Finalize"):
            if v_yes > ((v_yes + v_no) / 2):
                st.balloons()
                st.success("PASSED")
            else:
                st.error("FAILED")