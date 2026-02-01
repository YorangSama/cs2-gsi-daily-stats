# CS2 GSI OBS Kill Counter

Track **daily CT kills & headshots** from CS2 using Game State Integration  
and display them in **OBS Browser Source** with persistent local storage.

## ✨ Features

- 🎯 Track **CT (Human) kills & headshots only**
- 📅 Automatic **daily reset** (data grouped by date)
- 💾 Local `stats.json` persistence (crash & power-loss safe)
- 📺 OBS Browser Source support
- 🔌 Works with existing CS2 GSI (no game modding)
- 🧠 Delta-based counting (no duplicate kills)

## 🎮 Who is this for?

- CS2 streamers using OBS
- Zombie Escape / custom servers
- Players who want daily kill statistics on stream
- Developers learning CS2 GSI integration

## 📁 Project Structure

<pre>
CS2-GSI-Python/
├── 1.py                            # ⭐ Main entry (only one)
├── LICENSE
├── README.md
├── gamestate.py
├── gamestate_integration_GSI.cfg
├── information.py
├── payloadparser.py
├── server.py
└── templates
    ├── index.html                  # OBS display page
    └── stats.html                  # OBS browser source
</pre>


## 🚀 Getting Started

### 1. Requirements

- Python 3.9+
- CS2 with Game State Integration enabled
- OBS Studio

### 2. Install dependencies

```bash
pip install flask flask-socketio flask-cors

3. Run the server
python 1.py

The server will listen on:
http://127.0.0.1:3000

Create a file:
cs2/cfg/gamestate_integration_obs.cfg

cfg
"OBS Stats"
{
  "uri" "http://127.0.0.1:3000/game_state"
  "timeout" "5.0"
  "buffer" "0.1"
  "throttle" "0.1"
  "heartbeat" "30.0"
  "data"
  {
    "player_state" "1"
  }
}

## 📺 OBS Setup

1. Add a **Browser Source**
2. URL:
http://127.0.0.1:3000
3. Set width / height as needed
4. Enable "Refresh browser when scene becomes active" (optional)

## 💾 Data Storage

- All statistics are saved in `stats.json`
- Data is grouped by date
- Previous days are preserved
- Safe against crashes and unexpected power loss

## ❓ FAQ

### Why are kills counted using delta?
CS2 GSI reports `round_kills` repeatedly. Delta-based counting avoids duplicate increments.

### What happens if OBS or Python restarts?
Stats persist and continue counting for the current day.

### Does it track Terrorist (Zombie) kills?
No. Only CT (Human) kills and headshots are tracked by design.

