#!/usr/bin/env python3
"""
Zenith — Smart Detox & Digital Wellness
Single-file Python/Flask application
"""

import json, os, random, t#!/usr/bin/env python3
"""
Zenith — Smart Detox & Digital Wellness
Single-file Python/Flask application
"""

import json, os, random, threading, time, webbrowser, requests
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, Response

app = Flask(__name__)

# ─── DATA FILE ────────────────────────────────────────────────────────────────
DATA_FILE = os.path.join(os.path.dirname(__file__), "zenith_data.json")

DEFAULT_STATE = {
    "screen_time_today": 2.4,
    "goal_screen_time": 3.0,
    "goal_focus_mins": 90,
    "goal_sleep": 8.0,
    "goal_water": 8,
    "focus_sessions_today": 0,
    "mindfulness_minutes": 15,
    "breathing_sessions": 0,
    "challenges_completed": 0,
    "total_xp": 340,
    "detox_streak": 7,
    "sleep_hours": 7.2,
    "water_glasses": 5,
    "score_history": [72, 74, 68, 80, 78, 83, 85],
    "mood_log": [],
    "journal": [],
    "habits": [
        {"id": "h1", "icon": "🧘", "name": "Morning Meditation", "streak": 5, "done": False},
        {"id": "h2", "icon": "🚶", "name": "10k Steps", "streak": 3, "done": False},
        {"id": "h3", "icon": "📵", "name": "No Social Before 9am", "streak": 7, "done": True},
        {"id": "h4", "icon": "💧", "name": "Drink 8 Glasses", "streak": 2, "done": False},
        {"id": "h5", "icon": "📖", "name": "Read 20 Minutes", "streak": 4, "done": True},
    ],
    "achievements_unlocked": ["streak_7", "mood_log"],
    "unread_notifications": 3,
    "notifications": [
        {"icon": "🔥", "text": "You're on a 7-day streak! Keep it up.", "time": "2m ago", "unread": True},
        {"icon": "💧", "text": "Time to hydrate! You haven't logged water.", "time": "18m ago", "unread": True},
        {"icon": "🧘", "text": "Breathing session reminder — 5 min break.", "time": "1h ago", "unread": True},
        {"icon": "🎯", "text": "Focus session completed — great work!", "time": "3h ago", "unread": False},
        {"icon": "🏆", "text": "Challenge unlocked: 'Social Detox Warrior'", "time": "Yesterday", "unread": False},
    ],
    "yoga_sessions": 0,
    "hydration_log": [],
}

QUOTES = [
    {"text": "The quieter you become, the more you are able to hear.", "author": "Rumi"},
    {"text": "Almost everything will work again if you unplug it for a few minutes, including you.", "author": "Anne Lamott"},
    {"text": "You can't pour from an empty cup. Take care of yourself first.", "author": "Unknown"},
    {"text": "Tension is who you think you should be. Relaxation is who you are.", "author": "Chinese Proverb"},
    {"text": "In the middle of difficulty lies opportunity.", "author": "Albert Einstein"},
    {"text": "The present moment is the only moment available to us.", "author": "Thich Nhat Hanh"},
    {"text": "Peace comes from within. Do not seek it without.", "author": "Buddha"},
    {"text": "Within you there is a stillness and a sanctuary.", "author": "Hermann Hesse"},
    {"text": "Your calm mind is the ultimate weapon against your challenges.", "author": "Bryant McGill"},
    {"text": "Breathe. Let go. And remind yourself that this very moment is the only one you know you have for sure.", "author": "Oprah Winfrey"},
]

TIPS = [
    "🧠 Try a 20-20-20 rule: every 20 min, look 20 ft away for 20 seconds.",
    "📱 Charge your phone outside the bedroom tonight for better sleep.",
    "🌿 Replace 15 min of scrolling with a short walk outside.",
    "🔕 Batch your notifications to 3 check-in times per day.",
    "🌙 Use night shift mode after 7 PM to reduce blue light exposure.",
    "✋ Delete the social media apps from your home screen for a week.",
    "📚 Keep a physical book on your nightstand instead of your phone.",
    "⏰ Set an app timer: 30 minutes for social media maximum per day.",
    "🤝 Schedule tech-free meals with family or friends daily.",
    "🎨 Replace evening screen time with a creative offline hobby.",
    "💡 Turn off all non-essential notifications for 24 hours.",
    "🧘 Start your morning with 5 minutes of silence before touching your phone.",
]

CHALLENGES = [
    {"id": "c1", "icon": "📵", "title": "No Social Media", "desc": "Avoid social media for 4 hours", "xp": 60},
    {"id": "c2", "icon": "🚶", "title": "Digital Detox Walk", "desc": "Take a 20-min phone-free walk", "xp": 50},
    {"id": "c3", "icon": "📖", "title": "Read Instead", "desc": "Read a book for 30 minutes", "xp": 45},
    {"id": "c4", "icon": "🧘", "title": "Mindful Morning", "desc": "No phone for the first hour of the day", "xp": 80},
    {"id": "c5", "icon": "🍽️", "title": "Tech-Free Meal", "desc": "Eat lunch without any screens", "xp": 35},
    {"id": "c6", "icon": "💤", "title": "Sleep Hygiene", "desc": "Phone off 1h before bed tonight", "xp": 70},
]

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Merge missing keys from default
            for k, v in DEFAULT_STATE.items():
                if k not in data:
                    data[k] = v
            return data
        except Exception:
            pass
    return dict(DEFAULT_STATE)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def calc_wellness(data):
    score = 50
    if data["sleep_hours"] >= 7: score += 12
    elif data["sleep_hours"] >= 6: score += 6
    wg = data.get("goal_water", 8)
    if data["water_glasses"] >= wg: score += 10
    elif data["water_glasses"] >= wg // 2: score += 5
    if data["screen_time_today"] <= data["goal_screen_time"]: score += 10
    elif data["screen_time_today"] <= data["goal_screen_time"] * 1.5: score += 5
    score += min(10, data["focus_sessions_today"] * 2)
    score += min(8, data["breathing_sessions"] * 4)
    done_habits = sum(1 for h in data["habits"] if h["done"])
    score += done_habits * 2
    score += min(10, data["challenges_completed"] * 3)
    return min(100, max(0, score))

def get_score_level(score):
    if score >= 90: return "Zenith"
    if score >= 75: return "Thriving"
    if score >= 60: return "Balanced"
    if score >= 45: return "Growing"
    return "Starting"

def get_level_name(xp):
    if xp >= 1000: return "Sage"
    if xp >= 700: return "Mindful"
    if xp >= 400: return "Focused"
    if xp >= 200: return "Aware"
    return "Explorer"

def check_achievements(data):
    unlocked = set(data.get("achievements_unlocked", []))
    if data["breathing_sessions"] >= 1: unlocked.add("first_breath")
    if data["detox_streak"] >= 7: unlocked.add("streak_7")
    if data["focus_sessions_today"] >= 5: unlocked.add("focus_5")
    wg = data.get("goal_water", 8)
    if data["water_glasses"] >= wg: unlocked.add("hydrated")
    if data["sleep_hours"] >= 7: unlocked.add("sleep_champ")
    if data["challenges_completed"] >= 3: unlocked.add("challenge_3")
    if len(data.get("mood_log", [])) >= 1: unlocked.add("mood_log")
    if len(data.get("journal", [])) >= 1: unlocked.add("journaler")
    done_habits = sum(1 for h in data["habits"] if h["done"])
    if done_habits >= 5: unlocked.add("habit_5")
    if data["mindfulness_minutes"] >= 30: unlocked.add("mindful_30")
    if data.get("yoga_sessions", 0) >= 1: unlocked.add("zen_master")
    data["achievements_unlocked"] = list(unlocked)
    return data

# ─── API ROUTES ───────────────────────────────────────────────────────────────

@app.route("/api/login", methods=["POST"])
def api_login():
    req = request.get_json()
    username = req.get("username", "")
    password = req.get("password", "")
    
    profile = None
    user_name = "User"
    
    if username == "admin_r" and password == "productivity1":
        profile = "ryan"
        user_name = "Ryan Sharma"
    elif username == "dev_s" and password == "focus0":
        profile = "saaransh"
        user_name = "Saaransh Kharbanda"
    elif username == "user_n" and password == "balance5":
        profile = "neerab"
        user_name = "Neerab Hazarika"
    else:
        return jsonify({"status": "error", "message": "Invalid credentials"}), 401
        
    data = load_data()
    data["user_name"] = user_name
    data["profile_type"] = profile
    
    # Template Data
    if profile == "ryan":
        data["screen_time_today"] = 1.2
        data["focus_sessions_today"] = 5
        data["total_xp"] = 2800
        data["detox_streak"] = 14
        data["score_history"] = [85, 88, 90, 89, 92, 95]
        data["breathing_sessions"] = 3
        data["mindfulness_minutes"] = 45
    elif profile == "saaransh":
        data["screen_time_today"] = 6.5
        data["focus_sessions_today"] = 0
        data["total_xp"] = 150
        data["detox_streak"] = 0
        data["score_history"] = [45, 42, 38, 40, 41, 35]
        data["breathing_sessions"] = 0
        data["mindfulness_minutes"] = 5
    elif profile == "neerab":
        data["screen_time_today"] = 3.0
        data["focus_sessions_today"] = 2
        data["total_xp"] = 850
        data["detox_streak"] = 4
        data["score_history"] = [65, 70, 68, 72, 75, 78]
        data["breathing_sessions"] = 1
        data["mindfulness_minutes"] = 15
        
    save_data(data)
    return jsonify({"status": "ok", "name": user_name, "profile": profile})

@app.route("/api/state")
def api_state():
    data = load_data()
    data = check_achievements(data)
    save_data(data)
    score = calc_wellness(data)
    history = data.get("score_history", [])
    history = history[-7:] + [score]
    data["score_history"] = history[-7:]
    save_data(data)
    return jsonify({
        "user_name": data.get("user_name"),
        "wellness_score": score,
        "score_level": get_score_level(score),
        "score_history": data["score_history"],
        "focus_sessions_today": data["focus_sessions_today"],
        "challenges_completed": data["challenges_completed"],
        "breathing_sessions": data["breathing_sessions"],
        "total_xp": data["total_xp"],
        "level_name": get_level_name(data["total_xp"]),
        "detox_streak": data["detox_streak"],
        "screen_time_today": data["screen_time_today"],
        "goal_screen_time": data["goal_screen_time"],
        "mindfulness_minutes": data["mindfulness_minutes"],
        "sleep_hours": data["sleep_hours"],
        "water_glasses": data["water_glasses"],
        "habits": data["habits"],
        "achievements_unlocked": data["achievements_unlocked"],
        "unread_notifications": data["unread_notifications"],
        "quote": random.choice(QUOTES),
        "tip": random.choice(TIPS),
        "yoga_sessions": data.get("yoga_sessions", 0),
    })

@app.route("/api/notifications")
def api_notifications():
    data = load_data()
    data["unread_notifications"] = 0
    save_data(data)
    return jsonify(data.get("notifications", []))

@app.route("/api/set_goal", methods=["POST"])
def api_set_goal():
    data = load_data()
    body = request.get_json()
    data["goal_screen_time"] = body.get("screen_time", data["goal_screen_time"])
    data["goal_focus_mins"] = body.get("focus_mins", data["goal_focus_mins"])
    data["goal_sleep"] = body.get("sleep", data["goal_sleep"])
    data["goal_water"] = body.get("water", data["goal_water"])
    save_data(data)
    return jsonify({"ok": True})

@app.route("/api/weekly")
def api_weekly():
    days = [(datetime.now() - timedelta(days=6-i)).strftime("%a") for i in range(7)]
    random.seed(42)
    screen = [round(random.uniform(1.5, 5.5), 1) for _ in range(6)]
    data = load_data()
    screen.append(data["screen_time_today"])
    focus = [round(random.uniform(0.5, 3.0), 1) for _ in range(6)]
    focus.append(round(data["focus_sessions_today"] * 0.5, 1))
    goal = [data["goal_screen_time"]] * 7
    return jsonify({"labels": days, "screen": screen, "focus": focus, "goal": goal})

@app.route("/api/app_usage")
def api_app_usage():
    return jsonify([
        {"app": "Instagram", "hours": 1.4, "color": "#ff6b9d"},
        {"app": "YouTube", "hours": 2.1, "color": "#ff5f7e"},
        {"app": "Chrome", "hours": 1.8, "color": "#7c6dff"},
        {"app": "Slack", "hours": 0.9, "color": "#ffb347"},
        {"app": "Netflix", "hours": 0.7, "color": "#00e5c0"},
        {"app": "Other", "hours": 0.5, "color": "#4cde80"},
    ])

@app.route("/api/digital_diet")
def api_digital_diet():
    return jsonify({
        "labels": ["Focus", "Mindful", "Social", "Learning", "Rest", "Creation"],
        "current": [72, 65, 30, 55, 70, 45],
        "ideal":   [85, 80, 20, 70, 85, 60],
    })

@app.route("/api/heatmap")
def api_heatmap():
    cells = []
    base = datetime.now() - timedelta(days=34)
    random.seed(7)
    for i in range(35):
        d = base + timedelta(days=i)
        val = random.choices([0, 1, 2, 3], weights=[20, 30, 35, 15])[0]
        cells.append({"val": val, "day": d.strftime("%A"), "date": d.strftime("%b %d")})
    return jsonify(cells)

@app.route("/api/habits")
def api_habits():
    return jsonify(load_data()["habits"])

@app.route("/api/toggle_habit", methods=["POST"])
def api_toggle_habit():
    data = load_data()
    hid = request.get_json().get("id")
    for h in data["habits"]:
        if h["id"] == hid:
            if not h["done"]:
                h["done"] = True
                h["streak"] += 1
                data["total_xp"] += 20
            else:
                h["done"] = False
            break
    data = check_achievements(data)
    save_data(data)
    return jsonify({"habits": data["habits"], "xp": data["total_xp"]})

@app.route("/api/challenges")
def api_challenges():
    return jsonify(CHALLENGES)

@app.route("/api/complete_challenge", methods=["POST"])
def api_complete_challenge():
    data = load_data()
    xp = request.get_json().get("xp", 50)
    data["total_xp"] += xp
    data["challenges_completed"] += 1
    data = check_achievements(data)
    save_data(data)
    return jsonify({"xp": data["total_xp"]})

@app.route("/api/log_mood", methods=["POST"])
def api_log_mood():
    data = load_data()
    mood = request.get_json().get("mood", "okay")
    ts = datetime.now().strftime("%H:%M")
    data.setdefault("mood_log", []).append({"mood": mood, "time": ts})
    data["mood_log"] = data["mood_log"][-10:]
    data["total_xp"] += 15
    data = check_achievements(data)
    save_data(data)
    return jsonify({"mood_log": data["mood_log"]})

@app.route("/api/focus_complete", methods=["POST"])
def api_focus_complete():
    data = load_data()
    mins = request.get_json().get("minutes", 25)
    data["focus_sessions_today"] += 1
    data["mindfulness_minutes"] = min(120, data["mindfulness_minutes"] + mins)
    data["total_xp"] += 40
    data = check_achievements(data)
    save_data(data)
    return jsonify({"ok": True})

@app.route("/api/breathing_done", methods=["POST"])
def api_breathing_done():
    data = load_data()
    data["breathing_sessions"] += 1
    data["mindfulness_minutes"] = min(120, data["mindfulness_minutes"] + 5)
    data["total_xp"] += 20
    data = check_achievements(data)
    save_data(data)
    return jsonify({"ok": True})

@app.route("/api/log_sleep", methods=["POST"])
def api_log_sleep():
    data = load_data()
    data["sleep_hours"] = request.get_json().get("hours", 7.0)
    data = check_achievements(data)
    save_data(data)
    return jsonify({"ok": True})

@app.route("/api/log_water", methods=["POST"])
def api_log_water():
    data = load_data()
    wg = data.get("goal_water", 8)
    data["water_glasses"] = min(wg + 4, data["water_glasses"] + 1)
    if data["water_glasses"] <= wg:
        data["total_xp"] += 10
    ts = datetime.now().strftime("%H:%M")
    data.setdefault("hydration_log", []).append({"time": ts, "amount": 250})
    data = check_achievements(data)
    save_data(data)
    return jsonify({"glasses": data["water_glasses"]})

@app.route("/api/journal", methods=["GET"])
def api_journal_get():
    return jsonify(load_data().get("journal", []))

@app.route("/api/journal", methods=["POST"])
def api_journal_post():
    data = load_data()
    text = request.get_json().get("text", "").strip()[:300]
    if text:
        ts = datetime.now().strftime("%b %d, %H:%M")
        data.setdefault("journal", []).insert(0, {"text": text, "time": ts})
        data["journal"] = data["journal"][:20]
        data["total_xp"] += 15
        data = check_achievements(data)
        save_data(data)
    return jsonify({"entries": data.get("journal", []), "xp": data["total_xp"]})

@app.route("/api/yoga_done", methods=["POST"])
def api_yoga_done():
    data = load_data()
    data["yoga_sessions"] = data.get("yoga_sessions", 0) + 1
    data["total_xp"] += 35
    data["mindfulness_minutes"] = min(120, data["mindfulness_minutes"] + 10)
    data = check_achievements(data)
    save_data(data)
    return jsonify({"ok": True, "yoga_sessions": data["yoga_sessions"]})

@app.route("/api/ai_coach", methods=["POST"])
def api_ai_coach():
    req = request.get_json()
    user_msg = req.get("message", "")
    mode = req.get("mode", "chat") # 'chat' or 'analysis'
    
    data = load_data()
    api_key = os.environ.get("GROK_API_KEY")
    
    if not api_key:
        # Simulation if no API key provided
        if mode == "analysis":
            return jsonify({"reply": f"Based on your current activity, {data.get('user_name', 'User')}, your wellness score is {data.get('wellness_score', 85)}. You've spent {data.get('screen_time_today', 0)}h on screens today. I recommend a 10-minute meditation session to offset digital fatigue."})
        else:
            return jsonify({"reply": "I'm currently in offline mode. Please configure your GROK_API_KEY to enable live AI coaching, but I can still tell you that your focus sessions are looking great!"})

    # Grok API Integration
    try:
        system_prompt = f"You are Zenith AI, a premium digital wellness coach. User Data: {json.dumps(data)}. "
        if mode == "analysis":
            system_prompt += "Provide a clinical yet motivating analysis of their current wellness metrics."
        else:
            system_prompt += "Be a friendly, encouraging coach. Keep responses concise and focused on digital detox."

        response = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "grok-beta",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_msg if user_msg else "Analyze my current status."}
                ]
            },
            timeout=10
        )
        res_data = response.json()
        reply = res_data['choices'][0]['message']['content']
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": f"Error connecting to Grok: {str(e)}"}), 500

@app.route("/api/hydration_log")
def api_hydration_log():
    data = load_data()
    return jsonify({
        "log": data.get("hydration_log", []),
        "glasses": data["water_glasses"],
        "goal": data.get("goal_water", 8),
    })

