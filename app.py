import streamlit as st
import requests
from datetime import date, timedelta, datetime
from zoneinfo import ZoneInfo
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Final Whistle",
    page_icon="🥅",
    initial_sidebar_state="locked",
    layout="centered",
    menu_items={
        'Report a bug': 'https://github.com/alikidimitoglou/morning-hockey-report/issues',
        'About': '''
        Welcome! I'm a hockey lover and an even bigger data nerd, and I wanted a centralized way to catch up on games I couldn't watch live and news I might've missed.
        
        Naturally, I thought, *why not combine what I love, and just make the darn thing myself?* 

        So with a bit of determination and some help from the Streamlit and GitHub documentation, now I (and you!) have an up-to-date web app with all the hockey info you could ever want, plus an automated email sent out each morning while you drink your coffe.
                
        Thanks for checking out my project! Hope you enjoy.
        
        &mdash; Aliki :four_leaf_clover:'''
    }
)

st.title("The Final Whistle")
st.markdown(''':orange[Welcome to the show!]''')
st.caption("A recap of yesterday's NHL scores, game highlights, and the latest news and standings.")

# team filter #
teamoptions = st.multiselect(
    "Choose a team (or two, or three!) to read more about.",
    ["Penguins", "Avalanche"],
    filter_mode="contains",
)

# my version of inky! #

# sidebar for scores #
with st.sidebar:
    # date select #
    game_date = st.date_input(
        "Choose a game date:",
        value=date.today() - timedelta(days=1),
        max_value=date.today(),
        format="MM-DD-YYYY",
    )
    st.title("Scores:")
    @st.cache_data(ttl=900)
    def get_scores(selected_date):
        url = (
            "https://api-web.nhle.com/v1/score/"
            f"{selected_date.isoformat()}"
        )
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        return response.json()
    
    try:
        data = get_scores(game_date)
        games = data.get("games", [])
    
        if not games:
            st.info("No games found for this date.")

        for game in games:
            away = game.get("awayTeam", {})
            home = game.get("homeTeam", {})
            game_id = game.get("id")
            utc_starttime = game.get("startTimeUTC")
            state = game.get("gameState", "Unknown")
            timeremaining = game.get("timeRemaining")
    
            away_name = away.get("name", {}).get(
                "default", away.get("abbrev", "Away")
            )
            home_name = home.get("name", {}).get(
                "default", home.get("abbrev", "Home")
            )
            
            away_score = away.get("score", "—")
            home_score = home.get("score", "—")
    
            with st.container(border=True):
                st.subheader(
                    f"{home_name}  {home_score} – "
                    f"{away_name}  {away_score}"
                    )
                st.caption(f"Game status: {state}")
                
                if state != "OFF" and state != "FINAL":
                    st.caption(f"Time remaining: {timeremaining}")
                    dt = datetime.fromisoformat(
                        utc_starttime.replace("Z", "+00:00")
                    )
                    starttime = dt.astimezone(
                        ZoneInfo("America/New_York")
                    ).strftime("%-I:%M %p")
                    st.caption(f"Puck drop **{starttime}** EST")
        
                    if game_id:
                        st.link_button(
                            "Open NHL game recap ↗",
                            f"https://www.nhl.com/gamecenter/{game_id}",
                        )
    
    except requests.RequestException:
        st.error(
            "Couldn't load NHL scores. Please try again in a moment."
        )

st.divider()

# little footer note and feedback #
left, middle, right = st.columns(3, vertical_alignment="top")

with left:
    st.caption("Powered by NHL data.")

with right:
    selected = st.feedback("stars")
    if selected is None:
        st.caption("Everybody loves feedback! :speech_balloon:")
    elif selected == 4:
        st.caption("Thank you for your input!")
    else:
        st.caption(
            "Thank you for your input! Please click *Report a Bug* in the top-right menu to share any comments, concerns, or issues.")
