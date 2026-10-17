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


st.html("""
<style>
#hockey-puck, #hockey-goal {
    position: fixed;
    z-index: 999999;
    font-size: 76px;
    line-height: 1;
    user-select: none;
    will-change: transform, left, top;
}

#hockey-puck {
    top: 25%;
    left: 5%;
    cursor: pointer;
    animation: puck-float 8s ease-in-out infinite alternate;
}

#hockey-goal {
    top: 60%;
    left: 70%;
    pointer-events: none;
    animation: goal-float 10s ease-in-out infinite alternate;
}

@keyframes puck-float {
    0%   { transform: translate(0,0) rotate(-8deg); }
    25%  { transform: translate(12vw,8vh) rotate(5deg); }
    50%  { transform: translate(28vw,-5vh) rotate(-5deg); }
    75%  { transform: translate(42vw,10vh) rotate(8deg); }
    100% { transform: translate(55vw,-5vh) rotate(-5deg); }
}

@keyframes goal-float {
    0%   { transform: translate(0,0) rotate(0); }
    50%  { transform: translate(-10vw,5vh) rotate(4deg); }
    100% { transform: translate(-25vw,-5vh) rotate(-4deg); }
}

.hockey-confetti {
    position: fixed;
    z-index: 1000000;
    pointer-events: none;
    font-size: 26px;
    animation: celebrate 3s ease-out forwards;
}

@keyframes celebrate {
    0% {
        opacity: 1;
        transform: translate(0,0) rotate(0) scale(.5);
    }
    50% {
        opacity: 1;
    }
    100% {
        opacity: 0;
        transform: translate(var(--dx),var(--dy))
                   rotate(540deg) scale(1);
    }
}
</style>

<div id="hockey-puck">🏒</div>
<div id="hockey-goal">🥅</div>

<script>
(() => {
    const puck = document.getElementById("hockey-puck");
    const goal = document.getElementById("hockey-goal");

    if (!puck || !goal || puck.dataset.ready) return;
    puck.dataset.ready = "1";

    puck.addEventListener("click", () => {
        if (puck.dataset.shooting) return;
        puck.dataset.shooting = "1";

        // Stop the floating animations for the shot.
        puck.style.animation = "none";
        goal.style.animation = "none";

        const p = puck.getBoundingClientRect();
        const g = goal.getBoundingClientRect();

        const dx = g.left - p.left;
        const dy = g.top - p.top;

        puck.animate([
            { transform: "translate(0,0) rotate(0deg) scale(1)" },
            {
                transform: `translate(${dx}px,${dy}px)
                            rotate(540deg) scale(.35)`
            }
        ], {
            duration: 1200,
            easing: "cubic-bezier(.2,.7,.3,1)",
            fill: "forwards"
        }).onfinish = () => {
            const r = goal.getBoundingClientRect();
            const emojis = ["🎉","✨","⭐","🏆","🎊"];

            for (let i = 0; i < 24; i++) {
                const bit = document.createElement("span");
                bit.className = "hockey-confetti";
                bit.textContent =
                    emojis[Math.floor(Math.random()*emojis.length)];

                bit.style.left = (r.left+r.width/2) + "px";
                bit.style.top = (r.top+r.height/2) + "px";
                bit.style.setProperty("--dx",
                    (Math.random()*300-150)+"px");
                bit.style.setProperty("--dy",
                    (Math.random()*260-130)+"px");

                document.body.appendChild(bit);
                setTimeout(() => bit.remove(), 3200);
            }

            puck.remove();
            goal.remove();
        };
    });
})();
</script>
""")


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
st.caption("Your daily morning hockey recap + live stats and standings · Powered by NHL data")
