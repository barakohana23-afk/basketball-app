import streamlit as st
import random
from itertools import combinations

# הגדרת כותרת האפליקציה והגדרות עמוד
st.set_page_config(page_title="חלוקת קבוצות כדורסל", page_icon="🏀", layout="centered")

# --- מנגנון להצגת Toast בסלולר (שורד st.rerun) ---
if "toast_message" in st.session_state and st.session_state.toast_message:
    msg, icon = st.session_state.toast_message
    st.toast(msg, icon=icon)
    st.session_state.toast_message = None

# --- עיצוב CSS מותאם ---
st.markdown("""
    <style>
        html, body, [class*="css"], .stMarkdown, h1, h2, h3, h4, h5, h6, p, label {
            text-align: center !important;
        }
        
        div[data-testid="stColumn"] div[data-testid="stCheckbox"] {
            background-color: #E0F2FE !important;
            border: 2px solid #38BDF8 !important;
            border-radius: 12px !important;
            padding: 12px 8px !important;
            margin-bottom: 12px !important;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05) !important;
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
        }

        div[data-testid="stColumn"] div[data-testid="stCheckbox"] * {
            color: #000000 !important;
            -webkit-text-fill-color: #000000 !important;
        }

        div[data-testid="stCheckbox"] label span p {
            font-size: 15px !important;
            line-height: 1.4 !important;
            font-weight: 600 !important;
            margin: 0 !important;
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

st.title("🏀 מחלק הקבוצות לכדורסל")
st.write("הכנס את רשימת השחקנים, העמדה והרמה לקבלת קבוצות מאוזנות!")

LEVEL_OPTIONS = ["חלש", "בינוני", "חזק"]
POSITION_OPTIONS = ["רכז", "קלעי", "גבוה"]

# מפת ניקוד מדויקת לפי עמדה ורמה
PLAYER_SCORES = {
    ("גבוה", "חזק"): 4,
    ("גבוה", "בינוני"): 3,
    ("גבוה", "חלש"): 2,
    
    ("רכז", "חזק"): 4,
    ("רכז", "בינוני"): 2,
    ("רכז", "חלש"): 1,
    
    ("קלעי", "חזק"): 3,
    ("קלעי", "בינוני"): 2,
    ("קלעי", "חלש"): 1,
}

def get_player_score(player):
    return PLAYER_SCORES.get((player["position"], player["level"]), 1)

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

if "players" not in st.session_state:
    st.session_state.players = []

st.subheader("⚙️ הגדרת המשחק")
max_per_team = st.number_input("מספר שחקנים מקסימלי בכל קבוצה", min_value=1, max_value=15, value=5, step=1)

st.divider()

st.subheader("⚡ בחירה מהירה של שחקנים קבועים")
st.write("סמן את השחקנים שהגיעו היום ולחץ על הוספה:")

cols = st.columns(3)
selected_defaults = []

for idx, p in enumerate(DEFAULT_PLAYERS):
    col = cols[idx % 3]
    with col:
        label_text = f"**{p['name']}**\n\n{p['position']}"
        if st.checkbox(label_text, key=f"default_{idx}"):
            selected_defaults.append(p)

if st.button("➕ הוסף את המסומנים לרשימת המשחק"):
    added_count = 0
    existing_names = [p["name"].strip().lower() for p in st.session_state.players]
    
    for p in selected_defaults:
        if p["name"].strip().lower() not in existing_names:
            st.session_state.players.append(p.copy())
            added_count += 1
            
    if added_count > 0:
        st.session_state.toast_message = (f"נוספו {added_count} שחקנים לרשימה בהצלחה!", "🏀")
        st.rerun()
    elif len(selected_defaults) == 0:
        st.warning("לא סומנו שחקנים לבחירה.")
    else:
        st.info("כל השחקנים המסומנים כבר נמצאים ברשימה!")

st.divider()

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
                st.session_state.toast_message = (f"השחקן {clean_name} נוסף בהצלחה!", "👤")
                st.rerun()
        else:
            st.error("נא להזין שם שחקן.")

if st.session_state.players:
    st.subheader(f"📋 רשימת השחקנים למשחק ({len(st.session_state.players)})")
    st.write("💡 ניתן לשנות עמדה של שחקן ישירות ברשימה למטה:")

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
            st.write(player["level"])
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

    # --- אלגוריתם החלוקה לפי ניקוד וחוקי הברזל ---
    def split_teams(players_list, max_players):
        total_slots = max_players * 2
        
        # 1. ערבוב אקראי שוויוני לקביעת סיכוי שווה לכל השחקנים להיכנס לרוטציה
        shuffled = players_list.copy()
        random.shuffle(shuffled)
        
        # 2. הפרדה בין המשתתפים במשחק לבין רשימת ההמתנה
        active_players = shuffled[:total_slots]
        waiting = shuffled[total_slots:]
        
        if len(active_players) < 2:
            return active_players, [], waiting

        team_size = len(active_players) // 2
        
        best_team_a = []
        best_team_b = []
        
        min_score_diff = float('inf')
        max_diversity = -1
        max_pos_balance = -1

        # זיהוי השחקנים ששווים 4 נקודות מתוך אלו שנבחרו לשחק
        top_players = [p for p in active_players if get_player_score(p) == 4]

        # 3. בדיקת כל האפשרויות לחלוקה
        for team_a_combo in combinations(active_players, team_size):
            team_a = list(team_a_combo)
            team_b = [p for p in active_players if p not in team_a]
            
            # --- חוק הברזל: פיצול שחקני רמה 4 ---
            if len(top_players) == 2:
                top_in_a = sum(1 for p in team_a if get_player_score(p) == 4)
                if top_in_a != 1:
                    continue  # פוסל קומבינציה שבה שניהם ביחד באותה קבוצה!

            # תנאי 1: חישוב ניקוד הכוח וההפרש
            score_a = sum(get_player_score(p) for p in team_a)
            score_b = sum(get_player_score(p) for p in team_b)
            score_diff = abs(score_a - score_b)
            
            # תנאי 2: מגוון עמדות בכל קבוצה
            pos_a = set(p["position"] for p in team_a)
            pos_b = set(p["position"] for p in team_b)
            total_diversity = len(pos_a) + len(pos_b)
            
            # תנאי 3: איזון עמדות בין א' לב'
            positions_a = [p["position"] for p in team_a]
            positions_b = [p["position"] for p in team_b]
            all_positions = set(positions_a + positions_b)
            pos_balance = sum(min(positions_a.count(pos), positions_b.count(pos)) for pos in all_positions)
            
            # עדכון הקבוצה הטובה ביותר
            if (score_diff < min_score_diff) or \
               (score_diff == min_score_diff and total_diversity > max_diversity) or \
               (score_diff == min_score_diff and total_diversity == max_diversity and pos_balance > max_pos_balance):
                
                min_score_diff = score_diff
                max_diversity = total_diversity
                max_pos_balance = pos_balance
                best_team_a = team_a
                best_team_b = team_b

        return best_team_a, best_team_b, waiting

    # --- כפתור החלוקה ---
    with col_split:
        if st.button("⚡ חלק לקבוצות!", type="primary"):
            team_a, team_b, waiting = split_teams(st.session_state.players, max_per_team)
            
            score_a = sum(get_player_score(p) for p in team_a)
            score_b = sum(get_player_score(p) for p in team_b)
            
            st.divider()
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.success(f"🟢 **קבוצה א' ({len(team_a)}/{max_per_team})**\n\n💪 ניקוד כוח: **{score_a}**")
                for p in team_a:
                    pts = get_player_score(p)
                    st.write(f"• **{p['name']}** ({p['position']} | {p['level']} - {pts} נק')")
                    
            with col_b:
                st.info(f"🔵 **קבוצה ב' ({len(team_b)}/{max_per_team})**\n\n💪 ניקוד כוח: **{score_b}**")
                for p in team_b:
                    pts = get_player_score(p)
                    st.write(f"• **{p['name']}** ({p['position']} | {p['level']} - {pts} נק')")
                    
            if waiting:
                st.warning(f"📋 **רשימת מזמינים / המתנה ({len(waiting)})**")
                for p in waiting:
                    pts = get_player_score(p)
                    st.write(f"• **{p['name']}** ({p['position']} | {p['level']} - {pts} נק')")