# ─── MAIN HTML PAGE ───────────────────────────────────────────────────────────

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>Zenith — Smart Detox & Digital Wellness</title>
<meta name="description" content="AI-powered digital wellness dashboard. Track screen time, mood, habits, yoga, focus and more."/>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Space+Grotesk:wght@400;500;600;700;800&display=swap" rel="stylesheet"/>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
:root{
  --bg:#020202; /* Deep Black */
  --s1:rgba(255,255,255,0.02);--s2:rgba(255,255,255,0.04);--s3:rgba(255,255,255,0.07);
  --b1:rgba(255,255,255,0.12); /* Sharp white glass borders */
  --b2:rgba(255,255,255,0.25);
  --tx:#ffffff; /* Pure white text */
  --mu:rgba(255,255,255,0.5);
  --a:#ffffff; /* Neon White Accent */
  --a2:#cccccc; /* Silver Accent */
  --a3:#999999; /* Grey Accent */
  --warn:#e6e6e6;--err:#ff4d4d;--ok:#ffffff;
  --ga:rgba(255,255,255,0.15); /* White glow */
  --gb:rgba(200,200,200,0.1); /* Silver glow */
  --gc:rgba(150,150,150,0.1); /* Grey glow */
  --r:22px;--f:'Inter',sans-serif;--f2:'Space Grotesk',sans-serif;
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{font-family:var(--f);background:var(--bg);color:var(--tx);min-height:100vh;overflow-x:hidden}

/* LAYOUT */
.app-container{display:flex;min-height:100vh;position:relative;z-index:1}
.sidebar{width:250px;background:rgba(5,9,26,0.75);backdrop-filter:blur(28px);-webkit-backdrop-filter:blur(28px);border-right:1px solid var(--b1);padding:30px 16px;position:fixed;left:0;top:0;bottom:0;z-index:100;display:flex;flex-direction:column}
.sb-logo{display:flex;align-items:center;gap:12px;margin-bottom:40px;padding:0 10px}
.sb-logo-icon{width:42px;height:42px;border-radius:14px;background:linear-gradient(135deg,var(--a),var(--a2));display:flex;align-items:center;justify-content:center;font-size:22px;box-shadow:0 0 24px var(--ga);animation:pulse 4s infinite}
.sb-logo-text{font-family:var(--f2);font-size:22px;font-weight:800;background:linear-gradient(135deg,#9b8dff,var(--a2));-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.nav-links{display:flex;flex-direction:column;gap:6px;flex:1;overflow-y:auto}
.nb{display:flex;align-items:center;gap:14px;padding:13px 16px;border-radius:14px;font-size:13.5px;font-weight:600;color:var(--mu);cursor:pointer;transition:all .2s;border:1px solid transparent;background:transparent;width:100%;text-align:left}
.nb:hover{background:rgba(255,255,255,0.03);color:var(--tx)}
.nb.act{background:linear-gradient(90deg,rgba(124,109,255,0.14),transparent);border:1px solid var(--b1);border-left:3px solid var(--a);color:#fff;box-shadow:0 4px 20px rgba(0,0,0,0.18)}
.nb-ic{font-size:18px;width:22px;text-align:center;flex-shrink:0}
.main-content{margin-left:250px;flex:1;padding:20px 28px 90px;max-width:1420px}

/* TABS */
.tab-content{display:none;margin-top:10px;animation:slideInTab .45s cubic-bezier(0.2,0.8,0.2,1) forwards;opacity:0}
.tab-content.act{display:block}
@keyframes slideInTab{from{opacity:0;transform:translateY(22px)}to{opacity:1;transform:translateY(0)}}

/* BG EFFECTS */
#stars{position:fixed;inset:0;z-index:0;pointer-events:none}
.orbs{position:fixed;inset:0;z-index:0;pointer-events:none;overflow:hidden}
.orb{position:absolute;border-radius:50%;filter:blur(110px);opacity:0.13;animation:flt 24s ease-in-out infinite}
.o1{width:700px;height:700px;background:var(--a);top:-220px;left:-220px}
.o2{width:540px;height:540px;background:var(--a2);bottom:-140px;right:-140px;animation-delay:-9s}
.o3{width:420px;height:420px;background:var(--a3);top:38%;left:38%;animation-delay:-17s}
.o4{width:320px;height:320px;background:var(--warn);bottom:22%;left:6%;animation-delay:-6s;opacity:0.07}
.o5{width:280px;height:280px;background:#4cde80;top:15%;right:10%;animation-delay:-13s;opacity:0.06}
@keyframes flt{0%,100%{transform:translate(0,0) scale(1)}40%{transform:translate(55px,-65px) scale(1.08)}70%{transform:translate(-35px,45px) scale(0.93)}}
@keyframes pulse{0%,100%{box-shadow:0 0 24px var(--ga)}50%{box-shadow:0 0 50px var(--ga),0 0 70px rgba(0,229,192,0.18)}}

/* GLASS & CARDS */
.g{background:var(--s1);backdrop-filter:blur(28px) saturate(180%);-webkit-backdrop-filter:blur(28px) saturate(180%);border:1px solid var(--b1);border-radius:var(--r);transition:all .3s ease}
.g:hover{border-color:var(--b2);background:var(--s2);box-shadow:0 10px 38px rgba(0,0,0,0.22)}
.shim{position:relative;overflow:hidden}
.shim::after{content:'';position:absolute;inset:0;border-radius:inherit;pointer-events:none;background:linear-gradient(105deg,transparent 40%,rgba(255,255,255,0.04) 50%,transparent 60%);background-size:200% 100%;animation:shim 6s linear infinite}
@keyframes shim{0%{background-position:200% 0}100%{background-position:-200% 0}}

/* BENTO */
.bento{display:grid;grid-template-columns:repeat(12,1fr);gap:18px;align-items:start}
.card{padding:24px;border-radius:var(--r);position:relative;overflow:hidden}
.lbl{font-size:11px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:var(--mu);margin-bottom:14px;display:flex;align-items:center;gap:8px}
.c3{grid-column:span 3}.c4{grid-column:span 4}.c5{grid-column:span 5}
.c6{grid-column:span 6}.c7{grid-column:span 7}.c8{grid-column:span 8}
.c9{grid-column:span 9}.c12{grid-column:span 12}

/* HEADER */
header{display:flex;align-items:center;justify-content:space-between;padding:15px 24px;margin-bottom:22px;background:rgba(255,255,255,0.03);backdrop-filter:blur(28px);border:1px solid var(--b1);border-radius:var(--r);position:sticky;top:20px;z-index:90}
.hdr-title{font-family:var(--f2);font-size:21px;font-weight:700;letter-spacing:-0.5px}
.hdr-r{display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.pill{display:inline-flex;align-items:center;gap:7px;padding:7px 15px;border-radius:100px;font-size:13px;font-weight:600;cursor:default;white-space:nowrap}
.pill-xp{background:rgba(0,229,192,.1);border:1px solid rgba(0,229,192,.24);color:var(--a2)}
.pill-streak{background:rgba(255,179,71,.1);border:1px solid rgba(255,179,71,.28);color:var(--warn)}
.pill-clock{background:rgba(124,109,255,.12);border:1px solid rgba(124,109,255,.28);color:var(--a);font-family:var(--f2);letter-spacing:.5px}

/* NOTIFICATION */
.notif-wrap{position:relative}
.notif-bell{width:40px;height:40px;border-radius:12px;background:var(--s2);border:1px solid var(--b1);display:flex;align-items:center;justify-content:center;font-size:18px;cursor:pointer;transition:all .2s;position:relative}
.notif-bell:hover{background:var(--s3);border-color:var(--b2);transform:scale(1.07)}
.notif-badge{position:absolute;top:-4px;right:-4px;width:18px;height:18px;border-radius:50%;background:var(--a3);border:2px solid var(--bg);font-size:9px;font-weight:800;color:#fff;display:flex;align-items:center;justify-content:center;animation:bBounce .85s ease infinite alternate}
@keyframes bBounce{from{transform:scale(1)}to{transform:scale(1.18)}}
.notif-panel{position:absolute;top:calc(100% + 10px);right:0;width:320px;z-index:200;background:rgba(8,14,30,.98);backdrop-filter:blur(32px);border:1px solid var(--b2);border-radius:var(--r);box-shadow:0 22px 64px rgba(0,0,0,.55);display:none;overflow:hidden}
.notif-panel.open{display:block;animation:dropIn .22s ease}
@keyframes dropIn{from{opacity:0;transform:translateY(-14px)}to{opacity:1;transform:translateY(0)}}
.notif-head{padding:14px 18px;font-size:12px;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:var(--mu);border-bottom:1px solid var(--b1)}
.notif-item{display:flex;align-items:flex-start;gap:12px;padding:13px 18px;border-bottom:1px solid var(--b1);transition:background .2s}
.notif-item:hover{background:var(--s2)}
.notif-item.unread{background:rgba(124,109,255,.08)}
.ni-icon{font-size:20px;flex-shrink:0;margin-top:1px}
.ni-text{font-size:13px;font-weight:500;line-height:1.4}
.ni-time{font-size:11px;color:var(--mu);margin-top:3px}

/* SCORE */
.score-ring{width:155px;height:155px;position:relative;margin:10px auto 0}
.score-ring svg{transform:rotate(-90deg)}
.st-track{fill:none;stroke:rgba(255,255,255,.07);stroke-width:12}
.sf{fill:none;stroke-width:12;stroke-linecap:round;stroke:url(#sg);transition:stroke-dashoffset 1.6s cubic-bezier(.4,0,.2,1)}
.score-inner{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center}
.sn{font-family:var(--f2);font-size:46px;font-weight:800;line-height:1}
.sl{font-size:11px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:var(--a2);margin-top:4px}
.sparkline-wrap{margin:14px 0 8px;height:44px;position:relative}
.spark-svg{width:100%;height:100%;overflow:visible}
.tstats{display:flex;justify-content:space-around;padding:15px 0 0;border-top:1px solid var(--b1);margin-top:14px}
.tstat .v{font-family:var(--f2);font-size:24px;font-weight:700;text-align:center}
.tstat .l{font-size:11px;color:var(--mu);text-align:center;margin-top:3px}

/* QUOTE */
.qbody{font-size:19px;line-height:1.65;font-style:italic;margin-top:10px;opacity:.9}
.qattr{margin-top:16px;font-size:14px;font-weight:600;color:var(--a);display:flex;align-items:center;gap:10px}
.qattr::before{content:'';display:block;width:30px;height:2px;background:var(--a);border-radius:2px;flex-shrink:0}

/* SCREEN TIME */
.st-big{font-family:var(--f2);font-size:42px;font-weight:800;line-height:1;margin:12px 0 5px}
.prog-t{background:rgba(255,255,255,.07);border-radius:100px;height:11px;overflow:hidden;margin:16px 0 7px}
.prog-f{height:100%;border-radius:100px;transition:width 1.4s cubic-bezier(.4,0,.2,1)}
.prog-tks{display:flex;justify-content:space-between;font-size:12px;color:var(--mu)}

/* FOCUS TIMER */
.mp-row{display:flex;gap:7px;flex-wrap:wrap;justify-content:center;margin-bottom:10px}
.mp{padding:6px 16px;border-radius:100px;font-size:13px;font-weight:600;cursor:pointer;border:1px solid var(--b1);background:transparent;color:var(--mu);transition:all .2s}
.mp.act{background:rgba(124,109,255,.2);border-color:var(--a);color:#fff;box-shadow:0 0 18px rgba(124,109,255,.25)}
.timer-face{text-align:center;padding:22px 0 14px}
.tnum{font-family:var(--f2);font-size:68px;font-weight:800;line-height:1;letter-spacing:-4px;background:linear-gradient(135deg,#a08dff,var(--a2));-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.tiny-p{height:6px;background:rgba(255,255,255,.07);border-radius:6px;overflow:hidden;margin:14px 0 7px}
.tiny-pf{height:100%;border-radius:6px;background:linear-gradient(90deg,var(--a),var(--a2));transition:width 1s linear}
.sound-opts{display:flex;gap:7px;flex-wrap:wrap;margin-top:10px;justify-content:center}
.sound-btn{padding:5px 13px;border-radius:100px;font-size:12px;font-weight:600;cursor:pointer;border:1px solid var(--b1);background:transparent;color:var(--mu);transition:all .2s}
.sound-btn.act{background:rgba(0,229,192,.12);border-color:var(--a2);color:var(--a2)}

/* BREATHING */
.breath-sc{display:flex;flex-direction:column;align-items:center;padding:18px 0 10px}
.breath-ring{width:140px;height:140px;border-radius:50%;cursor:pointer;background:radial-gradient(circle,rgba(0,229,192,.18),rgba(124,109,255,.06));border:2px solid rgba(0,229,192,.35);display:flex;align-items:center;justify-content:center;box-shadow:0 0 50px rgba(0,229,192,.1);transition:box-shadow .3s}
.breath-ring.go{animation:breathAnim 19s ease-in-out infinite}
@keyframes breathAnim{0%,5%{transform:scale(1);box-shadow:0 0 50px rgba(0,229,192,.1)}22%,55%{transform:scale(1.5);box-shadow:0 0 100px rgba(0,229,192,.45)}72%,100%{transform:scale(1);box-shadow:0 0 50px rgba(0,229,192,.1)}}
.br-inner{width:88px;height:88px;border-radius:50%;background:rgba(0,229,192,.1);border:1px solid rgba(0,229,192,.25);display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:600;color:var(--a2);text-align:center;line-height:1.3}
.breath-phase{margin-top:16px;font-size:15px;font-weight:500;color:var(--mu)}
.breath-cyc{font-family:var(--f2);font-size:27px;font-weight:700;color:var(--a2);margin-top:3px}
.b-modes{display:flex;gap:7px;justify-content:center;margin-bottom:10px;flex-wrap:wrap}
.bm{padding:6px 13px;border-radius:100px;font-size:12px;font-weight:600;cursor:pointer;border:1px solid var(--b1);background:transparent;color:var(--mu);transition:all .2s}
.bm.act{background:rgba(0,229,192,.12);border-color:var(--a2);color:var(--a2)}

/* MOOD */
.mood-grid{display:flex;gap:10px;flex-wrap:wrap;justify-content:center;margin-top:14px}
.mb{display:flex;flex-direction:column;align-items:center;gap:6px;padding:15px 10px;border-radius:18px;cursor:pointer;background:rgba(255,255,255,.04);border:1px solid var(--b1);transition:all .22s;min-width:68px}
.mb:hover,.mb.sel{border-color:var(--b2);background:rgba(255,255,255,.1);transform:translateY(-5px);box-shadow:0 12px 30px rgba(0,0,0,.3)}
.me{font-size:32px;line-height:1}
.ml{font-size:12px;font-weight:600;color:var(--mu)}
.mood-hist{margin-top:16px;display:flex;gap:7px;flex-wrap:wrap}
.mood-tag{padding:6px 11px;border-radius:100px;font-size:12px;background:rgba(255,255,255,.05);border:1px solid var(--b1);color:var(--mu)}

/* HABITS */
.hab-list{display:flex;flex-direction:column;gap:9px;margin-top:10px}
.hab{display:flex;align-items:center;gap:14px;padding:13px 16px;background:rgba(255,255,255,.04);border:1px solid var(--b1);border-radius:16px;cursor:pointer;transition:all .22s}
.hab:hover{background:rgba(255,255,255,.08);transform:translateX(5px)}
.hab.done{background:rgba(0,229,192,.06);border-color:rgba(0,229,192,.25)}
.hab-icon{font-size:22px;flex-shrink:0}
.hab-body{flex:1}
.hab-name{font-size:13.5px;font-weight:600}
.hab-str{font-size:12px;color:var(--mu);margin-top:2px}
.hab-check{width:25px;height:25px;border-radius:50%;border:2px solid var(--b2);display:flex;align-items:center;justify-content:center;font-size:13px;flex-shrink:0;transition:all .3s}
.hab.done .hab-check{background:var(--a2);border-color:var(--a2);color:#05091a;font-weight:700}

/* CHARTS */
.chat-w{height:220px;margin-top:10px;width:100%}
.ul{display:flex;flex-direction:column;gap:9px;margin-top:14px}
.ur{display:flex;align-items:center;gap:11px}
.udot{width:9px;height:9px;border-radius:50%;flex-shrink:0}
.uname{font-size:13px;flex:1}
.ubg{flex:2;background:rgba(255,255,255,.07);border-radius:100px;height:5px;overflow:hidden}
.uf{height:100%;border-radius:100px;transition:width 1.3s ease}
.uh{font-size:12px;font-weight:600;color:var(--mu);min-width:30px;text-align:right}
.wleg{display:flex;gap:14px;flex-wrap:wrap;margin-bottom:8px}
.wl{display:flex;align-items:center;gap:7px;font-size:12px;color:var(--mu)}
.wlc{width:9px;height:9px;border-radius:3px;display:inline-block}

/* HEATMAP */
.hm-grid{display:grid;grid-template-columns:repeat(7,1fr);gap:6px;margin-top:14px}
.hm-cell{aspect-ratio:1;border-radius:8px;cursor:default;transition:transform .15s;position:relative}
.hm-cell:hover{transform:scale(1.2);z-index:2}
.hv0{background:rgba(255,255,255,.06)}.hv1{background:rgba(0,229,192,.22)}.hv2{background:rgba(0,229,192,.52)}.hv3{background:rgba(0,229,192,.88);box-shadow:0 0 8px rgba(0,229,192,.4)}
.hm-tip{position:absolute;bottom:130%;left:50%;transform:translateX(-50%);background:rgba(8,14,30,.95);border:1px solid var(--b2);border-radius:8px;padding:6px 11px;font-size:11px;white-space:nowrap;pointer-events:none;opacity:0;transition:opacity .15s;z-index:10}
.hm-cell:hover .hm-tip{opacity:1}

/* SLEEP & WATER */
.sw-row{display:flex;gap:16px;margin-top:12px}
.sw-box{flex:1;padding:16px;background:rgba(255,255,255,.03);border:1px solid var(--b1);border-radius:16px;text-align:center}
.sw-big{font-family:var(--f2);font-size:34px;font-weight:800;margin:7px 0}
.swl{font-size:13px;color:var(--mu)}
.wdots{display:flex;gap:6px;justify-content:center;flex-wrap:wrap;margin-top:10px}
.wd{width:15px;height:15px;border-radius:50%;background:rgba(255,255,255,.1);border:1px solid var(--b1);cursor:pointer;transition:all .3s}
.wd.on{background:var(--a);border-color:var(--a);box-shadow:0 0 10px rgba(124,109,255,.4)}
input[type=range]{width:100%;accent-color:var(--a);cursor:pointer;margin-top:13px;height:5px;background:linear-gradient(90deg,var(--a),var(--a2));border-radius:6px;appearance:none;outline:none}
input[type=range]::-webkit-slider-thumb{appearance:none;width:20px;height:20px;border-radius:50%;background:#fff;box-shadow:0 2px 10px rgba(0,0,0,.4);cursor:pointer;border:4px solid var(--a)}

/* QUICK ACTIONS */
.act-g{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-top:14px}
.act-b{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:7px;padding:18px 8px;border-radius:16px;background:rgba(255,255,255,.04);border:1px solid var(--b1);cursor:pointer;transition:all .22s;font-family:var(--f);color:var(--tx)}
.act-b:hover{background:rgba(255,255,255,.09);border-color:var(--b2);transform:translateY(-4px);box-shadow:0 12px 30px rgba(0,0,0,.3)}
.act-b:active{transform:translateY(-1px)}
.ai{font-size:26px;line-height:1}
.al{font-size:12px;font-weight:600;color:var(--mu);text-align:center}

/* JOURNAL */
.journal-list{display:flex;flex-direction:column;gap:9px;margin-top:12px;max-height:200px;overflow-y:auto;padding-right:4px}
.j-item{padding:13px 15px;background:rgba(255,255,255,.04);border:1px solid var(--b1);border-radius:14px}
.j-text{font-size:13.5px;line-height:1.5;color:var(--tx)}
.j-time{font-size:11px;color:var(--mu);margin-top:5px}
textarea.j-input{width:100%;background:rgba(255,255,255,.05);border:1px solid var(--b1);border-radius:14px;padding:13px 15px;font-family:var(--f);font-size:13.5px;color:var(--tx);resize:none;height:95px;outline:none;transition:border-color .2s;margin-top:12px}
textarea.j-input:focus{border-color:var(--b3);background:rgba(255,255,255,.07)}

/* ACHIEVEMENTS */
.ach-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:11px;margin-top:14px}
.ach-item{display:flex;flex-direction:column;align-items:center;gap:5px;padding:15px 7px;border-radius:16px;border:1px solid var(--b1);background:rgba(255,255,255,.03);transition:all .22s;cursor:default;text-align:center}
.ach-item.unlocked{background:rgba(124,109,255,.1);border-color:rgba(124,109,255,.35);box-shadow:0 0 20px rgba(124,109,255,.15)}
.ach-item.unlocked:hover{transform:translateY(-4px);box-shadow:0 10px 30px rgba(124,109,255,.25)}
.ach-icon{font-size:26px;line-height:1;filter:grayscale(1);opacity:.4;transition:all .4s}
.ach-item.unlocked .ach-icon{filter:none;opacity:1}
.ach-name{font-size:11px;font-weight:600;color:var(--mu);line-height:1.3}
.ach-item.unlocked .ach-name{color:var(--tx)}
.ach-xp{font-size:11px;font-weight:700;color:var(--a);opacity:0;transition:opacity .3s}
.ach-item.unlocked .ach-xp{opacity:1}
@keyframes newAch{0%,100%{box-shadow:0 0 20px rgba(124,109,255,.15)}50%{box-shadow:0 0 54px rgba(124,109,255,.55),0 0 85px rgba(0,229,192,.3)}}
.ach-item.just-unlocked{animation:newAch 1.5s ease 3}

/* CHALLENGES */
.ch-list{display:flex;flex-direction:column;gap:9px;margin-top:14px;max-height:380px;overflow-y:auto;padding-right:4px}
.chi{display:flex;align-items:center;gap:13px;padding:15px;background:rgba(255,255,255,.04);border:1px solid var(--b1);border-radius:16px;cursor:pointer;transition:all .22s}
.chi:hover{background:rgba(255,255,255,.09);transform:translateX(5px);border-color:var(--b2)}
.chi.done{opacity:.5;pointer-events:none}
.chi-icon{font-size:24px;flex-shrink:0}
.chi-body{flex:1}
.chi-title{font-size:14px;font-weight:600}
.chi-desc{font-size:12px;color:var(--mu);margin-top:3px}
.chi-xp{font-size:13px;font-weight:700;color:var(--a);white-space:nowrap}
.chi-check{width:25px;height:25px;border-radius:50%;border:2px solid var(--b2);display:flex;align-items:center;justify-content:center;font-size:13px;flex-shrink:0;transition:all .3s}
.chi.done .chi-check{background:var(--a2);border-color:var(--a2);color:#05091a}

/* ── YOGA SECTION ── */
.yoga-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:14px}
.yoga-card{background:rgba(255,255,255,.04);border:1px solid var(--b1);border-radius:20px;overflow:hidden;transition:all .3s;cursor:pointer}
.yoga-card:hover{border-color:var(--b2);background:rgba(255,255,255,.07);transform:translateY(-4px);box-shadow:0 14px 40px rgba(0,0,0,.3)}
.yoga-card.active-pose{border-color:rgba(0,229,192,.5);background:rgba(0,229,192,.06);box-shadow:0 0 30px rgba(0,229,192,.15)}
.yoga-illus{height:140px;display:flex;align-items:center;justify-content:center;position:relative;overflow:hidden}
.yoga-illus svg{width:100px;height:130px;filter:drop-shadow(0 0 16px rgba(0,229,192,.25));animation:yogaFloat 4s ease-in-out infinite}
@keyframes yogaFloat{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}
.yoga-info{padding:16px}
.yoga-title{font-family:var(--f2);font-size:15px;font-weight:700;margin-bottom:4px}
.yoga-sub{font-size:12px;color:var(--mu);margin-bottom:12px;line-height:1.4}
.yoga-meta{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:12px}
.yoga-tag{padding:4px 10px;border-radius:100px;font-size:11px;font-weight:600;background:rgba(124,109,255,.1);border:1px solid rgba(124,109,255,.25);color:var(--a)}
.yoga-tag.green{background:rgba(0,229,192,.1);border-color:rgba(0,229,192,.25);color:var(--a2)}
.yoga-tag.pink{background:rgba(255,107,157,.1);border-color:rgba(255,107,157,.25);color:var(--a3)}
.yoga-timer-wrap{display:none;padding:0 16px 16px}
.yoga-timer-wrap.open{display:block}
.yoga-timer-face{font-family:var(--f2);font-size:38px;font-weight:800;text-align:center;padding:10px 0;background:linear-gradient(135deg,#a08dff,var(--a2));-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.yoga-prog{height:6px;background:rgba(255,255,255,.07);border-radius:6px;overflow:hidden;margin:8px 0}
.yoga-pf{height:100%;border-radius:6px;background:linear-gradient(90deg,var(--a),var(--a2));transition:width .5s linear}
.yoga-btns{display:flex;gap:8px;justify-content:center;margin-top:10px}
.body-filter-bar{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:16px}
.bfb{padding:7px 16px;border-radius:100px;font-size:13px;font-weight:600;cursor:pointer;border:1px solid var(--b1);background:transparent;color:var(--mu);transition:all .2s}
.bfb.act{background:rgba(124,109,255,.18);border-color:var(--a);color:#fff}
.yoga-complete-banner{background:linear-gradient(135deg,rgba(0,229,192,.12),rgba(124,109,255,.08));border:1px solid rgba(0,229,192,.3);border-radius:16px;padding:20px;text-align:center;margin-bottom:20px;display:none}
.yoga-complete-banner.show{display:block;animation:slideInTab .4s ease}

/* ── HYDRATION CORNER ── */
.hydro-hero{display:flex;align-items:center;gap:28px;margin-top:14px;flex-wrap:wrap}
.hydro-vessel{position:relative;width:90px;flex-shrink:0}
.hydro-vessel svg{width:90px;height:150px}
.hydro-stats-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;margin-top:16px}
.hydro-stat{padding:16px;background:rgba(255,255,255,.04);border:1px solid var(--b1);border-radius:16px;text-align:center}
.hydro-stat-v{font-family:var(--f2);font-size:28px;font-weight:800;color:var(--a2)}
.hydro-stat-l{font-size:12px;color:var(--mu);margin-top:4px}
.hydro-log{margin-top:16px}
.hydro-log-title{font-size:12px;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:var(--mu);margin-bottom:10px}
.hydro-log-items{display:flex;flex-direction:column;gap:7px;max-height:180px;overflow-y:auto}
.hydro-log-item{display:flex;align-items:center;gap:10px;padding:9px 13px;background:rgba(0,229,192,.05);border:1px solid rgba(0,229,192,.12);border-radius:12px}
.hydro-log-icon{font-size:16px}
.hydro-log-text{font-size:12px;flex:1}
.hydro-log-time{font-size:11px;color:var(--mu)}
.intake-buttons{display:flex;gap:8px;flex-wrap:wrap;margin-top:16px}
.intake-btn{padding:9px 18px;border-radius:100px;font-size:13px;font-weight:600;cursor:pointer;border:1px solid rgba(0,229,192,.3);background:rgba(0,229,192,.07);color:var(--a2);transition:all .2s}
.intake-btn:hover{background:rgba(0,229,192,.18);transform:translateY(-2px)}
.hydro-reminder-row{display:flex;align-items:center;gap:12px;margin-top:16px;padding:14px;background:rgba(255,179,71,.05);border:1px solid rgba(255,179,71,.2);border-radius:14px}
.hydro-reminder-icon{font-size:22px}
.hydro-reminder-text{flex:1;font-size:13px}
.hydro-reminder-toggle{position:relative;width:42px;height:24px;flex-shrink:0}
.hydro-reminder-toggle input{opacity:0;width:0;height:0}
.hrt-slider{position:absolute;inset:0;border-radius:24px;background:rgba(255,255,255,.1);border:1px solid var(--b2);cursor:pointer;transition:all .3s}
.hrt-slider::before{content:'';position:absolute;left:3px;top:3px;width:16px;height:16px;border-radius:50%;background:var(--mu);transition:all .3s}
.hydro-reminder-toggle input:checked + .hrt-slider{background:var(--a2);border-color:var(--a2)}
.hydro-reminder-toggle input:checked + .hrt-slider::before{transform:translateX(18px);background:#fff}
.hydro-wave{animation:hydroWave 3s ease-in-out infinite}
@keyframes hydroWave{0%,100%{d:path("M 0 80 Q 22 72 45 80 Q 68 88 90 80 L 90 120 L 0 120 Z")}50%{d:path("M 0 80 Q 22 88 45 80 Q 68 72 90 80 L 90 120 L 0 120 Z")}}

/* UTILS */
.btn{padding:11px 22px;border-radius:100px;border:none;cursor:pointer;font-family:var(--f);font-size:13.5px;font-weight:600;transition:all .2s;display:inline-flex;align-items:center;justify-content:center;gap:7px}
.btn-p{background:linear-gradient(135deg,var(--a),#a86dff);color:#fff;box-shadow:0 6px 24px var(--ga)}
.btn-p:hover{transform:translateY(-2px);box-shadow:0 10px 36px var(--ga)}
.btn-g{background:rgba(255,255,255,.06);color:var(--tx);border:1px solid var(--b1)}
.btn-g:hover{background:rgba(255,255,255,.12);border-color:var(--b2)}
.btn-t{background:rgba(0,229,192,.1);color:var(--a2);border:1px solid rgba(0,229,192,.25)}
.btn-t:hover{background:rgba(0,229,192,.2)}
.btn-sm{padding:9px 18px;font-size:12.5px}
.chip{display:inline-flex;align-items:center;gap:6px;padding:5px 13px;border-radius:100px;font-size:12px;font-weight:600}
.cr{background:rgba(255,95,126,.1);color:var(--err);border:1px solid rgba(255,95,126,.25)}
.cg{background:rgba(0,229,192,.1);color:var(--a2);border:1px solid rgba(0,229,192,.25)}
.cw{background:rgba(255,179,71,.1);color:var(--warn);border:1px solid rgba(255,179,71,.25)}
.ga-{box-shadow:0 0 40px var(--ga)}.gb-{box-shadow:0 0 36px var(--gb)}

/* MODALS */
.modal-overlay{position:fixed;inset:0;z-index:300;background:rgba(0,0,0,.62);backdrop-filter:blur(10px);display:none;align-items:center;justify-content:center;animation:fadeIn .25s ease}
.modal-overlay.open{display:flex}
@keyframes fadeIn{from{opacity:0}to{opacity:1}}
.modal-box{background:rgba(8,14,30,.98);border:1px solid var(--b2);border-radius:var(--r);width:min(500px,94vw);padding:30px;box-shadow:0 26px 84px rgba(0,0,0,.65);animation:slideUp .3s ease}
@keyframes slideUp{from{opacity:0;transform:translateY(30px)}to{opacity:1;transform:translateY(0)}}
.modal-title{font-family:var(--f2);font-size:21px;font-weight:700;margin-bottom:22px;display:flex;align-items:center;gap:11px}
.goal-row{margin-bottom:18px}
.goal-label{font-size:13.5px;font-weight:600;margin-bottom:9px;display:flex;justify-content:space-between;align-items:center}
.goal-label span{font-family:var(--f2);font-size:17px;font-weight:700;color:var(--a2)}

/* BREAK BANNER */
#breakBanner{position:fixed;bottom:0;left:0;right:0;z-index:199;background:linear-gradient(90deg,rgba(255,95,126,.15),rgba(255,179,71,.12));backdrop-filter:blur(22px);border-top:1px solid rgba(255,95,126,.3);padding:15px 28px;display:flex;align-items:center;gap:18px;transform:translateY(100%);transition:transform .5s cubic-bezier(.4,0,.2,1)}
#breakBanner.show{transform:translateY(0)}
.bb-icon{font-size:24px}
.bb-text{flex:1;font-size:14px;font-weight:500}
.bb-close{font-size:13px;font-weight:600;cursor:pointer;opacity:.7;padding:7px 16px;border-radius:100px;background:rgba(255,255,255,.1);border:1px solid var(--b2);transition:all .2s}
.bb-close:hover{opacity:1;background:rgba(255,255,255,.15)}

/* TOAST */
#toast{position:fixed;bottom:85px;right:28px;z-index:9999;background:rgba(8,14,32,.97);backdrop-filter:blur(28px);border:1px solid var(--b2);border-radius:16px;padding:15px 22px;max-width:370px;transform:translateY(90px);opacity:0;transition:all .4s cubic-bezier(.4,0,.2,1);font-size:14px;font-weight:500;box-shadow:0 18px 52px rgba(0,0,0,.5);display:flex;align-items:center;gap:12px}
#toast.show{transform:translateY(0);opacity:1}
.ti{font-size:22px;flex-shrink:0}

/* CONFETTI */
.cf{position:fixed;z-index:99999;pointer-events:none;width:10px;height:10px;border-radius:2px;animation:cfFall 2.9s ease-in forwards}
@keyframes cfFall{0%{opacity:1;transform:translateY(0) rotate(0)}100%{opacity:0;transform:translateY(110vh) rotate(720deg)}}

/* SCROLLBAR */
::-webkit-scrollbar{width:5px}
::-webkit-scrollbar-thumb{background:var(--b2);border-radius:5px}

/* RESPONSIVE */
@media(max-width:900px){
  .sidebar{top:auto;width:100%;height:74px;border-right:none;border-top:1px solid var(--b2);flex-direction:row;align-items:center;justify-content:space-around;padding:0 6px;z-index:200;background:rgba(5,9,26,.92)}
  .sb-logo{display:none}
  .nav-links{flex-direction:row;gap:0;width:100%;justify-content:space-around;overflow:visible}
  .nb{flex-direction:column;gap:4px;padding:8px 4px;border:none;font-size:10px;width:12.5%;text-align:center;border-radius:8px;border-left:none !important;background:transparent !important}
  .nb.act{background:rgba(124,109,255,.12) !important;border-bottom:3px solid var(--a) !important;box-shadow:none !important}
  .nb-ic{font-size:20px}
  .main-content{margin-left:0;padding:14px 14px 88px}
  header{flex-direction:column;gap:12px;align-items:flex-start}
  .act-g{grid-template-columns:repeat(2,1fr)}
  .ach-grid{grid-template-columns:repeat(3,1fr)}
  .yoga-grid{grid-template-columns:repeat(2,1fr)}
  .c3,.c4,.c5,.c6,.c7,.c8,.c9,.c12{grid-column:span 12}
  .hydro-hero{flex-direction:column;align-items:flex-start}
}
@media(min-width:901px) and (max-width:1200px){
  .c3,.c4,.c5,.c6{grid-column:span 6}
  .c8,.c9,.c12{grid-column:span 12}
  .yoga-grid{grid-template-columns:repeat(2,1fr)}
}
</style>
</head>
<body>

<!-- BG -->
<canvas id="stars"></canvas>
<div class="orbs"><div class="orb o1"></div><div class="orb o2"></div><div class="orb o3"></div><div class="orb o4"></div><div class="orb o5"></div></div>

<!-- MODALS -->
<div class="modal-overlay" id="goalModal" onclick="if(event.target===this)closeGoalModal()">
  <div class="modal-box">
    <div class="modal-title">🎯 Set Your Goals</div>
    <div class="goal-row">
      <div class="goal-label">Screen Time Limit &nbsp;<span id="g-st-val">3.0h</span></div>
      <input type="range" id="g-st" min="1" max="8" step="0.5" value="3" oninput="document.getElementById('g-st-val').textContent=this.value+'h'">
    </div>
    <div class="goal-row">
      <div class="goal-label">Daily Focus Minutes &nbsp;<span id="g-fm-val">90m</span></div>
      <input type="range" id="g-fm" min="15" max="240" step="15" value="90" oninput="document.getElementById('g-fm-val').textContent=this.value+'m'">
    </div>
    <div class="goal-row">
      <div class="goal-label">Sleep Target &nbsp;<span id="g-sl-val">8.0h</span></div>
      <input type="range" id="g-sl" min="4" max="12" step="0.5" value="8" oninput="document.getElementById('g-sl-val').textContent=this.value+'h'">
    </div>
    <div class="goal-row">
      <div class="goal-label">Water Goal (glasses) &nbsp;<span id="g-wa-val">8</span></div>
      <input type="range" id="g-wa" min="4" max="16" step="1" value="8" oninput="document.getElementById('g-wa-val').textContent=this.value">
    </div>
    <div style="display:flex;gap:11px;margin-top:26px;justify-content:flex-end">
      <button class="btn btn-g" onclick="closeGoalModal()">Cancel</button>
      <button class="btn btn-p" onclick="saveGoals()">Save Goals</button>
    </div>
  </div>
</div>

<div id="breakBanner">
  <div class="bb-icon">⏰</div>
  <div class="bb-text"><strong>Break time!</strong> You've been focused — stand up, stretch, rest your eyes.</div>
  <div class="bb-close" onclick="dismissBreak()">Dismiss</div>
  <button class="btn btn-t btn-sm" onclick="startBreakTimer();dismissBreak()">Start 5m Break</button>
</div>

<div id="toast"><div class="ti" id="tIcon"></div><div id="tMsg"></div></div>

<!-- AUTHENTICATION OVERLAY -->
<div id="authOverlay" style="position:fixed;inset:0;background:rgba(2,2,2,0.95);backdrop-filter:blur(30px);z-index:9999;display:flex;align-items:center;justify-content:center;opacity:1;transition:opacity 0.6s cubic-bezier(0.2,0.8,0.2,1);">
  <div style="background:rgba(255,255,255,0.02);padding:50px 40px;border-radius:24px;border:1px solid rgba(255,255,255,0.1);max-width:400px;width:90%;text-align:center;box-shadow:0 0 40px rgba(255,255,255,0.05);">
    <h1 style="font-family:var(--f2);font-size:32px;margin-bottom:10px;color:var(--tx);text-shadow:0 0 15px rgba(255,255,255,0.4);font-weight:800;letter-spacing:-1px;">Zenith OS</h1>
    <p style="color:var(--mu);margin-bottom:30px;line-height:1.5;font-size:14px;">Log in to access your digital wellness dashboard.</p>
    
    <div style="display:flex;flex-direction:column;gap:15px;">
      <input type="text" id="authUsername" placeholder="Username" style="width:100%;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.1);padding:14px 18px;border-radius:12px;color:#fff;font-family:var(--f);font-size:15px;outline:none;transition:border-color 0.2s;" onfocus="this.style.borderColor='#ffffff'" onblur="this.style.borderColor='rgba(255,255,255,0.1)'" onkeydown="if(event.key==='Enter') document.getElementById('authPassword').focus()" />
      <input type="password" id="authPassword" placeholder="Password" style="width:100%;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.1);padding:14px 18px;border-radius:12px;color:#fff;font-family:var(--f);font-size:15px;outline:none;transition:border-color 0.2s;" onfocus="this.style.borderColor='#ffffff'" onblur="this.style.borderColor='rgba(255,255,255,0.1)'" onkeydown="if(event.key==='Enter') handleLogin()" />
      <button class="login-btn" onclick="handleLogin()" style="margin-top:10px;background:#ffffff;color:#000000;border:none;padding:15px;border-radius:12px;font-family:var(--f);font-size:16px;font-weight:700;cursor:pointer;transition:all 0.3s;box-shadow:0 0 15px rgba(255,255,255,0.3);">Sign In</button>
    </div>
  </div>
</div>

<style>
.login-btn:hover { background: #e0e0e0; transform: translateY(-2px); box-shadow: 0 0 25px rgba(255,255,255,0.5); }
.login-btn:active { transform: translateY(0); }
  .chat-u { align-self: flex-end; background: var(--a); color: #fff; padding: 10px 14px; border-radius: 14px 14px 0 14px; font-size: 13.5px; box-shadow: 0 4px 15px rgba(124,109,255,0.2); }
  .chat-a { align-self: flex-start; background: rgba(255,255,255,0.08); border: 1px solid var(--b1); padding: 10px 14px; border-radius: 14px 14px 14px 0; font-size: 13.5px; color: #eee; }
</style>

<!-- APP -->
<div class="app-container">
  <nav class="sidebar">
    <div class="sb-logo">
      <div class="sb-logo-icon" style="padding:4px; font-size:inherit;">
        <svg viewBox="0 0 100 100" width="100%" height="100%" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
          <!-- Lotus base -->
          <path d="M50 85 C30 85, 20 60, 50 40 C80 60, 70 85, 50 85 Z" fill="rgba(212,175,55,0.15)" stroke="var(--a)" stroke-width="2"/>
          <path d="M50 85 C15 75, 10 45, 35 35 C40 45, 45 65, 50 85 Z" fill="rgba(16,185,129,0.15)" stroke="var(--a2)" stroke-width="2"/>
          <path d="M50 85 C85 75, 90 45, 65 35 C60 45, 55 65, 50 85 Z" fill="rgba(139,92,246,0.15)" stroke="var(--a3)" stroke-width="2"/>
          <!-- AI Circuit Node -->
          <circle cx="50" cy="55" r="7" fill="var(--bg)" stroke="var(--a)" stroke-width="2"/>
          <circle cx="50" cy="55" r="3" fill="#fff" stroke="none"/>
          <line x1="50" y1="48" x2="50" y2="25" stroke="rgba(255,255,255,0.6)" stroke-width="2"/>
          <circle cx="50" cy="25" r="3" fill="var(--a)" stroke="none"/>
          <line x1="43" y1="52" x2="25" y2="40" stroke="rgba(255,255,255,0.6)" stroke-width="2"/>
          <circle cx="25" cy="40" r="3" fill="var(--a2)" stroke="none"/>
          <line x1="57" y1="52" x2="75" y2="40" stroke="rgba(255,255,255,0.6)" stroke-width="2"/>
          <circle cx="75" cy="40" r="3" fill="var(--a3)" stroke="none"/>
        </svg>
      </div>
      <div class="sb-logo-text" style="background: linear-gradient(135deg, var(--a), #fff); -webkit-background-clip: text; color: transparent;">Zenith</div>
    </div>
    <div class="nav-links">
      <button class="nb act" data-tab="tab-home" onclick="navTo(this)"><span class="nb-ic">🏠</span><span>Home</span></button>
      <button class="nb" data-tab="tab-focus" onclick="navTo(this)"><span class="nb-ic">🎯</span><span>Focus</span></button>
      <button class="nb" data-tab="tab-insights" onclick="navTo(this)"><span class="nb-ic">📊</span><span>Insights</span></button>
      <button class="nb" data-tab="tab-life" onclick="navTo(this)"><span class="nb-ic">🌿</span><span>Life & Habits</span></button>
      <button class="nb" data-tab="tab-yoga" onclick="navTo(this)"><span class="nb-ic">🧘</span><span>Yoga</span></button>
      <button class="nb" data-tab="tab-hydration" onclick="navTo(this)"><span class="nb-ic">💧</span><span>Hydration</span></button>
      <button class="nb" data-tab="tab-progress" onclick="navTo(this)"><span class="nb-ic">🏆</span><span>Journey</span></button>
      <button class="nb" data-tab="tab-ai" onclick="navTo(this)"><span class="nb-ic">🤖</span><span>AI Coach</span></button>
      <div style="margin-top:auto; padding: 10px 0; border-top: 1px solid rgba(255,255,255,0.05)">
        <button class="nb" style="color: #ff4d4d" onclick="logout()"><span class="nb-ic">🚪</span><span>Logout</span></button>
      </div>
    </div>
  </nav>

  <main class="main-content">
    <header>
      <div class="hdr-title" id="hdrTitle">Home Dashboard</div>
      <div class="hdr-r">
        <div class="pill pill-xp">⚡ <span id="xpVal">340 XP</span> <span style="font-size:12px;opacity:.65;font-weight:500;margin-left:3px" id="lvlName">Focused</span></div>
        <div class="pill pill-streak">🔥 <span id="streakVal">7</span>-day streak</div>
        <button class="btn btn-g btn-sm" onclick="openGoalModal()">🎯 Goals</button>
        <div class="notif-wrap">
          <div class="notif-bell" onclick="toggleNotif()" id="nBell">🔔<div class="notif-badge" id="nBadge" style="display:none">0</div></div>
          <div class="notif-panel" id="nPanel">
            <div class="notif-head">Notifications</div>
            <div id="nItems"></div>
          </div>
        </div>
        <div class="pill pill-clock" id="liveClock">—</div>
      </div>
    </header>

    <!-- HOME -->
    <div class="tab-content act" id="tab-home">
      <div class="bento">
        <div class="card g c4 ga- shim">
          <div class="lbl"><span>🏅</span> Wellness Score</div>
          <div class="score-ring">
            <svg viewBox="0 0 155 155" width="155" height="155">
              <defs><linearGradient id="sg" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" stop-color="#9b8dff"/><stop offset="100%" stop-color="#00e5c0"/></linearGradient></defs>
              <circle class="st-track" cx="77.5" cy="77.5" r="63"/><circle class="sf" id="scoreArc" cx="77.5" cy="77.5" r="63" stroke-dasharray="396" stroke-dashoffset="396"/>
            </svg>
            <div class="score-inner"><div class="sn" id="scoreNum">–</div><div class="sl" id="scoreLvl">–</div></div>
          </div>
          <div class="sparkline-wrap"><svg class="spark-svg" id="sparkSvg" viewBox="0 0 200 44" preserveAspectRatio="none"><defs><linearGradient id="spGrad" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="#7c6dff" stop-opacity=".5"/><stop offset="100%" stop-color="#00e5c0"/></linearGradient></defs></svg></div>
          <div class="tstats">
            <div class="tstat"><div class="v" id="focusSt">0</div><div class="l">Sessions</div></div>
            <div class="tstat"><div class="v" id="chalSt">0</div><div class="l">Challenges</div></div>
            <div class="tstat"><div class="v" id="brthSt">0</div><div class="l">Breathwork</div></div>
          </div>
        </div>
        <div class="card g c8" style="background:linear-gradient(135deg,rgba(124,109,255,.09),rgba(0,229,192,.04));display:flex;flex-direction:column;justify-content:center">
          <div class="lbl"><span>✦</span> Daily Wisdom</div>
          <div class="qbody" id="qText">"Loading…"</div>
          <div class="qattr" id="qAuth">Zenith</div>
          <div style="margin-top:22px"><button class="btn btn-g btn-sm" onclick="newQuote()">↻ Refresh Insight</button></div>
        </div>
        <div class="card g c4">
          <div class="lbl"><span>📱</span> Screen Time Today</div>
          <div class="st-big" id="stBig">–h –m</div>
          <div style="font-size:13px;color:var(--mu)" id="stGoalLine">Goal: –h</div>
          <div class="prog-t"><div class="prog-f" id="stBar" style="width:0%;background:linear-gradient(90deg,var(--a2),var(--err))"></div></div>
          <div class="prog-tks"><span>0h</span><span id="stGoalTk">3h</span><span>8h</span></div>
          <div id="stChip" style="margin-top:13px"></div>
        </div>
        <div class="card g c8">
          <div class="lbl"><span>⚡</span> Quick Actions</div>
          <div class="act-g">
            <button class="act-b" onclick="actDND()"><div class="ai">🔕</div><div class="al">Do Not Disturb</div></button>
            <button class="act-b" onclick="actGray()" id="grayB"><div class="ai">🐼</div><div class="al">Grayscale</div></button>
            <button class="act-b" onclick="actDetox()"><div class="ai">📵</div><div class="al">Social Detox</div></button>
            <button class="act-b" onclick="actStretch()"><div class="ai">🤸</div><div class="al">Stretch Break</div></button>
            <button class="act-b" onclick="navToBtn('tab-focus')"><div class="ai">☕</div><div class="al">Take a Break</div></button>
            <button class="act-b" onclick="openGoalModal()"><div class="ai">🎯</div><div class="al">Edit Goals</div></button>
            <button class="act-b" onclick="navToBtn('tab-yoga')"><div class="ai">🧘</div><div class="al">Quick Yoga</div></button>
            <button class="act-b" onclick="actNight()" id="nightB"><div class="ai">🌙</div><div class="al">Night Mode</div></button>
          </div>
        </div>
      </div>
    </div>

    <!-- FOCUS -->
    <div class="tab-content" id="tab-focus">
      <div class="bento">
        <div class="card g c6">
          <div class="lbl"><span>🎯</span> Deep Focus Timer</div>
          <div class="mp-row">
            <div class="mp act" onclick="setMode(this,25,'Focus')">25m Block</div>
            <div class="mp" onclick="setMode(this,50,'Deep Work')">50m Deep</div>
            <div class="mp" onclick="setMode(this,5,'Break')">5m Break</div>
            <div class="mp" onclick="setMode(this,15,'Long Break')">15m Break</div>
          </div>
          <div class="timer-face">
            <div class="tnum" id="timerDisp">25:00</div>
            <div style="font-size:12px;color:var(--mu);letter-spacing:1.5px;text-transform:uppercase;margin-top:7px" id="timerStat">Ready · Click Start</div>
          </div>
          <div class="tiny-p"><div class="tiny-pf" id="tProg" style="width:0%"></div></div>
          <div style="text-align:center;font-size:12px;color:var(--mu);margin-bottom:11px" id="timerSub">Sessions today: 0</div>
          <div style="display:flex;gap:10px;justify-content:center">
            <button class="btn btn-p" id="timerBtn" onclick="toggleTimer()">▶ Start Focus</button>
            <button class="btn btn-g" onclick="resetTimer()">↺ Reset</button>
            <button class="btn btn-g" id="sndBtn" onclick="cycleSnd()" title="Ambient Sound">🔇 Sound</button>
          </div>
          <div class="sound-opts" id="sndOpts">
            <div class="sound-btn act" data-snd="none" onclick="setSnd('none',this)">None</div>
            <div class="sound-btn" data-snd="white" onclick="setSnd('white',this)">White Noise</div>
            <div class="sound-btn" data-snd="rain" onclick="setSnd('rain',this)">Rain</div>
            <div class="sound-btn" data-snd="binaural" onclick="setSnd('binaural',this)">Binaural</div>
          </div>
        </div>
        <div class="card g c6 gb-">
          <div class="lbl"><span>🌿</span> Guided Breathing</div>
          <div class="b-modes">
            <div class="bm act" onclick="setBreathMode('478',this)">4-7-8 Relax</div>
            <div class="bm" onclick="setBreathMode('box',this)">Box (4×4)</div>
            <div class="bm" onclick="setBreathMode('22',this)">2-2 Calm</div>
          </div>
          <div class="breath-sc">
            <div class="breath-ring" id="bRing" onclick="toggleBreath()">
              <div class="br-inner" id="bLabel">Tap to<br>Begin</div>
            </div>
            <div class="breath-phase" id="bPhase">Inhale 4 · Hold 7 · Exhale 8</div>
            <div class="breath-cyc" id="bCyc">0 cycles</div>
          </div>
          <div style="display:flex;gap:10px;justify-content:center;margin-top:12px">
            <button class="btn btn-t" id="bBtn" onclick="toggleBreath()">▶ Start Flow</button>
            <button class="btn btn-g" onclick="resetBreath()">↺ Reset</button>
          </div>
        </div>
        <div class="card g c6">
          <div class="lbl"><span>🧠</span> Mindfulness Today</div>
          <div style="display:flex;align-items:center;gap:18px;margin-top:8px">
            <div style="font-family:var(--f2);font-size:52px;font-weight:800;color:var(--a2);line-height:1" id="mindMins">15</div>
            <div><div style="font-size:14px;font-weight:600">minutes mindful</div><div style="font-size:13px;color:var(--mu);margin-top:4px" id="mindSub">2 breathwork sessions</div></div>
          </div>
          <div class="prog-t" style="margin-top:18px"><div class="prog-f" id="mindBar" style="width:0%;background:linear-gradient(90deg,var(--a),var(--a2))"></div></div>
          <div style="font-size:12px;color:var(--mu);margin-top:5px">Daily Goal: 30 minutes</div>
        </div>
        <div class="card g c6" style="border-color:rgba(255,107,157,.18);background:linear-gradient(135deg,rgba(255,107,157,.06),rgba(255,179,71,.03))">
          <div class="lbl"><span>💡</span> Smart Detox Tip</div>
          <div style="font-size:17px;line-height:1.72;margin-top:10px" id="tipText">Loading…</div>
          <button class="btn btn-g btn-sm" style="margin-top:18px" onclick="refreshTip()">↻ Get Another Tip</button>
        </div>
      </div>
    </div>

    <!-- INSIGHTS -->
    <div class="tab-content" id="tab-insights">
      <div class="bento">
        <div class="card g c8">
          <div class="lbl"><span>📊</span> Weekly Perspective</div>
          <div class="wleg">
            <div class="wl"><span class="wlc" style="background:var(--err)"></span>Screen Time (h)</div>
            <div class="wl"><span class="wlc" style="background:var(--a)"></span>Focus Time (h)</div>
            <div class="wl"><span class="wlc" style="background:var(--a2)"></span>Goal Target</div>
          </div>
          <div class="chat-w" style="height:260px"><canvas id="weeklyChart"></canvas></div>
        </div>
        <div class="card g c4">
          <div class="lbl"><span>🥗</span> Digital Diet Fit</div>
          <div class="chat-w" style="height:220px"><canvas id="radarChart"></canvas></div>
          <div style="display:flex;gap:14px;font-size:12px;color:var(--mu);margin-top:12px;justify-content:center">
            <span style="display:flex;align-items:center;gap:5px"><span style="width:9px;height:9px;border-radius:50%;background:var(--a);display:inline-block"></span>Current</span>
            <span style="display:flex;align-items:center;gap:5px"><span style="width:9px;height:9px;border-radius:50%;background:var(--a2);display:inline-block"></span>Ideal</span>
          </div>
        </div>
        <div class="card g c8">
          <div class="lbl"><span>🗓️</span> Consistency Heatmap (Last 35 Days)</div>
          <div style="display:flex;gap:8px;align-items:center;font-size:12px;color:var(--mu);margin-bottom:8px;flex-wrap:wrap">
            <span>Low Focus</span>
            <span style="width:13px;height:13px;border-radius:4px;background:rgba(255,255,255,.06);display:inline-block"></span>
            <span style="width:13px;height:13px;border-radius:4px;background:rgba(0,229,192,.22);display:inline-block"></span>
            <span style="width:13px;height:13px;border-radius:4px;background:rgba(0,229,192,.52);display:inline-block"></span>
            <span style="width:13px;height:13px;border-radius:4px;background:rgba(0,229,192,.88);display:inline-block"></span>
            <span>Deep Focus</span>
          </div>
          <div class="hm-grid" id="hmGrid"></div>
        </div>
        <div class="card g c4">
          <div class="lbl"><span>📲</span> App Usage Breakdown</div>
          <div class="chat-w" style="height:150px"><canvas id="usageChart"></canvas></div>
          <div class="ul" id="usageList"></div>
        </div>
      </div>
    </div>

    <!-- LIFE & HABITS -->
    <div class="tab-content" id="tab-life">
      <div class="bento">
        <div class="card g c6">
          <div class="lbl"><span>✅</span> Daily Habits <span style="margin-left:auto;font-size:12px;color:var(--a2)" id="habScore">0/5</span></div>
          <div class="hab-list" id="habList"></div>
        </div>
        <div class="card g c6">
          <div class="lbl"><span>💤</span> Core Vitals</div>
          <div class="sw-row">
            <div class="sw-box">
              <div class="swl">Sleep Log</div>
              <div class="sw-big" id="sleepBig">7.2h</div>
              <div id="sleepChip"></div>
              <input type="range" id="sleepSlider" min="3" max="12" step="0.5" value="7.2" oninput="updateSleepUI(parseFloat(this.value));debounceSleep(parseFloat(this.value))">
            </div>
            <div class="sw-box">
              <div class="swl">Hydration</div>
              <div class="sw-big" id="waterBig">5/8</div>
              <div class="wdots" id="wDots"></div>
              <button class="btn btn-t btn-sm" style="margin-top:14px;width:100%" onclick="addWater()">+ Drink Glass</button>
            </div>
          </div>
        </div>
        <div class="card g c6" style="border-color:rgba(255,179,71,.15);background:linear-gradient(135deg,rgba(255,179,71,.05),rgba(255,107,157,.03))">
          <div class="lbl"><span>📓</span> Reflection Journal</div>
          <textarea class="j-input" id="jInput" placeholder="What are you grateful for today?…" maxlength="300"></textarea>
          <button class="btn btn-p btn-sm" style="margin-top:11px;width:100%" onclick="saveJournal()">Save Entry ✦</button>
          <div class="journal-list" id="jList"></div>
        </div>
        <div class="card g c6">
          <div class="lbl"><span>🎭</span> Mood Check-In</div>
          <div class="mood-grid">
            <div class="mb" onclick="logMood('amazing',this)"><div class="me">🤩</div><div class="ml">Amazing</div></div>
            <div class="mb" onclick="logMood('good',this)"><div class="me">😊</div><div class="ml">Good</div></div>
            <div class="mb" onclick="logMood('okay',this)"><div class="me">😐</div><div class="ml">Okay</div></div>
            <div class="mb" onclick="logMood('tired',this)"><div class="me">😴</div><div class="ml">Tired</div></div>
            <div class="mb" onclick="logMood('stressed',this)"><div class="me">😤</div><div class="ml">Stressed</div></div>
          </div>
          <div style="font-size:12px;font-weight:600;margin-top:18px;color:var(--mu)">Recent Logs:</div>
          <div class="mood-hist" id="mHist"></div>
        </div>
      </div>
    </div>

    <!-- YOGA -->
    <div class="tab-content" id="tab-yoga">
      <div id="yogaCompleteBanner" class="yoga-complete-banner">
        <div style="font-size:32px;margin-bottom:8px">🧘‍♀️</div>
        <div style="font-family:var(--f2);font-size:20px;font-weight:700;margin-bottom:6px">Yoga Session Complete!</div>
        <div style="color:var(--mu);font-size:14px">Amazing work. +35 XP earned. Your body thanks you 🙏</div>
      </div>
      <div class="body-filter-bar" id="bodyFilterBar">
        <button class="bfb act" data-filter="all" onclick="filterYoga('all',this)">All Poses</button>
        <button class="bfb" data-filter="neck" onclick="filterYoga('neck',this)">Neck &amp; Shoulders</button>
        <button class="bfb" data-filter="back" onclick="filterYoga('back',this)">Back &amp; Spine</button>
        <button class="bfb" data-filter="hip" onclick="filterYoga('hip',this)">Hips &amp; Legs</button>
        <button class="bfb" data-filter="core" onclick="filterYoga('core',this)">Core</button>
        <button class="bfb" data-filter="full" onclick="filterYoga('full',this)">Full Body</button>
      </div>
      <div class="yoga-grid" id="yogaGrid"></div>
    </div>

    <!-- HYDRATION CORNER -->
    <div class="tab-content" id="tab-hydration">
      <div class="bento">
        <div class="card g c6" style="background:linear-gradient(135deg,rgba(0,229,192,.06),rgba(124,109,255,.04))">
          <div class="lbl"><span>💧</span> Hydration Corner</div>
          <div class="hydro-hero">
            <div class="hydro-vessel">
              <svg viewBox="0 0 90 150" xmlns="http://www.w3.org/2000/svg">
                <defs>
                  <linearGradient id="bottleGrad" x1="0" y1="0" x2="1" y2="0">
                    <stop offset="0%" stop-color="rgba(0,229,192,0.15)"/>
                    <stop offset="100%" stop-color="rgba(124,109,255,0.1)"/>
                  </linearGradient>
                  <clipPath id="waterClip"><rect x="10" y="20" width="70" height="122" rx="8"/></clipPath>
                </defs>
                <!-- bottle outline -->
                <path d="M 32 10 L 32 22 Q 10 28 10 44 L 10 134 Q 10 144 20 144 L 70 144 Q 80 144 80 134 L 80 44 Q 80 28 58 22 L 58 10 Z" fill="url(#bottleGrad)" stroke="rgba(0,229,192,0.5)" stroke-width="1.5"/>
                <!-- cap -->
                <rect x="30" y="4" width="30" height="12" rx="4" fill="rgba(0,229,192,0.3)" stroke="rgba(0,229,192,0.6)" stroke-width="1"/>
                <!-- water fill -->
                <g clip-path="url(#waterClip)">
                  <rect id="waterFill" x="10" y="90" width="70" height="56" fill="rgba(0,229,192,0.35)" rx="2"/>
                  <path id="waveTop" d="M 10 90 Q 22 84 45 90 Q 68 96 80 90 L 80 96 L 10 96 Z" fill="rgba(0,229,192,0.55)" class="hydro-wave"/>
                </g>
                <!-- level markers -->
                <text x="84" y="52" fill="rgba(232,234,246,0.3)" font-size="8" font-family="Inter">100%</text>
                <text x="84" y="88" fill="rgba(232,234,246,0.3)" font-size="8" font-family="Inter">50%</text>
                <text x="84" y="130" fill="rgba(232,234,246,0.3)" font-size="8" font-family="Inter">0%</text>
                <line x1="80" y1="50" x2="83" y2="50" stroke="rgba(232,234,246,0.2)" stroke-width="1"/>
                <line x1="80" y1="88" x2="83" y2="88" stroke="rgba(232,234,246,0.2)" stroke-width="1"/>
              </svg>
            </div>
            <div style="flex:1">
              <div style="font-family:var(--f2);font-size:48px;font-weight:800;color:var(--a2);line-height:1" id="hydGlasses">5</div>
              <div style="font-size:14px;color:var(--mu);margin-top:4px">of <span id="hydGoal">8</span> glasses today</div>
              <div style="margin-top:12px">
                <div class="prog-t" style="height:8px"><div class="prog-f" id="hydBar" style="width:62.5%;background:linear-gradient(90deg,var(--a),var(--a2))"></div></div>
              </div>
              <div style="font-size:13px;color:var(--mu);margin-top:6px" id="hydStatus">Keep going! 3 more glasses to reach your goal.</div>
            </div>
          </div>
          <div class="intake-buttons">
            <button class="intake-btn" onclick="logIntake(150,'☕ Espresso')">☕ Espresso<br><span style="font-size:11px;opacity:.7">150ml</span></button>
            <button class="intake-btn" onclick="logIntake(250,'💧 Small Glass')">💧 Small<br><span style="font-size:11px;opacity:.7">250ml</span></button>
            <button class="intake-btn" onclick="logIntake(400,'🥤 Large Glass')">🥤 Large<br><span style="font-size:11px;opacity:.7">400ml</span></button>
            <button class="intake-btn" onclick="logIntake(500,'🍶 Bottle')">🍶 Bottle<br><span style="font-size:11px;opacity:.7">500ml</span></button>
          </div>
        </div>

        <div class="card g c6">
          <div class="lbl"><span>📈</span> Daily Hydration Stats</div>
          <div class="hydro-stats-grid">
            <div class="hydro-stat">
              <div class="hydro-stat-v" id="hydTotalMl">1250</div>
              <div class="hydro-stat-l">ml consumed</div>
            </div>
            <div class="hydro-stat">
              <div class="hydro-stat-v" id="hydPercent">62%</div>
              <div class="hydro-stat-l">of daily goal</div>
            </div>
            <div class="hydro-stat">
              <div class="hydro-stat-v" id="hydStreak">5</div>
              <div class="hydro-stat-l">day streak 🔥</div>
            </div>
            <div class="hydro-stat">
              <div class="hydro-stat-v" id="hydNext">45m</div>
              <div class="hydro-stat-l">next reminder</div>
            </div>
          </div>
          <div class="chat-w" style="height:170px;margin-top:18px"><canvas id="hydChart"></canvas></div>
        </div>

        <div class="card g c6">
          <div class="lbl"><span>🕐</span> Intake Log</div>
          <div class="hydro-log" id="hydLog">
            <div class="hydro-log-items" id="hydLogItems">
              <div style="font-size:13px;color:var(--mu);text-align:center;padding:20px">No entries yet. Start drinking!</div>
            </div>
          </div>
        </div>

        <div class="card g c6">
          <div class="lbl"><span>⏰</span> Smart Reminders</div>
          <div class="hydro-reminder-row">
            <div class="hydro-reminder-icon">🔔</div>
            <div class="hydro-reminder-text">
              <div style="font-weight:600;font-size:14px">Every 45 minutes</div>
              <div style="font-size:12px;color:var(--mu);margin-top:2px">Gentle nudge to drink water</div>
            </div>
            <label class="hydro-reminder-toggle">
              <input type="checkbox" id="remToggle" onchange="toggleReminder(this.checked)" checked>
              <span class="hrt-slider"></span>
            </label>
          </div>
          <div class="hydro-reminder-row" style="margin-top:10px">
            <div class="hydro-reminder-icon">🌅</div>
            <div class="hydro-reminder-text">
              <div style="font-weight:600;font-size:14px">Morning kickstart</div>
              <div style="font-size:12px;color:var(--mu);margin-top:2px">Drink a glass right after waking up</div>
            </div>
            <label class="hydro-reminder-toggle">
              <input type="checkbox" id="morningToggle" onchange="toast('🌅','Morning water reminder '+( this.checked ?'on':'off'))" checked>
              <span class="hrt-slider"></span>
            </label>
          </div>
          <div class="hydro-reminder-row" style="margin-top:10px">
            <div class="hydro-reminder-icon">🌙</div>
            <div class="hydro-reminder-text">
              <div style="font-weight:600;font-size:14px">Evening checkpoint</div>
              <div style="font-size:12px;color:var(--mu);margin-top:2px">Ensure you hit 80%+ before bed</div>
            </div>
            <label class="hydro-reminder-toggle">
              <input type="checkbox" id="eveningToggle" onchange="toast('🌙','Evening reminder '+( this.checked ?'on':'off'))" checked>
              <span class="hrt-slider"></span>
            </label>
          </div>
          <div style="margin-top:20px;padding:16px;background:rgba(0,229,192,.06);border:1px solid rgba(0,229,192,.18);border-radius:14px">
            <div style="font-size:13px;font-weight:600;margin-bottom:8px">💡 Hydration Tips</div>
            <div style="font-size:12px;color:var(--mu);line-height:1.7" id="hydTip">Loading tip…</div>
          </div>
        </div>
      </div>
    </div>

    <!-- PROGRESS / JOURNEY -->
    <div class="tab-content" id="tab-progress">
      <div class="bento">
        <div class="card g c6">
          <div class="lbl"><span>🏆</span> Daily Quests <span style="margin-left:auto;font-size:11px;color:var(--mu)">Tap to complete</span></div>
          <div class="ch-list" id="chalList"></div>
        </div>
        <div class="card g c6">
          <div class="lbl"><span>🎖️</span> Trophy Room <span style="margin-left:auto;font-size:13px;color:var(--a)" id="achCount">0/12 unlocked</span></div>
          <div class="ach-grid" id="achGrid"></div>
        </div>
      </div>
    </div>

    <!-- AI COACH -->
    <div class="tab-content" id="tab-ai">
      <div class="bento">
        <div class="card g c8">
          <div class="lbl"><span>🤖</span> Zenith AI Coach <span style="margin-left:auto;font-size:11px;color:var(--mu)">Powered by Grok</span></div>
          <div id="aiChat" style="height:400px;overflow-y:auto;padding:10px;display:flex;flex-direction:column;gap:12px;margin-bottom:15px;background:rgba(0,0,0,0.2);border-radius:12px">
            <div style="background:rgba(255,255,255,0.05);padding:10px 14px;border-radius:12px;max-width:85%;align-self:flex-start;font-size:13.5px">Hello! I'm your Zenith AI Coach. Ready for a digital detox analysis?</div>
          </div>
          <div style="display:flex;gap:10px">
            <input type="text" id="aiInp" placeholder="Ask your coach anything..." style="flex:1;background:rgba(255,255,255,0.05);border:1px solid var(--b1);padding:12px 16px;border-radius:10px;color:#fff;font-size:14px" onkeyup="if(event.key==='Enter')askAI()">
            <button class="btn btn-p" onclick="askAI()">Send</button>
          </div>
        </div>
        <div class="card g c4">
          <div class="lbl"><span>🧠</span> AI Analysis</div>
          <p style="font-size:13px;color:var(--mu);line-height:1.6;margin-bottom:15px">Get a comprehensive clinical analysis of your wellness metrics from the last 24 hours.</p>
          <button class="btn btn-g" style="width:100%" onclick="analyzeAI()">Run Analysis</button>
          <div id="anaRes" style="margin-top:20px;font-size:13px;color:#fff;line-height:1.5;padding:12px;border-left:2px solid var(--a);background:rgba(124,109,255,0.05);display:none"></div>
        </div>
      </div>
    </div>

  </main>
</div>

<script>
// ═══════════════════════════════════════════════════════════
//  NAVIGATION
// ═══════════════════════════════════════════════════════════
const TAB_TITLES = {
  'tab-home':'Home Dashboard','tab-focus':'Focus & Breathe',
  'tab-insights':'Insights','tab-life':'Life & Habits',
  'tab-yoga':'Yoga & Movement','tab-hydration':'Hydration Corner',
  'tab-progress':'Journey & Trophies','tab-ai':'Zenith AI Coach'
};
function navTo(btnEl){
  const tid = btnEl.getAttribute('data-tab');
  document.querySelectorAll('.nb').forEach(b=>b.classList.remove('act'));
  btnEl.classList.add('act');
  document.querySelectorAll('.tab-content').forEach(t=>t.classList.remove('act'));
  document.getElementById(tid).classList.add('act');
  document.getElementById('hdrTitle').textContent = TAB_TITLES[tid]||tid;
  if(tid==='tab-insights') resizeCharts();
  if(tid==='tab-yoga') renderYoga();
  if(tid==='tab-hydration') refreshHydration();
  if(tid==='tab-ai') scrollChat();
  window.scrollTo({top:0,behavior:'smooth'});
}
function scrollChat(){ const c=document.getElementById('aiChat'); c.scrollTop=c.scrollHeight; }

async function askAI(){
  const inp=document.getElementById('aiInp');
  const msg=inp.value.trim();
  if(!msg)return;
  inp.value='';
  addAI('user', msg);
  const loading = addAI('ai', 'Thinking...');
  try {
    const res=await fetch('/api/ai_coach',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:msg,mode:'chat'})});
    const data=await res.json();
    loading.textContent = data.reply;
    scrollChat();
  } catch(e) { loading.textContent = 'Error connecting to AI.'; }
}

async function analyzeAI(){
  const btn=event.target; btn.disabled=true; btn.textContent='Analyzing...';
  const resBox=document.getElementById('anaRes'); resBox.style.display='block'; resBox.textContent='Gathering metrics and processing...';
  try {
    const res=await fetch('/api/ai_coach',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({mode:'analysis'})});
    const data=await res.json();
    resBox.textContent = data.reply;
  } catch(e) { resBox.textContent = 'Analysis failed.'; }
  btn.disabled=false; btn.textContent='Run Analysis';
}

function addAI(role, txt){
  const chat=document.getElementById('aiChat');
  const div=document.createElement('div');
  div.className = role==='user'?'chat-u':'chat-a';
  div.style = role==='user'?'background:var(--a);padding:10px 14px;border-radius:12px;max-width:85%;align-self:flex-end;font-size:13.5px;color:#fff':'background:rgba(255,255,255,0.08);padding:10px 14px;border-radius:12px;max-width:85%;align-self:flex-start;font-size:13.5px;border:1px solid var(--b1)';
  div.textContent = txt;
  chat.appendChild(div);
  scrollChat();
  return div;
}
function navToBtn(tid){ const b=document.querySelector(`.nb[data-tab="${tid}"]`);if(b)navTo(b); }
function logout(){
  if(confirm('Are you sure you want to logout?')){
    location.reload();
  }
}
let chartInited=false;
function resizeCharts(){ if(!chartInited){initCharts();chartInited=true;} else Object.values(Chart.instances).forEach(c=>c.resize()); }

// ═══════════════════════════════════════════════════════════
//  STAR CANVAS
// ═══════════════════════════════════════════════════════════
(()=>{
  const c=document.getElementById('stars'),ctx=c.getContext('2d');
  let W,H,stars=[];
  const sz=()=>{W=c.width=window.innerWidth;H=c.height=window.innerHeight;};
  sz();addEventListener('resize',sz);
  for(let i=0;i<220;i++) stars.push({x:Math.random()*1e4,y:Math.random()*1e4,r:Math.random()*1.4+.2,a:Math.random(),da:(Math.random()*.008+.002)*(Math.random()<.5?1:-1)});
  (function draw(){ctx.clearRect(0,0,W,H);stars.forEach(s=>{s.a+=s.da;if(s.a>1||s.a<0)s.da*=-1;ctx.globalAlpha=Math.max(0,Math.min(1,s.a))*.7;ctx.fillStyle='#fff';ctx.beginPath();ctx.arc(s.x%W,s.y%H,s.r,0,Math.PI*2);ctx.fill()});requestAnimationFrame(draw);})();
})();

// ═══════════════════════════════════════════════════════════
//  UTILS
// ═══════════════════════════════════════════════════════════
const fmt=n=>n<10?'0'+n:''+n;
let toastTimer;
function toast(icon,msg,color='var(--a2)'){
  document.getElementById('tIcon').textContent=icon;
  document.getElementById('tMsg').textContent=msg;
  const t=document.getElementById('toast');
  t.style.borderColor=color;t.classList.add('show');
  clearTimeout(toastTimer);toastTimer=setTimeout(()=>t.classList.remove('show'),3300);
}
let activeUser = "Guest";

async function handleLogin() {
  const u = document.getElementById('authUsername').value.trim();
  const p = document.getElementById('authPassword').value.trim();
  if(!u || !p) return toast('⚠️', 'Please enter username and password', 'var(--err)');
  
  try {
    const res = await fetch('/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: u, password: p })
    });
    const d = await res.json();
    if(res.ok && d.status === 'ok') {
      activeUser = d.name;
      document.getElementById('authOverlay').style.opacity = '0';
      setTimeout(() => document.getElementById('authOverlay').style.display = 'none', 600);
      toast('✅', `Access Granted: ${d.name}`, 'var(--tx)');
      const audio = new Audio('https://github.com/interactive-learning-tools/audio/raw/main/success-chime.mp3');
      audio.volume = 0.5;
      audio.play().catch(e => console.log('Audio overlap'));
      await refreshState();
    } else {
      toast('🚫', 'Invalid credentials', 'var(--err)');
      document.getElementById('authPassword').value = '';
    }
  } catch(e){ console.error(e); }
}

function confetti(x,y){
  const cols=['#9b8dff','#00e5c0','#ff6b9d','#ffb347','#4cde80','#fff','#7c6dff'];
  for(let i=0;i<72;i++){
    const p=document.createElement('div');p.className='cf';
    p.style.cssText=`left:${x+Math.random()*200-100}px;top:${y-10}px;background:${cols[i%cols.length]};border-radius:${Math.random()<.4?'50%':'2px'};animation-duration:${2.2+Math.random()*1.8}s;animation-delay:${Math.random()*.5}s`;
    document.body.appendChild(p);setTimeout(()=>p.remove(),5000);
  }
}
const tickClock=()=>{const n=new Date();document.getElementById('liveClock').textContent=fmt(n.getHours())+':'+fmt(n.getMinutes());};
tickClock();setInterval(tickClock,15000);

// sparkline
function drawSparkline(data){
  const svg=document.getElementById('sparkSvg');if(!svg||!data.length)return;
  svg.innerHTML=`<defs><linearGradient id="spGrad" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="#7c6dff" stop-opacity=".6"/><stop offset="100%" stop-color="#00e5c0" stop-opacity=".9"/></linearGradient></defs>`;
  const W=200,H=44,min=Math.min(...data)-5,max=Math.max(...data)+5,rng=max-min||10;
  const pts=data.map((v,i)=>`${(i/(data.length-1))*W},${H-(((v-min)/rng)*H)}`);
  svg.innerHTML+=`<path d="M${pts.join('L')}L${W},${H}L0,${H}Z" fill="url(#spGrad)" opacity=".18"/>`;
  svg.innerHTML+=`<path d="M${pts.join('L')}" fill="none" stroke="url(#spGrad)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>`;
  const last=pts[pts.length-1].split(',');
  svg.innerHTML+=`<circle cx="${last[0]}" cy="${last[1]}" r="4" fill="#00e5c0"/>`;
}

// ═══════════════════════════════════════════════════════════
//  STATE
// ═══════════════════════════════════════════════════════════
let quoteCache=null,tipCache='';
async function refreshState(){
  try{
    const d=await(await fetch('/api/state')).json();
    if(d.user_name) {
      document.getElementById('hdrTitle').textContent = `Welcome, ${d.user_name}`;
    } else {
      document.getElementById('hdrTitle').textContent = `Home Dashboard`;
    }
    const circ=2*Math.PI*63;
    document.getElementById('scoreArc').style.strokeDashoffset=circ*(1-d.wellness_score/100);
    document.getElementById('scoreNum').textContent=d.wellness_score;
    document.getElementById('scoreLvl').textContent=d.score_level;
    document.getElementById('focusSt').textContent=d.focus_sessions_today;
    document.getElementById('chalSt').textContent=d.challenges_completed;
    document.getElementById('brthSt').textContent=d.breathing_sessions;
    document.getElementById('xpVal').textContent=d.total_xp+' XP';
    document.getElementById('lvlName').textContent=d.level_name;
    document.getElementById('streakVal').textContent=d.detox_streak;
    const st=d.screen_time_today,g=d.goal_screen_time;
    const h=Math.floor(st),m=Math.round((st%1)*60);
    document.getElementById('stBig').textContent=h+'h '+fmt(m)+'m';
    document.getElementById('stGoalLine').textContent='Daily Limit: '+g+'h';
    document.getElementById('stGoalTk').textContent=g+'h';
    document.getElementById('stBar').style.width=Math.min(100,(st/8)*100)+'%';
    document.getElementById('stChip').innerHTML=(st-g)>0?`<span class="chip cr">▲ ${+(st-g).toFixed(1)}h over goal</span>`:`<span class="chip cg">▼ ${+(g-st).toFixed(1)}h remaining</span>`;
    if(!quoteCache){quoteCache=d.quote;document.getElementById('qText').textContent='"'+d.quote.text+'"';document.getElementById('qAuth').textContent=d.quote.author;}
    if(!tipCache){tipCache=d.tip;document.getElementById('tipText').textContent=tipCache;}
    document.getElementById('mindMins').textContent=d.mindfulness_minutes;
    document.getElementById('mindSub').textContent=d.breathing_sessions+' breathwork session'+(d.breathing_sessions!==1?'s':'');
    document.getElementById('mindBar').style.width=Math.min(100,(d.mindfulness_minutes/30)*100)+'%';
    updateSleepUI(d.sleep_hours);updateWaterUI(d.water_glasses,8);
    const hDone=d.habits.filter(h=>h.done).length;
    document.getElementById('habScore').textContent=hDone+'/'+d.habits.length;
    document.getElementById('timerSub').textContent='Sessions today: '+d.focus_sessions_today;
    const badge=document.getElementById('nBadge');
    badge.style.display=d.unread_notifications>0?'flex':'none';badge.textContent=d.unread_notifications;
    drawSparkline(d.score_history);
    renderAchievements(d.achievements_unlocked);
  }catch(e){console.error(e);}
}
async function newQuote(){ const d=await(await fetch('/api/state')).json();quoteCache=d.quote;document.getElementById('qText').textContent='"'+d.quote.text+'"';document.getElementById('qAuth').textContent=d.quote.author; }
async function refreshTip(){ const d=await(await fetch('/api/state')).json();tipCache=d.tip;document.getElementById('tipText').textContent=tipCache; }

// ═══════════════════════════════════════════════════════════
//  ACHIEVEMENTS
// ═══════════════════════════════════════════════════════════
const ACHIEVEMENTS=[
  {id:'first_breath',icon:'🌬️',title:'First Breath',xp:25},{id:'streak_7',icon:'🔥',title:'Streak Master',xp:100},
  {id:'focus_5',icon:'🎯',title:'Focus Champ',xp:80},{id:'hydrated',icon:'💧',title:'Hydrated Hero',xp:40},
  {id:'sleep_champ',icon:'💤',title:'Sleep Champ',xp:50},{id:'challenge_3',icon:'🏆',title:'Challenger',xp:70},
  {id:'mood_log',icon:'🎭',title:'Mood Tracker',xp:30},{id:'social_detox',icon:'📵',title:'Detox Warrior',xp:90},
  {id:'zen_master',icon:'🧘',title:'Zen Master',xp:150},{id:'journaler',icon:'📓',title:'Journaler',xp:45},
  {id:'habit_5',icon:'✅',title:'Habit Hero',xp:120},{id:'mindful_30',icon:'🌿',title:'Mindful',xp:60}
];
let prevUnlocked=new Set();
function renderAchievements(unlocked){
  const grid=document.getElementById('achGrid');const ul=new Set(unlocked);grid.innerHTML='';let cnt=0;
  ACHIEVEMENTS.forEach(a=>{
    const on=ul.has(a.id);if(on)cnt++;
    const d=document.createElement('div');d.className='ach-item'+(on?' unlocked':'');
    if(on&&!prevUnlocked.has(a.id))d.classList.add('just-unlocked');
    d.innerHTML=`<div class="ach-icon">${a.icon}</div><div class="ach-name">${a.title}</div><div class="ach-xp">+${a.xp}</div>`;
    grid.appendChild(d);
    if(on&&!prevUnlocked.has(a.id))toast('🎖️','Achievement: '+a.title+'! +'+a.xp+' XP','#ffb347');
  });
  prevUnlocked=ul;document.getElementById('achCount').textContent=cnt+' / '+ACHIEVEMENTS.length+' unlocked';
}

// ═══════════════════════════════════════════════════════════
//  NOTIFICATIONS
// ═══════════════════════════════════════════════════════════
function toggleNotif(){ const p=document.getElementById('nPanel');p.classList.toggle('open');if(p.classList.contains('open'))loadNotifs(); }
async function loadNotifs(){
  const data=await(await fetch('/api/notifications')).json();const el=document.getElementById('nItems');el.innerHTML='';
  data.slice(0,8).forEach(n=>{ el.innerHTML+=`<div class="notif-item${n.unread?' unread':''}"><div class="ni-icon">${n.icon}</div><div><div class="ni-text">${n.text}</div><div class="ni-time">${n.time}</div></div></div>`; });
  document.getElementById('nBadge').style.display='none';
}
document.addEventListener('click',e=>{ if(!document.getElementById('nPanel').contains(e.target)&&!document.getElementById('nBell').contains(e.target)) document.getElementById('nPanel').classList.remove('open'); });

// ═══════════════════════════════════════════════════════════
//  GOALS
// ═══════════════════════════════════════════════════════════
function openGoalModal(){document.getElementById('goalModal').classList.add('open');}
function closeGoalModal(){document.getElementById('goalModal').classList.remove('open');}
async function saveGoals(){
  const goals={screen_time:parseFloat(document.getElementById('g-st').value),focus_mins:parseInt(document.getElementById('g-fm').value),sleep:parseFloat(document.getElementById('g-sl').value),water:parseInt(document.getElementById('g-wa').value)};
  await fetch('/api/set_goal',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(goals)});
  closeGoalModal();toast('🎯','Goals saved! Stay consistent','var(--a)');await refreshState();
}

// ═══════════════════════════════════════════════════════════
//  CHARTS
// ═══════════════════════════════════════════════════════════
async function initCharts(){
  const dW=await(await fetch('/api/weekly')).json();
  new Chart(document.getElementById('weeklyChart').getContext('2d'),{
    type:'bar',data:{labels:dW.labels,datasets:[
      {label:'Screen',data:dW.screen,backgroundColor:'rgba(255,95,126,.5)',borderColor:'rgba(255,95,126,.85)',borderWidth:1.5,borderRadius:6,barPercentage:0.6},
      {label:'Focus',data:dW.focus,backgroundColor:'rgba(124,109,255,.5)',borderColor:'rgba(124,109,255,.85)',borderWidth:1.5,borderRadius:6,barPercentage:0.6},
      {label:'Goal',data:dW.goal,type:'line',fill:false,borderColor:'rgba(0,229,192,.75)',borderDash:[5,5],pointRadius:0,borderWidth:2,tension:0},
    ]},
    options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false},tooltip:{backgroundColor:'rgba(5,9,26,.97)',borderColor:'rgba(255,255,255,.12)',borderWidth:1,bodyColor:'#e8eaf6',titleColor:'#9b8dff',cornerRadius:12,padding:12}},scales:{x:{grid:{color:'rgba(255,255,255,.04)'},ticks:{color:'rgba(232,234,246,.4)',font:{size:11}}},y:{grid:{color:'rgba(255,255,255,.04)'},ticks:{color:'rgba(232,234,246,.4)',font:{size:11}},beginAtZero:true,max:12}}}
  });
  const dU=await(await fetch('/api/app_usage')).json();
  new Chart(document.getElementById('usageChart').getContext('2d'),{
    type:'doughnut',data:{labels:dU.map(d=>d.app),datasets:[{data:dU.map(d=>d.hours),backgroundColor:dU.map(d=>d.color+'bb'),borderColor:dU.map(d=>d.color),borderWidth:1.5,hoverOffset:10}]},
    options:{responsive:true,maintainAspectRatio:false,cutout:'72%',plugins:{legend:{display:false},tooltip:{backgroundColor:'rgba(5,9,26,.97)',borderColor:'rgba(255,255,255,.12)',borderWidth:1,bodyColor:'#e8eaf6',cornerRadius:12,padding:12,callbacks:{label:c=>' '+c.label+': '+c.parsed+'h'}}}}
  });
  const maxH=Math.max(...dU.map(d=>d.hours));
  const ul=document.getElementById('usageList');ul.innerHTML='';
  dU.forEach(d=>{ul.innerHTML+=`<div class="ur"><div class="udot" style="background:${d.color}"></div><div class="uname">${d.app}</div><div class="ubg"><div class="uf" style="width:0%;background:${d.color}bb" data-w="${(d.hours/maxH)*100}"></div></div><div class="uh">${d.hours}h</div></div>`;});
  setTimeout(()=>document.querySelectorAll('.uf').forEach(b=>b.style.width=b.dataset.w+'%'),350);
  const dR=await(await fetch('/api/digital_diet')).json();
  new Chart(document.getElementById('radarChart').getContext('2d'),{
    type:'radar',data:{labels:dR.labels,datasets:[
      {label:'Current',data:dR.current,backgroundColor:'rgba(124,109,255,.18)',borderColor:'rgba(124,109,255,.8)',borderWidth:2,pointBackgroundColor:'rgba(124,109,255,.9)',pointRadius:3},
      {label:'Ideal',data:dR.ideal,backgroundColor:'rgba(0,229,192,.08)',borderColor:'rgba(0,229,192,.7)',borderWidth:2,borderDash:[5,4],pointRadius:2,pointBackgroundColor:'rgba(0,229,192,.8)'},
    ]},
    options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false},tooltip:{backgroundColor:'rgba(5,9,26,.97)',borderColor:'rgba(255,255,255,.12)',borderWidth:1,bodyColor:'#e8eaf6',cornerRadius:12,padding:12}},scales:{r:{grid:{color:'rgba(255,255,255,.07)'},ticks:{display:false},pointLabels:{color:'rgba(232,234,246,.55)',font:{size:11}},angleLines:{color:'rgba(255,255,255,.06)'}}}}
  });
}

let hydChartInst=null;
function initHydChart(data){
  const ctx=document.getElementById('hydChart').getContext('2d');
  if(hydChartInst){hydChartInst.destroy();}
  const labels=['6am','8am','10am','12pm','2pm','4pm','6pm','8pm'];
  const vals=labels.map((_,i)=>i<data.glasses?Math.floor(Math.random()*2)+1:0);
  hydChartInst=new Chart(ctx,{
    type:'bar',data:{labels,datasets:[{data:vals,backgroundColor:'rgba(0,229,192,.35)',borderColor:'rgba(0,229,192,.7)',borderWidth:1.5,borderRadius:8,barPercentage:.7}]},
    options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false},tooltip:{backgroundColor:'rgba(5,9,26,.97)',borderColor:'rgba(255,255,255,.12)',borderWidth:1,bodyColor:'#e8eaf6',cornerRadius:12,padding:10}},scales:{x:{grid:{color:'rgba(255,255,255,.04)'},ticks:{color:'rgba(232,234,246,.4)',font:{size:10}}},y:{grid:{color:'rgba(255,255,255,.04)'},ticks:{color:'rgba(232,234,246,.4)',font:{size:10}},beginAtZero:true,max:4}}}
  });
}

// ═══════════════════════════════════════════════════════════
//  HEATMAP
// ═══════════════════════════════════════════════════════════
async function initHeatmap(){
  const data=await(await fetch('/api/heatmap')).json();
  const g=document.getElementById('hmGrid');g.innerHTML='';
  data.forEach(d=>{const c=document.createElement('div');c.className=`hm-cell hv${d.val}`;c.innerHTML=`<div class="hm-tip">${d.day}, ${d.date}</div>`;g.appendChild(c);});
}

// ═══════════════════════════════════════════════════════════
//  HABITS
// ═══════════════════════════════════════════════════════════
async function initHabits(){renderHabits(await(await fetch('/api/habits')).json());}
function renderHabits(habits){
  const el=document.getElementById('habList');el.innerHTML='';
  habits.forEach(h=>{
    const d=document.createElement('div');d.className='hab'+(h.done?' done':'');d.onclick=()=>toggleHabit(h.id,h.done);
    d.innerHTML=`<div class="hab-icon">${h.icon}</div><div class="hab-body"><div class="hab-name">${h.name}</div><div class="hab-str">🔥 ${h.streak}-day streak</div></div><div class="hab-check">${h.done?'✓':''}</div>`;
    el.appendChild(d);
  });
}
async function toggleHabit(id,was){
  const res=await(await fetch('/api/toggle_habit',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id})})).json();
  renderHabits(res.habits);document.getElementById('xpVal').textContent=res.xp+' XP';
  if(!was)toast('✅','Habit done! +20 XP','var(--a2)');
  await refreshState();
}

// ═══════════════════════════════════════════════════════════
//  CHALLENGES
// ═══════════════════════════════════════════════════════════
let doneCh=new Set();
async function initChallenges(){
  const data=await(await fetch('/api/challenges')).json();const el=document.getElementById('chalList');el.innerHTML='';
  data.forEach(c=>{
    const d=document.createElement('div');d.className='chi';d.id='ch-'+c.id;
    d.innerHTML=`<div class="chi-icon">${c.icon}</div><div class="chi-body"><div class="chi-title">${c.title}</div><div class="chi-desc">${c.desc}</div></div><div class="chi-xp">+${c.xp} XP</div><div class="chi-check"></div>`;
    d.onclick=e=>completeCh(c.id,c.xp,c.title,e);el.appendChild(d);
  });
}
async function completeCh(id,xp,title,e){
  if(doneCh.has(id))return;doneCh.add(id);
  const el=document.getElementById('ch-'+id);el.classList.add('done');el.querySelector('.chi-check').textContent='✓';confetti(e.clientX,e.clientY);
  const res=await(await fetch('/api/complete_challenge',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({xp})})).json();
  toast('🏆',`Quest: ${title}! +${xp} XP`,'#ffb347');await refreshState();
}

// ═══════════════════════════════════════════════════════════
//  MOOD
// ═══════════════════════════════════════════════════════════
async function logMood(mood,el){
  document.querySelectorAll('.mb').forEach(b=>b.classList.remove('sel'));el.classList.add('sel');
  const emj={amazing:'🤩',good:'😊',okay:'😐',tired:'😴',stressed:'😤'};
  const res=await(await fetch('/api/log_mood',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({mood})})).json();
  const h=document.getElementById('mHist');h.innerHTML='';
  res.mood_log.slice(-5).forEach(m=>{h.innerHTML+=`<span class="mood-tag">${emj[m.mood]||''} ${m.mood} · ${m.time}</span>`;});
  toast(emj[mood]||'','Mood logged!','var(--a)');await refreshState();
}

// ═══════════════════════════════════════════════════════════
//  FOCUS TIMER
// ═══════════════════════════════════════════════════════════
let tDur=1500,tRem=1500,tRun=false,tIv=null,tName='Focus';
let audioCtx=null,bgNode=null,bgGain=null,curSnd='none';
function setMode(el,mins,name){
  document.querySelectorAll('.mp').forEach(p=>p.classList.remove('act'));el.classList.add('act');
  tDur=mins*60;tRem=mins*60;tRun=false;tName=name;clearInterval(tIv);updateTimerUI();
  document.getElementById('timerBtn').textContent='▶ Start '+name;document.getElementById('timerStat').textContent='Ready · Click Start';document.getElementById('tProg').style.width='0%';
}
function updateTimerUI(){ const m=Math.floor(tRem/60),s=tRem%60;document.getElementById('timerDisp').textContent=fmt(m)+':'+fmt(s);document.getElementById('tProg').style.width=((tDur-tRem)/tDur*100)+'%'; }
async function toggleTimer(){
  if(tRun){clearInterval(tIv);tRun=false;document.getElementById('timerBtn').textContent='▶ Resume';document.getElementById('timerStat').textContent='Paused';}
  else{
    tRun=true;document.getElementById('timerBtn').innerHTML='⏸ Pause';document.getElementById('timerStat').textContent=tName+' · In Progress';
    tIv=setInterval(async()=>{
      tRem--;updateTimerUI();
      if(tRem<=0){
        clearInterval(tIv);tRun=false;document.getElementById('timerStat').textContent='Complete! 🎉';document.getElementById('timerBtn').textContent='▶ Start';playDing();toast('🎯',tName+' complete! Great work!','var(--a)');
        await fetch('/api/focus_complete',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({minutes:Math.round(tDur/60)})});
        tRem=tDur;updateTimerUI();await refreshState();
      }
    },1000);
  }
}
function resetTimer(){clearInterval(tIv);tRun=false;tRem=tDur;updateTimerUI();document.getElementById('timerBtn').textContent='▶ Start '+tName;document.getElementById('timerStat').textContent='Ready · Click Start';document.getElementById('tProg').style.width='0%';}

