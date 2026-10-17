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

hockey_egg = r"""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">

<style>
html, body {
    margin: 0;
    padding: 0;
    width: 100%;
    height: 100%;
    overflow: hidden;
    background: transparent;
}

#arena {
    position: relative;
    width: 100%;
    height: 650px;
    overflow: hidden;
    background: transparent;
}

.emoji {
    position: absolute;
    left: 0;
    top: 0;
    font-size: 45px;
    line-height: 1;
    cursor: pointer;
    user-select: none;
    -webkit-user-select: none;
    touch-action: manipulation;
    will-change: transform;
    filter: drop-shadow(0 3px 5px #0002);
}

.hockey {
    z-index: 3;
}

.goal {
    z-index: 2;
    cursor: default;
}

.confetti {
    position: absolute;
    z-index: 5;
    pointer-events: none;
    font-size: 23px;
    will-change: transform, opacity;
    animation: burst 900ms cubic-bezier(.15,.7,.3,1) forwards;
}

@keyframes burst {
    0% {
        opacity: 1;
        transform: translate(0,0) scale(1);
    }
    100% {
        opacity: 0;
        transform: translate(var(--dx),var(--dy))
                   rotate(360deg) scale(.4);
    }
}

@media (prefers-reduced-motion: reduce) {
    .confetti {
        animation-duration: 300ms;
    }
}
</style>
</head>

<body>
<div id="arena"></div>

<script>
(() => {
    const arena = document.getElementById("arena");

    let currentPair = null;
    let nextTimer = null;
    let animationFrame = null;
    let lastTime = 0;

    const rand = (min, max) =>
        min + Math.random() * (max - min);

    function bounds() {
        return {
            w: arena.clientWidth,
            h: arena.clientHeight
        };
    }

    function spawnPair() {
        if (currentPair) return;

        const {w, h} = bounds();
        if (w < 100 || h < 100) {
            nextTimer = setTimeout(spawnPair, 1500);
            return;
        }

        const size = 80;
        const margin = 12;

        const gx = rand(margin, Math.max(margin, w - size));
        const gy = rand(margin, Math.max(margin, h - size));

        let px = rand(margin, Math.max(margin, w - size));
        let py = rand(margin, Math.max(margin, h - size));

        if (Math.hypot(px - gx, py - gy) < 180) {
            px = Math.max(margin, Math.min(w - size, gx + 180));
        }

        const goal = document.createElement("div");
        goal.className = "emoji goal";
        goal.textContent = "🥅";
        goal.setAttribute("aria-label", "Hockey goal");

        const puck = document.createElement("div");
        puck.className = "emoji hockey";
        puck.textContent = "🏒";
        puck.setAttribute("role", "button");
        puck.setAttribute("tabindex", "0");
        puck.setAttribute("aria-label", "Shoot the puck into the goal!");

        arena.append(goal, puck);

        // Each emoji follows a continuous, smooth path.
        // Position and velocity are animated with requestAnimationFrame.
        const pair = {
            puck,
            goal,
            px, py, gx, gy,
            pvx: rand(22, 48) * (Math.random() < .5 ? -1 : 1),
            pvy: rand(18, 42) * (Math.random() < .5 ? -1 : 1),
            gvx: rand(12, 25) * (Math.random() < .5 ? -1 : 1),
            gvy: rand(10, 22) * (Math.random() < .5 ? -1 : 1),
            phase: rand(0, Math.PI * 2),
            shooting: false,
            dead: false
        };

        currentPair = pair;

        function shoot() {
            if (pair.shooting || pair.dead) return;
            pair.shooting = true;

            const {w, h} = bounds();
            const startX = pair.px;
            const startY = pair.py;

            // Aim at the center of the net.
            const endX = pair.gx;
            const endY = pair.gy;
            const start = performance.now();
            const duration = 650;

            // Ignore floating while the shot is in progress.
            function shotFrame(now) {
                if (pair.dead) return;

                const t = Math.min(1, (now - start) / duration);
                const eased = 1 - Math.pow(1 - t, 3);

                pair.puck.style.transform =
                    `translate3d(${
                      startX + (endX - startX) * eased
                    }px, ${
                      startY + (endY - startY) * eased
                    }px, 0) rotate(${720 * eased}deg) scale(${
                      1 - eased * .65
                    })`;

                if (t < 1) {
                    animationFrame = requestAnimationFrame(shotFrame);
                } else {
                    celebrate(endX + 35, endY + 35);
                    removePair(pair);
                    scheduleNext();
                }
            }

            animationFrame = requestAnimationFrame(shotFrame);
        }

        puck.addEventListener("click", shoot);
        puck.addEventListener("keydown", (event) => {
            if (event.key === "Enter" || event.key === " ") {
                event.preventDefault();
                shoot();
            }
        });

        pair.shoot = shoot;
        pair.startedAt = performance.now();

        if (animationFrame) cancelAnimationFrame(animationFrame);
        lastTime = 0;
        animationFrame = requestAnimationFrame(move);
    }

    function move(now) {
        const pair = currentPair;
        if (!pair || pair.dead) return;

        if (pair.shooting) return;

        if (!lastTime) lastTime = now;
        const dt = Math.min((now - lastTime) / 1000, 0.04);
        lastTime = now;

        const {w, h} = bounds();
        const size = 82;

        // Constant drifting velocity, with gentle sinusoidal motion.
        pair.px += pair.pvx * dt;
        pair.py += pair.pvy * dt;
        pair.gx += pair.gvx * dt;
        pair.gy += pair.gvy * dt;

        if (pair.px < 0 || pair.px > w - size) pair.pvx *= -1;
        if (pair.py < 0 || pair.py > h - size) pair.pvy *= -1;
        if (pair.gx < 0 || pair.gx > w - size) pair.gvx *= -1;
        if (pair.gy < 0 || pair.gy > h - size) pair.gvy *= -1;

        pair.px = Math.max(0, Math.min(w - size, pair.px));
        pair.py = Math.max(0, Math.min(h - size, pair.py));
        pair.gx = Math.max(0, Math.min(w - size, pair.gx));
        pair.gy = Math.max(0, Math.min(h - size, pair.gy));

        const elapsed = (now - pair.startedAt) / 1000;
        const bob = Math.sin(elapsed * 1.7 + pair.phase) * 7;
        const tilt = Math.sin(elapsed * 1.1 + pair.phase) * 9;

        pair.puck.style.transform =
            `translate3d(${pair.px}px, ${pair.py + bob}px, 0) rotate(${tilt}deg)`;

        pair.goal.style.transform =
            `translate3d(${pair.gx}px, ${
              pair.gy + Math.sin(elapsed * 1.3) * 5
            }px, 0) rotate(${Math.sin(elapsed) * 4}deg)`;

        animationFrame = requestAnimationFrame(move);
    }

    function celebrate(x, y) {
        const {w, h} = bounds();
        x = Math.max(0, Math.min(w - 20, x));
        y = Math.max(0, Math.min(h - 20, y));

        const icons = ["🎉", "✨", "⭐", "🎊", "🏆"];

        for (let i = 0; i < 18; i++) {
            const bit = document.createElement("span");
            bit.className = "confetti";
            bit.textContent = icons[Math.floor(rand(0, icons.length))];
            bit.style.left = x + "px";
            bit.style.top = y + "px";
            bit.style.setProperty("--dx", rand(-100, 100) + "px");
            bit.style.setProperty("--dy", rand(-100, 80) + "px");
            arena.appendChild(bit);
            setTimeout(() => bit.remove(), 1000);
        }
    }

    function removePair(pair) {
        pair.dead = true;
        pair.puck.remove();
        pair.goal.remove();

        if (currentPair === pair) currentPair = null;
        lastTime = 0;
    }

    function scheduleNext() {
        clearTimeout(nextTimer);
        nextTimer = setTimeout(spawnPair, rand(3000, 8000));
    }

    // Start with a short delay.
    nextTimer = setTimeout(spawnPair, 2500);
})();
</script>
</body>
</html>
"""

components.html(hockey_egg, height=660, scrolling=False)




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
