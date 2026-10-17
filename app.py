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
hockey_overlay = r"""
<div id="hockey-easter-egg">
<style>
  #hockey-easter-egg {
    position: fixed;
    inset: 0;
    width: 100vw;
    height: 100vh;
    z-index: 999999;
    pointer-events: none;
    overflow: hidden;
  }

  #hockey-easter-egg .emoji {
    position: absolute;
    left: 0;
    top: 0;
    font-size: 76px;
    line-height: 1;
    cursor: pointer;
    user-select: none;
    pointer-events: auto;
    touch-action: manipulation;
    will-change: transform;
    filter: drop-shadow(0 3px 5px #0002);
  }

  #hockey-easter-egg .puck {
    z-index: 3;
  }

  #hockey-easter-egg .goal {
    z-index: 2;
    pointer-events: none;
  }

  #hockey-easter-egg .confetti {
    position: absolute;
    left: 0;
    top: 0;
    font-size: 25px;
    pointer-events: none;
    will-change: transform, opacity;
  }

  @media (prefers-reduced-motion: reduce) {
    #hockey-easter-egg .confetti {
      opacity: 0.8;
    }
  }
</style>

<script>
(() => {
  const root = document.getElementById("hockey-easter-egg");
  if (!root || root.dataset.started) return;
  root.dataset.started = "1";

  let pair = null;
  let raf = null;
  let spawnTimer = null;
  let lastTime = 0;
  let destroyed = false;

  const rand = (a, b) => a + Math.random() * (b - a);

  function spawn() {
    if (destroyed || pair) return;

    const w = window.innerWidth;
    const h = window.innerHeight;
    const size = 85;

    const puck = document.createElement("div");
    puck.className = "emoji puck";
    puck.textContent = "🏒";
    puck.title = "Take the shot!";
    puck.setAttribute("role", "button");
    puck.setAttribute("tabindex", "0");
    puck.setAttribute("aria-label", "Shoot for the goal");

    const goal = document.createElement("div");
    goal.className = "emoji goal";
    goal.textContent = "🥅";
    goal.setAttribute("aria-label", "Hockey goal");

    root.append(puck, goal);

    const p = {
      puck, goal,
      x: rand(20, Math.max(21, w - size)),
      y: rand(80, Math.max(81, h - size)),
      gx: rand(20, Math.max(21, w - size)),
      gy: rand(80, Math.max(81, h - size)),
      vx: rand(30, 65) * (Math.random() < .5 ? -1 : 1),
      vy: rand(20, 50) * (Math.random() < .5 ? -1 : 1),
      gvx: rand(15, 35) * (Math.random() < .5 ? -1 : 1),
      gvy: rand(12, 28) * (Math.random() < .5 ? -1 : 1),
      phase: rand(0, Math.PI * 2),
      shooting: false,
      dead: false
    };

    pair = p;

    function shoot() {
      if (p.shooting || p.dead) return;
      p.shooting = true;

      if (raf) cancelAnimationFrame(raf);
      lastTime = 0;

      const startX = p.x;
      const startY = p.y;
      const endX = p.gx;
      const endY = p.gy;
      const start = performance.now();

      // A slower, satisfying shot into the net.
      const duration = 1200;

      function shotFrame(now) {
        if (p.dead) return;

        const t = Math.min(1, (now - start) / duration);
        const eased = t * t * (3 - 2 * t);

        p.puck.style.transform =
          `translate3d(${startX + (endX-startX)*eased}px,
          ${startY + (endY-startY)*eased}px,0)
          rotate(${540*eased}deg) scale(${1-.7*eased})`;

        if (t < 1) {
          raf = requestAnimationFrame(shotFrame);
        } else {
          celebrate(endX + 35, endY + 35);
          removePair();
          spawnTimer = setTimeout(spawn, rand(4000, 9000));
        }
      }

      raf = requestAnimationFrame(shotFrame);
    }

    puck.addEventListener("click", shoot);
    puck.addEventListener("keydown", e => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        shoot();
      }
    });

    lastTime = 0;
    raf = requestAnimationFrame(move);
  }

  function move(now) {
    if (!pair || pair.dead || pair.shooting || destroyed) return;

    const p = pair;
    if (!lastTime) lastTime = now;

    // Small time steps prevent jumps after a slow frame.
    const dt = Math.min((now - lastTime) / 1000, 0.035);
    lastTime = now;

    const w = window.innerWidth;
    const h = window.innerHeight;
    const size = 90;

    // Both emojis drift continuously and independently.
    p.x += p.vx * dt;
    p.y += p.vy * dt;
    p.gx += p.gvx * dt;
    p.gy += p.gvy * dt;

    if (p.x < 0 || p.x > w-size) p.vx *= -1;
    if (p.y < 45 || p.y > h-size) p.vy *= -1;
    if (p.gx < 0 || p.gx > w-size) p.gvx *= -1;
    if (p.gy < 45 || p.gy > h-size) p.gvy *= -1;

    p.x = Math.max(0, Math.min(w-size, p.x));
    p.y = Math.max(45, Math.min(h-size, p.y));
    p.gx = Math.max(0, Math.min(w-size, p.gx));
    p.gy = Math.max(45, Math.min(h-size, p.gy));

    const elapsed = now / 1000;
    const bob = Math.sin(elapsed * 1.6 + p.phase) * 8;
    const tilt = Math.sin(elapsed * 1.1 + p.phase) * 8;

    p.puck.style.transform =
      `translate3d(${p.x}px,${p.y+bob}px,0) rotate(${tilt}deg)`;

    p.goal.style.transform =
      `translate3d(${p.gx}px,
      ${p.gy+Math.sin(elapsed*1.2)*5}px,0)
      rotate(${Math.sin(elapsed*.8)*3}deg)`;

    raf = requestAnimationFrame(move);
  }

  function celebrate(x, y) {
    const icons = ["🎉", "✨", "⭐", "🎊", "🏆"];

    // Slower confetti that drifts outward for three seconds.
    for (let i = 0; i < 24; i++) {
      const bit = document.createElement("span");
      bit.className = "confetti";
      bit.textContent = icons[Math.floor(rand(0, icons.length))];

      root.appendChild(bit);

      const dx = rand(-150, 150);
      const dy = rand(-160, 100);
      const spin = rand(-500, 500);

      bit.animate([
        {
          opacity: 1,
          transform: `translate3d(${x}px,${y}px,0) scale(.6)`
        },
        {
          opacity: 1,
          offset: .55,
          transform:
            `translate3d(${x+dx*.65}px,${y+dy*.65}px,0)
             rotate(${spin*.65}deg) scale(1)`
        },
        {
          opacity: 0,
          transform:
            `translate3d(${x+dx}px,${y+dy}px,0)
             rotate(${spin}deg) scale(.5)`
        }
      ], {
        duration: rand(2400, 3200),
        easing: "cubic-bezier(.2,.6,.3,1)",
        fill: "forwards"
      }).onfinish = () => bit.remove();
    }
  }

  function removePair() {
    if (!pair) return;
    pair.dead = true;
    pair.puck.remove();
    pair.goal.remove();
    pair = null;
    lastTime = 0;
  }

  function onResize() {
    if (!pair || pair.dead) return;
    const w = window.innerWidth;
    const h = window.innerHeight;
    pair.x = Math.min(pair.x, Math.max(0, w-90));
    pair.gx = Math.min(pair.gx, Math.max(0, w-90));
    pair.y = Math.min(pair.y, Math.max(45, h-90));
    pair.gy = Math.min(pair.gy, Math.max(45, h-90));
  }

  window.addEventListener("resize", onResize);

  // First pair appears after two seconds.
  spawnTimer = setTimeout(spawn, 2000);

  // Clean up if this overlay is removed during an app rerun.
  const observer = new MutationObserver(() => {
    if (!root.isConnected) {
      destroyed = true;
      clearTimeout(spawnTimer);
      if (raf) cancelAnimationFrame(raf);
      observer.disconnect();
      window.removeEventListener("resize", onResize);
    }
  });

  observer.observe(document.documentElement, {
    childList: true,
    subtree: true
  });
})();
</script>
</div>
"""

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