// AUDIO
function getACtx(){if(!audioCtx)audioCtx=new(window.AudioContext||window.webkitAudioContext)();return audioCtx;}
function stopBg(){if(bgNode){try{bgNode.stop()}catch(e){}bgNode=null;}}
function createWhiteNoise(ctx){
  const buf=ctx.createBuffer(1,ctx.sampleRate*2,ctx.sampleRate);const d=buf.getChannelData(0);
  let b0, b1, b2, b3, b4, b5, b6; b0=b1=b2=b3=b4=b5=b6=0.0;
  for(let i=0;i<d.length;i++){
    let w=Math.random()*2-1;
    b0=0.99886*b0+w*0.0555179; b1=0.99332*b1+w*0.0750759; b2=0.96900*b2+w*0.1538520;
    b3=0.86650*b3+w*0.3104856; b4=0.55000*b4+w*0.5329522; b5=-0.7616*b5-w*0.0168980;
    d[i]=(b0+b1+b2+b3+b4+b5+b6+w*0.5362)*0.04; b6=w*0.115926;
  }
  const s=ctx.createBufferSource();s.buffer=buf;s.loop=true;
  bgGain=ctx.createGain();bgGain.gain.value=0.6;s.connect(bgGain);bgGain.connect(ctx.destination);return s;
}
function createRain(ctx){
  const s=createWhiteNoise(ctx);
  const filter = ctx.createBiquadFilter(); filter.type = 'lowpass'; filter.frequency.value = 800; filter.Q.value = 0.5;
  s.disconnect(); s.connect(filter); filter.connect(bgGain);
  bgGain.gain.value=0.5; return s;
}
function createBinaural(ctx){
  const g=ctx.createGain();g.gain.value=0.15;g.connect(ctx.destination);
  const oL=ctx.createOscillator(),oR=ctx.createOscillator();
  oL.frequency.value=432; oR.frequency.value=436; // 4Hz delta wave for deep focus
  const pL=ctx.createStereoPanner(), pR=ctx.createStereoPanner();
  pL.pan.value=-1; pR.pan.value=1;
  oL.connect(pL); pL.connect(g); oR.connect(pR); pR.connect(g);
  oL.start(); oR.start(); bgGain=g; return {start:()=>null, stop:()=> {oL.stop();oR.stop();}};
}
function setSnd(type,el){
  document.querySelectorAll('.sound-btn').forEach(b=>b.classList.remove('act'));if(el)el.classList.add('act');stopBg();curSnd=type;
  if(type==='none'){document.getElementById('sndBtn').textContent='🔇 Sound';return;}
  try{const ctx=getACtx();if(type==='white')bgNode=createWhiteNoise(ctx);else if(type==='rain')bgNode=createRain(ctx);else if(type==='binaural')bgNode=createBinaural(ctx);bgNode.start();document.getElementById('sndBtn').textContent='🔊 '+type.charAt(0).toUpperCase()+type.slice(1);toast('🔊',type+' ambient active','var(--a2)');}catch(e){console.error(e);}
}
function cycleSnd(){const snds=['none','white','rain','binaural'];const next=snds[(snds.indexOf(curSnd)+1)%snds.length];const btn=document.querySelector(`.sound-btn[data-snd="${next}"]`);setSnd(next,btn);}
function playDing(){
  try{
    const ctx=getACtx();
    [440, 554.37, 659.25, 830.61].forEach((freq, i) => { // A Major 7th Chord
      const o=ctx.createOscillator(),g=ctx.createGain(); o.frequency.value=freq; o.type='sine';
      g.gain.setValueAtTime(0, ctx.currentTime);
      g.gain.linearRampToValueAtTime(0.15, ctx.currentTime + 0.05 + (i * 0.02));
      g.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 2.5);
      o.connect(g);g.connect(ctx.destination);o.start();o.stop(ctx.currentTime+2.5);
    });
  }catch(e){}
}

