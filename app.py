import streamlit as st
import requests
from datetime import date, timedelta

st.set_page_config(
    page_title="Final Whistle",
    page_icon="🥅",
    initial_sidebar_state="locked",
    layout="centered",
    menu_items={
        'Submit an issue/bug to my GitHub': 'https://github.com/alikidimitoglou/morning-hockey-report/issues'
        'About': "#Test header."\
    }
)

st.title("The Final Whistle")
st.markdown(''':orange[Welcome to the show!]''')
st.caption("A recap of yesterday's NHL scores and game highlights.")

game_date = st.date_input(
    "Choose a game date",
    value=date.today() - timedelta(days=1),
    max_value=date.today(),
)

with st.sidebar:
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
            state = game.get("gameState", "Unknown")
    
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
                    f"{away_name}  {away_score} – "
                    f"{home_score}  {home_name}"
                )
                st.caption(f"Game status: {state}")
    
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
st.caption("Your daily morning hockey recap · Powered by NHL data")
