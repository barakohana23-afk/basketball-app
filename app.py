import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# הגדרת כותרת האפליקציה והגדרות עמוד
st.set_page_config(page_title="חלוקת קבוצות כדורסל", page_icon="🏀", layout="centered")

# --- מנגנון אימות בסיסמה ---
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.title("🔒 גישה מוגבלת")
        password = st.text_input("הכנס סיסמה כדי להיכנס לאפליקציה:", type="password")
        if st.button("התחבר"):
            if password == "1234":  # <--- הסיסמה שלך
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("🔑 סיסמה שגויה, נסה שוב.")
        return False
    return True

if check_password():
    # --- עיצוב CSS מותאם ---
    st.markdown("""
        <style>
            html, body, [class*="css"], .stMarkdown, h1, h2, h3, h4, h5, h6, p, label {
                text-align: center !important;
            }
            div[data-baseweb="select"] {
                min-height: 32px !important;
                max-width: 130px !important;
                margin: 0 auto !important;
            }
            div[data-baseweb="select"] > div {
                min-height: 32px !important;
                padding-top: 0px !important;
                padding-bottom: 0px !important;
                font-size: 14px !important;
            }
            [data-testid="stHorizontalBlock"] {
                align-items: center !important;
            }
            div[data-testid="stNumberInput"] {
                margin: 0 auto !important;
                max-width: 300px;
            }
            div[data-testid="stNumberInput"] input {
                text-align: center !important;
            }
            .stButton>button {
                display: block !important;
                margin: 0 auto !important;
            }
            div[data-baseweb="input"] input {
                text-align: center !important;
            }
        </style>
    """, unsafe_allow_html=True)

    # --- חיבור ל-Google Sheets ---
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    def load_data():
        try:
            df = conn.read(spreadsheet=st.secrets["sheet_url"], ttl=0)
            return df.dropna(how="all")
        except Exception:
            return pd.DataFrame(columns=["name", "position", "level"])

    df_players = load_data()

    st.title("🏀 מחלק הקבוצות לכדורסל")
    st.write("הכנס את רשימת השחקנים, העמדה והרמה לקבלת קבוצות מאוזנות!")

    LEVEL_MAP = {"חלש": 1, "בינוני": 2, "חזק": 3}
    LEVEL_OPTIONS = ["חלש", "בינוני", "חזק"]
    POSITION_OPTIONS = ["רכז", "קלעי", "גבוה"]

    # --- הגדרת גודל קבוצה ---
    st.subheader("⚙️ הגדרת המשחק")
    max_per_team = st.number_input("מספר שחקנים מקסימלי בכל קבוצה", min_value=1, max_value=15, value=5, step=1)

    st.divider()

    # --- טופס להוספת שחקן חדש ---
    st.subheader("➕ הוספת שחקן חדש (יישמר בבסיס הנתונים)")
    with st.form("add_player_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            name = st.text_input("שם השחקן")
        with col2:
            position = st.selectbox("עמדה", POSITION_OPTIONS)
        with col3:
            level = st.select_slider("רמה", options=LEVEL_OPTIONS, value="בינוני")
            
        submit_button = st.form_submit_button("הוסף ושמור")
        
        if submit_button:
            clean_name = name.strip()
            if clean_name:
                # רשימת השמות הקיימים (באותיות קטנות לטובת בדיקה מדויקת)
                existing_names = [str(n).strip().lower() for n in df_players["name"].tolist()] if not df_players.empty else []
                
                # --- בדיקת כפילות ---
                if clean_name.lower() in existing_names:
                    st.error(f"⚠️ השחקן '{clean_name}' כבר קיים ברשימה!")
                else:
                    new_row = pd.DataFrame([{"name": clean_name, "position": position, "level": level}])
                    updated_df = pd.concat([df_players, new_row], ignore_index=True)
                    conn.update(spreadsheet=st.secrets["sheet_url"], data=updated_df)
                    st.success(f"השחקן {clean_name} נוסף ונשמר בגיליון!")
                    st.rerun()
            else:
                st.error("נא להזין שם שחקן.")

    # --- הצגה ועריכת שחקנים ---
    players_list = df_players.to_dict("records") if not df_players.empty else []

    if players_list:
        st.subheader(f"📋 רשימת השחקנים הקבועה ({len(players_list)})")
        st.write("💡 שינוי עמדה/רמה או מחיקה יעדכנו את בסיס הנתונים בזמן אמת:")

        to_delete = None
        has_changed = False

        for idx, player in enumerate(players_list):
            col_name, col_pos, col_lvl, col_del = st.columns([3, 2, 2, 1])
            
            with col_name:
                st.markdown(f"**{player['name']}**")
            with col_pos:
                curr_pos = player["position"] if player["position"] in POSITION_OPTIONS else POSITION_OPTIONS[0]
                new_pos = st.selectbox(
                    f"עמדה עבור {player['name']}",
                    POSITION_OPTIONS,
                    index=POSITION_OPTIONS.index(curr_pos),
                    key=f"pos_{idx}",
                    label_visibility="collapsed"
                )
                if new_pos != player["position"]:
                    players_list[idx]["position"] = new_pos
                    has_changed = True

            with col_lvl:
                curr_lvl = player["level"] if player["level"] in LEVEL_OPTIONS else LEVEL_OPTIONS[1]
                new_lvl = st.selectbox(
                    f"רמה עבור {player['name']}",
                    LEVEL_OPTIONS,
                    index=LEVEL_OPTIONS.index(curr_lvl),
                    key=f"lvl_{idx}",
                    label_visibility="collapsed"
                )
                if new_lvl != player["level"]:
                    players_list[idx]["level"] = new_lvl
                    has_changed = True

            with col_del:
                if st.button("❌", key=f"del_{idx}"):
                    to_delete = idx

        # עדכון שינויים בגיליון
        if has_changed:
            updated_df = pd.DataFrame(players_list)
            conn.update(spreadsheet=st.secrets["sheet_url"], data=updated_df)
            st.rerun()

        if to_delete is not None:
            players_list.pop(to_delete)
            updated_df = pd.DataFrame(players_list)
            conn.update(spreadsheet=st.secrets["sheet_url"], data=updated_df)
            st.rerun()

        st.write("---")

        # --- אלגוריתם החלוקה ---
        def split_teams(p_list, max_players):
            sorted_p = sorted(p_list, key=lambda x: LEVEL_MAP.get(x["level"], 2), reverse=True)
            
            positions = {"רכז": [], "קלעי": [], "גבוה": []}
            for p in sorted_p:
                pos = p["position"] if p["position"] in positions else "רכז"
                positions[pos].append(p)
                
            team_a, team_b, waiting = [], [], []
            toggle = True
            
            for pos, pos_players in positions.items():
                for p in pos_players:
                    if len(team_a) < max_players or len(team_b) < max_players:
                        if len(team_a) < max_players and (toggle or len(team_b) >= max_players):
                            team_a.append(p)
                        else:
                            team_b.append(p)
                        toggle = not toggle
                    else:
                        waiting.append(p)
                        
            return team_a, team_b, waiting

        # --- כפתור החלוקה ---
        if st.button("⚡ חלק לקבוצות!", type="primary"):
            team_a, team_b, waiting = split_teams(players_list, max_per_team)
            
            st.divider()
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.success(f"🟢 **קבוצה א' ({len(team_a)}/{max_per_team})**")
                for p in team_a:
                    st.write(f"• **{p['name']}** ({p['position']} | {p['level']})")
                    
            with col_b:
                st.info(f"🔵 **קבוצה ב' ({len(team_b)}/{max_per_team})**")
                for p in team_b:
                    st.write(f"• **{p['name']}** ({p['position']} | {p['level']})")
                    
            if waiting:
                st.warning(f"📋 **רשימת מזמינים / המתנה ({len(waiting)})**")
                for p in waiting:
                    st.write(f"• **{p['name']}** ({p['position']} | {p['level']})")
