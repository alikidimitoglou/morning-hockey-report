import streamlit as st
import requests
from datetime import date, timedelta, datetime
from zoneinfo import ZoneInfo
import streamlist.components.v1 as components

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
html = """
<!DOCTYPE html>
<html>
<head>
<style>
  html, body {
    margin: 0;
    padding: 0;
    background: transparent;
    overflow: hidden;
    font-family: sans-serif;
  }

  #arena {
    position: relative;
    width: 100%;
    height: 400px;
    overflow: hidden;
  }

  .emoji {
    position: absolute;
    font-size: 30px;
    cursor: pointer;
    user-select: none;
    touch-action: manipulation;
    filter: drop-shadow(0 2px 3px #0002);
    animation: bob 2s ease-in-out infinite alternate;
    will-change: transform, left, top;
  }

  .puck {
    z-index: 2;
  }

  .goal {
    z-index: 1;
    animation-duration: 2.7s;
  }

  @keyframes bob {
    from { transform: translate(0, 0) rotate(-8deg); }
    to   { transform: translate(8px, -12px) rotate(8deg); }
  }

  .confetti {
    position: absolute;
    z-index: 5;
    pointer-events: none;
    font-size: 18px;
    animation: burst 850ms ease-out forwards;
  }

  @keyframes burst {
    from {
      opacity: 1;
      transform: translate(0, 0) scale(1);
    }
    to {
      opacity: 0;
      transform:
        translate(var(--dx), var(--dy))
        rotate(360deg) scale(.5);
    }
  }
</style>
</head>
<body>
<div id="arena"></div>

<script>
const arena = document.getElementById("arena");
let active = false;

function rand(max) {
  return Math.random() * max;
}

function spawn() {
  if (active) return;
  active = true;

  const w = arena.clientWidth;
  const h = arena.clientHeight;

  const goal = document.createElement("div");
  goal.className = "emoji goal";
  goal.textContent = "🥅";

  const puck = document.createElement("div");
  puck.className = "emoji puck";
  puck.textContent = "🏒";
  puck.title = "Take the shot!";

  const gx = rand(Math.max(1, w - 55));
  const gy = rand(Math.max(1, h - 55));
  let px = rand(Math.max(1, w - 55));
  let py = rand(Math.max(1, h - 55));

  // Keep the puck and goal from appearing on top of each other.
  if (Math.hypot(px - gx, py - gy) < 120) {
    px = Math.max(0, Math.min(w - 55, gx + 140));
  }

  goal.style.left = gx + "px";
  goal.style.top = gy + "px";
  puck.style.left = px + "px";
  puck.style.top = py + "px";

  arena.append(goal, puck);

  // Give the emojis a little wandering movement.
  let moves = 0;
  const wander = setInterval(() => {
    if (!puck.isConnected || moves++ > 8) {
      clearInterval(wander);
      return;
    }
    puck.style.left = rand(Math.max(1, w - 55)) + "px";
    puck.style.top = rand(Math.max(1, h - 55)) + "px";
    goal.style.left = Math.max(
      0, Math.min(w - 55, gx + rand(50) - 25)
    ) + "px";
  }, 700);

  puck.addEventListener("click", () => {
    if (!puck.isConnected) return;
    puck.style.pointerEvents = "none";
    clearInterval(wander);

    const p = puck.getBoundingClientRect();
    const g = goal.getBoundingClientRect();

    // Animate the stick toward the center of the net.
    const dx = (g.left + g.width / 2) - (p.left + p.width / 2);
    const dy = (g.top + g.height / 2) - (p.top + p.height / 2);

    puck.style.animation = "none";
    puck.animate([
      { transform: "translate(0,0) scale(1) rotate(0deg)" },
      {
        transform: `translate(${dx}px, ${dy}px)
                    scale(.35) rotate(540deg)`
      }
    ], {
      duration: 550,
      easing: "cubic-bezier(.2,.7,.3,1)",
      fill: "forwards"
    }).onfinish = () => {
      puck.remove();
      goal.remove();
      celebrate(gx + 20, gy + 15);
      active = false;
      setTimeout(spawn, 1800 + rand(2500));
    };
  });

  // Clean up untouched emojis after a while.
  setTimeout(() => {
    if (!puck.isConnected) return;
    clearInterval(wander);
    puck.remove();
    goal.remove();
    active = false;
    setTimeout(spawn, 2500);
  }, 10000);
}

function celebrate(x, y) {
  const bits = ["🎉", "✨", "⭐", "🏆", "🎊"];
  for (let i = 0; i < 16; i++) {
    const bit = document.createElement("span");
    bit.className = "confetti";
    bit.textContent = bits[Math.floor(rand(bits.length))];
    bit.style.left = x + "px";
    bit.style.top = y + "px";
    bit.style.setProperty("--dx", (rand(180) - 90) + "px");
    bit.style.setProperty("--dy", (rand(150) - 100) + "px");
    arena.appendChild(bit);
    setTimeout(() => bit.remove(), 1000);
  }
}

// Start after a short delay, then keep spawning occasionally.
setTimeout(spawn, 2000);
</script>
</body>
</html>
"""

components.html(html, height=420, scrolling=False)

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