// BREATHING
let bRun=false,bTimer=null,bPhIdx=0,bCycs=0,bMode='478';
const B_MODES={'478':[{l:'Inhale',d:4000},{l:'Hold',d:7000},{l:'Exhale',d:8000},{l:'',d:500}],'box':[{l:'Inhale',d:4000},{l:'Hold',d:4000},{l:'Exhale',d:4000},{l:'Hold',d:4000}],'22':[{l:'Inhale',d:2000},{l:'Exhale',d:2000},{l:'',d:200}]};
const B_LABELS={'478':'Inhale 4 · Hold 7 · Exhale 8','box':'Box: 4 · 4 · 4 · 4','22':'Calm: 2 in · 2 out'};
function setBreathMode(m,el){document.querySelectorAll('.bm').forEach(b=>b.classList.remove('act'));el.classList.add('act');bMode=m;bRun&&stopBreath();bCycs=0;bPhIdx=0;document.getElementById('bPhase').textContent=B_LABELS[m];document.getElementById('bCyc').textContent='0 cycles';}
function toggleBreath(){bRun?stopBreath():startBreath();}
function startBreath(){bRun=true;document.getElementById('bRing').classList.add('go');document.getElementById('bBtn').textContent='⏸ Pause';runBPhase();}
function runBPhase(){if(!bRun)return;const phases=B_MODES[bMode],p=phases[bPhIdx];document.getElementById('bPhase').textContent=p.l||B_LABELS[bMode];document.getElementById('bLabel').innerHTML=p.l?`${p.l}<br><span style="font-size:12px;opacity:.8">${Math.round(p.d/1000)}s</span>`:'&nbsp;';bTimer=setTimeout(()=>{bPhIdx++;if(bPhIdx>=phases.length){bPhIdx=0;bCycs++;document.getElementById('bCyc').textContent=bCycs+' cycle'+(bCycs!==1?'s':'');if(bCycs%3===0){toast('🌿',bCycs+' cycles done!','var(--a2)');fetch('/api/breathing_done',{method:'POST'}).then(()=>refreshState());}}runBPhase();},p.d);}
function stopBreath(){bRun=false;clearTimeout(bTimer);document.getElementById('bRing').classList.remove('go');document.getElementById('bBtn').textContent='▶ Start Flow';document.getElementById('bPhase').textContent=B_LABELS[bMode];document.getElementById('bLabel').innerHTML='Tap to<br>Begin';}
function resetBreath(){stopBreath();bCycs=0;bPhIdx=0;document.getElementById('bCyc').textContent='0 cycles';}

// SLEEP / WATER
function updateSleepUI(h){document.getElementById('sleepBig').textContent=h+'h';document.getElementById('sleepSlider').value=h;const c=document.getElementById('sleepChip');c.innerHTML=h>=7&&h<=9?'<span class="chip cg">Optimal</span>':h<6?'<span class="chip cr">Too little</span>':'<span class="chip cw">Improve</span>';}
let sDebounce;function debounceSleep(v){clearTimeout(sDebounce);sDebounce=setTimeout(async()=>{await fetch('/api/log_sleep',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({hours:v})});toast('💤','Sleep logged','var(--a)');await refreshState();},700);}
function updateWaterUI(g,max=8){document.getElementById('waterBig').textContent=g+'/'+max;const d=document.getElementById('wDots');d.innerHTML='';for(let i=0;i<max;i++){const w=document.createElement('div');w.className='wd'+(i<g?' on':'');w.onclick=addWater;d.appendChild(w);}}
async function addWater(){const res=await(await fetch('/api/log_water',{method:'POST'})).json();updateWaterUI(res.glasses);toast('💧','Hydration logged!','var(--a2)');if(res.glasses===8)toast('🎉','Water goal reached! 💧','var(--a2)');}

// JOURNAL
async function loadJournal(){const data=await(await fetch('/api/journal')).json();renderJournal(data);}
function renderJournal(entries){const el=document.getElementById('jList');el.innerHTML='';if(!entries.length){el.innerHTML='<div style="font-size:12px;color:var(--mu);text-align:center;padding:10px">No entries yet.</div>';return;}entries.forEach(e=>{el.innerHTML+=`<div class="j-item"><div class="j-text">${e.text}</div><div class="j-time">${e.time}</div></div>`;});}
async function saveJournal(){const inp=document.getElementById('jInput');const txt=inp.value.trim();if(!txt)return;const res=await(await fetch('/api/journal',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text:txt})})).json();inp.value='';renderJournal(res.entries);document.getElementById('xpVal').textContent=res.xp+' XP';toast('📓','Reflection saved! +15 XP','var(--warn)');await refreshState();}

// ═══════════════════════════════════════════════════════════
//  YOGA SECTION
// ═══════════════════════════════════════════════════════════
const YOGA_DATA = [
  { id:'y1', body:'neck', title:"Neck Rolls", sub:"Release screen-time tension.", reps:"8 reps", duration:120, difficulty:"Beginner", tag:"Neck", img:"https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?auto=format&fit=crop&w=400&q=80" },
  { id:'y2', body:'neck', title:"Shoulder Shrugs", sub:"Melt trapezius tension.", reps:"12 reps", duration:90, difficulty:"Beginner", tag:"Neck", img:"https://images.unsplash.com/photo-1552196564-972b22ec30bb?auto=format&fit=crop&w=400&q=80" },
  { id:'y3', body:'back', title:"Cat-Cow Stretch", sub:"Spinal mobilization.", reps:"10 cycles", duration:180, difficulty:"Beginner", tag:"Back", img:"https://images.unsplash.com/photo-1566730623145-886ec0d8ae8a?auto=format&fit=crop&w=400&q=80" },
  { id:'y4', body:'back', title:"Child's Pose", sub:"Deeply restful stretch.", reps:"Hold 30s", duration:150, difficulty:"Beginner", tag:"Back", img:"https://images.unsplash.com/photo-1599447292180-45fd880c72f2?auto=format&fit=crop&w=400&q=80" },
  { id:'y5', body:'hip', title:"Butterfly Pose", sub:"Opens hips and groin.", reps:"Hold 45s", duration:120, difficulty:"Beginner", tag:"Hips", img:"https://images.unsplash.com/photo-1575052814086-f385e2e2ad1b?auto=format&fit=crop&w=400&q=80" },
  { id:'y6', body:'hip', title:"Low Lunge", sub:"Deep hip flexor stretch.", reps:"30s/side", duration:180, difficulty:"Intermediate", tag:"Hips", img:"https://images.unsplash.com/photo-1506126613408-eca07ce68773?auto=format&fit=crop&w=400&q=80" },
  { id:'y7', body:'core', title:"Plank Hold", sub:"Core endurance.", reps:"30-60s", duration:210, difficulty:"Intermediate", tag:"Core", img:"https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?auto=format&fit=crop&w=400&q=80" },
  { id:'y8', body:'core', title:"Boat Pose", sub:"Abdominal strengthener.", reps:"20s", duration:150, difficulty:"Advanced", tag:"Core", img:"https://images.unsplash.com/photo-1518310383802-640c2de311b2?auto=format&fit=crop&w=400&q=80" },
  { id:'y9', body:'full', title:"Sun Salutation", sub:"Classic warm-up flow.", reps:"6 rounds", duration:300, difficulty:"All Levels", tag:"Full Body", img:"https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?auto=format&fit=crop&w=400&q=80" },
  { id:'y10', body:'full', title:"Warrior II", sub:"Strength and focus.", reps:"Hold 30s", duration:240, difficulty:"Intermediate", tag:"Full Body", img:"https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?auto=format&fit=crop&w=400&q=80" },
  { id:'y11', body:'full', title:"Tree Pose", sub:"Balance and poise.", reps:"30s/side", duration:120, difficulty:"Beginner", tag:"Balance", img:"https://images.unsplash.com/photo-1506126613408-eca07ce68773?auto=format&fit=crop&w=400&q=80" },
  { id:'y12', body:'back', title:"Cobra Pose", sub:"Spinal extension.", reps:"Hold 30s", duration:120, difficulty:"Beginner", tag:"Back", img:"https://images.unsplash.com/photo-1593164841882-78d1f0565062?auto=format&fit=crop&w=400&q=80" },
  { id:'y13', body:'full', title:"Downward Dog", sub:"Full body stretch.", reps:"Hold 30s", duration:120, difficulty:"Beginner", tag:"Full Body", img:"https://images.unsplash.com/photo-1599447421416-3414500d18a5?auto=format&fit=crop&w=400&q=80" },
  { id:'y14', body:'full', title:"Triangle Pose", sub:"Side body lateral stretch.", reps:"30s/side", duration:180, difficulty:"Intermediate", tag:"Full Body", img:"https://images.unsplash.com/photo-1510894347713-fc3ad6cb0322?auto=format&fit=crop&w=400&q=80" },
  { id:'y15', body:'full', title:"Warrior I", sub:"Foundational strength.", reps:"Hold 30s", duration:180, difficulty:"Beginner", tag:"Full Body", img:"https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?auto=format&fit=crop&w=400&q=80" },
  { id:'y16', body:'full', title:"Bridge Pose", sub:"Glute and back opener.", reps:"Hold 30s", duration:120, difficulty:"Beginner", tag:"Back", img:"https://images.unsplash.com/photo-1599447421416-3414500d18a5?auto=format&fit=crop&w=400&q=80" },
  { id:'y17', body:'hip', title:"Pigeon Pose", sub:"Deep hip opener.", reps:"1m/side", duration:240, difficulty:"Advanced", tag:"Hips", img:"https://images.unsplash.com/photo-1575052814086-f385e2e2ad1b?auto=format&fit=crop&w=400&q=80" },
  { id:'y18', body:'core', title:"Side Plank", sub:"Oblique strength.", reps:"30s/side", duration:180, difficulty:"Intermediate", tag:"Core", img:"https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?auto=format&fit=crop&w=400&q=80" },
  { id:'y19', body:'full', title:"Corpse Pose", sub:"Ultimate restoration.", reps:"5-10 mins", duration:300, difficulty:"Beginner", tag:"Relax", img:"https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?auto=format&fit=crop&w=400&q=80" },
  { id:'y20', body:'full', title:"Mountain Pose", sub:"Posture and focus.", reps:"Hold 1m", duration:300, difficulty:"Beginner", tag:"Posture", img:"https://images.unsplash.com/photo-1506126613408-eca07ce68773?auto=format&fit=crop&w=400&q=80" },
  { id:'y21', body:'full', title:"Eagle Pose", sub:"Internal focus.", reps:"30s/side", duration:180, difficulty:"Intermediate", tag:"Balance", img:"https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?auto=format&fit=crop&w=400&q=80" },
  { id:'y22', body:'full', title:"Wheel Pose", sub:"Powerful backbend.", reps:"Hold 15s", duration:120, difficulty:"Advanced", tag:"Back", img:"https://images.unsplash.com/photo-1599447421416-3414500d18a5?auto=format&fit=crop&w=400&q=80" },
  { id:'y23', body:'full', title:"Crow Pose", sub:"Arm balance challenge.", reps:"Hold 15s", duration:120, difficulty:"Advanced", tag:"Balance", img:"https://images.unsplash.com/photo-1510894347713-fc3ad6cb0322?auto=format&fit=crop&w=400&q=80" },
  { id:'y24', body:'full', title:"Camel Pose", sub:"Chest expander.", reps:"Hold 30s", duration:120, difficulty:"Intermediate", tag:"Back", img:"https://images.unsplash.com/photo-1593164841882-78d1f0565062?auto=format&fit=crop&w=400&q=80" },
  { id:'y25', body:'full', title:"Extended Side Angle", sub:"Leg and side strength.", reps:"30s/side", duration:180, difficulty:"Intermediate", tag:"Full Body", img:"https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?auto=format&fit=crop&w=400&q=80" },
  { id:'y26', body:'full', title:"Pyramid Pose", sub:"Hamstring stretch.", reps:"30s/side", duration:120, difficulty:"Intermediate", tag:"Legs", img:"https://images.unsplash.com/photo-1510894347713-fc3ad6cb0322?auto=format&fit=crop&w=400&q=80" },
  { id:'y27', body:'full', title:"Half Moon Pose", sub:"Advanced balance.", reps:"20s/side", duration:120, difficulty:"Advanced", tag:"Balance", img:"https://images.unsplash.com/photo-1506126613408-eca07ce68773?auto=format&fit=crop&w=400&q=80" },
  { id:'y28', body:'full', title:"Chair Pose", sub:"Powerful standing pose.", reps:"Hold 30s", duration:120, difficulty:"Beginner", tag:"Full Body", img:"https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?auto=format&fit=crop&w=400&q=80" },
  { id:'y29', body:'full', title:"Lizard Pose", sub:"Deep hip and groin.", reps:"30s/side", duration:180, difficulty:"Advanced", tag:"Hips", img:"https://images.unsplash.com/photo-1575052814086-f385e2e2ad1b?auto=format&fit=crop&w=400&q=80" },
  { id:'y30', body:'full', title:"Dolphin Pose", sub:"Shoulder strength.", reps:"Hold 30s", duration:120, difficulty:"Intermediate", tag:"Shoulders", img:"https://images.unsplash.com/photo-1599447421416-3414500d18a5?auto=format&fit=crop&w=400&q=80" },
  { id:'y31', body:'full', title:"Revolved Triangle", sub:"Twisting hamstrings.", reps:"20s/side", duration:120, difficulty:"Advanced", tag:"Full Body", img:"https://images.unsplash.com/photo-1510894347713-fc3ad6cb0322?auto=format&fit=crop&w=400&q=80" },
  { id:'y32', body:'full', title:"Seated Twist", sub:"Spinal detox twist.", reps:"30s/side", duration:120, difficulty:"Beginner", tag:"Back", img:"https://images.unsplash.com/photo-1593164841882-78d1f0565062?auto=format&fit=crop&w=400&q=80" }
];

let yogaFilter='all', activeYogaTimer=null, yogaTimerRunning=false;
function filterYoga(filter, btn){
  document.querySelectorAll('.bfb').forEach(b=>b.classList.remove('act'));btn.classList.add('act');
  yogaFilter=filter;renderYoga();
}
function renderYoga(){
  const grid=document.getElementById('yogaGrid');grid.innerHTML='';
  const poses=(yogaFilter==='all')?YOGA_DATA:YOGA_DATA.filter(p=>p.tag.toLowerCase().includes(yogaFilter.toLowerCase()) || p.body.toLowerCase().includes(yogaFilter.toLowerCase()));
  poses.forEach(p=>{
    const card=document.createElement('div');card.className='yoga-card';card.id='yc-'+p.id;
    card.innerHTML=`
      <div class="yoga-illus" style="background:url('${p.img}') center/cover no-repeat; border-radius:12px 12px 0 0; height:180px"></div>
      <div class="yoga-info">
        <div class="yoga-title">${p.title}</div>
        <div class="yoga-sub">${p.sub}</div>
        <div class="yoga-meta">
          <span class="yoga-tag">${p.difficulty}</span>
          <span class="yoga-tag green">${p.reps}</span>
          <span class="yoga-tag pink">${p.tag}</span>
        </div>
        <div style="display:flex;gap:8px">
          <button class="btn btn-p btn-sm" style="flex:1;font-size:12px" onclick="startYogaTimer('${p.id}',${p.duration},event)">▶ Start</button>
        </div>
      </div>
      <div class="yoga-timer-wrap" id="ytw-${p.id}">
        <div class="yoga-timer-face" id="ytf-${p.id}">00:${String(Math.floor(p.duration/60)).padStart(2,'0')}:${String(p.duration%60).padStart(2,'0')}</div>
        <div class="yoga-prog"><div class="yoga-pf" id="ypf-${p.id}" style="width:0%"></div></div>
        <div class="yoga-btns">
          <button class="btn btn-t btn-sm" onclick="pauseYogaTimer('${p.id}')">⏸ Pause</button>
          <button class="btn btn-g btn-sm" onclick="stopYogaTimer('${p.id}',${p.duration})">🔄 Reset</button>
        </div>
      </div>
    `;
    grid.appendChild(card);
  });
}
let yogaTimerState={};
function startYogaTimer(id, total, e){
  e.stopPropagation();
  // stop any other running timer
  Object.keys(yogaTimerState).forEach(k=>{if(k!==id&&yogaTimerState[k].running)pauseYogaTimer(k);});
  document.getElementById('yc-'+id).classList.add('active-pose');
  document.getElementById('ytw-'+id).classList.add('open');
  if(yogaTimerState[id]&&yogaTimerState[id].running) return;
  if(!yogaTimerState[id]) yogaTimerState[id]={rem:total,total,running:false,iv:null};
  const st=yogaTimerState[id];
  st.running=true;
  clearInterval(st.iv);
  st.iv=setInterval(async()=>{
    st.rem--;
    updateYogaTimerUI(id);
    if(st.rem<=0){
      clearInterval(st.iv);st.running=false;
      document.getElementById('ytf-'+id).textContent='Done! 🎉';
      document.getElementById('ypf-'+id).style.width='100%';
      playDing();
      document.getElementById('yc-'+id).classList.remove('active-pose');
      toast('🧘','Yoga pose complete! +35 XP','var(--a2)');
      const banner=document.getElementById('yogaCompleteBanner');banner.classList.add('show');setTimeout(()=>banner.classList.remove('show'),4000);
      await fetch('/api/yoga_done',{method:'POST'});await refreshState();
      yogaTimerState[id]=null;
    }
  },1000);
}
function pauseYogaTimer(id){
  if(!yogaTimerState[id])return;
  const st=yogaTimerState[id];
  if(st.running){clearInterval(st.iv);st.running=false;}
  else{
    st.running=true;
    st.iv=setInterval(async()=>{st.rem--;updateYogaTimerUI(id);if(st.rem<=0){clearInterval(st.iv);st.running=false;document.getElementById('ytf-'+id).textContent='Done! 🎉';}},1000);
  }
}
function stopYogaTimer(id,total){
  if(yogaTimerState[id]){clearInterval(yogaTimerState[id].iv);yogaTimerState[id]=null;}
  document.getElementById('ytf-'+id).textContent=fmt(Math.floor(total/60))+':'+fmt(total%60);
  document.getElementById('ypf-'+id).style.width='0%';
  document.getElementById('yc-'+id).classList.remove('active-pose');
}
function updateYogaTimerUI(id){
  const st=yogaTimerState[id];if(!st)return;
  const m=Math.floor(st.rem/60),s=st.rem%60;
  document.getElementById('ytf-'+id).textContent=fmt(m)+':'+fmt(s);
  document.getElementById('ypf-'+id).style.width=((st.total-st.rem)/st.total*100)+'%';
}
function toggleYogaInfo(id){document.getElementById('ytw-'+id).classList.toggle('open');}

// ═══════════════════════════════════════════════════════════
//  HYDRATION CORNER
// ═══════════════════════════════════════════════════════════
const HYDRATION_TIPS=[
  "Drink 2 glasses of water first thing in the morning to kickstart your metabolism.",
  "Carry a reusable water bottle so you always have water within reach.",
  "Eat water-rich foods like cucumber, watermelon, oranges and celery.",
  "Set phone reminders every 45 minutes as a hydration cue.",
  "Drink a glass before every meal — it also helps mindful eating.",
  "Herbal teas count towards your daily fluid intake!",
  "Feeling hungry? It might actually be thirst. Try water first.",
  "Cold water burns slightly more calories — but any temperature counts.",
];
let intakeLog=[], hydReminderInterval=null, hydGoal=8;

async function refreshHydration(){
  const data=await(await fetch('/api/hydration_log')).json();
  hydGoal=data.goal;const g=data.glasses;
  document.getElementById('hydGlasses').textContent=g;
  document.getElementById('hydGoal').textContent=hydGoal;
  const pct=Math.min(100,Math.round((g/hydGoal)*100));
  document.getElementById('hydBar').style.width=pct+'%';
  document.getElementById('hydPercent').textContent=pct+'%';
  document.getElementById('hydTotalMl').textContent=(g*250)+'ml';
  const rem=Math.max(0,hydGoal-g);
  document.getElementById('hydStatus').textContent=rem>0?`Keep going! ${rem} more glass${rem!==1?'es':''} to reach your goal.`:'🎉 Daily goal reached! Excellent hydration!';
  // update bottle fill
  const fillY=90-(70*(g/hydGoal));
  const fillH=56+(70*(g/hydGoal));
  const wf=document.getElementById('waterFill');if(wf){wf.setAttribute('y',fillY);wf.setAttribute('height',fillH);}
  const wt=document.getElementById('waveTop');if(wt){wt.setAttribute('d',`M 10 ${fillY} Q 22 ${fillY-6} 45 ${fillY} Q 68 ${fillY+6} 80 ${fillY} L 80 ${fillY+6} L 10 ${fillY+6} Z`);}
  // log items
  const logItems=document.getElementById('hydLogItems');
  const logData=data.log||[];
  if(logData.length===0){logItems.innerHTML='<div style="font-size:13px;color:var(--mu);text-align:center;padding:20px">No entries yet. Start drinking!</div>';return;}
  logItems.innerHTML='';
  logData.slice(-10).reverse().forEach(item=>{
    logItems.innerHTML+=`<div class="hydro-log-item"><div class="hydro-log-icon">💧</div><div class="hydro-log-text">Water intake (250ml)</div><div class="hydro-log-time">${item.time}</div></div>`;
  });
  document.getElementById('hydStreak').textContent=Math.min(g,5);
  // tip
  document.getElementById('hydTip').textContent=HYDRATION_TIPS[Math.floor(Math.random()*HYDRATION_TIPS.length)];
  initHydChart({glasses:g,goal:hydGoal});
}

async function logIntake(ml, label){
  const res=await(await fetch('/api/log_water',{method:'POST'})).json();
  toast('💧',`${label} logged!`,'var(--a2)');
  await refreshHydration();
  await refreshState();
}

let reminderEnabled=true, reminderTimeout=null;
function toggleReminder(on){
  reminderEnabled=on;
  if(on){toast('🔔','Hydration reminders enabled','var(--a2)');scheduleReminder();}
  else{toast('🔕','Reminders disabled','var(--mu)');clearTimeout(reminderTimeout);}
}
function scheduleReminder(){
  if(!reminderEnabled)return;
  reminderTimeout=setTimeout(()=>{toast('💧','Time to drink some water!','var(--a2)');scheduleReminder();},45*60*1000);
}
scheduleReminder();

// ═══════════════════════════════════════════════════════════
//  QUICK ACTIONS
// ═══════════════════════════════════════════════════════════
let breakShown=false;
function showBreak(){if(!breakShown){breakShown=true;document.getElementById('breakBanner').classList.add('show');}}
function dismissBreak(){document.getElementById('breakBanner').classList.remove('show');}
function startBreakTimer(){setMode(document.querySelector('.mp:nth-child(3)'),5,'Break');toast('☕','5-minute break started!','var(--warn)');navToBtn('tab-focus');}
setTimeout(showBreak,28*60*1000);
let grayOn=false,nightOn=false;
function actDND(){toast('🔕','Do Not Disturb activated','var(--a)');}
function actGray(){grayOn=!grayOn;document.body.style.filter=grayOn?'grayscale(1)':'';document.getElementById('grayB').querySelector('.al').textContent=grayOn?'Color On':'Grayscale';toast(grayOn?'🐼':'🎨',grayOn?'Grayscale enabled':'Color restored','var(--mu)');}
async function actDetox(){toast('📵','Social detox +30 XP','var(--a2)');await fetch('/api/complete_challenge',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({xp:30})});await refreshState();}
function actStretch(){toast('🤸','Stand up and stretch for 2 minutes!','var(--a2)');}
function actWalk(){toast('🚶','Perfect time for a mindful walk!','var(--a2)');}
function actNight(){nightOn=!nightOn;document.documentElement.style.filter=nightOn?'sepia(.35) brightness(.88)':'';document.getElementById('nightB').querySelector('.al').textContent=nightOn?'Day Mode':'Night Mode';toast(nightOn?'🌙':'☀️',nightOn?'Night mode on':'Day mode restored','var(--warn)');}

// ═══════════════════════════════════════════════════════════
//  BOOT
// ═══════════════════════════════════════════════════════════
(async()=>{
  await refreshState();
  await Promise.all([initHeatmap(),initHabits(),initChallenges(),loadJournal()]);
  renderYoga();
  setInterval(refreshState, 30000);
})();
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return Response(HTML, mimetype="text/html")

# ─── LAUNCHER ─────────────────────────────────────────────────────────────────
def open_browser(port):
    time.sleep(1.5)
    webbrowser.open(f"http://127.0.0.1:{port}")

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8", errors="replace") if hasattr(sys.stdout, "reconfigure") else None
    
    port = int(os.environ.get("PORT", 5050))
    is_render = os.environ.get("RENDER") is not None
    
    print("\n" + "="*55)
    print("  Zenith - Smart Detox & Digital Wellness")
    print("="*55)
    print(f"  -> Bound to port {port}")
    print("  Press Ctrl+C to stop\n")
    
    if not is_render:
        t = threading.Thread(target=open_browser, args=(port,), daemon=True)
        t.start()
        
    app.run(host="0.0.0.0", port=port, debug=False)
