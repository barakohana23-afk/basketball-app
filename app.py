import streamlit as st
import pandas as pd

# הגדרת כותרת האפליקציה והגדרות עמוד
st.set_page_config(page_title="חלוקת קבוצות כדורסל", page_icon="🏀", layout="centered")

# עיצוב CSS למרכוז טקסטים וכותרות
st.markdown("""
    <style>
        html, body, [class*="css"], .stMarkdown, h1, h2, h3, h4, h5, h6, p, label {
            text-align: center !important;
        }
        .stButton>button {
            display: block !important;
            margin: 0 auto !important;
        }
        div[data-testid="stNumberInput"] {
            margin: 0 auto !important;
            max-width: 300px;
        }
        div[data-testid="stNumberInput"] input {
            text-align: center !important;
        }
        div[data-baseweb="input"] input {
            text-align: center !important;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🏀 מחלק הקבוצות לכדורסל")
st.write("הכנס את רשימת השחקנים, העמדה והרמה לקבלת קבוצות מאוזנות!")

LEVEL_MAP = {"חלש": 1, "בינוני": 2, "חזק": 3}
LEVEL_OPTIONS = ["חלש", "בינוני", "חזק"]
POSITION_OPTIONS = ["רכז", "קלעי", "גבוה"]

# שמירת רשימת השחקנים
if "players" not in st.session_state:
    st.session_state.players = []

# --- הגדרת גודל קבוצה ---
st.subheader("⚙️ הגדרת המשחק")
max_per_team = st.number_input("מספר שחקנים מקסימלי בכל קבוצה", min_value=1, max_value=15, value=5, step=1)

# --- טופס להוספת שחקן ---
st.subheader("➕ הוספת שחקן חדש")
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
        if name.strip():
            st.session_state.players.append({"מחיקה": False, "שם": name.strip(), "עמדה": position, "רמה": level})
            st.success(f"השחקן {name} נוסף בהצלחה!")
            st.rerun()
        else:
            st.error("נא להזין שם שחקן.")

# --- הצגה ועריכת שחקנים בטבלה מעוצבת ---
if st.session_state.players:
    st.subheader(f"📋 רשימת השחקנים ({len(st.session_state.players)})")
    st.write("💡 לחץ על תא בטבלה כדי לשנות עמדה/רמה, או סמן בתיבה כדי למחוק שחקן:")

    df = pd.DataFrame(st.session_state.players)

    # הצגת טבלה אינטראקטיבית עם יישור ומבנה מותאם
    edited_df = st.data_editor(
        df,
        column_config={
            "מחיקה": st.column_config.CheckboxColumn("מחק?", default=False, width="small"),
            "שם": st.column_config.TextColumn("שם השחקן", disabled=True),
            "עמדה": st.column_config.SelectboxColumn("עמדה", options=POSITION_OPTIONS, required=True),
            "רמה": st.column_config.SelectboxColumn("רמה", options=LEVEL_OPTIONS, required=True),
        },
        hide_index=True,
        use_container_width=True,
        key="players_editor"
    )

    # סינון שחקנים שסומנו למחיקה
    filtered_players = [row for row in edited_df.to_dict("records") if not row["מחיקה"]]
    
    # אם נמחקו שחקנים - מעדכנים את הזיכרון ומדרנרים מחדש
    if len(filtered_players) != len(st.session_state.players):
        st.session_state.players = filtered_players
        st.rerun()
    else:
        st.session_state.players = filtered_players

    st.write("---")
    col_clear, col_split = st.columns([1, 2])
    
    with col_clear:
        if st.button("🗑️ נקה את כל הרשימה"):
            st.session_state.players = []
            st.rerun()

    # --- אלגוריתם החלוקה ---
    def split_teams(players_list, max_players):
        sorted_p = sorted(players_list, key=lambda x: LEVEL_MAP[x["רמה"]], reverse=True)
        
        positions = {"רכז": [], "קלעי": [], "גבוה": []}
        for p in sorted_p:
            positions[p["עמדה"]].append(p)
            
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
                    st.write(f"• **{p['שם']}** ({p['עמדה']} | {p['רמה']})")
                    
            with col_b:
                st.info(f"🔵 **קבוצה ב' ({len(team_b)}/{max_per_team})**")
                for p in team_b:
                    st.write(f"• **{p['שם']}** ({p['עמדה']} | {p['רמה']})")
                    
            if waiting:
                st.warning(f"📋 **רשימת מזמינים / המתנה ({len(waiting)})**")
                for p in waiting:
                    st.write(f"• **{p['שם']}** ({p['עמדה']} | {p['רמה']})")
