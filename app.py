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

    # --- אלגוריתם חלוקה תומך מרובה קבוצות (2, 3 או יותר) ---
    def generate_team_partitions(players, team_size, num_teams):
        if num_teams == 1:
            yield [players]
            return
            
        for first_team in combinations(players, team_size):
            remaining = [p for p in players if p not in first_team]
            for rest in generate_team_partitions(remaining, team_size, num_teams - 1):
                yield [list(first_team)] + rest

    def split_teams(players_list, max_players):
        num_teams = len(players_list) // max_players
        if num_teams < 2:
            num_teams = 2
            
        total_slots = num_teams * max_players
        
        shuffled = players_list.copy()
        random.shuffle(shuffled)
        
        active_players = shuffled[:total_slots]
        waiting = shuffled[total_slots:]
        
        if len(active_players) < max_players * 2:
            return [active_players], waiting

        best_partition = None
        min_score_diff = float('inf')
        max_diversity = -1
        max_pos_balance = -1

        top_players = [p for p in active_players if get_player_score(p) == 4]

        for partition in generate_team_partitions(active_players, max_players, num_teams):
            # חוק הברזל: פיצול שחקני רמה 4 שווה בשווה
            if len(top_players) == num_teams:
                if any(sum(1 for p in team if get_player_score(p) == 4) != 1 for team in partition):
                    continue

            scores = [sum(get_player_score(p) for p in team) for team in partition]
            score_diff = max(scores) - min(scores)
            
            total_diversity = sum(len(set(p["position"] for p in team)) for team in partition)
            
            all_positions = set(p["position"] for p in active_players)
            pos_balance = 0
            for pos in all_positions:
                pos_counts = [sum(1 for p in team if p["position"] == pos) for team in partition]
                pos_balance += min(pos_counts)

            if (score_diff < min_score_diff) or \
               (score_diff == min_score_diff and total_diversity > max_diversity) or \
               (score_diff == min_score_diff and total_diversity == max_diversity and pos_balance > max_pos_balance):
                
                min_score_diff = score_diff
                max_diversity = total_diversity
                max_pos_balance = pos_balance
                best_partition = partition

        return best_partition, waiting

    # --- כפתור החלוקה ---
    with col_split:
        if st.button("⚡ חלק לקבוצות!", type="primary"):
            teams, waiting = split_teams(st.session_state.players, max_per_team)
            
            st.divider()
            
            hebrew_letters = ["א'", "ב'", "ג'", "ד'", "ה'"]
            colors = ["🟢", "🔵", "🟠", "🟣", "🔴"]
            
            # --- סדר משחקים כשיש 3 קבוצות או יותר ---
            if len(teams) >= 3:
                team_names = [f"קבוצה {hebrew_letters[i]}" for i in range(len(teams))]
                # הגרלת הקבוצה שתנוח במשחק הראשון
                resting_team_idx = random.randint(0, len(teams) - 1)
                resting_team_name = team_names[resting_team_idx]
                
                playing_teams = [name for i, name in enumerate(team_names) if i != resting_team_idx]
                
                st.subheader("🎲 תוצאות הגרלת סדר המשחקים")
                st.info(f"🔥 **משחק 1 (פתיחה):** {playing_teams[0]} 🆚 {playing_teams[1]}")
                st.warning(f"☕ **נחה במשחק הראשון:** {resting_team_name}")
                st.write("---")

            cols_teams = st.columns(len(teams))
            
            for i, team in enumerate(teams):
                col = cols_teams[i % len(cols_teams)]
                score = sum(get_player_score(p) for p in team)
                team_char = chr(65 + i)
                team_name = hebrew_letters[i] if i < len(hebrew_letters) else team_char
                
                with col:
                    st.success(f"{colors[i % len(colors)]} **קבוצה {team_name} ({len(team)}/{max_per_team})**\n\n💪 ניקוד כוח: **{score}**")
                    for p in team:
                        pts = get_player_score(p)
                        st.write(f"• **{p['name']}** ({p['position']} | {p['level']} - {pts} נק')")
                    
            if waiting:
                st.write("")
                st.warning(f"📋 **רשימת מזמינים / המתנה ({len(waiting)})**")
                for p in waiting:
                    pts = get_player_score(p)
                    st.write(f"• **{p['name']}** ({p['position']} | {p['level']} - {pts} נק')")