hreading, time, webbrowser, requests
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, Response

app = Flask(__name__)

# ─── DATA FILE ────────────────────────────────────────────────────────────────
DATA_FILE = os.path.join(os.path.dirname(__file__), "zenith_data.json")

DEFAULT_STATE = {
    "screen_time_today": 2.4,
    "goal_screen_time": 3.0,
    "goal_focus_mins": 90,
    "goal_sleep": 8.0,
    "goal_water": 8,
    "focus_sessions_today": 0,
    "mindfulness_minutes": 15,
    "breathing_sessions": 0,
    "challenges_completed": 0,
    "total_xp": 340,
    "detox_streak": 7,
    "sleep_hours": 7.2,
    "water_glasses": 5,
    "score_history": [72, 74, 68, 80, 78, 83, 85],
    "mood_log": [],
    "journal": [],
    "habits": [
        {"id": "h1", "icon": "🧘", "name": "Morning Meditation", "streak": 5, "done": False},
        {"id": "h2", "icon": "🚶", "name": "10k Steps", "streak": 3, "done": False},
        {"id": "h3", "icon": "📵", "name": "No Social Before 9am", "streak": 7, "done": True},
        {"id": "h4", "icon": "💧", "name": "Drink 8 Glasses", "streak": 2, "done": False},
        {"id": "h5", "icon": "📖", "name": "Read 20 Minutes", "streak": 4, "done": True},
    ],
    "achievements_unlocked": ["streak_7", "mood_log"],
    "unread_notifications": 3,
    "notifications": [
        {"icon": "🔥", "text": "You're on a 7-day streak! Keep it up.", "time": "2m ago", "unread": True},
        {"icon": "💧", "text": "Time to hydrate! You haven't logged water.", "time": "18m ago", "unread": True},
        {"icon": "🧘", "text": "Breathing session reminder — 5 min break.", "time": "1h ago", "unread": True},
        {"icon": "🎯", "text": "Focus session completed — great work!", "time": "3h ago", "unread": False},
        {"icon": "🏆", "text": "Challenge unlocked: 'Social Detox Warrior'", "time": "Yesterday", "unread": False},
    ],
    "yoga_sessions": 0,
    "hydration_log": [],
}

QUOTES = [
    {"text": "The quieter you become, the more you are able to hear.", "author": "Rumi"},
    {"text": "Almost everything will work again if you unplug it for a few minutes, including you.", "author": "Anne Lamott"},
    {"text": "You can't pour from an empty cup. Take care of yourself first.", "author": "Unknown"},
    {"text": "Tension is who you think you should be. Relaxation is who you are.", "author": "Chinese Proverb"},
    {"text": "In the middle of difficulty lies opportunity.", "author": "Albert Einstein"},
    {"text": "The present moment is the only moment available to us.", "author": "Thich Nhat Hanh"},
    {"text": "Peace comes from within. Do not seek it without.", "author": "Buddha"},
    {"text": "Within you there is a stillness and a sanctuary.", "author": "Hermann Hesse"},
    {"text": "Your calm mind is the ultimate weapon against your challenges.", "author": "Bryant McGill"},
    {"text": "Breathe. Let go. And remind yourself that this very moment is the only one you know you have for sure.", "author": "Oprah Winfrey"},
]

TIPS = [
    "🧠 Try a 20-20-20 rule: every 20 min, look 20 ft away for 20 seconds.",
    "📱 Charge your phone outside the bedroom tonight for better sleep.",
    "🌿 Replace 15 min of scrolling with a short walk outside.",
    "🔕 Batch your notifications to 3 check-in times per day.",
    "🌙 Use night shift mode after 7 PM to reduce blue light exposure.",
    "✋ Delete the social media apps from your home screen for a week.",
    "📚 Keep a physical book on your nightstand instead of your phone.",
    "⏰ Set an app timer: 30 minutes for social media maximum per day.",
    "🤝 Schedule tech-free meals with family or friends daily.",
    "🎨 Replace evening screen time with a creative offline hobby.",
    "💡 Turn off all non-essential notifications for 24 hours.",
    "🧘 Start your morning with 5 minutes of silence before touching your phone.",
]

CHALLENGES = [
    {"id": "c1", "icon": "📵", "title": "No Social Media", "desc": "Avoid social media for 4 hours", "xp": 60},
    {"id": "c2", "icon": "🚶", "title": "Digital Detox Walk", "desc": "Take a 20-min phone-free walk", "xp": 50},
    {"id": "c3", "icon": "📖", "title": "Read Instead", "desc": "Read a book for 30 minutes", "xp": 45},
    {"id": "c4", "icon": "🧘", "title": "Mindful Morning", "desc": "No phone for the first hour of the day", "xp": 80},
    {"id": "c5", "icon": "🍽️", "title": "Tech-Free Meal", "desc": "Eat lunch without any screens", "xp": 35},
    {"id": "c6", "icon": "💤", "title": "Sleep Hygiene", "desc": "Phone off 1h before bed tonight", "xp": 70},
]

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Merge missing keys from default
            for k, v in DEFAULT_STATE.items():
                if k not in data:
                    data[k] = v
            return data
        except Exception:
            pass
    return dict(DEFAULT_STATE)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def calc_wellness(data):
    score = 50
    if data["sleep_hours"] >= 7: score += 12
    elif data["sleep_hours"] >= 6: score += 6
    wg = data.get("goal_water", 8)
    if data["water_glasses"] >= wg: score += 10
    elif data["water_glasses"] >= wg // 2: score += 5
    if data["screen_time_today"] <= data["goal_screen_time"]: score += 10
    elif data["screen_time_today"] <= data["goal_screen_time"] * 1.5: score += 5
    score += min(10, data["focus_sessions_today"] * 2)
    score += min(8, data["breathing_sessions"] * 4)
    done_habits = sum(1 for h in data["habits"] if h["done"])
    score += done_habits * 2
    score += min(10, data["challenges_completed"] * 3)
    return min(100, max(0, score))

def get_score_level(score):
    if score >= 90: return "Zenith"
    if score >= 75: return "Thriving"
    if score >= 60: return "Balanced"
    if score >= 45: return "Growing"
    return "Starting"

def get_level_name(xp):
    if xp >= 1000: return "Sage"
    if xp >= 700: return "Mindful"
    if xp >= 400: return "Focused"
    if xp >= 200: return "Aware"
    return "Explorer"

def check_achievements(data):
    unlocked = set(data.get("achievements_unlocked", []))
    if data["breathing_sessions"] >= 1: unlocked.add("first_breath")
    if data["detox_streak"] >= 7: unlocked.add("streak_7")
    if data["focus_sessions_today"] >= 5: unlocked.add("focus_5")
    wg = data.get("goal_water", 8)
    if data["water_glasses"] >= wg: unlocked.add("hydrated")
    if data["sleep_hours"] >= 7: unlocked.add("sleep_champ")
    if data["challenges_completed"] >= 3: unlocked.add("challenge_3")
    if len(data.get("mood_log", [])) >= 1: unlocked.add("mood_log")
    if len(data.get("journal", [])) >= 1: unlocked.add("journaler")
    done_habits = sum(1 for h in data["habits"] if h["done"])
    if done_habits >= 5: unlocked.add("habit_5")
    if data["mindfulness_minutes"] >= 30: unlocked.add("mindful_30")
    if data.get("yoga_sessions", 0) >= 1: unlocked.add("zen_master")
    data["achievements_unlocked"] = list(unlocked)
    return data

# ─── API ROUTES ───────────────────────────────────────────────────────────────

@app.route("/api/login", methods=["POST"])
def api_login():
    req = request.get_json()
    username = req.get("username", "")
    password = req.get("password", "")
    
    profile = None
    user_name = "User"
    
    if username == "admin_r" and password == "productivity1":
        profile = "ryan"
        user_name = "Ryan Sharma"
    elif username == "dev_s" and password == "focus0":
        profile = "saaransh"
        user_name = "Saaransh Kharbanda"
    elif username == "user_n" and password == "balance5":
        profile = "neerab"
        user_name = "Neerab Hazarika"
    else:
        return jsonify({"status": "error", "message": "Invalid credentials"}), 401
        
    data = load_data()
    data["user_name"] = user_name
    data["profile_type"] = profile
    
    # Template Data
    if profile == "ryan":
        data["screen_time_today"] = 1.2
        data["focus_sessions_today"] = 5
        data["total_xp"] = 2800
        data["detox_streak"] = 14
        data["score_history"] = [85, 88, 90, 89, 92, 95]
        data["breathing_sessions"] = 3
        data["mindfulness_minutes"] = 45
    elif profile == "saaransh":
        data["screen_time_today"] = 6.5
        data["focus_sessions_today"] = 0
        data["total_xp"] = 150
        data["detox_streak"] = 0
        data["score_history"] = [45, 42, 38, 40, 41, 35]
        data["breathing_sessions"] = 0
        data["mindfulness_minutes"] = 5
    elif profile == "neerab":
        data["screen_time_today"] = 3.0
        data["focus_sessions_today"] = 2
        data["total_xp"] = 850
        data["detox_streak"] = 4
        data["score_history"] = [65, 70, 68, 72, 75, 78]
        data["breathing_sessions"] = 1
        data["mindfulness_minutes"] = 15
        
    save_data(data)
    return jsonify({"status": "ok", "name": user_name, "profile": profile})

@app.route("/api/state")
def api_state():
    data = load_data()
    data = check_achievements(data)
    save_data(data)
    score = calc_wellness(data)
    history = data.get("score_history", [])
    history = history[-7:] + [score]
    data["score_history"] = history[-7:]
    save_data(data)
    return jsonify({
        "user_name": data.get("user_name"),
        "wellness_score": score,
        "score_level": get_score_level(score),
        "score_history": data["score_history"],
        "focus_sessions_today": data["focus_sessions_today"],
        "challenges_completed": data["challenges_completed"],
        "breathing_sessions": data["breathing_sessions"],
        "total_xp": data["total_xp"],
        "level_name": get_level_name(data["total_xp"]),
        "detox_streak": data["detox_streak"],
        "screen_time_today": data["screen_time_today"],
        "goal_screen_time": data["goal_screen_time"],
        "mindfulness_minutes": data["mindfulness_minutes"],
        "sleep_hours": data["sleep_hours"],
        "water_glasses": data["water_glasses"],
        "habits": data["habits"],
        "achievements_unlocked": data["achievements_unlocked"],
        "unread_notifications": data["unread_notifications"],
        "quote": random.choice(QUOTES),
        "tip": random.choice(TIPS),
        "yoga_sessions": data.get("yoga_sessions", 0),
    })

@app.route("/api/notifications")
def api_notifications():
    data = load_data()
    data["unread_notifications"] = 0
    save_data(data)
    return jsonify(data.get("notifications", []))

@app.route("/api/set_goal", methods=["POST"])
def api_set_goal():
    data = load_data()
    body = request.get_json()
    data["goal_screen_time"] = body.get("screen_time", data["goal_screen_time"])
    data["goal_focus_mins"] = body.get("focus_mins", data["goal_focus_mins"])
    data["goal_sleep"] = body.get("sleep", data["goal_sleep"])
    data["goal_water"] = body.get("water", data["goal_water"])
    save_data(data)
    return jsonify({"ok": True})

@app.route("/api/weekly")
def api_weekly():
    days = [(datetime.now() - timedelta(days=6-i)).strftime("%a") for i in range(7)]
    random.seed(42)
    screen = [round(random.uniform(1.5, 5.5), 1) for _ in range(6)]
    data = load_data()
    screen.append(data["screen_time_today"])
    focus = [round(random.uniform(0.5, 3.0), 1) for _ in range(6)]
    focus.append(round(data["focus_sessions_today"] * 0.5, 1))
    goal = [data["goal_screen_time"]] * 7
    return jsonify({"labels": days, "screen": screen, "focus": focus, "goal": goal})

@app.route("/api/app_usage")
def api_app_usage():
    return jsonify([
        {"app": "Instagram", "hours": 1.4, "color": "#ff6b9d"},
        {"app": "YouTube", "hours": 2.1, "color": "#ff5f7e"},
        {"app": "Chrome", "hours": 1.8, "color": "#7c6dff"},
        {"app": "Slack", "hours": 0.9, "color": "#ffb347"},
        {"app": "Netflix", "hours": 0.7, "color": "#00e5c0"},
        {"app": "Other", "hours": 0.5, "color": "#4cde80"},
    ])

@app.route("/api/digital_diet")
def api_digital_diet():
    return jsonify({
        "labels": ["Focus", "Mindful", "Social", "Learning", "Rest", "Creation"],
        "current": [72, 65, 30, 55, 70, 45],
        "ideal":   [85, 80, 20, 70, 85, 60],
    })

@app.route("/api/heatmap")
def api_heatmap():
    cells = []
    base = datetime.now() - timedelta(days=34)
    random.seed(7)
    for i in range(35):
        d = base + timedelta(days=i)
        val = random.choices([0, 1, 2, 3], weights=[20, 30, 35, 15])[0]
        cells.append({"val": val, "day": d.strftime("%A"), "date": d.strftime("%b %d")})
    return jsonify(cells)

@app.route("/api/habits")
def api_habits():
    return jsonify(load_data()["habits"])

@app.route("/api/toggle_habit", methods=["POST"])
def api_toggle_habit():
    data = load_data()
    hid = request.get_json().get("id")
    for h in data["habits"]:
        if h["id"] == hid:
            if not h["done"]:
                h["done"] = True
                h["streak"] += 1
                data["total_xp"] += 20
            else:
                h["done"] = False
            break
    data = check_achievements(data)
    save_data(data)
    return jsonify({"habits": data["habits"], "xp": data["total_xp"]})

@app.route("/api/challenges")
def api_challenges():
    return jsonify(CHALLENGES)

@app.route("/api/complete_challenge", methods=["POST"])
def api_complete_challenge():
    data = load_data()
    xp = request.get_json().get("xp", 50)
    data["total_xp"] += xp
    data["challenges_completed"] += 1
    data = check_achievements(data)
    save_data(data)
    return jsonify({"xp": data["total_xp"]})

@app.route("/api/log_mood", methods=["POST"])
def api_log_mood():
    data = load_data()
    mood = request.get_json().get("mood", "okay")
    ts = datetime.now().strftime("%H:%M")
    data.setdefault("mood_log", []).append({"mood": mood, "time": ts})
    data["mood_log"] = data["mood_log"][-10:]
    data["total_xp"] += 15
    data = check_achievements(data)
    save_data(data)
    return jsonify({"mood_log": data["mood_log"]})

@app.route("/api/focus_complete", methods=["POST"])
def api_focus_complete():
    data = load_data()
    mins = request.get_json().get("minutes", 25)
    data["focus_sessions_today"] += 1
    data["mindfulness_minutes"] = min(120, data["mindfulness_minutes"] + mins)
    data["total_xp"] += 40
    data = check_achievements(data)
    save_data(data)
    return jsonify({"ok": True})

@app.route("/api/breathing_done", methods=["POST"])
def api_breathing_done():
    data = load_data()
    data["breathing_sessions"] += 1
    data["mindfulness_minutes"] = min(120, data["mindfulness_minutes"] + 5)
    data["total_xp"] += 20
    data = check_achievements(data)
    save_data(data)
    return jsonify({"ok": True})

@app.route("/api/log_sleep", methods=["POST"])
def api_log_sleep():
    data = load_data()
    data["sleep_hours"] = request.get_json().get("hours", 7.0)
    data = check_achievements(data)
    save_data(data)
    return jsonify({"ok": True})

@app.route("/api/log_water", methods=["POST"])
def api_log_water():
    data = load_data()
    wg = data.get("goal_water", 8)
    data["water_glasses"] = min(wg + 4, data["water_glasses"] + 1)
    if data["water_glasses"] <= wg:
        data["total_xp"] += 10
    ts = datetime.now().strftime("%H:%M")
    data.setdefault("hydration_log", []).append({"time": ts, "amount": 250})
    data = check_achievements(data)
    save_data(data)
    return jsonify({"glasses": data["water_glasses"]})

@app.route("/api/journal", methods=["GET"])
def api_journal_get():
    return jsonify(load_data().get("journal", []))

@app.route("/api/journal", methods=["POST"])
def api_journal_post():
    data = load_data()
    text = request.get_json().get("text", "").strip()[:300]
    if text:
        ts = datetime.now().strftime("%b %d, %H:%M")
        data.setdefault("journal", []).insert(0, {"text": text, "time": ts})
        data["journal"] = data["journal"][:20]
        data["total_xp"] += 15
        data = check_achievements(data)
        save_data(data)
    return jsonify({"entries": data.get("journal", []), "xp": data["total_xp"]})

@app.route("/api/yoga_done", methods=["POST"])
def api_yoga_done():
    data = load_data()
    data["yoga_sessions"] = data.get("yoga_sessions", 0) + 1
    data["total_xp"] += 35
    data["mindfulness_minutes"] = min(120, data["mindfulness_minutes"] + 10)
    data = check_achievements(data)
    save_data(data)
    return jsonify({"ok": True, "yoga_sessions": data["yoga_sessions"]})

@app.route("/api/ai_coach", methods=["POST"])
def api_ai_coach():
    req = request.get_json()
    user_msg = req.get("message", "")
    mode = req.get("mode", "chat") # 'chat' or 'analysis'
    
    data = load_data()
    api_key = os.environ.get("GROK_API_KEY")
    
    if not api_key:
        # Simulation if no API key provided
        if mode == "analysis":
            return jsonify({"reply": f"Based on your current activity, {data.get('user_name', 'User')}, your wellness score is {data.get('wellness_score', 85)}. You've spent {data.get('screen_time_today', 0)}h on screens today. I recommend a 10-minute meditation session to offset digital fatigue."})
        else:
            return jsonify({"reply": "I'm currently in offline mode. Please configure your GROK_API_KEY to enable live AI coaching, but I can still tell you that your focus sessions are looking great!"})

    # Grok API Integration
    try:
        system_prompt = f"You are Zenith AI, a premium digital wellness coach. User Data: {json.dumps(data)}. "
        if mode == "analysis":
            system_prompt += "Provide a clinical yet motivating analysis of their current wellness metrics."
        else:
            system_prompt += "Be a friendly, encouraging coach. Keep responses concise and focused on digital detox."

        response = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "grok-beta",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_msg if user_msg else "Analyze my current status."}
                ]
            },
            timeout=10
        )
        res_data = response.json()
        reply = res_data['choices'][0]['message']['content']
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": f"Error connecting to Grok: {str(e)}"}), 500

@app.route("/api/hydration_log")
def api_hydration_log():
    data = load_data()
    return jsonify({
        "log": data.get("hydration_log", []),
        "glasses": data["water_glasses"],
        "goal": data.get("goal_water", 8),
    })

