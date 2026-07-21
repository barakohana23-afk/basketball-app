import streamlit as st

# הגדרת כותרת האפליקציה והגדרות עמוד
st.set_page_config(page_title="חלוקת קבוצות כדורסל", page_icon="🏀", layout="centered")

# --- עיצוב CSS מותאם: הקטנת התיבות ומרכוז הטקסטים ---
st.markdown("""
    <style>
        /* מרכוז טקסט כללי וכותרות */
        html, body, [class*="css"], .stMarkdown, h1, h2, h3, h4, h5, h6, p, label {
            text-align: center !important;
        }
        
        /* הקטנת הגובה והרווחים בתיבות הבחירה ברשימה */
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

        /* יישור אנכי לכל העמודות ברשימה */
        [data-testid="stHorizontalBlock"] {
            align-items: center !important;
        }

        /* מרכוז שדות מספר (number_input) */
        div[data-testid="stNumberInput"] {
            margin: 0 auto !important;
            max-width: 300px;
        }
        div[data-testid="stNumberInput"] input {
            text-align: center !important;
        }

        /* מרכוז כפתורים */
        .stButton>button {
            display: block !important;
            margin: 0 auto !important;
        }
        
        /* מרכוז שדות קלט טקסט */
        div[data-baseweb="input"] input {
            text-align: center !important;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🏀 מחלק הקבוצות לכדורסל")
st.write("הכנס את רשימת השחקנים, העמדה והרמה לקבלת קבוצות מאוזנות!")

# מיפוי רמות ממילים למספרים לצורך חישוב האלגוריתם
LEVEL_MAP = {"חלש": 1, "בינוני": 2, "חזק": 3}
LEVEL_OPTIONS = ["חלש", "בינוני", "חזק"]
POSITION_OPTIONS = ["רכז", "קלעי", "גבוה"]

# רשימת שחקני הבית הקבועים
DEFAULT_PLAYERS = [
    {"name": "לירון", "position": "גבוה", "level": "חזק"},
    {"name": "ירין", "position": "רכז", "level": "חזק"},
    {"name": "ברק", "position": "רכז", "level": "חזק"},
    {"name": "מוטי", "position": "רכז", "level": "בינוני"},
    {"name": "בנצי", "position": "קלעי", "level": "חזק"},
    {"name": "חיים", "position": "קלעי", "level": "חזק"},
    {"name": "חזוט", "position": "קלעי", "level": "בינוני"},
    {"name": "אילן", "position": "קלעי", "level": "חזק"},
    {"name": "שאול", "position": "גבוה", "level": "בינוני"},
    {"name": "דודי", "position": "קלעי", "level": "חלש"},
    {"name": "דור", "position": "גבוה", "level": "חזק"},
    {"name": "איציק", "position": "קלעי", "level": "בינוני"},
    {"name": "יהודה", "position": "קלעי", "level": "חלש"},
]

# שמירת רשימת השחקנים בזיכרון הריצה של האפליקציה
if "players" not in st.session_state:
    st.session_state.players = []

# --- הגדרת גודל קבוצה ---
st.subheader("⚙️ הגדרת המשחק")
max_per_team = st.number_input("מספר שחקנים מקסימלי בכל קבוצה", min_value=1, max_value=15, value=5, step=1)

st.divider()

# --- בחירה מהירה משחקנים קבועים ---
st.subheader("⚡ בחירה מהירה של שחקנים קבועים")
st.write("סמן את השחקנים שהגיעו היום ולחץ על הוספה:")

# תצוגה נוחה בעמודות (3 שחקנים בשורה)
cols = st.columns(3)
selected_defaults = []

for idx, p in enumerate(DEFAULT_PLAYERS):
    col = cols[idx % 3]
    with col:
        label = f"{p['name']} ({p['position']} | {p['level']})"
        if st.checkbox(label, key=f"default_{idx}"):
            selected_defaults.append(p)

if st.button("➕ הוסף את המסומנים לרשימת המשחק"):
    added_count = 0
    existing_names = [p["name"].strip().lower() for p in st.session_state.players]
    
    for p in selected_defaults:
        if p["name"].strip().lower() not in existing_names:
            st.session_state.players.append(p.copy())
            added_count += 1
            
    if added_count > 0:
        st.success(f"נוספו {added_count} שחקנים לרשימה!")
        st.rerun()
    elif len(selected_defaults) == 0:
        st.warning("לא סומנו שחקנים לבחירה.")
    else:
        st.info("כל השחקנים המסומנים כבר נמצאים ברשימה!")

st.divider()

# --- טופס להוספת שחקן חדש/אורח ---
st.subheader("➕ הוספת שחקן חדש / אורח")
with st.form("add_player_form", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        name = st.text_input("שם השחקן")
    with col2:
        position = st.selectbox("עמדה", POSITION_OPTIONS)
    with col3:
        level = st.select_slider("רמה", options=LEVEL_OPTIONS, value="בינוני")
        
    submit_button = st.form_submit_button("הוסף לרשימה")
    
    if submit_button:
        clean_name = name.strip()
        if clean_name:
            existing_names = [p["name"].strip().lower() for p in st.session_state.players]
            if clean_name.lower() in existing_names:
                st.error(f"⚠️ השחקן '{clean_name}' כבר קיים ברשימה!")
            else:
                st.session_state.players.append({"name": clean_name, "position": position, "level": level})
                st.success(f"השחקן {clean_name} נוסף בהצלחה!")
                st.rerun()
        else:
            st.error("נא להזין שם שחקן.")

# --- הצגה ועריכת שחקנים ---
if st.session_state.players:
    st.subheader(f"📋 רשימת השחקנים למשחק ({len(st.session_state.players)})")
    st.write("💡 ניתן לשנות עמדה ורמה של שחקן ישירות ברשימה למטה:")

    to_delete = None
    for idx, player in enumerate(st.session_state.players):
        col_name, col_pos, col_lvl, col_del = st.columns([3, 2, 2, 1])
        
        with col_name:
            st.markdown(f"**{player['name']}**")
        with col_pos:
            new_pos = st.selectbox(
                f"עמדה עבור {player['name']}",
                POSITION_OPTIONS,
                index=POSITION_OPTIONS.index(player["position"]),
                key=f"pos_{idx}",
                label_visibility="collapsed"
            )
            st.session_state.players[idx]["position"] = new_pos
        with col_lvl:
            new_lvl = st.selectbox(
                f"רמה עבור {player['name']}",
                LEVEL_OPTIONS,
                index=LEVEL_OPTIONS.index(player["level"]),
                key=f"lvl_{idx}",
                label_visibility="collapsed"
            )
            st.session_state.players[idx]["level"] = new_lvl
        with col_del:
            if st.button("❌", key=f"del_{idx}"):
                to_delete = idx

    if to_delete is not None:
        st.session_state.players.pop(to_delete)
        st.rerun()

    st.write("---")
    col_clear, col_split = st.columns([1, 2])
    with col_clear:
        if st.button("🗑️ נקה את כל הרשימה"):
            st.session_state.players = []
            st.rerun()

    # --- אלגוריתם החלוקה ---
    def split_teams(players_list, max_players):
        sorted_p = sorted(players_list, key=lambda x: LEVEL_MAP[x["level"]], reverse=True)
        
        positions = {"רכז": [], "קלעי": [], "גבוה": []}
        for p in sorted_p:
            positions[p["position"]].append(p)
            
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
    with col_split:
        if st.button("⚡ חלק לקבוצות!", type="primary"):
            team_a, team_b, waiting = split_teams(st.session_state.players, max_per_team)
            
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