# ─── MAIN HTML PAGE ───────────────────────────────────────────────────────────

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>Zenith — Smart Detox & Digital Wellness</title>
<meta name="description" content="AI-powered digital wellness dashboard. Track screen time, mood, habits, yoga, focus and more."/>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Space+Grotesk:wght@400;500;600;700;800&display=swap" rel="stylesheet"/>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
:root{
  --bg:#020202; /* Deep Black */
  --s1:rgba(255,255,255,0.02);--s2:rgba(255,255,255,0.04);--s3:rgba(255,255,255,0.07);
  --b1:rgba(255,255,255,0.12); /* Sharp white glass borders */
  --b2:rgba(255,255,255,0.25);
  --tx:#ffffff; /* Pure white text */
  --mu:rgba(255,255,255,0.5);
  --a:#ffffff; /* Neon White Accent */
  --a2:#cccccc; /* Silver Accent */
  --a3:#999999; /* Grey Accent */
  --warn:#e6e6e6;--err:#ff4d4d;--ok:#ffffff;
  --ga:rgba(255,255,255,0.15); /* White glow */
  --gb:rgba(200,200,200,0.1); /* Silver glow */
  --gc:rgba(150,150,150,0.1); /* Grey glow */
  --r:22px;--f:'Inter',sans-serif;--f2:'Space Grotesk',sans-serif;
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{font-family:var(--f);background:var(--bg);color:var(--tx);min-height:100vh;overflow-x:hidden}

/* LAYOUT */
.app-container{display:flex;min-height:100vh;position:relative;z-index:1}
.sidebar{width:250px;background:rgba(5,9,26,0.75);backdrop-filter:blur(28px);-webkit-backdrop-filter:blur(28px);border-right:1px solid var(--b1);padding:30px 16px;position:fixed;left:0;top:0;bottom:0;z-index:100;display:flex;flex-direction:column}
.sb-logo{display:flex;align-items:center;gap:12px;margin-bottom:40px;padding:0 10px}
.sb-logo-icon{width:42px;height:42px;border-radius:14px;background:linear-gradient(135deg,var(--a),var(--a2));display:flex;align-items:center;justify-content:center;font-size:22px;box-shadow:0 0 24px var(--ga);animation:pulse 4s infinite}
.sb-logo-text{font-family:var(--f2);font-size:22px;font-weight:800;background:linear-gradient(135deg,#9b8dff,var(--a2));-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.nav-links{display:flex;flex-direction:column;gap:6px;flex:1;overflow-y:auto}
.nb{display:flex;align-items:center;gap:14px;padding:13px 16px;border-radius:14px;font-size:13.5px;font-weight:600;color:var(--mu);cursor:pointer;transition:all .2s;border:1px solid transparent;background:transparent;width:100%;text-align:left}
.nb:hover{background:rgba(255,255,255,0.03);color:var(--tx)}
.nb.act{background:linear-gradient(90deg,rgba(124,109,255,0.14),transparent);border:1px solid var(--b1);border-left:3px solid var(--a);color:#fff;box-shadow:0 4px 20px rgba(0,0,0,0.18)}
.nb-ic{font-size:18px;width:22px;text-align:center;flex-shrink:0}
.main-content{margin-left:250px;flex:1;padding:20px 28px 90px;max-width:1420px}

/* TABS */
.tab-content{display:none;margin-top:10px;animation:slideInTab .45s cubic-bezier(0.2,0.8,0.2,1) forwards;opacity:0}
.tab-content.act{display:block}
@keyframes slideInTab{from{opacity:0;transform:translateY(22px)}to{opacity:1;transform:translateY(0)}}

/* BG EFFECTS */
#stars{position:fixed;inset:0;z-index:0;pointer-events:none}
.orbs{position:fixed;inset:0;z-index:0;pointer-events:none;overflow:hidden}
.orb{position:absolute;border-radius:50%;filter:blur(110px);opacity:0.13;animation:flt 24s ease-in-out infinite}
.o1{width:700px;height:700px;background:var(--a);top:-220px;left:-220px}
.o2{width:540px;height:540px;background:var(--a2);bottom:-140px;right:-140px;animation-delay:-9s}
.o3{width:420px;height:420px;background:var(--a3);top:38%;left:38%;animation-delay:-17s}
.o4{width:320px;height:320px;background:var(--warn);bottom:22%;left:6%;animation-delay:-6s;opacity:0.07}
.o5{width:280px;height:280px;background:#4cde80;top:15%;right:10%;animation-delay:-13s;opacity:0.06}
@keyframes flt{0%,100%{transform:translate(0,0) scale(1)}40%{transform:translate(55px,-65px) scale(1.08)}70%{transform:translate(-35px,45px) scale(0.93)}}
@keyframes pulse{0%,100%{box-shadow:0 0 24px var(--ga)}50%{box-shadow:0 0 50px var(--ga),0 0 70px rgba(0,229,192,0.18)}}

/* GLASS & CARDS */
.g{background:var(--s1);backdrop-filter:blur(28px) saturate(180%);-webkit-backdrop-filter:blur(28px) saturate(180%);border:1px solid var(--b1);border-radius:var(--r);transition:all .3s ease}
.g:hover{border-color:var(--b2);background:var(--s2);box-shadow:0 10px 38px rgba(0,0,0,0.22)}
.shim{position:relative;overflow:hidden}
.shim::after{content:'';position:absolute;inset:0;border-radius:inherit;pointer-events:none;background:linear-gradient(105deg,transparent 40%,rgba(255,255,255,0.04) 50%,transparent 60%);background-size:200% 100%;animation:shim 6s linear infinite}
@keyframes shim{0%{background-position:200% 0}100%{background-position:-200% 0}}

/* BENTO */
.bento{display:grid;grid-template-columns:repeat(12,1fr);gap:18px;align-items:start}
.card{padding:24px;border-radius:var(--r);position:relative;overflow:hidden}
.lbl{font-size:11px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:var(--mu);margin-bottom:14px;display:flex;align-items:center;gap:8px}
.c3{grid-column:span 3}.c4{grid-column:span 4}.c5{grid-column:span 5}
.c6{grid-column:span 6}.c7{grid-column:span 7}.c8{grid-column:span 8}
.c9{grid-column:span 9}.c12{grid-column:span 12}

/* HEADER */
header{display:flex;align-items:center;justify-content:space-between;padding:15px 24px;margin-bottom:22px;background:rgba(255,255,255,0.03);backdrop-filter:blur(28px);border:1px solid var(--b1);border-radius:var(--r);position:sticky;top:20px;z-index:90}
.hdr-title{font-family:var(--f2);font-size:21px;font-weight:700;letter-spacing:-0.5px}
.hdr-r{display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.pill{display:inline-flex;align-items:center;gap:7px;padding:7px 15px;border-radius:100px;font-size:13px;font-weight:600;cursor:default;white-space:nowrap}
.pill-xp{background:rgba(0,229,192,.1);border:1px solid rgba(0,229,192,.24);color:var(--a2)}
.pill-streak{background:rgba(255,179,71,.1);border:1px solid rgba(255,179,71,.28);color:var(--warn)}
.pill-clock{background:rgba(124,109,255,.12);border:1px solid rgba(124,109,255,.28);color:var(--a);font-family:var(--f2);letter-spacing:.5px}

/* NOTIFICATION */
.notif-wrap{position:relative}
.notif-bell{width:40px;height:40px;border-radius:12px;background:var(--s2);border:1px solid var(--b1);display:flex;align-items:center;justify-content:center;font-size:18px;cursor:pointer;transition:all .2s;position:relative}
.notif-bell:hover{background:var(--s3);border-color:var(--b2);transform:scale(1.07)}
.notif-badge{position:absolute;top:-4px;right:-4px;width:18px;height:18px;border-radius:50%;background:var(--a3);border:2px solid var(--bg);font-size:9px;font-weight:800;color:#fff;display:flex;align-items:center;justify-content:center;animation:bBounce .85s ease infinite alternate}
@keyframes bBounce{from{transform:scale(1)}to{transform:scale(1.18)}}
.notif-panel{position:absolute;top:calc(100% + 10px);right:0;width:320px;z-index:200;background:rgba(8,14,30,.98);backdrop-filter:blur(32px);border:1px solid var(--b2);border-radius:var(--r);box-shadow:0 22px 64px rgba(0,0,0,.55);display:none;overflow:hidden}
.notif-panel.open{display:block;animation:dropIn .22s ease}
@keyframes dropIn{from{opacity:0;transform:translateY(-14px)}to{opacity:1;transform:translateY(0)}}
.notif-head{padding:14px 18px;font-size:12px;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:var(--mu);border-bottom:1px solid var(--b1)}
.notif-item{display:flex;align-items:flex-start;gap:12px;padding:13px 18px;border-bottom:1px solid var(--b1);transition:background .2s}
.notif-item:hover{background:var(--s2)}
.notif-item.unread{background:rgba(124,109,255,.08)}
.ni-icon{font-size:20px;flex-shrink:0;margin-top:1px}
.ni-text{font-size:13px;font-weight:500;line-height:1.4}
.ni-time{font-size:11px;color:var(--mu);margin-top:3px}

/* SCORE */
.score-ring{width:155px;height:155px;position:relative;margin:10px auto 0}
.score-ring svg{transform:rotate(-90deg)}
.st-track{fill:none;stroke:rgba(255,255,255,.07);stroke-width:12}
.sf{fill:none;stroke-width:12;stroke-linecap:round;stroke:url(#sg);transition:stroke-dashoffset 1.6s cubic-bezier(.4,0,.2,1)}
.score-inner{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center}
.sn{font-family:var(--f2);font-size:46px;font-weight:800;line-height:1}
.sl{font-size:11px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:var(--a2);margin-top:4px}
.sparkline-wrap{margin:14px 0 8px;height:44px;position:relative}
.spark-svg{width:100%;height:100%;overflow:visible}
.tstats{display:flex;justify-content:space-around;padding:15px 0 0;border-top:1px solid var(--b1);margin-top:14px}
.tstat .v{font-family:var(--f2);font-size:24px;font-weight:700;text-align:center}
.tstat .l{font-size:11px;color:var(--mu);text-align:center;margin-top:3px}

/* QUOTE */
.qbody{font-size:19px;line-height:1.65;font-style:italic;margin-top:10px;opacity:.9}
.qattr{margin-top:16px;font-size:14px;font-weight:600;color:var(--a);display:flex;align-items:center;gap:10px}
.qattr::before{content:'';display:block;width:30px;height:2px;background:var(--a);border-radius:2px;flex-shrink:0}

/* SCREEN TIME */
.st-big{font-family:var(--f2);font-size:42px;font-weight:800;line-height:1;margin:12px 0 5px}
.prog-t{background:rgba(255,255,255,.07);border-radius:100px;height:11px;overflow:hidden;margin:16px 0 7px}
.prog-f{height:100%;border-radius:100px;transition:width 1.4s cubic-bezier(.4,0,.2,1)}
.prog-tks{display:flex;justify-content:space-between;font-size:12px;color:var(--mu)}

/* FOCUS TIMER */
.mp-row{display:flex;gap:7px;flex-wrap:wrap;justify-content:center;margin-bottom:10px}
.mp{padding:6px 16px;border-radius:100px;font-size:13px;font-weight:600;cursor:pointer;border:1px solid var(--b1);background:transparent;color:var(--mu);transition:all .2s}
.mp.act{background:rgba(124,109,255,.2);border-color:var(--a);color:#fff;box-shadow:0 0 18px rgba(124,109,255,.25)}
.timer-face{text-align:center;padding:22px 0 14px}
.tnum{font-family:var(--f2);font-size:68px;font-weight:800;line-height:1;letter-spacing:-4px;background:linear-gradient(135deg,#a08dff,var(--a2));-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.tiny-p{height:6px;background:rgba(255,255,255,.07);border-radius:6px;overflow:hidden;margin:14px 0 7px}
.tiny-pf{height:100%;border-radius:6px;background:linear-gradient(90deg,var(--a),var(--a2));transition:width 1s linear}
.sound-opts{display:flex;gap:7px;flex-wrap:wrap;margin-top:10px;justify-content:center}
.sound-btn{padding:5px 13px;border-radius:100px;font-size:12px;font-weight:600;cursor:pointer;border:1px solid var(--b1);background:transparent;color:var(--mu);transition:all .2s}
.sound-btn.act{background:rgba(0,229,192,.12);border-color:var(--a2);color:var(--a2)}

/* BREATHING */
.breath-sc{display:flex;flex-direction:column;align-items:center;padding:18px 0 10px}
.breath-ring{width:140px;height:140px;border-radius:50%;cursor:pointer;background:radial-gradient(circle,rgba(0,229,192,.18),rgba(124,109,255,.06));border:2px solid rgba(0,229,192,.35);display:flex;align-items:center;justify-content:center;box-shadow:0 0 50px rgba(0,229,192,.1);transition:box-shadow .3s}
.breath-ring.go{animation:breathAnim 19s ease-in-out infinite}
@keyframes breathAnim{0%,5%{transform:scale(1);box-shadow:0 0 50px rgba(0,229,192,.1)}22%,55%{transform:scale(1.5);box-shadow:0 0 100px rgba(0,229,192,.45)}72%,100%{transform:scale(1);box-shadow:0 0 50px rgba(0,229,192,.1)}}
.br-inner{width:88px;height:88px;border-radius:50%;background:rgba(0,229,192,.1);border:1px solid rgba(0,229,192,.25);display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:600;color:var(--a2);text-align:center;line-height:1.3}
.breath-phase{margin-top:16px;font-size:15px;font-weight:500;color:var(--mu)}
.breath-cyc{font-family:var(--f2);font-size:27px;font-weight:700;color:var(--a2);margin-top:3px}
.b-modes{display:flex;gap:7px;justify-content:center;margin-bottom:10px;flex-wrap:wrap}
.bm{padding:6px 13px;border-radius:100px;font-size:12px;font-weight:600;cursor:pointer;border:1px solid var(--b1);background:transparent;color:var(--mu);transition:all .2s}
.bm.act{background:rgba(0,229,192,.12);border-color:var(--a2);color:var(--a2)}

/* MOOD */
.mood-grid{display:flex;gap:10px;flex-wrap:wrap;justify-content:center;margin-top:14px}
.mb{display:flex;flex-direction:column;align-items:center;gap:6px;padding:15px 10px;border-radius:18px;cursor:pointer;background:rgba(255,255,255,.04);border:1px solid var(--b1);transition:all .22s;min-width:68px}
.mb:hover,.mb.sel{border-color:var(--b2);background:rgba(255,255,255,.1);transform:translateY(-5px);box-shadow:0 12px 30px rgba(0,0,0,.3)}
.me{font-size:32px;line-height:1}
.ml{font-size:12px;font-weight:600;color:var(--mu)}
.mood-hist{margin-top:16px;display:flex;gap:7px;flex-wrap:wrap}
.mood-tag{padding:6px 11px;border-radius:100px;font-size:12px;background:rgba(255,255,255,.05);border:1px solid var(--b1);color:var(--mu)}

/* HABITS */
.hab-list{display:flex;flex-direction:column;gap:9px;margin-top:10px}
.hab{display:flex;align-items:center;gap:14px;padding:13px 16px;background:rgba(255,255,255,.04);border:1px solid var(--b1);border-radius:16px;cursor:pointer;transition:all .22s}
.hab:hover{background:rgba(255,255,255,.08);transform:translateX(5px)}
.hab.done{background:rgba(0,229,192,.06);border-color:rgba(0,229,192,.25)}
.hab-icon{font-size:22px;flex-shrink:0}
.hab-body{flex:1}
.hab-name{font-size:13.5px;font-weight:600}
.hab-str{font-size:12px;color:var(--mu);margin-top:2px}
.hab-check{width:25px;height:25px;border-radius:50%;border:2px solid var(--b2);display:flex;align-items:center;justify-content:center;font-size:13px;flex-shrink:0;transition:all .3s}
.hab.done .hab-check{background:var(--a2);border-color:var(--a2);color:#05091a;font-weight:700}

/* CHARTS */
.chat-w{height:220px;margin-top:10px;width:100%}
.ul{display:flex;flex-direction:column;gap:9px;margin-top:14px}
.ur{display:flex;align-items:center;gap:11px}
.udot{width:9px;height:9px;border-radius:50%;flex-shrink:0}
.uname{font-size:13px;flex:1}
.ubg{flex:2;background:rgba(255,255,255,.07);border-radius:100px;height:5px;overflow:hidden}
.uf{height:100%;border-radius:100px;transition:width 1.3s ease}
.uh{font-size:12px;font-weight:600;color:var(--mu);min-width:30px;text-align:right}
.wleg{display:flex;gap:14px;flex-wrap:wrap;margin-bottom:8px}
.wl{display:flex;align-items:center;gap:7px;font-size:12px;color:var(--mu)}
.wlc{width:9px;height:9px;border-radius:3px;display:inline-block}

/* HEATMAP */
.hm-grid{display:grid;grid-template-columns:repeat(7,1fr);gap:6px;margin-top:14px}
.hm-cell{aspect-ratio:1;border-radius:8px;cursor:default;transition:transform .15s;position:relative}
.hm-cell:hover{transform:scale(1.2);z-index:2}
.hv0{background:rgba(255,255,255,.06)}.hv1{background:rgba(0,229,192,.22)}.hv2{background:rgba(0,229,192,.52)}.hv3{background:rgba(0,229,192,.88);box-shadow:0 0 8px rgba(0,229,192,.4)}
.hm-tip{position:absolute;bottom:130%;left:50%;transform:translateX(-50%);background:rgba(8,14,30,.95);border:1px solid var(--b2);border-radius:8px;padding:6px 11px;font-size:11px;white-space:nowrap;pointer-events:none;opacity:0;transition:opacity .15s;z-index:10}
.hm-cell:hover .hm-tip{opacity:1}

/* SLEEP & WATER */
.sw-row{display:flex;gap:16px;margin-top:12px}
.sw-box{flex:1;padding:16px;background:rgba(255,255,255,.03);border:1px solid var(--b1);border-radius:16px;text-align:center}
.sw-big{font-family:var(--f2);font-size:34px;font-weight:800;margin:7px 0}
.swl{font-size:13px;color:var(--mu)}
.wdots{display:flex;gap:6px;justify-content:center;flex-wrap:wrap;margin-top:10px}
.wd{width:15px;height:15px;border-radius:50%;background:rgba(255,255,255,.1);border:1px solid var(--b1);cursor:pointer;transition:all .3s}
.wd.on{background:var(--a);border-color:var(--a);box-shadow:0 0 10px rgba(124,109,255,.4)}
input[type=range]{width:100%;accent-color:var(--a);cursor:pointer;margin-top:13px;height:5px;background:linear-gradient(90deg,var(--a),var(--a2));border-radius:6px;appearance:none;outline:none}
input[type=range]::-webkit-slider-thumb{appearance:none;width:20px;height:20px;border-radius:50%;background:#fff;box-shadow:0 2px 10px rgba(0,0,0,.4);cursor:pointer;border:4px solid var(--a)}

/* QUICK ACTIONS */
.act-g{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-top:14px}
.act-b{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:7px;padding:18px 8px;border-radius:16px;background:rgba(255,255,255,.04);border:1px solid var(--b1);cursor:pointer;transition:all .22s;font-family:var(--f);color:var(--tx)}
.act-b:hover{background:rgba(255,255,255,.09);border-color:var(--b2);transform:translateY(-4px);box-shadow:0 12px 30px rgba(0,0,0,.3)}
.act-b:active{transform:translateY(-1px)}
.ai{font-size:26px;line-height:1}
.al{font-size:12px;font-weight:600;color:var(--mu);text-align:center}

/* JOURNAL */
.journal-list{display:flex;flex-direction:column;gap:9px;margin-top:12px;max-height:200px;overflow-y:auto;padding-right:4px}
.j-item{padding:13px 15px;background:rgba(255,255,255,.04);border:1px solid var(--b1);border-radius:14px}
.j-text{font-size:13.5px;line-height:1.5;color:var(--tx)}
.j-time{font-size:11px;color:var(--mu);margin-top:5px}
textarea.j-input{width:100%;background:rgba(255,255,255,.05);border:1px solid var(--b1);border-radius:14px;padding:13px 15px;font-family:var(--f);font-size:13.5px;color:var(--tx);resize:none;height:95px;outline:none;transition:border-color .2s;margin-top:12px}
textarea.j-input:focus{border-color:var(--b3);background:rgba(255,255,255,.07)}

/* ACHIEVEMENTS */
.ach-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:11px;margin-top:14px}
.ach-item{display:flex;flex-direction:column;align-items:center;gap:5px;padding:15px 7px;border-radius:16px;border:1px solid var(--b1);background:rgba(255,255,255,.03);transition:all .22s;cursor:default;text-align:center}
.ach-item.unlocked{background:rgba(124,109,255,.1);border-color:rgba(124,109,255,.35);box-shadow:0 0 20px rgba(124,109,255,.15)}
.ach-item.unlocked:hover{transform:translateY(-4px);box-shadow:0 10px 30px rgba(124,109,255,.25)}
.ach-icon{font-size:26px;line-height:1;filter:grayscale(1);opacity:.4;transition:all .4s}
.ach-item.unlocked .ach-icon{filter:none;opacity:1}
.ach-name{font-size:11px;font-weight:600;color:var(--mu);line-height:1.3}
.ach-item.unlocked .ach-name{color:var(--tx)}
.ach-xp{font-size:11px;font-weight:700;color:var(--a);opacity:0;transition:opacity .3s}
.ach-item.unlocked .ach-xp{opacity:1}
@keyframes newAch{0%,100%{box-shadow:0 0 20px rgba(124,109,255,.15)}50%{box-shadow:0 0 54px rgba(124,109,255,.55),0 0 85px rgba(0,229,192,.3)}}
.ach-item.just-unlocked{animation:newAch 1.5s ease 3}

/* CHALLENGES */
.ch-list{display:flex;flex-direction:column;gap:9px;margin-top:14px;max-height:380px;overflow-y:auto;padding-right:4px}
.chi{display:flex;align-items:center;gap:13px;padding:15px;background:rgba(255,255,255,.04);border:1px solid var(--b1);border-radius:16px;cursor:pointer;transition:all .22s}
.chi:hover{background:rgba(255,255,255,.09);transform:translateX(5px);border-color:var(--b2)}
.chi.done{opacity:.5;pointer-events:none}
.chi-icon{font-size:24px;flex-shrink:0}
.chi-body{flex:1}
.chi-title{font-size:14px;font-weight:600}
.chi-desc{font-size:12px;color:var(--mu);margin-top:3px}
.chi-xp{font-size:13px;font-weight:700;color:var(--a);white-space:nowrap}
.chi-check{width:25px;height:25px;border-radius:50%;border:2px solid var(--b2);display:flex;align-items:center;justify-content:center;font-size:13px;flex-shrink:0;transition:all .3s}
.chi.done .chi-check{background:var(--a2);border-color:var(--a2);color:#05091a}

/* ── YOGA SECTION ── */
.yoga-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:14px}
.yoga-card{background:rgba(255,255,255,.04);border:1px solid var(--b1);border-radius:20px;overflow:hidden;transition:all .3s;cursor:pointer}
.yoga-card:hover{border-color:var(--b2);background:rgba(255,255,255,.07);transform:translateY(-4px);box-shadow:0 14px 40px rgba(0,0,0,.3)}
.yoga-card.active-pose{border-color:rgba(0,229,192,.5);background:rgba(0,229,192,.06);box-shadow:0 0 30px rgba(0,229,192,.15)}
.yoga-illus{height:140px;display:flex;align-items:center;justify-content:center;position:relative;overflow:hidden}
.yoga-illus svg{width:100px;height:130px;filter:drop-shadow(0 0 16px rgba(0,229,192,.25));animation:yogaFloat 4s ease-in-out infinite}
@keyframes yogaFloat{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}
.yoga-info{padding:16px}
.yoga-title{font-family:var(--f2);font-size:15px;font-weight:700;margin-bottom:4px}
.yoga-sub{font-size:12px;color:var(--mu);margin-bottom:12px;line-height:1.4}
.yoga-meta{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:12px}
.yoga-tag{padding:4px 10px;border-radius:100px;font-size:11px;font-weight:600;background:rgba(124,109,255,.1);border:1px solid rgba(124,109,255,.25);color:var(--a)}
.yoga-tag.green{background:rgba(0,229,192,.1);border-color:rgba(0,229,192,.25);color:var(--a2)}
.yoga-tag.pink{background:rgba(255,107,157,.1);border-color:rgba(255,107,157,.25);color:var(--a3)}
.yoga-timer-wrap{display:none;padding:0 16px 16px}
.yoga-timer-wrap.open{display:block}
.yoga-timer-face{font-family:var(--f2);font-size:38px;font-weight:800;text-align:center;padding:10px 0;background:linear-gradient(135deg,#a08dff,var(--a2));-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.yoga-prog{height:6px;background:rgba(255,255,255,.07);border-radius:6px;overflow:hidden;margin:8px 0}
.yoga-pf{height:100%;border-radius:6px;background:linear-gradient(90deg,var(--a),var(--a2));transition:width .5s linear}
.yoga-btns{display:flex;gap:8px;justify-content:center;margin-top:10px}
.body-filter-bar{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:16px}
.bfb{padding:7px 16px;border-radius:100px;font-size:13px;font-weight:600;cursor:pointer;border:1px solid var(--b1);background:transparent;color:var(--mu);transition:all .2s}
.bfb.act{background:rgba(124,109,255,.18);border-color:var(--a);color:#fff}
.yoga-complete-banner{background:linear-gradient(135deg,rgba(0,229,192,.12),rgba(124,109,255,.08));border:1px solid rgba(0,229,192,.3);border-radius:16px;padding:20px;text-align:center;margin-bottom:20px;display:none}
.yoga-complete-banner.show{display:block;animation:slideInTab .4s ease}

/* ── HYDRATION CORNER ── */
.hydro-hero{display:flex;align-items:center;gap:28px;margin-top:14px;flex-wrap:wrap}
.hydro-vessel{position:relative;width:90px;flex-shrink:0}
.hydro-vessel svg{width:90px;height:150px}
.hydro-stats-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;margin-top:16px}
.hydro-stat{padding:16px;background:rgba(255,255,255,.04);border:1px solid var(--b1);border-radius:16px;text-align:center}
.hydro-stat-v{font-family:var(--f2);font-size:28px;font-weight:800;color:var(--a2)}
.hydro-stat-l{font-size:12px;color:var(--mu);margin-top:4px}
.hydro-log{margin-top:16px}
.hydro-log-title{font-size:12px;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:var(--mu);margin-bottom:10px}
.hydro-log-items{display:flex;flex-direction:column;gap:7px;max-height:180px;overflow-y:auto}
.hydro-log-item{display:flex;align-items:center;gap:10px;padding:9px 13px;background:rgba(0,229,192,.05);border:1px solid rgba(0,229,192,.12);border-radius:12px}
.hydro-log-icon{font-size:16px}
.hydro-log-text{font-size:12px;flex:1}
.hydro-log-time{font-size:11px;color:var(--mu)}
.intake-buttons{display:flex;gap:8px;flex-wrap:wrap;margin-top:16px}
.intake-btn{padding:9px 18px;border-radius:100px;font-size:13px;font-weight:600;cursor:pointer;border:1px solid rgba(0,229,192,.3);background:rgba(0,229,192,.07);color:var(--a2);transition:all .2s}
.intake-btn:hover{background:rgba(0,229,192,.18);transform:translateY(-2px)}
.hydro-reminder-row{display:flex;align-items:center;gap:12px;margin-top:16px;padding:14px;background:rgba(255,179,71,.05);border:1px solid rgba(255,179,71,.2);border-radius:14px}
.hydro-reminder-icon{font-size:22px}
.hydro-reminder-text{flex:1;font-size:13px}
.hydro-reminder-toggle{position:relative;width:42px;height:24px;flex-shrink:0}
.hydro-reminder-toggle input{opacity:0;width:0;height:0}
.hrt-slider{position:absolute;inset:0;border-radius:24px;background:rgba(255,255,255,.1);border:1px solid var(--b2);cursor:pointer;transition:all .3s}
.hrt-slider::before{content:'';position:absolute;left:3px;top:3px;width:16px;height:16px;border-radius:50%;background:var(--mu);transition:all .3s}
.hydro-reminder-toggle input:checked + .hrt-slider{background:var(--a2);border-color:var(--a2)}
.hydro-reminder-toggle input:checked + .hrt-slider::before{transform:translateX(18px);background:#fff}
.hydro-wave{animation:hydroWave 3s ease-in-out infinite}
@keyframes hydroWave{0%,100%{d:path("M 0 80 Q 22 72 45 80 Q 68 88 90 80 L 90 120 L 0 120 Z")}50%{d:path("M 0 80 Q 22 88 45 80 Q 68 72 90 80 L 90 120 L 0 120 Z")}}

/* UTILS */
.btn{padding:11px 22px;border-radius:100px;border:none;cursor:pointer;font-family:var(--f);font-size:13.5px;font-weight:600;transition:all .2s;display:inline-flex;align-items:center;justify-content:center;gap:7px}
.btn-p{background:linear-gradient(135deg,var(--a),#a86dff);color:#fff;box-shadow:0 6px 24px var(--ga)}
.btn-p:hover{transform:translateY(-2px);box-shadow:0 10px 36px var(--ga)}
.btn-g{background:rgba(255,255,255,.06);color:var(--tx);border:1px solid var(--b1)}
.btn-g:hover{background:rgba(255,255,255,.12);border-color:var(--b2)}
.btn-t{background:rgba(0,229,192,.1);color:var(--a2);border:1px solid rgba(0,229,192,.25)}
.btn-t:hover{background:rgba(0,229,192,.2)}
.btn-sm{padding:9px 18px;font-size:12.5px}
.chip{display:inline-flex;align-items:center;gap:6px;padding:5px 13px;border-radius:100px;font-size:12px;font-weight:600}
.cr{background:rgba(255,95,126,.1);color:var(--err);border:1px solid rgba(255,95,126,.25)}
.cg{background:rgba(0,229,192,.1);color:var(--a2);border:1px solid rgba(0,229,192,.25)}
.cw{background:rgba(255,179,71,.1);color:var(--warn);border:1px solid rgba(255,179,71,.25)}
.ga-{box-shadow:0 0 40px var(--ga)}.gb-{box-shadow:0 0 36px var(--gb)}

/* MODALS */
.modal-overlay{position:fixed;inset:0;z-index:300;background:rgba(0,0,0,.62);backdrop-filter:blur(10px);display:none;align-items:center;justify-content:center;animation:fadeIn .25s ease}
.modal-overlay.open{display:flex}
@keyframes fadeIn{from{opacity:0}to{opacity:1}}
.modal-box{background:rgba(8,14,30,.98);border:1px solid var(--b2);border-radius:var(--r);width:min(500px,94vw);padding:30px;box-shadow:0 26px 84px rgba(0,0,0,.65);animation:slideUp .3s ease}
@keyframes slideUp{from{opacity:0;transform:translateY(30px)}to{opacity:1;transform:translateY(0)}}
.modal-title{font-family:var(--f2);font-size:21px;font-weight:700;margin-bottom:22px;display:flex;align-items:center;gap:11px}
.goal-row{margin-bottom:18px}
.goal-label{font-size:13.5px;font-weight:600;margin-bottom:9px;display:flex;justify-content:space-between;align-items:center}
.goal-label span{font-family:var(--f2);font-size:17px;font-weight:700;color:var(--a2)}

/* BREAK BANNER */
#breakBanner{position:fixed;bottom:0;left:0;right:0;z-index:199;background:linear-gradient(90deg,rgba(255,95,126,.15),rgba(255,179,71,.12));backdrop-filter:blur(22px);border-top:1px solid rgba(255,95,126,.3);padding:15px 28px;display:flex;align-items:center;gap:18px;transform:translateY(100%);transition:transform .5s cubic-bezier(.4,0,.2,1)}
#breakBanner.show{transform:translateY(0)}
.bb-icon{font-size:24px}
.bb-text{flex:1;font-size:14px;font-weight:500}
.bb-close{font-size:13px;font-weight:600;cursor:pointer;opacity:.7;padding:7px 16px;border-radius:100px;background:rgba(255,255,255,.1);border:1px solid var(--b2);transition:all .2s}
.bb-close:hover{opacity:1;background:rgba(255,255,255,.15)}

/* TOAST */
#toast{position:fixed;bottom:85px;right:28px;z-index:9999;background:rgba(8,14,32,.97);backdrop-filter:blur(28px);border:1px solid var(--b2);border-radius:16px;padding:15px 22px;max-width:370px;transform:translateY(90px);opacity:0;transition:all .4s cubic-bezier(.4,0,.2,1);font-size:14px;font-weight:500;box-shadow:0 18px 52px rgba(0,0,0,.5);display:flex;align-items:center;gap:12px}
#toast.show{transform:translateY(0);opacity:1}
.ti{font-size:22px;flex-shrink:0}

/* CONFETTI */
.cf{position:fixed;z-index:99999;pointer-events:none;width:10px;height:10px;border-radius:2px;animation:cfFall 2.9s ease-in forwards}
@keyframes cfFall{0%{opacity:1;transform:translateY(0) rotate(0)}100%{opacity:0;transform:translateY(110vh) rotate(720deg)}}

/* SCROLLBAR */
::-webkit-scrollbar{width:5px}
::-webkit-scrollbar-thumb{background:var(--b2);border-radius:5px}

/* RESPONSIVE */
@media(max-width:900px){
  .sidebar{top:auto;width:100%;height:74px;border-right:none;border-top:1px solid var(--b2);flex-direction:row;align-items:center;justify-content:space-around;padding:0 6px;z-index:200;background:rgba(5,9,26,.92)}
  .sb-logo{display:none}
  .nav-links{flex-direction:row;gap:0;width:100%;justify-content:space-around;overflow:visible}
  .nb{flex-direction:column;gap:4px;padding:8px 4px;border:none;font-size:10px;width:12.5%;text-align:center;border-radius:8px;border-left:none !important;background:transparent !important}
  .nb.act{background:rgba(124,109,255,.12) !important;border-bottom:3px solid var(--a) !important;box-shadow:none !important}
  .nb-ic{font-size:20px}
  .main-content{margin-left:0;padding:14px 14px 88px}
  header{flex-direction:column;gap:12px;align-items:flex-start}
  .act-g{grid-template-columns:repeat(2,1fr)}
  .ach-grid{grid-template-columns:repeat(3,1fr)}
  .yoga-grid{grid-template-columns:repeat(2,1fr)}
  .c3,.c4,.c5,.c6,.c7,.c8,.c9,.c12{grid-column:span 12}
  .hydro-hero{flex-direction:column;align-items:flex-start}
}
@media(min-width:901px) and (max-width:1200px){
  .c3,.c4,.c5,.c6{grid-column:span 6}
  .c8,.c9,.c12{grid-column:span 12}
  .yoga-grid{grid-template-columns:repeat(2,1fr)}
}
</style>
</head>
<body>

<!-- BG -->
<canvas id="stars"></canvas>
<div class="orbs"><div class="orb o1"></div><div class="orb o2"></div><div class="orb o3"></div><div class="orb o4"></div><div class="orb o5"></div></div>

<!-- MODALS -->
<div class="modal-overlay" id="goalModal" onclick="if(event.target===this)closeGoalModal()">
  <div class="modal-box">
    <div class="modal-title">🎯 Set Your Goals</div>
    <div class="goal-row">
      <div class="goal-label">Screen Time Limit &nbsp;<span id="g-st-val">3.0h</span></div>
      <input type="range" id="g-st" min="1" max="8" step="0.5" value="3" oninput="document.getElementById('g-st-val').textContent=this.value+'h'">
    </div>
    <div class="goal-row">
      <div class="goal-label">Daily Focus Minutes &nbsp;<span id="g-fm-val">90m</span></div>
      <input type="range" id="g-fm" min="15" max="240" step="15" value="90" oninput="document.getElementById('g-fm-val').textContent=this.value+'m'">
    </div>
    <div class="goal-row">
      <div class="goal-label">Sleep Target &nbsp;<span id="g-sl-val">8.0h</span></div>
      <input type="range" id="g-sl" min="4" max="12" step="0.5" value="8" oninput="document.getElementById('g-sl-val').textContent=this.value+'h'">
    </div>
    <div class="goal-row">
      <div class="goal-label">Water Goal (glasses) &nbsp;<span id="g-wa-val">8</span></div>
      <input type="range" id="g-wa" min="4" max="16" step="1" value="8" oninput="document.getElementById('g-wa-val').textContent=this.value">
    </div>
    <div style="display:flex;gap:11px;margin-top:26px;justify-content:flex-end">
      <button class="btn btn-g" onclick="closeGoalModal()">Cancel</button>
      <button class="btn btn-p" onclick="saveGoals()">Save Goals</button>
    </div>
  </div>
</div>

<div id="breakBanner">
  <div class="bb-icon">⏰</div>
  <div class="bb-text"><strong>Break time!</strong> You've been focused — stand up, stretch, rest your eyes.</div>
  <div class="bb-close" onclick="dismissBreak()">Dismiss</div>
  <button class="btn btn-t btn-sm" onclick="startBreakTimer();dismissBreak()">Start 5m Break</button>
</div>

<div id="toast"><div class="ti" id="tIcon"></div><div id="tMsg"></div></div>

<!-- AUTHENTICATION OVERLAY -->
<div id="authOverlay" style="position:fixed;inset:0;background:rgba(2,2,2,0.95);backdrop-filter:blur(30px);z-index:9999;display:flex;align-items:center;justify-content:center;opacity:1;transition:opacity 0.6s cubic-bezier(0.2,0.8,0.2,1);">
  <div style="background:rgba(255,255,255,0.02);padding:50px 40px;border-radius:24px;border:1px solid rgba(255,255,255,0.1);max-width:400px;width:90%;text-align:center;box-shadow:0 0 40px rgba(255,255,255,0.05);">
    <h1 style="font-family:var(--f2);font-size:32px;margin-bottom:10px;color:var(--tx);text-shadow:0 0 15px rgba(255,255,255,0.4);font-weight:800;letter-spacing:-1px;">Zenith OS</h1>
    <p style="color:var(--mu);margin-bottom:30px;line-height:1.5;font-size:14px;">Log in to access your digital wellness dashboard.</p>
    
    <div style="display:flex;flex-direction:column;gap:15px;">
      <input type="text" id="authUsername" placeholder="Username" style="width:100%;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.1);padding:14px 18px;border-radius:12px;color:#fff;font-family:var(--f);font-size:15px;outline:none;transition:border-color 0.2s;" onfocus="this.style.borderColor='#ffffff'" onblur="this.style.borderColor='rgba(255,255,255,0.1)'" onkeydown="if(event.key==='Enter') document.getElementById('authPassword').focus()" />
      <input type="password" id="authPassword" placeholder="Password" style="width:100%;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.1);padding:14px 18px;border-radius:12px;color:#fff;font-family:var(--f);font-size:15px;outline:none;transition:border-color 0.2s;" onfocus="this.style.borderColor='#ffffff'" onblur="this.style.borderColor='rgba(255,255,255,0.1)'" onkeydown="if(event.key==='Enter') handleLogin()" />
      <button class="login-btn" onclick="handleLogin()" style="margin-top:10px;background:#ffffff;color:#000000;border:none;padding:15px;border-radius:12px;font-family:var(--f);font-size:16px;font-weight:700;cursor:pointer;transition:all 0.3s;box-shadow:0 0 15px rgba(255,255,255,0.3);">Sign In</button>
    </div>
  </div>
</div>

<style>
.login-btn:hover { background: #e0e0e0; transform: translateY(-2px); box-shadow: 0 0 25px rgba(255,255,255,0.5); }
.login-btn:active { transform: translateY(0); }
  .chat-u { align-self: flex-end; background: var(--a); color: #fff; padding: 10px 14px; border-radius: 14px 14px 0 14px; font-size: 13.5px; box-shadow: 0 4px 15px rgba(124,109,255,0.2); }
  .chat-a { align-self: flex-start; background: rgba(255,255,255,0.08); border: 1px solid var(--b1); padding: 10px 14px; border-radius: 14px 14px 14px 0; font-size: 13.5px; color: #eee; }
</style>

<!-- APP -->
<div class="app-container">
  <nav class="sidebar">
    <div class="sb-logo">
      <div class="sb-logo-icon" style="padding:4px; font-size:inherit;">
        <svg viewBox="0 0 100 100" width="100%" height="100%" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
          <!-- Lotus base -->
          <path d="M50 85 C30 85, 20 60, 50 40 C80 60, 70 85, 50 85 Z" fill="rgba(212,175,55,0.15)" stroke="var(--a)" stroke-width="2"/>
          <path d="M50 85 C15 75, 10 45, 35 35 C40 45, 45 65, 50 85 Z" fill="rgba(16,185,129,0.15)" stroke="var(--a2)" stroke-width="2"/>
          <path d="M50 85 C85 75, 90 45, 65 35 C60 45, 55 65, 50 85 Z" fill="rgba(139,92,246,0.15)" stroke="var(--a3)" stroke-width="2"/>
          <!-- AI Circuit Node -->
          <circle cx="50" cy="55" r="7" fill="var(--bg)" stroke="var(--a)" stroke-width="2"/>
          <circle cx="50" cy="55" r="3" fill="#fff" stroke="none"/>
          <line x1="50" y1="48" x2="50" y2="25" stroke="rgba(255,255,255,0.6)" stroke-width="2"/>
          <circle cx="50" cy="25" r="3" fill="var(--a)" stroke="none"/>
          <line x1="43" y1="52" x2="25" y2="40" stroke="rgba(255,255,255,0.6)" stroke-width="2"/>
          <circle cx="25" cy="40" r="3" fill="var(--a2)" stroke="none"/>
          <line x1="57" y1="52" x2="75" y2="40" stroke="rgba(255,255,255,0.6)" stroke-width="2"/>
          <circle cx="75" cy="40" r="3" fill="var(--a3)" stroke="none"/>
        </svg>
      </div>
      <div class="sb-logo-text" style="background: linear-gradient(135deg, var(--a), #fff); -webkit-background-clip: text; color: transparent;">Zenith</div>
    </div>
    <div class="nav-links">
      <button class="nb act" data-tab="tab-home" onclick="navTo(this)"><span class="nb-ic">🏠</span><span>Home</span></button>
      <button class="nb" data-tab="tab-focus" onclick="navTo(this)"><span class="nb-ic">🎯</span><span>Focus</span></button>
      <button class="nb" data-tab="tab-insights" onclick="navTo(this)"><span class="nb-ic">📊</span><span>Insights</span></button>
      <button class="nb" data-tab="tab-life" onclick="navTo(this)"><span class="nb-ic">🌿</span><span>Life & Habits</span></button>
      <button class="nb" data-tab="tab-yoga" onclick="navTo(this)"><span class="nb-ic">🧘</span><span>Yoga</span></button>
      <button class="nb" data-tab="tab-hydration" onclick="navTo(this)"><span class="nb-ic">💧</span><span>Hydration</span></button>
      <button class="nb" data-tab="tab-progress" onclick="navTo(this)"><span class="nb-ic">🏆</span><span>Journey</span></button>
      <button class="nb" data-tab="tab-ai" onclick="navTo(this)"><span class="nb-ic">🤖</span><span>AI Coach</span></button>
    </div>
  </nav>

  <main class="main-content">
    <header>
      <div class="hdr-title" id="hdrTitle">Home Dashboard</div>
      <div class="hdr-r">
        <div class="pill pill-xp">⚡ <span id="xpVal">340 XP</span> <span style="font-size:12px;opacity:.65;font-weight:500;margin-left:3px" id="lvlName">Focused</span></div>
        <div class="pill pill-streak">🔥 <span id="streakVal">7</span>-day streak</div>
        <button class="btn btn-g btn-sm" onclick="openGoalModal()">🎯 Goals</button>
        <div class="notif-wrap">
          <div class="notif-bell" onclick="toggleNotif()" id="nBell">🔔<div class="notif-badge" id="nBadge" style="display:none">0</div></div>
          <div class="notif-panel" id="nPanel">
            <div class="notif-head">Notifications</div>
            <div id="nItems"></div>
          </div>
        </div>
        <div class="pill pill-clock" id="liveClock">—</div>
      </div>
    </header>

    <!-- HOME -->
    <div class="tab-content act" id="tab-home">
      <div class="bento">
        <div class="card g c4 ga- shim">
          <div class="lbl"><span>🏅</span> Wellness Score</div>
          <div class="score-ring">
            <svg viewBox="0 0 155 155" width="155" height="155">
              <defs><linearGradient id="sg" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" stop-color="#9b8dff"/><stop offset="100%" stop-color="#00e5c0"/></linearGradient></defs>
              <circle class="st-track" cx="77.5" cy="77.5" r="63"/><circle class="sf" id="scoreArc" cx="77.5" cy="77.5" r="63" stroke-dasharray="396" stroke-dashoffset="396"/>
            </svg>
            <div class="score-inner"><div class="sn" id="scoreNum">–</div><div class="sl" id="scoreLvl">–</div></div>
          </div>
          <div class="sparkline-wrap"><svg class="spark-svg" id="sparkSvg" viewBox="0 0 200 44" preserveAspectRatio="none"><defs><linearGradient id="spGrad" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="#7c6dff" stop-opacity=".5"/><stop offset="100%" stop-color="#00e5c0"/></linearGradient></defs></svg></div>
          <div class="tstats">
            <div class="tstat"><div class="v" id="focusSt">0</div><div class="l">Sessions</div></div>
            <div class="tstat"><div class="v" id="chalSt">0</div><div class="l">Challenges</div></div>
            <div class="tstat"><div class="v" id="brthSt">0</div><div class="l">Breathwork</div></div>
          </div>
        </div>
        <div class="card g c8" style="background:linear-gradient(135deg,rgba(124,109,255,.09),rgba(0,229,192,.04));display:flex;flex-direction:column;justify-content:center">
          <div class="lbl"><span>✦</span> Daily Wisdom</div>
          <div class="qbody" id="qText">"Loading…"</div>
          <div class="qattr" id="qAuth">Zenith</div>
          <div style="margin-top:22px"><button class="btn btn-g btn-sm" onclick="newQuote()">↻ Refresh Insight</button></div>
        </div>
        <div class="card g c4">
          <div class="lbl"><span>📱</span> Screen Time Today</div>
          <div class="st-big" id="stBig">–h –m</div>
          <div style="font-size:13px;color:var(--mu)" id="stGoalLine">Goal: –h</div>
          <div class="prog-t"><div class="prog-f" id="stBar" style="width:0%;background:linear-gradient(90deg,var(--a2),var(--err))"></div></div>
          <div class="prog-tks"><span>0h</span><span id="stGoalTk">3h</span><span>8h</span></div>
          <div id="stChip" style="margin-top:13px"></div>
        </div>
        <div class="card g c8">
          <div class="lbl"><span>⚡</span> Quick Actions</div>
          <div class="act-g">
            <button class="act-b" onclick="actDND()"><div class="ai">🔕</div><div class="al">Do Not Disturb</div></button>
            <button class="act-b" onclick="actGray()" id="grayB"><div class="ai">🐼</div><div class="al">Grayscale</div></button>
            <button class="act-b" onclick="actDetox()"><div class="ai">📵</div><div class="al">Social Detox</div></button>
            <button class="act-b" onclick="actStretch()"><div class="ai">🤸</div><div class="al">Stretch Break</div></button>
            <button class="act-b" onclick="navToBtn('tab-focus')"><div class="ai">☕</div><div class="al">Take a Break</div></button>
            <button class="act-b" onclick="openGoalModal()"><div class="ai">🎯</div><div class="al">Edit Goals</div></button>
            <button class="act-b" onclick="navToBtn('tab-yoga')"><div class="ai">🧘</div><div class="al">Quick Yoga</div></button>
            <button class="act-b" onclick="actNight()" id="nightB"><div class="ai">🌙</div><div class="al">Night Mode</div></button>
          </div>
        </div>
      </div>
    </div>

    <!-- FOCUS -->
    <div class="tab-content" id="tab-focus">
      <div class="bento">
        <div class="card g c6">
          <div class="lbl"><span>🎯</span> Deep Focus Timer</div>
          <div class="mp-row">
            <div class="mp act" onclick="setMode(this,25,'Focus')">25m Block</div>
            <div class="mp" onclick="setMode(this,50,'Deep Work')">50m Deep</div>
            <div class="mp" onclick="setMode(this,5,'Break')">5m Break</div>
            <div class="mp" onclick="setMode(this,15,'Long Break')">15m Break</div>
          </div>
          <div class="timer-face">
            <div class="tnum" id="timerDisp">25:00</div>
            <div style="font-size:12px;color:var(--mu);letter-spacing:1.5px;text-transform:uppercase;margin-top:7px" id="timerStat">Ready · Click Start</div>
          </div>
          <div class="tiny-p"><div class="tiny-pf" id="tProg" style="width:0%"></div></div>
          <div style="text-align:center;font-size:12px;color:var(--mu);margin-bottom:11px" id="timerSub">Sessions today: 0</div>
          <div style="display:flex;gap:10px;justify-content:center">
            <button class="btn btn-p" id="timerBtn" onclick="toggleTimer()">▶ Start Focus</button>
            <button class="btn btn-g" onclick="resetTimer()">↺ Reset</button>
            <button class="btn btn-g" id="sndBtn" onclick="cycleSnd()" title="Ambient Sound">🔇 Sound</button>
          </div>
          <div class="sound-opts" id="sndOpts">
            <div class="sound-btn act" data-snd="none" onclick="setSnd('none',this)">None</div>
            <div class="sound-btn" data-snd="white" onclick="setSnd('white',this)">White Noise</div>
            <div class="sound-btn" data-snd="rain" onclick="setSnd('rain',this)">Rain</div>
            <div class="sound-btn" data-snd="binaural" onclick="setSnd('binaural',this)">Binaural</div>
          </div>
        </div>
        <div class="card g c6 gb-">
          <div class="lbl"><span>🌿</span> Guided Breathing</div>
          <div class="b-modes">
            <div class="bm act" onclick="setBreathMode('478',this)">4-7-8 Relax</div>
            <div class="bm" onclick="setBreathMode('box',this)">Box (4×4)</div>
            <div class="bm" onclick="setBreathMode('22',this)">2-2 Calm</div>
          </div>
          <div class="breath-sc">
            <div class="breath-ring" id="bRing" onclick="toggleBreath()">
              <div class="br-inner" id="bLabel">Tap to<br>Begin</div>
            </div>
            <div class="breath-phase" id="bPhase">Inhale 4 · Hold 7 · Exhale 8</div>
            <div class="breath-cyc" id="bCyc">0 cycles</div>
          </div>
          <div style="display:flex;gap:10px;justify-content:center;margin-top:12px">
            <button class="btn btn-t" id="bBtn" onclick="toggleBreath()">▶ Start Flow</button>
            <button class="btn btn-g" onclick="resetBreath()">↺ Reset</button>
          </div>
        </div>
        <div class="card g c6">
          <div class="lbl"><span>🧠</span> Mindfulness Today</div>
          <div style="display:flex;align-items:center;gap:18px;margin-top:8px">
            <div style="font-family:var(--f2);font-size:52px;font-weight:800;color:var(--a2);line-height:1" id="mindMins">15</div>
            <div><div style="font-size:14px;font-weight:600">minutes mindful</div><div style="font-size:13px;color:var(--mu);margin-top:4px" id="mindSub">2 breathwork sessions</div></div>
          </div>
          <div class="prog-t" style="margin-top:18px"><div class="prog-f" id="mindBar" style="width:0%;background:linear-gradient(90deg,var(--a),var(--a2))"></div></div>
          <div style="font-size:12px;color:var(--mu);margin-top:5px">Daily Goal: 30 minutes</div>
        </div>
        <div class="card g c6" style="border-color:rgba(255,107,157,.18);background:linear-gradient(135deg,rgba(255,107,157,.06),rgba(255,179,71,.03))">
          <div class="lbl"><span>💡</span> Smart Detox Tip</div>
          <div style="font-size:17px;line-height:1.72;margin-top:10px" id="tipText">Loading…</div>
          <button class="btn btn-g btn-sm" style="margin-top:18px" onclick="refreshTip()">↻ Get Another Tip</button>
        </div>
      </div>
    </div>

    <!-- INSIGHTS -->
    <div class="tab-content" id="tab-insights">
      <div class="bento">
        <div class="card g c8">
          <div class="lbl"><span>📊</span> Weekly Perspective</div>
          <div class="wleg">
            <div class="wl"><span class="wlc" style="background:var(--err)"></span>Screen Time (h)</div>
            <div class="wl"><span class="wlc" style="background:var(--a)"></span>Focus Time (h)</div>
            <div class="wl"><span class="wlc" style="background:var(--a2)"></span>Goal Target</div>
          </div>
          <div class="chat-w" style="height:260px"><canvas id="weeklyChart"></canvas></div>
        </div>
        <div class="card g c4">
          <div class="lbl"><span>🥗</span> Digital Diet Fit</div>
          <div class="chat-w" style="height:220px"><canvas id="radarChart"></canvas></div>
          <div style="display:flex;gap:14px;font-size:12px;color:var(--mu);margin-top:12px;justify-content:center">
            <span style="display:flex;align-items:center;gap:5px"><span style="width:9px;height:9px;border-radius:50%;background:var(--a);display:inline-block"></span>Current</span>
            <span style="display:flex;align-items:center;gap:5px"><span style="width:9px;height:9px;border-radius:50%;background:var(--a2);display:inline-block"></span>Ideal</span>
          </div>
        </div>
        <div class="card g c8">
          <div class="lbl"><span>🗓️</span> Consistency Heatmap (Last 35 Days)</div>
          <div style="display:flex;gap:8px;align-items:center;font-size:12px;color:var(--mu);margin-bottom:8px;flex-wrap:wrap">
            <span>Low Focus</span>
            <span style="width:13px;height:13px;border-radius:4px;background:rgba(255,255,255,.06);display:inline-block"></span>
            <span style="width:13px;height:13px;border-radius:4px;background:rgba(0,229,192,.22);display:inline-block"></span>
            <span style="width:13px;height:13px;border-radius:4px;background:rgba(0,229,192,.52);display:inline-block"></span>
            <span style="width:13px;height:13px;border-radius:4px;background:rgba(0,229,192,.88);display:inline-block"></span>
            <span>Deep Focus</span>
          </div>
          <div class="hm-grid" id="hmGrid"></div>
        </div>
        <div class="card g c4">
          <div class="lbl"><span>📲</span> App Usage Breakdown</div>
          <div class="chat-w" style="height:150px"><canvas id="usageChart"></canvas></div>
          <div class="ul" id="usageList"></div>
        </div>
      </div>
    </div>

    <!-- LIFE & HABITS -->
    <div class="tab-content" id="tab-life">
      <div class="bento">
        <div class="card g c6">
          <div class="lbl"><span>✅</span> Daily Habits <span style="margin-left:auto;font-size:12px;color:var(--a2)" id="habScore">0/5</span></div>
          <div class="hab-list" id="habList"></div>
        </div>
        <div class="card g c6">
          <div class="lbl"><span>💤</span> Core Vitals</div>
          <div class="sw-row">
            <div class="sw-box">
              <div class="swl">Sleep Log</div>
              <div class="sw-big" id="sleepBig">7.2h</div>
              <div id="sleepChip"></div>
              <input type="range" id="sleepSlider" min="3" max="12" step="0.5" value="7.2" oninput="updateSleepUI(parseFloat(this.value));debounceSleep(parseFloat(this.value))">
            </div>
            <div class="sw-box">
              <div class="swl">Hydration</div>
              <div class="sw-big" id="waterBig">5/8</div>
              <div class="wdots" id="wDots"></div>
              <button class="btn btn-t btn-sm" style="margin-top:14px;width:100%" onclick="addWater()">+ Drink Glass</button>
            </div>
          </div>
        </div>
        <div class="card g c6" style="border-color:rgba(255,179,71,.15);background:linear-gradient(135deg,rgba(255,179,71,.05),rgba(255,107,157,.03))">
          <div class="lbl"><span>📓</span> Reflection Journal</div>
          <textarea class="j-input" id="jInput" placeholder="What are you grateful for today?…" maxlength="300"></textarea>
          <button class="btn btn-p btn-sm" style="margin-top:11px;width:100%" onclick="saveJournal()">Save Entry ✦</button>
          <div class="journal-list" id="jList"></div>
        </div>
        <div class="card g c6">
          <div class="lbl"><span>🎭</span> Mood Check-In</div>
          <div class="mood-grid">
            <div class="mb" onclick="logMood('amazing',this)"><div class="me">🤩</div><div class="ml">Amazing</div></div>
            <div class="mb" onclick="logMood('good',this)"><div class="me">😊</div><div class="ml">Good</div></div>
            <div class="mb" onclick="logMood('okay',this)"><div class="me">😐</div><div class="ml">Okay</div></div>
            <div class="mb" onclick="logMood('tired',this)"><div class="me">😴</div><div class="ml">Tired</div></div>
            <div class="mb" onclick="logMood('stressed',this)"><div class="me">😤</div><div class="ml">Stressed</div></div>
          </div>
          <div style="font-size:12px;font-weight:600;margin-top:18px;color:var(--mu)">Recent Logs:</div>
          <div class="mood-hist" id="mHist"></div>
        </div>
      </div>
    </div>

    <!-- YOGA -->
    <div class="tab-content" id="tab-yoga">
      <div id="yogaCompleteBanner" class="yoga-complete-banner">
        <div style="font-size:32px;margin-bottom:8px">🧘‍♀️</div>
        <div style="font-family:var(--f2);font-size:20px;font-weight:700;margin-bottom:6px">Yoga Session Complete!</div>
        <div style="color:var(--mu);font-size:14px">Amazing work. +35 XP earned. Your body thanks you 🙏</div>
      </div>
      <div class="body-filter-bar" id="bodyFilterBar">
        <button class="bfb act" data-filter="all" onclick="filterYoga('all',this)">All Poses</button>
        <button class="bfb" data-filter="neck" onclick="filterYoga('neck',this)">Neck &amp; Shoulders</button>
        <button class="bfb" data-filter="back" onclick="filterYoga('back',this)">Back &amp; Spine</button>
        <button class="bfb" data-filter="hip" onclick="filterYoga('hip',this)">Hips &amp; Legs</button>
        <button class="bfb" data-filter="core" onclick="filterYoga('core',this)">Core</button>
        <button class="bfb" data-filter="full" onclick="filterYoga('full',this)">Full Body</button>
      </div>
      <div class="yoga-grid" id="yogaGrid"></div>
    </div>

    <!-- HYDRATION CORNER -->
    <div class="tab-content" id="tab-hydration">
      <div class="bento">
        <div class="card g c6" style="background:linear-gradient(135deg,rgba(0,229,192,.06),rgba(124,109,255,.04))">
          <div class="lbl"><span>💧</span> Hydration Corner</div>
          <div class="hydro-hero">
            <div class="hydro-vessel">
              <svg viewBox="0 0 90 150" xmlns="http://www.w3.org/2000/svg">
                <defs>
                  <linearGradient id="bottleGrad" x1="0" y1="0" x2="1" y2="0">
                    <stop offset="0%" stop-color="rgba(0,229,192,0.15)"/>
                    <stop offset="100%" stop-color="rgba(124,109,255,0.1)"/>
                  </linearGradient>
                  <clipPath id="waterClip"><rect x="10" y="20" width="70" height="122" rx="8"/></clipPath>
                </defs>
                <!-- bottle outline -->
                <path d="M 32 10 L 32 22 Q 10 28 10 44 L 10 134 Q 10 144 20 144 L 70 144 Q 80 144 80 134 L 80 44 Q 80 28 58 22 L 58 10 Z" fill="url(#bottleGrad)" stroke="rgba(0,229,192,0.5)" stroke-width="1.5"/>
                <!-- cap -->
                <rect x="30" y="4" width="30" height="12" rx="4" fill="rgba(0,229,192,0.3)" stroke="rgba(0,229,192,0.6)" stroke-width="1"/>
                <!-- water fill -->
                <g clip-path="url(#waterClip)">
                  <rect id="waterFill" x="10" y="90" width="70" height="56" fill="rgba(0,229,192,0.35)" rx="2"/>
                  <path id="waveTop" d="M 10 90 Q 22 84 45 90 Q 68 96 80 90 L 80 96 L 10 96 Z" fill="rgba(0,229,192,0.55)" class="hydro-wave"/>
                </g>
                <!-- level markers -->
                <text x="84" y="52" fill="rgba(232,234,246,0.3)" font-size="8" font-family="Inter">100%</text>
                <text x="84" y="88" fill="rgba(232,234,246,0.3)" font-size="8" font-family="Inter">50%</text>
                <text x="84" y="130" fill="rgba(232,234,246,0.3)" font-size="8" font-family="Inter">0%</text>
                <line x1="80" y1="50" x2="83" y2="50" stroke="rgba(232,234,246,0.2)" stroke-width="1"/>
                <line x1="80" y1="88" x2="83" y2="88" stroke="rgba(232,234,246,0.2)" stroke-width="1"/>
              </svg>
            </div>
            <div style="flex:1">
              <div style="font-family:var(--f2);font-size:48px;font-weight:800;color:var(--a2);line-height:1" id="hydGlasses">5</div>
              <div style="font-size:14px;color:var(--mu);margin-top:4px">of <span id="hydGoal">8</span> glasses today</div>
              <div style="margin-top:12px">
                <div class="prog-t" style="height:8px"><div class="prog-f" id="hydBar" style="width:62.5%;background:linear-gradient(90deg,var(--a),var(--a2))"></div></div>
              </div>
              <div style="font-size:13px;color:var(--mu);margin-top:6px" id="hydStatus">Keep going! 3 more glasses to reach your goal.</div>
            </div>
          </div>
          <div class="intake-buttons">
            <button class="intake-btn" onclick="logIntake(150,'☕ Espresso')">☕ Espresso<br><span style="font-size:11px;opacity:.7">150ml</span></button>
            <button class="intake-btn" onclick="logIntake(250,'💧 Small Glass')">💧 Small<br><span style="font-size:11px;opacity:.7">250ml</span></button>
            <button class="intake-btn" onclick="logIntake(400,'🥤 Large Glass')">🥤 Large<br><span style="font-size:11px;opacity:.7">400ml</span></button>
            <button class="intake-btn" onclick="logIntake(500,'🍶 Bottle')">🍶 Bottle<br><span style="font-size:11px;opacity:.7">500ml</span></button>
          </div>
        </div>

        <div class="card g c6">
          <div class="lbl"><span>📈</span> Daily Hydration Stats</div>
          <div class="hydro-stats-grid">
            <div class="hydro-stat">
              <div class="hydro-stat-v" id="hydTotalMl">1250</div>
              <div class="hydro-stat-l">ml consumed</div>
            </div>
            <div class="hydro-stat">
              <div class="hydro-stat-v" id="hydPercent">62%</div>
              <div class="hydro-stat-l">of daily goal</div>
            </div>
            <div class="hydro-stat">
              <div class="hydro-stat-v" id="hydStreak">5</div>
              <div class="hydro-stat-l">day streak 🔥</div>
            </div>
            <div class="hydro-stat">
              <div class="hydro-stat-v" id="hydNext">45m</div>
              <div class="hydro-stat-l">next reminder</div>
            </div>
          </div>
          <div class="chat-w" style="height:170px;margin-top:18px"><canvas id="hydChart"></canvas></div>
        </div>

        <div class="card g c6">
          <div class="lbl"><span>🕐</span> Intake Log</div>
          <div class="hydro-log" id="hydLog">
            <div class="hydro-log-items" id="hydLogItems">
              <div style="font-size:13px;color:var(--mu);text-align:center;padding:20px">No entries yet. Start drinking!</div>
            </div>
          </div>
        </div>

        <div class="card g c6">
          <div class="lbl"><span>⏰</span> Smart Reminders</div>
          <div class="hydro-reminder-row">
            <div class="hydro-reminder-icon">🔔</div>
            <div class="hydro-reminder-text">
              <div style="font-weight:600;font-size:14px">Every 45 minutes</div>
              <div style="font-size:12px;color:var(--mu);margin-top:2px">Gentle nudge to drink water</div>
            </div>
            <label class="hydro-reminder-toggle">
              <input type="checkbox" id="remToggle" onchange="toggleReminder(this.checked)" checked>
              <span class="hrt-slider"></span>
            </label>
          </div>
          <div class="hydro-reminder-row" style="margin-top:10px">
            <div class="hydro-reminder-icon">🌅</div>
            <div class="hydro-reminder-text">
              <div style="font-weight:600;font-size:14px">Morning kickstart</div>
              <div style="font-size:12px;color:var(--mu);margin-top:2px">Drink a glass right after waking up</div>
            </div>
            <label class="hydro-reminder-toggle">
              <input type="checkbox" id="morningToggle" onchange="toast('🌅','Morning water reminder '+( this.checked ?'on':'off'))" checked>
              <span class="hrt-slider"></span>
            </label>
          </div>
          <div class="hydro-reminder-row" style="margin-top:10px">
            <div class="hydro-reminder-icon">🌙</div>
            <div class="hydro-reminder-text">
              <div style="font-weight:600;font-size:14px">Evening checkpoint</div>
              <div style="font-size:12px;color:var(--mu);margin-top:2px">Ensure you hit 80%+ before bed</div>
            </div>
            <label class="hydro-reminder-toggle">
              <input type="checkbox" id="eveningToggle" onchange="toast('🌙','Evening reminder '+( this.checked ?'on':'off'))" checked>
              <span class="hrt-slider"></span>
            </label>
          </div>
          <div style="margin-top:20px;padding:16px;background:rgba(0,229,192,.06);border:1px solid rgba(0,229,192,.18);border-radius:14px">
            <div style="font-size:13px;font-weight:600;margin-bottom:8px">💡 Hydration Tips</div>
            <div style="font-size:12px;color:var(--mu);line-height:1.7" id="hydTip">Loading tip…</div>
          </div>
        </div>
      </div>
    </div>

    <!-- PROGRESS / JOURNEY -->
    <div class="tab-content" id="tab-progress">
      <div class="bento">
        <div class="card g c6">
          <div class="lbl"><span>🏆</span> Daily Quests <span style="margin-left:auto;font-size:11px;color:var(--mu)">Tap to complete</span></div>
          <div class="ch-list" id="chalList"></div>
        </div>
        <div class="card g c6">
          <div class="lbl"><span>🎖️</span> Trophy Room <span style="margin-left:auto;font-size:13px;color:var(--a)" id="achCount">0/12 unlocked</span></div>
          <div class="ach-grid" id="achGrid"></div>
        </div>
      </div>
    </div>

    <!-- AI COACH -->
    <div class="tab-content" id="tab-ai">
      <div class="bento">
        <div class="card g c8">
          <div class="lbl"><span>🤖</span> Zenith AI Coach <span style="margin-left:auto;font-size:11px;color:var(--mu)">Powered by Grok</span></div>
          <div id="aiChat" style="height:400px;overflow-y:auto;padding:10px;display:flex;flex-direction:column;gap:12px;margin-bottom:15px;background:rgba(0,0,0,0.2);border-radius:12px">
            <div style="background:rgba(255,255,255,0.05);padding:10px 14px;border-radius:12px;max-width:85%;align-self:flex-start;font-size:13.5px">Hello! I'm your Zenith AI Coach. Ready for a digital detox analysis?</div>
          </div>
          <div style="display:flex;gap:10px">
            <input type="text" id="aiInp" placeholder="Ask your coach anything..." style="flex:1;background:rgba(255,255,255,0.05);border:1px solid var(--b1);padding:12px 16px;border-radius:10px;color:#fff;font-size:14px" onkeyup="if(event.key==='Enter')askAI()">
            <button class="btn btn-p" onclick="askAI()">Send</button>
          </div>
        </div>
        <div class="card g c4">
          <div class="lbl"><span>🧠</span> AI Analysis</div>
          <p style="font-size:13px;color:var(--mu);line-height:1.6;margin-bottom:15px">Get a comprehensive clinical analysis of your wellness metrics from the last 24 hours.</p>
          <button class="btn btn-g" style="width:100%" onclick="analyzeAI()">Run Analysis</button>
          <div id="anaRes" style="margin-top:20px;font-size:13px;color:#fff;line-height:1.5;padding:12px;border-left:2px solid var(--a);background:rgba(124,109,255,0.05);display:none"></div>
        </div>
      </div>
    </div>

  </main>
</div>

<script>
// ═══════════════════════════════════════════════════════════
//  NAVIGATION
// ═══════════════════════════════════════════════════════════
const TAB_TITLES = {
  'tab-home':'Home Dashboard','tab-focus':'Focus & Breathe',
  'tab-insights':'Insights','tab-life':'Life & Habits',
  'tab-yoga':'Yoga & Movement','tab-hydration':'Hydration Corner',
  'tab-progress':'Journey & Trophies','tab-ai':'Zenith AI Coach'
};
function navTo(btnEl){
  const tid = btnEl.getAttribute('data-tab');
  document.querySelectorAll('.nb').forEach(b=>b.classList.remove('act'));
  btnEl.classList.add('act');
  document.querySelectorAll('.tab-content').forEach(t=>t.classList.remove('act'));
  document.getElementById(tid).classList.add('act');
  document.getElementById('hdrTitle').textContent = TAB_TITLES[tid]||tid;
  if(tid==='tab-insights') resizeCharts();
  if(tid==='tab-yoga') renderYoga();
  if(tid==='tab-hydration') refreshHydration();
  if(tid==='tab-ai') scrollChat();
  window.scrollTo({top:0,behavior:'smooth'});
}
function scrollChat(){ const c=document.getElementById('aiChat'); c.scrollTop=c.scrollHeight; }

async function askAI(){
  const inp=document.getElementById('aiInp');
  const msg=inp.value.trim();
  if(!msg)return;
  inp.value='';
  addAI('user', msg);
  const loading = addAI('ai', 'Thinking...');
  try {
    const res=await fetch('/api/ai_coach',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:msg,mode:'chat'})});
    const data=await res.json();
    loading.textContent = data.reply;
    scrollChat();
  } catch(e) { loading.textContent = 'Error connecting to AI.'; }
}

async function analyzeAI(){
  const btn=event.target; btn.disabled=true; btn.textContent='Analyzing...';
  const resBox=document.getElementById('anaRes'); resBox.style.display='block'; resBox.textContent='Gathering metrics and processing...';
  try {
    const res=await fetch('/api/ai_coach',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({mode:'analysis'})});
    const data=await res.json();
    resBox.textContent = data.reply;
  } catch(e) { resBox.textContent = 'Analysis failed.'; }
  btn.disabled=false; btn.textContent='Run Analysis';
}

function addAI(role, txt){
  const chat=document.getElementById('aiChat');
  const div=document.createElement('div');
  div.className = role==='user'?'chat-u':'chat-a';
  div.style = role==='user'?'background:var(--a);padding:10px 14px;border-radius:12px;max-width:85%;align-self:flex-end;font-size:13.5px;color:#fff':'background:rgba(255,255,255,0.08);padding:10px 14px;border-radius:12px;max-width:85%;align-self:flex-start;font-size:13.5px;border:1px solid var(--b1)';
  div.textContent = txt;
  chat.appendChild(div);
  scrollChat();
  return div;
}
function navToBtn(tid){ const b=document.querySelector(`.nb[data-tab="${tid}"]`);if(b)navTo(b); }
let chartInited=false;
function resizeCharts(){ if(!chartInited){initCharts();chartInited=true;} else Object.values(Chart.instances).forEach(c=>c.resize()); }

// ═══════════════════════════════════════════════════════════
//  STAR CANVAS
// ═══════════════════════════════════════════════════════════
(()=>{
  const c=document.getElementById('stars'),ctx=c.getContext('2d');
  let W,H,stars=[];
  const sz=()=>{W=c.width=window.innerWidth;H=c.height=window.innerHeight;};
  sz();addEventListener('resize',sz);
  for(let i=0;i<220;i++) stars.push({x:Math.random()*1e4,y:Math.random()*1e4,r:Math.random()*1.4+.2,a:Math.random(),da:(Math.random()*.008+.002)*(Math.random()<.5?1:-1)});
  (function draw(){ctx.clearRect(0,0,W,H);stars.forEach(s=>{s.a+=s.da;if(s.a>1||s.a<0)s.da*=-1;ctx.globalAlpha=Math.max(0,Math.min(1,s.a))*.7;ctx.fillStyle='#fff';ctx.beginPath();ctx.arc(s.x%W,s.y%H,s.r,0,Math.PI*2);ctx.fill()});requestAnimationFrame(draw);})();
})();

// ═══════════════════════════════════════════════════════════
//  UTILS
// ═══════════════════════════════════════════════════════════
const fmt=n=>n<10?'0'+n:''+n;
let toastTimer;
function toast(icon,msg,color='var(--a2)'){
  document.getElementById('tIcon').textContent=icon;
  document.getElementById('tMsg').textContent=msg;
  const t=document.getElementById('toast');
  t.style.borderColor=color;t.classList.add('show');
  clearTimeout(toastTimer);toastTimer=setTimeout(()=>t.classList.remove('show'),3300);
}
let activeUser = "Guest";

async function handleLogin() {
  const u = document.getElementById('authUsername').value.trim();
  const p = document.getElementById('authPassword').value.trim();
  if(!u || !p) return toast('⚠️', 'Please enter username and password', 'var(--err)');
  
  try {
    const res = await fetch('/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: u, password: p })
    });
    const d = await res.json();
    if(res.ok && d.status === 'ok') {
      activeUser = d.name;
      document.getElementById('authOverlay').style.opacity = '0';
      setTimeout(() => document.getElementById('authOverlay').style.display = 'none', 600);
      toast('✅', `Access Granted: ${d.name}`, 'var(--tx)');
      const audio = new Audio('https://github.com/interactive-learning-tools/audio/raw/main/success-chime.mp3');
      audio.volume = 0.5;
      audio.play().catch(e => console.log('Audio overlap'));
      await refreshState();
    } else {
      toast('🚫', 'Invalid credentials', 'var(--err)');
      document.getElementById('authPassword').value = '';
    }
  } catch(e){ console.error(e); }
}

function confetti(x,y){
  const cols=['#9b8dff','#00e5c0','#ff6b9d','#ffb347','#4cde80','#fff','#7c6dff'];
  for(let i=0;i<72;i++){
    const p=document.createElement('div');p.className='cf';
    p.style.cssText=`left:${x+Math.random()*200-100}px;top:${y-10}px;background:${cols[i%cols.length]};border-radius:${Math.random()<.4?'50%':'2px'};animation-duration:${2.2+Math.random()*1.8}s;animation-delay:${Math.random()*.5}s`;
    document.body.appendChild(p);setTimeout(()=>p.remove(),5000);
  }
}
const tickClock=()=>{const n=new Date();document.getElementById('liveClock').textContent=fmt(n.getHours())+':'+fmt(n.getMinutes());};
tickClock();setInterval(tickClock,15000);

// sparkline
function drawSparkline(data){
  const svg=document.getElementById('sparkSvg');if(!svg||!data.length)return;
  svg.innerHTML=`<defs><linearGradient id="spGrad" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="#7c6dff" stop-opacity=".6"/><stop offset="100%" stop-color="#00e5c0" stop-opacity=".9"/></linearGradient></defs>`;
  const W=200,H=44,min=Math.min(...data)-5,max=Math.max(...data)+5,rng=max-min||10;
  const pts=data.map((v,i)=>`${(i/(data.length-1))*W},${H-(((v-min)/rng)*H)}`);
  svg.innerHTML+=`<path d="M${pts.join('L')}L${W},${H}L0,${H}Z" fill="url(#spGrad)" opacity=".18"/>`;
  svg.innerHTML+=`<path d="M${pts.join('L')}" fill="none" stroke="url(#spGrad)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>`;
  const last=pts[pts.length-1].split(',');
  svg.innerHTML+=`<circle cx="${last[0]}" cy="${last[1]}" r="4" fill="#00e5c0"/>`;
}

// ═══════════════════════════════════════════════════════════
//  STATE
// ═══════════════════════════════════════════════════════════
let quoteCache=null,tipCache='';
async function refreshState(){
  try{
    const d=await(await fetch('/api/state')).json();
    if(d.user_name) {
      document.getElementById('hdrTitle').textContent = `Welcome, ${d.user_name}`;
    } else {
      document.getElementById('hdrTitle').textContent = `Home Dashboard`;
    }
    const circ=2*Math.PI*63;
    document.getElementById('scoreArc').style.strokeDashoffset=circ*(1-d.wellness_score/100);
    document.getElementById('scoreNum').textContent=d.wellness_score;
    document.getElementById('scoreLvl').textContent=d.score_level;
    document.getElementById('focusSt').textContent=d.focus_sessions_today;
    document.getElementById('chalSt').textContent=d.challenges_completed;
    document.getElementById('brthSt').textContent=d.breathing_sessions;
    document.getElementById('xpVal').textContent=d.total_xp+' XP';
    document.getElementById('lvlName').textContent=d.level_name;
    document.getElementById('streakVal').textContent=d.detox_streak;
    const st=d.screen_time_today,g=d.goal_screen_time;
    const h=Math.floor(st),m=Math.round((st%1)*60);
    document.getElementById('stBig').textContent=h+'h '+fmt(m)+'m';
    document.getElementById('stGoalLine').textContent='Daily Limit: '+g+'h';
    document.getElementById('stGoalTk').textContent=g+'h';
    document.getElementById('stBar').style.width=Math.min(100,(st/8)*100)+'%';
    document.getElementById('stChip').innerHTML=(st-g)>0?`<span class="chip cr">▲ ${+(st-g).toFixed(1)}h over goal</span>`:`<span class="chip cg">▼ ${+(g-st).toFixed(1)}h remaining</span>`;
    if(!quoteCache){quoteCache=d.quote;document.getElementById('qText').textContent='"'+d.quote.text+'"';document.getElementById('qAuth').textContent=d.quote.author;}
    if(!tipCache){tipCache=d.tip;document.getElementById('tipText').textContent=tipCache;}
    document.getElementById('mindMins').textContent=d.mindfulness_minutes;
    document.getElementById('mindSub').textContent=d.breathing_sessions+' breathwork session'+(d.breathing_sessions!==1?'s':'');
    document.getElementById('mindBar').style.width=Math.min(100,(d.mindfulness_minutes/30)*100)+'%';
    updateSleepUI(d.sleep_hours);updateWaterUI(d.water_glasses,8);
    const hDone=d.habits.filter(h=>h.done).length;
    document.getElementById('habScore').textContent=hDone+'/'+d.habits.length;
    document.getElementById('timerSub').textContent='Sessions today: '+d.focus_sessions_today;
    const badge=document.getElementById('nBadge');
    badge.style.display=d.unread_notifications>0?'flex':'none';badge.textContent=d.unread_notifications;
    drawSparkline(d.score_history);
    renderAchievements(d.achievements_unlocked);
  }catch(e){console.error(e);}
}
async function newQuote(){ const d=await(await fetch('/api/state')).json();quoteCache=d.quote;document.getElementById('qText').textContent='"'+d.quote.text+'"';document.getElementById('qAuth').textContent=d.quote.author; }
async function refreshTip(){ const d=await(await fetch('/api/state')).json();tipCache=d.tip;document.getElementById('tipText').textContent=tipCache; }

// ═══════════════════════════════════════════════════════════
//  ACHIEVEMENTS
// ═══════════════════════════════════════════════════════════
const ACHIEVEMENTS=[
  {id:'first_breath',icon:'🌬️',title:'First Breath',xp:25},{id:'streak_7',icon:'🔥',title:'Streak Master',xp:100},
  {id:'focus_5',icon:'🎯',title:'Focus Champ',xp:80},{id:'hydrated',icon:'💧',title:'Hydrated Hero',xp:40},
  {id:'sleep_champ',icon:'💤',title:'Sleep Champ',xp:50},{id:'challenge_3',icon:'🏆',title:'Challenger',xp:70},
  {id:'mood_log',icon:'🎭',title:'Mood Tracker',xp:30},{id:'social_detox',icon:'📵',title:'Detox Warrior',xp:90},
  {id:'zen_master',icon:'🧘',title:'Zen Master',xp:150},{id:'journaler',icon:'📓',title:'Journaler',xp:45},
  {id:'habit_5',icon:'✅',title:'Habit Hero',xp:120},{id:'mindful_30',icon:'🌿',title:'Mindful',xp:60}
];
let prevUnlocked=new Set();
function renderAchievements(unlocked){
  const grid=document.getElementById('achGrid');const ul=new Set(unlocked);grid.innerHTML='';let cnt=0;
  ACHIEVEMENTS.forEach(a=>{
    const on=ul.has(a.id);if(on)cnt++;
    const d=document.createElement('div');d.className='ach-item'+(on?' unlocked':'');
    if(on&&!prevUnlocked.has(a.id))d.classList.add('just-unlocked');
    d.innerHTML=`<div class="ach-icon">${a.icon}</div><div class="ach-name">${a.title}</div><div class="ach-xp">+${a.xp}</div>`;
    grid.appendChild(d);
    if(on&&!prevUnlocked.has(a.id))toast('🎖️','Achievement: '+a.title+'! +'+a.xp+' XP','#ffb347');
  });
  prevUnlocked=ul;document.getElementById('achCount').textContent=cnt+' / '+ACHIEVEMENTS.length+' unlocked';
}

// ═══════════════════════════════════════════════════════════
//  NOTIFICATIONS
// ═══════════════════════════════════════════════════════════
function toggleNotif(){ const p=document.getElementById('nPanel');p.classList.toggle('open');if(p.classList.contains('open'))loadNotifs(); }
async function loadNotifs(){
  const data=await(await fetch('/api/notifications')).json();const el=document.getElementById('nItems');el.innerHTML='';
  data.slice(0,8).forEach(n=>{ el.innerHTML+=`<div class="notif-item${n.unread?' unread':''}"><div class="ni-icon">${n.icon}</div><div><div class="ni-text">${n.text}</div><div class="ni-time">${n.time}</div></div></div>`; });
  document.getElementById('nBadge').style.display='none';
}
document.addEventListener('click',e=>{ if(!document.getElementById('nPanel').contains(e.target)&&!document.getElementById('nBell').contains(e.target)) document.getElementById('nPanel').classList.remove('open'); });

// ═══════════════════════════════════════════════════════════
//  GOALS
// ═══════════════════════════════════════════════════════════
function openGoalModal(){document.getElementById('goalModal').classList.add('open');}
function closeGoalModal(){document.getElementById('goalModal').classList.remove('open');}
async function saveGoals(){
  const goals={screen_time:parseFloat(document.getElementById('g-st').value),focus_mins:parseInt(document.getElementById('g-fm').value),sleep:parseFloat(document.getElementById('g-sl').value),water:parseInt(document.getElementById('g-wa').value)};
  await fetch('/api/set_goal',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(goals)});
  closeGoalModal();toast('🎯','Goals saved! Stay consistent','var(--a)');await refreshState();
}

// ═══════════════════════════════════════════════════════════
//  CHARTS
// ═══════════════════════════════════════════════════════════
async function initCharts(){
  const dW=await(await fetch('/api/weekly')).json();
  new Chart(document.getElementById('weeklyChart').getContext('2d'),{
    type:'bar',data:{labels:dW.labels,datasets:[
      {label:'Screen',data:dW.screen,backgroundColor:'rgba(255,95,126,.5)',borderColor:'rgba(255,95,126,.85)',borderWidth:1.5,borderRadius:6,barPercentage:0.6},
      {label:'Focus',data:dW.focus,backgroundColor:'rgba(124,109,255,.5)',borderColor:'rgba(124,109,255,.85)',borderWidth:1.5,borderRadius:6,barPercentage:0.6},
      {label:'Goal',data:dW.goal,type:'line',fill:false,borderColor:'rgba(0,229,192,.75)',borderDash:[5,5],pointRadius:0,borderWidth:2,tension:0},
    ]},
    options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false},tooltip:{backgroundColor:'rgba(5,9,26,.97)',borderColor:'rgba(255,255,255,.12)',borderWidth:1,bodyColor:'#e8eaf6',titleColor:'#9b8dff',cornerRadius:12,padding:12}},scales:{x:{grid:{color:'rgba(255,255,255,.04)'},ticks:{color:'rgba(232,234,246,.4)',font:{size:11}}},y:{grid:{color:'rgba(255,255,255,.04)'},ticks:{color:'rgba(232,234,246,.4)',font:{size:11}},beginAtZero:true,max:12}}}
  });
  const dU=await(await fetch('/api/app_usage')).json();
  new Chart(document.getElementById('usageChart').getContext('2d'),{
    type:'doughnut',data:{labels:dU.map(d=>d.app),datasets:[{data:dU.map(d=>d.hours),backgroundColor:dU.map(d=>d.color+'bb'),borderColor:dU.map(d=>d.color),borderWidth:1.5,hoverOffset:10}]},
    options:{responsive:true,maintainAspectRatio:false,cutout:'72%',plugins:{legend:{display:false},tooltip:{backgroundColor:'rgba(5,9,26,.97)',borderColor:'rgba(255,255,255,.12)',borderWidth:1,bodyColor:'#e8eaf6',cornerRadius:12,padding:12,callbacks:{label:c=>' '+c.label+': '+c.parsed+'h'}}}}
  });
  const maxH=Math.max(...dU.map(d=>d.hours));
  const ul=document.getElementById('usageList');ul.innerHTML='';
  dU.forEach(d=>{ul.innerHTML+=`<div class="ur"><div class="udot" style="background:${d.color}"></div><div class="uname">${d.app}</div><div class="ubg"><div class="uf" style="width:0%;background:${d.color}bb" data-w="${(d.hours/maxH)*100}"></div></div><div class="uh">${d.hours}h</div></div>`;});
  setTimeout(()=>document.querySelectorAll('.uf').forEach(b=>b.style.width=b.dataset.w+'%'),350);
  const dR=await(await fetch('/api/digital_diet')).json();
  new Chart(document.getElementById('radarChart').getContext('2d'),{
    type:'radar',data:{labels:dR.labels,datasets:[
      {label:'Current',data:dR.current,backgroundColor:'rgba(124,109,255,.18)',borderColor:'rgba(124,109,255,.8)',borderWidth:2,pointBackgroundColor:'rgba(124,109,255,.9)',pointRadius:3},
      {label:'Ideal',data:dR.ideal,backgroundColor:'rgba(0,229,192,.08)',borderColor:'rgba(0,229,192,.7)',borderWidth:2,borderDash:[5,4],pointRadius:2,pointBackgroundColor:'rgba(0,229,192,.8)'},
    ]},
    options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false},tooltip:{backgroundColor:'rgba(5,9,26,.97)',borderColor:'rgba(255,255,255,.12)',borderWidth:1,bodyColor:'#e8eaf6',cornerRadius:12,padding:12}},scales:{r:{grid:{color:'rgba(255,255,255,.07)'},ticks:{display:false},pointLabels:{color:'rgba(232,234,246,.55)',font:{size:11}},angleLines:{color:'rgba(255,255,255,.06)'}}}}
  });
}

let hydChartInst=null;
function initHydChart(data){
  const ctx=document.getElementById('hydChart').getContext('2d');
  if(hydChartInst){hydChartInst.destroy();}
  const labels=['6am','8am','10am','12pm','2pm','4pm','6pm','8pm'];
  const vals=labels.map((_,i)=>i<data.glasses?Math.floor(Math.random()*2)+1:0);
  hydChartInst=new Chart(ctx,{
    type:'bar',data:{labels,datasets:[{data:vals,backgroundColor:'rgba(0,229,192,.35)',borderColor:'rgba(0,229,192,.7)',borderWidth:1.5,borderRadius:8,barPercentage:.7}]},
    options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false},tooltip:{backgroundColor:'rgba(5,9,26,.97)',borderColor:'rgba(255,255,255,.12)',borderWidth:1,bodyColor:'#e8eaf6',cornerRadius:12,padding:10}},scales:{x:{grid:{color:'rgba(255,255,255,.04)'},ticks:{color:'rgba(232,234,246,.4)',font:{size:10}}},y:{grid:{color:'rgba(255,255,255,.04)'},ticks:{color:'rgba(232,234,246,.4)',font:{size:10}},beginAtZero:true,max:4}}}
  });
}

// ═══════════════════════════════════════════════════════════
//  HEATMAP
// ═══════════════════════════════════════════════════════════
async function initHeatmap(){
  const data=await(await fetch('/api/heatmap')).json();
  const g=document.getElementById('hmGrid');g.innerHTML='';
  data.forEach(d=>{const c=document.createElement('div');c.className=`hm-cell hv${d.val}`;c.innerHTML=`<div class="hm-tip">${d.day}, ${d.date}</div>`;g.appendChild(c);});
}

// ═══════════════════════════════════════════════════════════
//  HABITS
// ═══════════════════════════════════════════════════════════
async function initHabits(){renderHabits(await(await fetch('/api/habits')).json());}
function renderHabits(habits){
  const el=document.getElementById('habList');el.innerHTML='';
  habits.forEach(h=>{
    const d=document.createElement('div');d.className='hab'+(h.done?' done':'');d.onclick=()=>toggleHabit(h.id,h.done);
    d.innerHTML=`<div class="hab-icon">${h.icon}</div><div class="hab-body"><div class="hab-name">${h.name}</div><div class="hab-str">🔥 ${h.streak}-day streak</div></div><div class="hab-check">${h.done?'✓':''}</div>`;
    el.appendChild(d);
  });
}
async function toggleHabit(id,was){
  const res=await(await fetch('/api/toggle_habit',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id})})).json();
  renderHabits(res.habits);document.getElementById('xpVal').textContent=res.xp+' XP';
  if(!was)toast('✅','Habit done! +20 XP','var(--a2)');
  await refreshState();
}

// ═══════════════════════════════════════════════════════════
//  CHALLENGES
// ═══════════════════════════════════════════════════════════
let doneCh=new Set();
async function initChallenges(){
  const data=await(await fetch('/api/challenges')).json();const el=document.getElementById('chalList');el.innerHTML='';
  data.forEach(c=>{
    const d=document.createElement('div');d.className='chi';d.id='ch-'+c.id;
    d.innerHTML=`<div class="chi-icon">${c.icon}</div><div class="chi-body"><div class="chi-title">${c.title}</div><div class="chi-desc">${c.desc}</div></div><div class="chi-xp">+${c.xp} XP</div><div class="chi-check"></div>`;
    d.onclick=e=>completeCh(c.id,c.xp,c.title,e);el.appendChild(d);
  });
}
async function completeCh(id,xp,title,e){
  if(doneCh.has(id))return;doneCh.add(id);
  const el=document.getElementById('ch-'+id);el.classList.add('done');el.querySelector('.chi-check').textContent='✓';confetti(e.clientX,e.clientY);
  const res=await(await fetch('/api/complete_challenge',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({xp})})).json();
  toast('🏆',`Quest: ${title}! +${xp} XP`,'#ffb347');await refreshState();
}

// ═══════════════════════════════════════════════════════════
//  MOOD
// ═══════════════════════════════════════════════════════════
async function logMood(mood,el){
  document.querySelectorAll('.mb').forEach(b=>b.classList.remove('sel'));el.classList.add('sel');
  const emj={amazing:'🤩',good:'😊',okay:'😐',tired:'😴',stressed:'😤'};
  const res=await(await fetch('/api/log_mood',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({mood})})).json();
  const h=document.getElementById('mHist');h.innerHTML='';
  res.mood_log.slice(-5).forEach(m=>{h.innerHTML+=`<span class="mood-tag">${emj[m.mood]||''} ${m.mood} · ${m.time}</span>`;});
  toast(emj[mood]||'','Mood logged!','var(--a)');await refreshState();
}

// ═══════════════════════════════════════════════════════════
//  FOCUS TIMER
// ═══════════════════════════════════════════════════════════
let tDur=1500,tRem=1500,tRun=false,tIv=null,tName='Focus';
let audioCtx=null,bgNode=null,bgGain=null,curSnd='none';
function setMode(el,mins,name){
  document.querySelectorAll('.mp').forEach(p=>p.classList.remove('act'));el.classList.add('act');
  tDur=mins*60;tRem=mins*60;tRun=false;tName=name;clearInterval(tIv);updateTimerUI();
  document.getElementById('timerBtn').textContent='▶ Start '+name;document.getElementById('timerStat').textContent='Ready · Click Start';document.getElementById('tProg').style.width='0%';
}
function updateTimerUI(){ const m=Math.floor(tRem/60),s=tRem%60;document.getElementById('timerDisp').textContent=fmt(m)+':'+fmt(s);document.getElementById('tProg').style.width=((tDur-tRem)/tDur*100)+'%'; }
async function toggleTimer(){
  if(tRun){clearInterval(tIv);tRun=false;document.getElementById('timerBtn').textContent='▶ Resume';document.getElementById('timerStat').textContent='Paused';}
  else{
    tRun=true;document.getElementById('timerBtn').innerHTML='⏸ Pause';document.getElementById('timerStat').textContent=tName+' · In Progress';
    tIv=setInterval(async()=>{
      tRem--;updateTimerUI();
      if(tRem<=0){
        clearInterval(tIv);tRun=false;document.getElementById('timerStat').textContent='Complete! 🎉';document.getElementById('timerBtn').textContent='▶ Start';playDing();toast('🎯',tName+' complete! Great work!','var(--a)');
        await fetch('/api/focus_complete',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({minutes:Math.round(tDur/60)})});
        tRem=tDur;updateTimerUI();await refreshState();
      }
    },1000);
  }
}
function resetTimer(){clearInterval(tIv);tRun=false;tRem=tDur;updateTimerUI();document.getElementById('timerBtn').textContent='▶ Start '+tName;document.getElementById('timerStat').textContent='Ready · Click Start';document.getElementById('tProg').style.width='0%';}

// AUDIO
function getACtx(){if(!audioCtx)audioCtx=new(window.AudioContext||window.webkitAudioContext)();return audioCtx;}
function stopBg(){if(bgNode){try{bgNode.stop()}catch(e){}bgNode=null;}}
function createWhiteNoise(ctx){
  const buf=ctx.createBuffer(1,ctx.sampleRate*2,ctx.sampleRate);const d=buf.getChannelData(0);
  let b0, b1, b2, b3, b4, b5, b6; b0=b1=b2=b3=b4=b5=b6=0.0;
  for(let i=0;i<d.length;i++){
    let w=Math.random()*2-1;
    b0=0.99886*b0+w*0.0555179; b1=0.99332*b1+w*0.0750759; b2=0.96900*b2+w*0.1538520;
    b3=0.86650*b3+w*0.3104856; b4=0.55000*b4+w*0.5329522; b5=-0.7616*b5-w*0.0168980;
    d[i]=(b0+b1+b2+b3+b4+b5+b6+w*0.5362)*0.04; b6=w*0.115926;
  }
  const s=ctx.createBufferSource();s.buffer=buf;s.loop=true;
  bgGain=ctx.createGain();bgGain.gain.value=0.6;s.connect(bgGain);bgGain.connect(ctx.destination);return s;
}
function createRain(ctx){
  const s=createWhiteNoise(ctx);
  const filter = ctx.createBiquadFilter(); filter.type = 'lowpass'; filter.frequency.value = 800; filter.Q.value = 0.5;
  s.disconnect(); s.connect(filter); filter.connect(bgGain);
  bgGain.gain.value=0.5; return s;
}
function createBinaural(ctx){
  const g=ctx.createGain();g.gain.value=0.15;g.connect(ctx.destination);
  const oL=ctx.createOscillator(),oR=ctx.createOscillator();
  oL.frequency.value=432; oR.frequency.value=436; // 4Hz delta wave for deep focus
  const pL=ctx.createStereoPanner(), pR=ctx.createStereoPanner();
  pL.pan.value=-1; pR.pan.value=1;
  oL.connect(pL); pL.connect(g); oR.connect(pR); pR.connect(g);
  oL.start(); oR.start(); bgGain=g; return {start:()=>null, stop:()=> {oL.stop();oR.stop();}};
}
function setSnd(type,el){
  document.querySelectorAll('.sound-btn').forEach(b=>b.classList.remove('act'));if(el)el.classList.add('act');stopBg();curSnd=type;
  if(type==='none'){document.getElementById('sndBtn').textContent='🔇 Sound';return;}
  try{const ctx=getACtx();if(type==='white')bgNode=createWhiteNoise(ctx);else if(type==='rain')bgNode=createRain(ctx);else if(type==='binaural')bgNode=createBinaural(ctx);bgNode.start();document.getElementById('sndBtn').textContent='🔊 '+type.charAt(0).toUpperCase()+type.slice(1);toast('🔊',type+' ambient active','var(--a2)');}catch(e){console.error(e);}
}
function cycleSnd(){const snds=['none','white','rain','binaural'];const next=snds[(snds.indexOf(curSnd)+1)%snds.length];const btn=document.querySelector(`.sound-btn[data-snd="${next}"]`);setSnd(next,btn);}
function playDing(){
  try{
    const ctx=getACtx();
    [440, 554.37, 659.25, 830.61].forEach((freq, i) => { // A Major 7th Chord
      const o=ctx.createOscillator(),g=ctx.createGain(); o.frequency.value=freq; o.type='sine';
      g.gain.setValueAtTime(0, ctx.currentTime);
      g.gain.linearRampToValueAtTime(0.15, ctx.currentTime + 0.05 + (i * 0.02));
      g.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 2.5);
      o.connect(g);g.connect(ctx.destination);o.start();o.stop(ctx.currentTime+2.5);
    });
  }catch(e){}
}

// BREATHING
let bRun=false,bTimer=null,bPhIdx=0,bCycs=0,bMode='478';
const B_MODES={'478':[{l:'Inhale',d:4000},{l:'Hold',d:7000},{l:'Exhale',d:8000},{l:'',d:500}],'box':[{l:'Inhale',d:4000},{l:'Hold',d:4000},{l:'Exhale',d:4000},{l:'Hold',d:4000}],'22':[{l:'Inhale',d:2000},{l:'Exhale',d:2000},{l:'',d:200}]};
const B_LABELS={'478':'Inhale 4 · Hold 7 · Exhale 8','box':'Box: 4 · 4 · 4 · 4','22':'Calm: 2 in · 2 out'};
function setBreathMode(m,el){document.querySelectorAll('.bm').forEach(b=>b.classList.remove('act'));el.classList.add('act');bMode=m;bRun&&stopBreath();bCycs=0;bPhIdx=0;document.getElementById('bPhase').textContent=B_LABELS[m];document.getElementById('bCyc').textContent='0 cycles';}
function toggleBreath(){bRun?stopBreath():startBreath();}
function startBreath(){bRun=true;document.getElementById('bRing').classList.add('go');document.getElementById('bBtn').textContent='⏸ Pause';runBPhase();}
function runBPhase(){if(!bRun)return;const phases=B_MODES[bMode],p=phases[bPhIdx];document.getElementById('bPhase').textContent=p.l||B_LABELS[bMode];document.getElementById('bLabel').innerHTML=p.l?`${p.l}<br><span style="font-size:12px;opacity:.8">${Math.round(p.d/1000)}s</span>`:'&nbsp;';bTimer=setTimeout(()=>{bPhIdx++;if(bPhIdx>=phases.length){bPhIdx=0;bCycs++;document.getElementById('bCyc').textContent=bCycs+' cycle'+(bCycs!==1?'s':'');if(bCycs%3===0){toast('🌿',bCycs+' cycles done!','var(--a2)');fetch('/api/breathing_done',{method:'POST'}).then(()=>refreshState());}}runBPhase();},p.d);}
function stopBreath(){bRun=false;clearTimeout(bTimer);document.getElementById('bRing').classList.remove('go');document.getElementById('bBtn').textContent='▶ Start Flow';document.getElementById('bPhase').textContent=B_LABELS[bMode];document.getElementById('bLabel').innerHTML='Tap to<br>Begin';}
function resetBreath(){stopBreath();bCycs=0;bPhIdx=0;document.getElementById('bCyc').textContent='0 cycles';}

// SLEEP / WATER
function updateSleepUI(h){document.getElementById('sleepBig').textContent=h+'h';document.getElementById('sleepSlider').value=h;const c=document.getElementById('sleepChip');c.innerHTML=h>=7&&h<=9?'<span class="chip cg">Optimal</span>':h<6?'<span class="chip cr">Too little</span>':'<span class="chip cw">Improve</span>';}
let sDebounce;function debounceSleep(v){clearTimeout(sDebounce);sDebounce=setTimeout(async()=>{await fetch('/api/log_sleep',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({hours:v})});toast('💤','Sleep logged','var(--a)');await refreshState();},700);}
function updateWaterUI(g,max=8){document.getElementById('waterBig').textContent=g+'/'+max;const d=document.getElementById('wDots');d.innerHTML='';for(let i=0;i<max;i++){const w=document.createElement('div');w.className='wd'+(i<g?' on':'');w.onclick=addWater;d.appendChild(w);}}
async function addWater(){const res=await(await fetch('/api/log_water',{method:'POST'})).json();updateWaterUI(res.glasses);toast('💧','Hydration logged!','var(--a2)');if(res.glasses===8)toast('🎉','Water goal reached! 💧','var(--a2)');}

// JOURNAL
async function loadJournal(){const data=await(await fetch('/api/journal')).json();renderJournal(data);}
function renderJournal(entries){const el=document.getElementById('jList');el.innerHTML='';if(!entries.length){el.innerHTML='<div style="font-size:12px;color:var(--mu);text-align:center;padding:10px">No entries yet.</div>';return;}entries.forEach(e=>{el.innerHTML+=`<div class="j-item"><div class="j-text">${e.text}</div><div class="j-time">${e.time}</div></div>`;});}
async function saveJournal(){const inp=document.getElementById('jInput');const txt=inp.value.trim();if(!txt)return;const res=await(await fetch('/api/journal',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text:txt})})).json();inp.value='';renderJournal(res.entries);document.getElementById('xpVal').textContent=res.xp+' XP';toast('📓','Reflection saved! +15 XP','var(--warn)');await refreshState();}

// ═══════════════════════════════════════════════════════════
//  YOGA SECTION
// ═══════════════════════════════════════════════════════════
const YOGA_DATA = [
  { id:'y1', body:'neck', title:"Neck Rolls", sub:"Release screen-time tension.", reps:"8 reps", duration:120, difficulty:"Beginner", tag:"Neck", img:"https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?auto=format&fit=crop&w=400&q=80" },
  { id:'y2', body:'neck', title:"Shoulder Shrugs", sub:"Melt trapezius tension.", reps:"12 reps", duration:90, difficulty:"Beginner", tag:"Neck", img:"https://images.unsplash.com/photo-1552196564-972b22ec30bb?auto=format&fit=crop&w=400&q=80" },
  { id:'y3', body:'back', title:"Cat-Cow Stretch", sub:"Spinal mobilization.", reps:"10 cycles", duration:180, difficulty:"Beginner", tag:"Back", img:"https://images.unsplash.com/photo-1566730623145-886ec0d8ae8a?auto=format&fit=crop&w=400&q=80" },
  { id:'y4', body:'back', title:"Child's Pose", sub:"Deeply restful stretch.", reps:"Hold 30s", duration:150, difficulty:"Beginner", tag:"Back", img:"https://images.unsplash.com/photo-1599447292180-45fd880c72f2?auto=format&fit=crop&w=400&q=80" },
  { id:'y5', body:'hip', title:"Butterfly Pose", sub:"Opens hips and groin.", reps:"Hold 45s", duration:120, difficulty:"Beginner", tag:"Hips", img:"https://images.unsplash.com/photo-1575052814086-f385e2e2ad1b?auto=format&fit=crop&w=400&q=80" },
  { id:'y6', body:'hip', title:"Low Lunge", sub:"Deep hip flexor stretch.", reps:"30s/side", duration:180, difficulty:"Intermediate", tag:"Hips", img:"https://images.unsplash.com/photo-1506126613408-eca07ce68773?auto=format&fit=crop&w=400&q=80" },
  { id:'y7', body:'core', title:"Plank Hold", sub:"Core endurance.", reps:"30-60s", duration:210, difficulty:"Intermediate", tag:"Core", img:"https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?auto=format&fit=crop&w=400&q=80" },
  { id:'y8', body:'core', title:"Boat Pose", sub:"Abdominal strengthener.", reps:"20s", duration:150, difficulty:"Advanced", tag:"Core", img:"https://images.unsplash.com/photo-1518310383802-640c2de311b2?auto=format&fit=crop&w=400&q=80" },
  { id:'y9', body:'full', title:"Sun Salutation", sub:"Classic warm-up flow.", reps:"6 rounds", duration:300, difficulty:"All Levels", tag:"Full Body", img:"https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?auto=format&fit=crop&w=400&q=80" },
  { id:'y10', body:'full', title:"Warrior II", sub:"Strength and focus.", reps:"Hold 30s", duration:240, difficulty:"Intermediate", tag:"Full Body", img:"https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?auto=format&fit=crop&w=400&q=80" },
  { id:'y11', body:'full', title:"Tree Pose", sub:"Balance and poise.", reps:"30s/side", duration:120, difficulty:"Beginner", tag:"Balance", img:"https://images.unsplash.com/photo-1506126613408-eca07ce68773?auto=format&fit=crop&w=400&q=80" },
  { id:'y12', body:'back', title:"Cobra Pose", sub:"Spinal extension.", reps:"Hold 30s", duration:120, difficulty:"Beginner", tag:"Back", img:"https://images.unsplash.com/photo-1593164841882-78d1f0565062?auto=format&fit=crop&w=400&q=80" },
  { id:'y13', body:'full', title:"Downward Dog", sub:"Full body stretch.", reps:"Hold 30s", duration:120, difficulty:"Beginner", tag:"Full Body", img:"https://images.unsplash.com/photo-1599447421416-3414500d18a5?auto=format&fit=crop&w=400&q=80" },
  { id:'y14', body:'full', title:"Triangle Pose", sub:"Side body lateral stretch.", reps:"30s/side", duration:180, difficulty:"Intermediate", tag:"Full Body", img:"https://images.unsplash.com/photo-1510894347713-fc3ad6cb0322?auto=format&fit=crop&w=400&q=80" },
  { id:'y15', body:'full', title:"Warrior I", sub:"Foundational strength.", reps:"Hold 30s", duration:180, difficulty:"Beginner", tag:"Full Body", img:"https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?auto=format&fit=crop&w=400&q=80" },
  { id:'y16', body:'full', title:"Bridge Pose", sub:"Glute and back opener.", reps:"Hold 30s", duration:120, difficulty:"Beginner", tag:"Back", img:"https://images.unsplash.com/photo-1599447421416-3414500d18a5?auto=format&fit=crop&w=400&q=80" },
  { id:'y17', body:'hip', title:"Pigeon Pose", sub:"Deep hip opener.", reps:"1m/side", duration:240, difficulty:"Advanced", tag:"Hips", img:"https://images.unsplash.com/photo-1575052814086-f385e2e2ad1b?auto=format&fit=crop&w=400&q=80" },
  { id:'y18', body:'core', title:"Side Plank", sub:"Oblique strength.", reps:"30s/side", duration:180, difficulty:"Intermediate", tag:"Core", img:"https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?auto=format&fit=crop&w=400&q=80" },
  { id:'y19', body:'full', title:"Corpse Pose", sub:"Ultimate restoration.", reps:"5-10 mins", duration:300, difficulty:"Beginner", tag:"Relax", img:"https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?auto=format&fit=crop&w=400&q=80" },
  { id:'y20', body:'full', title:"Mountain Pose", sub:"Posture and focus.", reps:"Hold 1m", duration:300, difficulty:"Beginner", tag:"Posture", img:"https://images.unsplash.com/photo-1506126613408-eca07ce68773?auto=format&fit=crop&w=400&q=80" },
  { id:'y21', body:'full', title:"Eagle Pose", sub:"Internal focus.", reps:"30s/side", duration:180, difficulty:"Intermediate", tag:"Balance", img:"https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?auto=format&fit=crop&w=400&q=80" },
  { id:'y22', body:'full', title:"Wheel Pose", sub:"Powerful backbend.", reps:"Hold 15s", duration:120, difficulty:"Advanced", tag:"Back", img:"https://images.unsplash.com/photo-1599447421416-3414500d18a5?auto=format&fit=crop&w=400&q=80" },
  { id:'y23', body:'full', title:"Crow Pose", sub:"Arm balance challenge.", reps:"Hold 15s", duration:120, difficulty:"Advanced", tag:"Balance", img:"https://images.unsplash.com/photo-1510894347713-fc3ad6cb0322?auto=format&fit=crop&w=400&q=80" },
  { id:'y24', body:'full', title:"Camel Pose", sub:"Chest expander.", reps:"Hold 30s", duration:120, difficulty:"Intermediate", tag:"Back", img:"https://images.unsplash.com/photo-1593164841882-78d1f0565062?auto=format&fit=crop&w=400&q=80" },
  { id:'y25', body:'full', title:"Extended Side Angle", sub:"Leg and side strength.", reps:"30s/side", duration:180, difficulty:"Intermediate", tag:"Full Body", img:"https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?auto=format&fit=crop&w=400&q=80" },
  { id:'y26', body:'full', title:"Pyramid Pose", sub:"Hamstring stretch.", reps:"30s/side", duration:120, difficulty:"Intermediate", tag:"Legs", img:"https://images.unsplash.com/photo-1510894347713-fc3ad6cb0322?auto=format&fit=crop&w=400&q=80" },
  { id:'y27', body:'full', title:"Half Moon Pose", sub:"Advanced balance.", reps:"20s/side", duration:120, difficulty:"Advanced", tag:"Balance", img:"https://images.unsplash.com/photo-1506126613408-eca07ce68773?auto=format&fit=crop&w=400&q=80" },
  { id:'y28', body:'full', title:"Chair Pose", sub:"Powerful standing pose.", reps:"Hold 30s", duration:120, difficulty:"Beginner", tag:"Full Body", img:"https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?auto=format&fit=crop&w=400&q=80" },
  { id:'y29', body:'full', title:"Lizard Pose", sub:"Deep hip and groin.", reps:"30s/side", duration:180, difficulty:"Advanced", tag:"Hips", img:"https://images.unsplash.com/photo-1575052814086-f385e2e2ad1b?auto=format&fit=crop&w=400&q=80" },
  { id:'y30', body:'full', title:"Dolphin Pose", sub:"Shoulder strength.", reps:"Hold 30s", duration:120, difficulty:"Intermediate", tag:"Shoulders", img:"https://images.unsplash.com/photo-1599447421416-3414500d18a5?auto=format&fit=crop&w=400&q=80" },
  { id:'y31', body:'full', title:"Revolved Triangle", sub:"Twisting hamstrings.", reps:"20s/side", duration:120, difficulty:"Advanced", tag:"Full Body", img:"https://images.unsplash.com/photo-1510894347713-fc3ad6cb0322?auto=format&fit=crop&w=400&q=80" },
  { id:'y32', body:'full', title:"Seated Twist", sub:"Spinal detox twist.", reps:"30s/side", duration:120, difficulty:"Beginner", tag:"Back", img:"https://images.unsplash.com/photo-1593164841882-78d1f0565062?auto=format&fit=crop&w=400&q=80" }
];

let yogaFilter='all', activeYogaTimer=null, yogaTimerRunning=false;
function filterYoga(filter, btn){
  document.querySelectorAll('.bfb').forEach(b=>b.classList.remove('act'));btn.classList.add('act');
  yogaFilter=filter;renderYoga();
}
function renderYoga(){
  const grid=document.getElementById('yogaGrid');grid.innerHTML='';
  const poses=(yogaFilter==='all')?YOGA_DATA:YOGA_DATA.filter(p=>p.tag.toLowerCase().includes(yogaFilter.toLowerCase()) || p.body.toLowerCase().includes(yogaFilter.toLowerCase()));
  poses.forEach(p=>{
    const card=document.createElement('div');card.className='yoga-card';card.id='yc-'+p.id;
    card.innerHTML=`
      <div class="yoga-illus" style="background:url('${p.img}') center/cover no-repeat; border-radius:12px 12px 0 0; height:180px"></div>
      <div class="yoga-info">
        <div class="yoga-title">${p.title}</div>
        <div class="yoga-sub">${p.sub}</div>
        <div class="yoga-meta">
          <span class="yoga-tag">${p.difficulty}</span>
          <span class="yoga-tag green">${p.reps}</span>
          <span class="yoga-tag pink">${p.tag}</span>
        </div>
        <div style="display:flex;gap:8px">
          <button class="btn btn-p btn-sm" style="flex:1;font-size:12px" onclick="startYogaTimer('${p.id}',${p.duration},event)">▶ Start</button>
        </div>
      </div>
      <div class="yoga-timer-wrap" id="ytw-${p.id}">
        <div class="yoga-timer-face" id="ytf-${p.id}">00:${String(Math.floor(p.duration/60)).padStart(2,'0')}:${String(p.duration%60).padStart(2,'0')}</div>
        <div class="yoga-prog"><div class="yoga-pf" id="ypf-${p.id}" style="width:0%"></div></div>
        <div class="yoga-btns">
          <button class="btn btn-t btn-sm" onclick="pauseYogaTimer('${p.id}')">⏸ Pause</button>
          <button class="btn btn-g btn-sm" onclick="stopYogaTimer('${p.id}',${p.duration})">🔄 Reset</button>
        </div>
      </div>
    `;
    grid.appendChild(card);
  });
}
let yogaTimerState={};
function startYogaTimer(id, total, e){
  e.stopPropagation();
  // stop any other running timer
  Object.keys(yogaTimerState).forEach(k=>{if(k!==id&&yogaTimerState[k].running)pauseYogaTimer(k);});
  document.getElementById('yc-'+id).classList.add('active-pose');
  document.getElementById('ytw-'+id).classList.add('open');
  if(yogaTimerState[id]&&yogaTimerState[id].running) return;
  if(!yogaTimerState[id]) yogaTimerState[id]={rem:total,total,running:false,iv:null};
  const st=yogaTimerState[id];
  st.running=true;
  clearInterval(st.iv);
  st.iv=setInterval(async()=>{
    st.rem--;
    updateYogaTimerUI(id);
    if(st.rem<=0){
      clearInterval(st.iv);st.running=false;
      document.getElementById('ytf-'+id).textContent='Done! 🎉';
      document.getElementById('ypf-'+id).style.width='100%';
      playDing();
      document.getElementById('yc-'+id).classList.remove('active-pose');
      toast('🧘','Yoga pose complete! +35 XP','var(--a2)');
      const banner=document.getElementById('yogaCompleteBanner');banner.classList.add('show');setTimeout(()=>banner.classList.remove('show'),4000);
      await fetch('/api/yoga_done',{method:'POST'});await refreshState();
      yogaTimerState[id]=null;
    }
  },1000);
}
function pauseYogaTimer(id){
  if(!yogaTimerState[id])return;
  const st=yogaTimerState[id];
  if(st.running){clearInterval(st.iv);st.running=false;}
  else{
    st.running=true;
    st.iv=setInterval(async()=>{st.rem--;updateYogaTimerUI(id);if(st.rem<=0){clearInterval(st.iv);st.running=false;document.getElementById('ytf-'+id).textContent='Done! 🎉';}},1000);
  }
}
function stopYogaTimer(id,total){
  if(yogaTimerState[id]){clearInterval(yogaTimerState[id].iv);yogaTimerState[id]=null;}
  document.getElementById('ytf-'+id).textContent=fmt(Math.floor(total/60))+':'+fmt(total%60);
  document.getElementById('ypf-'+id).style.width='0%';
  document.getElementById('yc-'+id).classList.remove('active-pose');
}
function updateYogaTimerUI(id){
  const st=yogaTimerState[id];if(!st)return;
  const m=Math.floor(st.rem/60),s=st.rem%60;
  document.getElementById('ytf-'+id).textContent=fmt(m)+':'+fmt(s);
  document.getElementById('ypf-'+id).style.width=((st.total-st.rem)/st.total*100)+'%';
}
function toggleYogaInfo(id){document.getElementById('ytw-'+id).classList.toggle('open');}

// ═══════════════════════════════════════════════════════════
//  HYDRATION CORNER
// ═══════════════════════════════════════════════════════════
const HYDRATION_TIPS=[
  "Drink 2 glasses of water first thing in the morning to kickstart your metabolism.",
  "Carry a reusable water bottle so you always have water within reach.",
  "Eat water-rich foods like cucumber, watermelon, oranges and celery.",
  "Set phone reminders every 45 minutes as a hydration cue.",
  "Drink a glass before every meal — it also helps mindful eating.",
  "Herbal teas count towards your daily fluid intake!",
  "Feeling hungry? It might actually be thirst. Try water first.",
  "Cold water burns slightly more calories — but any temperature counts.",
];
let intakeLog=[], hydReminderInterval=null, hydGoal=8;

async function refreshHydration(){
  const data=await(await fetch('/api/hydration_log')).json();
  hydGoal=data.goal;const g=data.glasses;
  document.getElementById('hydGlasses').textContent=g;
  document.getElementById('hydGoal').textContent=hydGoal;
  const pct=Math.min(100,Math.round((g/hydGoal)*100));
  document.getElementById('hydBar').style.width=pct+'%';
  document.getElementById('hydPercent').textContent=pct+'%';
  document.getElementById('hydTotalMl').textContent=(g*250)+'ml';
  const rem=Math.max(0,hydGoal-g);
  document.getElementById('hydStatus').textContent=rem>0?`Keep going! ${rem} more glass${rem!==1?'es':''} to reach your goal.`:'🎉 Daily goal reached! Excellent hydration!';
  // update bottle fill
  const fillY=90-(70*(g/hydGoal));
  const fillH=56+(70*(g/hydGoal));
  const wf=document.getElementById('waterFill');if(wf){wf.setAttribute('y',fillY);wf.setAttribute('height',fillH);}
  const wt=document.getElementById('waveTop');if(wt){wt.setAttribute('d',`M 10 ${fillY} Q 22 ${fillY-6} 45 ${fillY} Q 68 ${fillY+6} 80 ${fillY} L 80 ${fillY+6} L 10 ${fillY+6} Z`);}
  // log items
  const logItems=document.getElementById('hydLogItems');
  const logData=data.log||[];
  if(logData.length===0){logItems.innerHTML='<div style="font-size:13px;color:var(--mu);text-align:center;padding:20px">No entries yet. Start drinking!</div>';return;}
  logItems.innerHTML='';
  logData.slice(-10).reverse().forEach(item=>{
    logItems.innerHTML+=`<div class="hydro-log-item"><div class="hydro-log-icon">💧</div><div class="hydro-log-text">Water intake (250ml)</div><div class="hydro-log-time">${item.time}</div></div>`;
  });
  document.getElementById('hydStreak').textContent=Math.min(g,5);
  // tip
  document.getElementById('hydTip').textContent=HYDRATION_TIPS[Math.floor(Math.random()*HYDRATION_TIPS.length)];
  initHydChart({glasses:g,goal:hydGoal});
}

async function logIntake(ml, label){
  const res=await(await fetch('/api/log_water',{method:'POST'})).json();
  toast('💧',`${label} logged!`,'var(--a2)');
  await refreshHydration();
  await refreshState();
}

let reminderEnabled=true, reminderTimeout=null;
function toggleReminder(on){
  reminderEnabled=on;
  if(on){toast('🔔','Hydration reminders enabled','var(--a2)');scheduleReminder();}
  else{toast('🔕','Reminders disabled','var(--mu)');clearTimeout(reminderTimeout);}
}
function scheduleReminder(){
  if(!reminderEnabled)return;
  reminderTimeout=setTimeout(()=>{toast('💧','Time to drink some water!','var(--a2)');scheduleReminder();},45*60*1000);
}
scheduleReminder();

// ═══════════════════════════════════════════════════════════
//  QUICK ACTIONS
// ═══════════════════════════════════════════════════════════
let breakShown=false;
function showBreak(){if(!breakShown){breakShown=true;document.getElementById('breakBanner').classList.add('show');}}
function dismissBreak(){document.getElementById('breakBanner').classList.remove('show');}
function startBreakTimer(){setMode(document.querySelector('.mp:nth-child(3)'),5,'Break');toast('☕','5-minute break started!','var(--warn)');navToBtn('tab-focus');}
setTimeout(showBreak,28*60*1000);
let grayOn=false,nightOn=false;
function actDND(){toast('🔕','Do Not Disturb activated','var(--a)');}
function actGray(){grayOn=!grayOn;document.body.style.filter=grayOn?'grayscale(1)':'';document.getElementById('grayB').querySelector('.al').textContent=grayOn?'Color On':'Grayscale';toast(grayOn?'🐼':'🎨',grayOn?'Grayscale enabled':'Color restored','var(--mu)');}
async function actDetox(){toast('📵','Social detox +30 XP','var(--a2)');await fetch('/api/complete_challenge',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({xp:30})});await refreshState();}
function actStretch(){toast('🤸','Stand up and stretch for 2 minutes!','var(--a2)');}
function actWalk(){toast('🚶','Perfect time for a mindful walk!','var(--a2)');}
function actNight(){nightOn=!nightOn;document.documentElement.style.filter=nightOn?'sepia(.35) brightness(.88)':'';document.getElementById('nightB').querySelector('.al').textContent=nightOn?'Day Mode':'Night Mode';toast(nightOn?'🌙':'☀️',nightOn?'Night mode on':'Day mode restored','var(--warn)');}

// ═══════════════════════════════════════════════════════════
//  BOOT
// ═══════════════════════════════════════════════════════════
(async()=>{
  await refreshState();
  await Promise.all([initHeatmap(),initHabits(),initChallenges(),loadJournal()]);
  renderYoga();
  setInterval(refreshState, 30000);
})();
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return Response(HTML, mimetype="text/html")

# ─── LAUNCHER ─────────────────────────────────────────────────────────────────
def open_browser(port):
    time.sleep(1.5)
    webbrowser.open(f"http://127.0.0.1:{port}")

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8", errors="replace") if hasattr(sys.stdout, "reconfigure") else None
    
    port = int(os.environ.get("PORT", 5050))
    is_render = os.environ.get("RENDER") is not None
    
    print("\n" + "="*55)
    print("  Zenith - Smart Detox & Digital Wellness")
    print("="*55)
    print(f"  -> Bound to port {port}")
    print("  Press Ctrl+C to stop\n")
    
    if not is_render:
        t = threading.Thread(target=open_browser, args=(port,), daemon=True)
        t.start()
        
    app.run(host="0.0.0.0", port=port, debug=False)
