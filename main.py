"""
Emotion Tracker & Recommendation System — Ultra-Dark Professional Edition
Optimized for High-Visibility & Comprehensive Monitoring
Restructured by: Gemini AI
"""

import sys
import os
import csv
import time
import threading
import webbrowser
from datetime import datetime
from collections import deque

try:
    import cv2
    from deepface import DeepFace
    import numpy as np
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
    from PIL import Image, ImageTk
    import pyttsx3
except Exception as e:
    print(f"Missing Library Error: {e}")
    sys.exit(1)

# =========================
# UI COLOR CONFIGURATION (ULTRA DARK)
# =========================
THEME = {
    "bg_root": "#050505",       # Pure Black
    "bg_card": "#111111",       # Deep Gray Card
    "fg_main": "#E0E0E0",       # Off-White Text
    "accent": "#00D4FF",        # Neon Cyan
    "btn_bg": "#1A1A1A",        # Button Background
    "btn_fg": "#FFFFFF",        # Button Text
    "danger": "#FF3131",        # Neon Red
    "success": "#00FF41"        # Matrix Green
}

# =========================
# CONFIGURATION DATA (PRESERVED)
# =========================
EMOTION_CYCLES = {
    "happy": {
        "color": "#FFD700",
        "steps": [
            {"name": "Recognition", "description": "Acknowledging the positive feeling", "action": "Notice and appreciate the moment", "duration": 30, "exercises": ["Take 3 deep breaths and smile", "List 3 things you're grateful for"], "affirmations": ["I deserve this happiness"], "completion_criteria": "Feel present"},
            {"name": "Amplification", "description": "Enhancing the positive state", "action": "Share with others", "duration": 45, "exercises": ["Dance to a song", "Call a friend"], "affirmations": ["My joy multiplies"], "completion_criteria": "Expressed joy"},
            {"name": "Integration", "description": "Learning from the experience", "action": "Reflect on causes", "duration": 30, "exercises": ["Journal the trigger"], "affirmations": ["I understand my joy"], "completion_criteria": "Trigger identified"},
            {"name": "Maintenance", "description": "Sustaining momentum", "action": "Plan fun activity", "duration": 15, "exercises": ["Schedule fun for tomorrow"], "affirmations": ["I choose joy daily"], "completion_criteria": "Plan created"}
        ]
    },
    "sad": {
        "color": "#4169E1",
        "steps": [
            {"name": "Acceptance", "description": "Allowing the feeling", "action": "Acknowledge without judgment", "duration": 60, "exercises": ["Sit quietly"], "affirmations": ["It's okay to feel sad"], "completion_criteria": "Full acceptance"},
            {"name": "Processing", "description": "Understanding emotion", "action": "Journal or talk", "duration": 60, "exercises": ["Write it down"], "affirmations": ["I heal through feeling"], "completion_criteria": "Clear understanding"},
            {"name": "Support", "description": "Seeking comfort", "action": "Reach out", "duration": 45, "exercises": ["Warm bath", "Comforting music"], "affirmations": ["I deserve support"], "completion_criteria": "Feeling cared for"},
            {"name": "Recovery", "description": "Healing steps", "action": "Small positive move", "duration": 15, "exercises": ["Gentle stretching"], "affirmations": ["I heal at my own pace"], "completion_criteria": "Ready to act"}
        ]
    },
    "angry": {
        "color": "#DC143C",
        "steps": [
            {"name": "Pause", "description": "Stopping before reacting", "action": "10 Deep breaths", "duration": 15, "exercises": ["Count to 10"], "affirmations": ["I am in control"], "completion_criteria": "Calm mind"},
            {"name": "Identify", "description": "Understanding trigger", "action": "Ask why", "duration": 30, "exercises": ["Write the trigger"], "affirmations": ["I understand my anger"], "completion_criteria": "Trigger found"},
            {"name": "Release", "description": "Safely expressing", "action": "Physical exercise", "duration": 30, "exercises": ["Jumping jacks"], "affirmations": ["I release anger healthily"], "completion_criteria": "Tension released"},
            {"name": "Resolve", "description": "Addressing root", "action": "Calm talk", "duration": 15, "exercises": ["Plan conversation"], "affirmations": ["I resolve with wisdom"], "completion_criteria": "Resolution plan"}
        ]
    },
    "fear": {
        "color": "#9932CC",
        "steps": [
            {"name": "Ground", "description": "Stay present", "action": "5-4-3-2-1 Technique", "duration": 45, "exercises": ["Focus on breathing"], "affirmations": ["I am safe now"], "completion_criteria": "Feeling grounded"},
            {"name": "Assess", "description": "Evaluating threat", "action": "Fact vs Fear", "duration": 45, "exercises": ["List the facts"], "affirmations": ["I see things clearly"], "completion_criteria": "Realistic view"},
            {"name": "Plan", "description": "Strategy", "action": "Break down task", "duration": 45, "exercises": ["3 Small solutions"], "affirmations": ["I can handle this"], "completion_criteria": "Plan ready"},
            {"name": "Act", "description": "Build courage", "action": "One brave step", "duration": 15, "exercises": ["Take first step"], "affirmations": ["I am brave"], "completion_criteria": "Action taken"}
        ]
    },
    "surprise": {
        "color": "#FF8C00",
        "steps": [
            {"name": "Orient", "description": "Process shock", "action": "Understand event", "duration": 15, "exercises": ["3 Deep breaths"], "affirmations": ["I can handle this"], "completion_criteria": "Clear view"},
            {"name": "Evaluate", "description": "Assessing impact", "action": "Good or Bad?", "duration": 15, "exercises": ["Rate impact"], "affirmations": ["I find opportunities"], "completion_criteria": "Evaluation done"},
            {"name": "Adapt", "description": "Adjusting plans", "action": "Stay flexible", "duration": 20, "exercises": ["Modify schedule"], "affirmations": ["I adapt easily"], "completion_criteria": "Adaptive plan"},
            {"name": "Integrate", "description": "Learning", "action": "Reflect", "duration": 10, "exercises": ["Journal lesson"], "affirmations": ["Surprises help me grow"], "completion_criteria": "Integrated lesson"}
        ]
    },
    "neutral": {
        "color": "#708090",
        "steps": [
            {"name": "Awareness", "description": "Recognize calm", "action": "Enjoy balance", "duration": 20, "exercises": ["Mindful breathing"], "affirmations": ["I am centered"], "completion_criteria": "Balanced state"},
            {"name": "Preparation", "description": "Use clarity", "action": "Set intentions", "duration": 30, "exercises": ["Set 3 intentions"], "affirmations": ["I make wise decisions"], "completion_criteria": "Priorities set"},
            {"name": "Focus", "description": "Meaningful work", "action": "Tackle task", "duration": 40, "exercises": ["Deep work"], "affirmations": ["I am productive"], "completion_criteria": "Progress made"},
            {"name": "Reflection", "description": "Check growth", "action": "Review insights", "duration": 10, "exercises": ["Review learning"], "affirmations": ["I am evolving"], "completion_criteria": "Insight gained"}
        ]
    }
}

MEDIA_CYCLES = {
    "happy": {
        "songs": ["https://www.youtube.com/results?search_query=happy+music", "https://www.youtube.com/results?search_query=uplifting+songs", "https://www.youtube.com/results?search_query=joyful+beats"],
        "poetry": ["https://www.youtube.com/results?search_query=inspiring+poetry", "https://www.youtube.com/results?search_query=celebration+poetry", "https://www.youtube.com/results?search_query=uplifting+shayari"],
        "novels": ["https://www.youtube.com/results?search_query=The+Alchemist+summary", "https://www.youtube.com/results?search_query=The+Rosie+Project+summary", "https://www.youtube.com/results?search_query=feel+good+books"],
        "alt": "https://www.youtube.com/results?search_query=high+energy+mix"
    },
    "sad": {
        "songs": ["https://www.youtube.com/results?search_query=Talha+Anjum+sad", "https://www.youtube.com/results?search_query=healing+music", "https://www.youtube.com/results?search_query=deep+melancholy"],
        "poetry": ["https://www.youtube.com/results?search_query=Jaun+Elia+sad", "https://www.youtube.com/results?search_query=healing+poetry", "https://www.youtube.com/results?search_query=comforting+verses"],
        "novels": ["https://www.youtube.com/results?search_query=Peer+e+Kamil+summary", "https://www.youtube.com/results?search_query=Milan+Kundera+summary", "https://www.youtube.com/results?search_query=books+for+healing"],
        "alt": "https://www.youtube.com/results?search_query=emotional+processing+music"
    },
    "angry": {
        "songs": ["https://www.youtube.com/results?search_query=Sidhu+Moose+Wala+intense", "https://www.youtube.com/results?search_query=metal+release", "https://www.youtube.com/results?search_query=high+tempo+workout"],
        "poetry": ["https://www.youtube.com/results?search_query=stoic+poetry", "https://www.youtube.com/results?search_query=anger+management+verses", "https://www.youtube.com/results?search_query=calm+poetry"],
        "novels": ["https://www.youtube.com/results?search_query=The+Power+of+Now+summary", "https://www.youtube.com/results?search_query=Crawdads+Sing+summary", "https://www.youtube.com/results?search_query=resilience+books"],
        "alt": "https://www.youtube.com/results?search_query=intense+release+playlist"
    }
}
# Default for missing media keys
for emo in ["fear", "surprise", "neutral"]:
    if emo not in MEDIA_CYCLES:
        MEDIA_CYCLES[emo] = {"songs": ["https://www.youtube.com/results?search_query=focus+music"], "poetry": ["https://www.youtube.com/results?search_query=peaceful+poetry"], "novels": ["https://www.youtube.com/results?search_query=mindfulness+books"], "alt": "https://www.youtube.com/results?search_query=lofi+beats"}

EMOTION_DATA = {
    "happy": {"emoji": "😊", "color": "#00FF41", "reason": "Positive vibes! Share your joy.", "book": "The Alchemist", "summary": "A journey to find your destiny."},
    "sad": {"emoji": "😢", "color": "#4169E1", "reason": "Low energy detected. Take it easy.", "book": "Peer-e-Kamil", "summary": "A path of spiritual discovery."},
    "angry": {"emoji": "😡", "color": "#FF3131", "reason": "Tension detected. Take deep breaths.", "book": "The Power of Now", "summary": "Living in the present moment."},
    "fear": {"emoji": "😨", "color": "#9932CC", "reason": "Anxiety detected. You are safe.", "book": "Atomic Habits", "summary": "Tiny changes, big results."},
    "surprise": {"emoji": "😲", "color": "#FF8C00", "reason": "Shock detected. Adapt and learn.", "book": "Who Moved My Cheese", "summary": "Dealing with change."},
    "neutral": {"emoji": "😐", "color": "#708090", "reason": "Balanced state. Keep focusing.", "book": "Think Like a Monk", "summary": "Purpose and clarity."}
}

# =========================
# LOGIC MANAGERS
# =========================

class EmotionSmoother:
    def __init__(self, size=5):
        self.history = deque(maxlen=size)
    def add(self, emo): self.history.append(emo)
    def get(self):
        if not self.history: return "neutral"
        return max(set(self.history), key=self.history.count)

class MediaCycleManager:
    def __init__(self):
        self.counters = {e: 0 for e in EMOTION_CYCLES}
        self.last_emo = None
        self.streak = 0
    def get_media(self, emo):
        if emo == self.last_emo: self.streak += 1
        else: self.streak = 1; self.last_emo = emo
        idx = self.counters[emo]
        self.counters[emo] = (idx + 1) % 3
        return MEDIA_CYCLES[emo], idx, self.streak

# =========================
# MAIN APPLICATION
# =========================

class EmotionTrackerApp:
    face_rect = None

    def __init__(self, master):
        self.master = master
        self.master.title("NEURAL MOOD PRO — ASADULLAH FARZAND EDITION")
        self.master.geometry("1200x850")
        self.master.configure(bg=THEME["bg_root"])

        # Systems
        self.cap = None
        self.running = False
        self.frame = None
        self.smoother = EmotionSmoother()
        self.media_mgr = MediaCycleManager()
        self.history = deque(maxlen=500)
        self.current_emo_key = "neutral"
        self.last_analysis = 0

        try:
            self.tts = pyttsx3.init()
            self.tts.setProperty('rate', 140)
        except: self.tts = None

        self._apply_styles()
        self._build_interface()

    def _apply_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background=THEME["bg_root"])
        style.configure("TLabelframe", background=THEME["bg_root"], foreground=THEME["accent"], font=("Orbitron", 10, "bold"))
        style.configure("TLabelframe.Label", background=THEME["bg_root"], foreground=THEME["accent"])
        style.configure("Treeview", background=THEME["bg_card"], foreground=THEME["fg_main"], fieldbackground=THEME["bg_card"], rowheight=25)
        style.map("Treeview", background=[('selected', THEME['accent'])], foreground=[('selected', 'black')])
        style.configure("Treeview.Heading", background=THEME["btn_bg"], foreground=THEME["accent"], font=("Arial", 9, "bold"))

    def _build_interface(self):
        # Header
        hdr = tk.Frame(self.master, bg=THEME["bg_root"], pady=15)
        hdr.pack(fill=tk.X)
        tk.Label(hdr, text="NEURAL MOOD PRO", font=("Orbitron", 24, "bold"), bg=THEME["bg_root"], fg=THEME["accent"]).pack()
        tk.Label(hdr, text="Advanced Emotion Intelligence System", font=("Arial", 10), bg=THEME["bg_root"], fg="#666").pack()

        main_paned = tk.PanedWindow(self.master, orient=tk.HORIZONTAL, bg="#222", bd=0, sashwidth=2)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # --- LEFT PANEL: FEED & SYSTEM ---
        left_p = tk.Frame(main_paned, bg=THEME["bg_root"])
        main_paned.add(left_p, width=550)

        self.preview = tk.Label(left_p, bg="#000", bd=2, relief="flat", highlightbackground=THEME["accent"], highlightthickness=1)
        self.preview.pack(pady=5)
        self._placeholder()

        # Controls Card
        ctrl_f = tk.LabelFrame(left_p, text=" SYSTEM CONTROLS ", padx=15, pady=15)
        ctrl_f.pack(fill=tk.X, pady=10, padx=5)

        tk.Button(ctrl_f, text="START AI SCAN", command=self.start, bg=THEME["success"], fg="black", font=("Arial", 10, "bold"), height=2).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        tk.Button(ctrl_f, text="STOP", command=self.stop, bg=THEME["danger"], fg="white", font=("Arial", 10, "bold"), height=2).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        
        self.voice_var = tk.BooleanVar(value=True)
        tk.Checkbutton(ctrl_f, text="AI Voice", variable=self.voice_var, bg=THEME["bg_root"], fg="white", selectcolor="black", activebackground="black").pack(side=tk.LEFT, padx=10)

        # Settings Sub-Card
        set_f = tk.Frame(left_p, bg=THEME["bg_root"])
        set_f.pack(fill=tk.X, padx=5)
        tk.Label(set_f, text="Camera Index:", bg=THEME["bg_root"], fg="#888").pack(side=tk.LEFT)
        self.cam_entry = tk.Entry(set_f, width=5, bg="#222", fg="white", bd=0); self.cam_entry.insert(0, "0")
        self.cam_entry.pack(side=tk.LEFT, padx=5)

        # --- RIGHT PANEL: DASHBOARD & LOGS ---
        right_p = tk.Frame(main_paned, bg=THEME["bg_root"])
        main_paned.add(right_p)

        # Live Status Card
        dash = tk.Frame(right_p, bg=THEME["bg_card"], padx=20, pady=20)
        dash.pack(fill=tk.X, padx=10, pady=5)
        
        self.lbl_emoji = tk.Label(dash, text="❓", font=("Segoe UI Emoji", 70), bg=THEME["bg_card"])
        self.lbl_emoji.pack(side=tk.LEFT)
        
        info_f = tk.Frame(dash, bg=THEME["bg_card"])
        info_f.pack(side=tk.LEFT, padx=25)
        self.lbl_emo = tk.Label(info_f, text="AWAITING DATA", font=("Helvetica", 24, "bold"), bg=THEME["bg_card"], fg=THEME["accent"])
        self.lbl_emo.pack(anchor="w")
        self.lbl_adv = tk.Label(info_f, text="System ready for facial analysis...", font=("Arial", 11), bg=THEME["bg_card"], fg="#AAA", wraplength=350, justify="left")
        self.lbl_adv.pack(anchor="w")

        # Media Cycle Dashboard
        cycle_f = tk.Frame(right_p, bg=THEME["bg_root"])
        cycle_f.pack(fill=tk.X, padx=10, pady=10)
        self.lbl_cycle = tk.Label(cycle_f, text="Cycle: 0/3 | Streak: 0", bg=THEME["bg_root"], fg=THEME["accent"], font=("Courier", 10))
        self.lbl_cycle.pack()

        # Recommendation Hub
        hub = tk.Frame(right_p, bg=THEME["bg_root"])
        hub.pack(fill=tk.X, padx=10, pady=5)
        btns = [("🎵 SONG", self.open_song), ("📝 POETRY", self.open_poetry), ("📚 NOVEL", self.open_novel), ("🔥 ALTERNATE", self.open_alt)]
        for text, cmd in btns:
            tk.Button(hub, text=text, command=cmd, bg=THEME["btn_bg"], fg=THEME["btn_fg"], bd=1, height=2).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        # History Tree
        tk.Label(right_p, text="DETECTION HISTORY", bg=THEME["bg_root"], fg="#555", font=("Arial", 8, "bold")).pack(anchor="w", padx=10, pady=(15, 0))
        self.tree = ttk.Treeview(right_p, columns=("T", "E", "C"), show="headings", height=10)
        self.tree.heading("T", text="TIMESTAMP"); self.tree.heading("E", text="EMOTION"); self.tree.heading("C", text="COMMENT")
        self.tree.column("T", width=100); self.tree.column("E", width=120); self.tree.column("C", width=250)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10)

        # Data Actions
        data_f = tk.Frame(right_p, bg=THEME["bg_root"], pady=10)
        data_f.pack(fill=tk.X, padx=10)
        tk.Button(data_f, text="💬 ADD COMMENT", command=self.add_comment, bg="#333", fg="white").pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        tk.Button(data_f, text="🗑️ CLEAR LOG", command=self.clear_history, bg="#333", fg=THEME["danger"]).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        tk.Button(data_f, text="💾 EXPORT CSV", command=self.export_csv, bg="#333", fg=THEME["success"]).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        # Feature Footer
        feat_f = tk.Frame(right_p, bg=THEME["bg_root"], pady=5)
        feat_f.pack(fill=tk.X, padx=10)
        tk.Button(feat_f, text="🤖 AI WELLNESS REPORT", command=self.ai_report, bg=THEME["accent"], fg="black", font=("Arial", 9, "bold")).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        tk.Button(feat_f, text="🔄 4-STEP CYCLE", command=self.show_4_step, bg="#222", fg="white").pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        tk.Button(feat_f, text="📸 SNAPSHOT", command=self.take_snapshot, bg="#222", fg="white").pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

    # --- FUNCTIONAL LOGIC ---

    def _placeholder(self):
        img = Image.new('RGB', (550, 400), color='#080808')
        tk_img = ImageTk.PhotoImage(img)
        self.preview.config(image=tk_img); self.preview.image = tk_img

    def start(self):
        if self.running: return
        idx = int(self.cam_entry.get())
        self.cap = cv2.VideoCapture(idx)
        if not self.cap.isOpened(): messagebox.showerror("Error", "Camera Not Found"); return
        self.running = True
        threading.Thread(target=self._main_loop, daemon=True).start()

    def stop(self):
        self.running = False
        if self.cap: self.cap.release()
        self._placeholder()

    def _main_loop(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret: break
            self.frame = frame.copy()
            
            if EmotionTrackerApp.face_rect:
                x, y, w, h = EmotionTrackerApp.face_rect
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 212, 255), 2)

            if time.time() - self.last_analysis > 1.5:
                self.last_analysis = time.time()
                threading.Thread(target=self._ai_analysis, args=(frame.copy(),), daemon=True).start()

            img = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img).resize((550, 400))
            tk_img = ImageTk.PhotoImage(img)
            self.master.after(0, self._update_video, tk_img)
            time.sleep(0.01)

    def _update_video(self, img):
        self.preview.config(image=img); self.preview.image = img

    def _ai_analysis(self, frame):
        try:
            res = DeepFace.analyze(frame, actions=['emotion'], silent=True)[0]
            dom = res['dominant_emotion']
            r = res['region']
            EmotionTrackerApp.face_rect = (r['x'], r['y'], r['w'], r['h'])
            self.smoother.add(dom)
            smoothed = self.smoother.get()
            self.master.after(0, lambda: self._process_result(smoothed))
        except: EmotionTrackerApp.face_rect = None

    def _process_result(self, emo):
        self.current_emo_key = emo
        data = EMOTION_DATA.get(emo, EMOTION_DATA["neutral"])
        media, pos, streak = self.media_mgr.get_media(emo)
        
        # UI Updates
        self.lbl_emoji.config(text=data['emoji'])
        self.lbl_emo.config(text=emo.upper(), fg=data['color'])
        self.lbl_adv.config(text=data['reason'])
        self.lbl_cycle.config(text=f"Cycle: {pos+1}/3 | Streak: {streak} detections")
        
        # History
        t = datetime.now().strftime("%H:%M:%S")
        self.tree.insert("", 0, values=(t, emo.upper(), ""), tags=(emo,))
        self.history.appendleft({"time": t, "emo": emo, "media": media, "comment": ""})

        if self.voice_var.get():
            threading.Thread(target=lambda: (self.tts.say(f"{emo}"), self.tts.runAndWait()), daemon=True).start()

    # --- ACTION METHODS ---

    def add_comment(self):
        sel = self.tree.selection()
        if not sel: messagebox.showinfo("Tip", "Select a history row first"); return
        comment = tk.simpledialog.askstring("Log", "Add a personal note:")
        if comment:
            curr = list(self.tree.item(sel[0], 'values'))
            curr[2] = comment
            self.tree.item(sel[0], values=curr)
            # Sync with history list
            for h in self.history:
                if h["time"] == curr[0]: h["comment"] = comment; break

    def clear_history(self):
        if messagebox.askyesno("Confirm", "Clear all session logs?"):
            self.tree.delete(*self.tree.get_children())
            self.history.clear()

    def open_song(self): 
        if self.history: webbrowser.open(self.history[0]['media']['songs'][0])
    def open_poetry(self): 
        if self.history: webbrowser.open(self.history[0]['media']['poetry'][0])
    def open_novel(self): 
        if self.history: webbrowser.open(self.history[0]['media']['novels'][0])
    def open_alt(self): 
        if self.history: webbrowser.open(self.history[0]['media']['alt'])

    def take_snapshot(self):
        if self.frame is not None:
            fn = f"scan_{datetime.now().strftime('%H%M%S')}.jpg"
            cv2.imwrite(fn, self.frame); messagebox.showinfo("Saved", f"Snapshot: {fn}")

    def export_csv(self):
        if not self.history: return
        with open("emotion_pro_report.csv", "w", newline="") as f:
            w = csv.writer(f); w.writerow(["Time", "Emotion", "Comment"])
            for h in self.history: w.writerow([h['time'], h['emo'], h['comment']])
        messagebox.showinfo("Export", "CSV Saved!")

    def ai_report(self):
        emo = self.current_emo_key
        data = EMOTION_DATA[emo]
        msg = f"NEURAL ANALYSIS REPORT\n\nDetected State: {emo.upper()}\nIntelligence Advice: {data['reason']}\nSuggested Reading: {data['book']}\n\nSummary: {data['summary']}"
        self._popup("AI Assistant", msg)

    def show_4_step(self):
        emo = self.current_emo_key
        steps = EMOTION_CYCLES[emo]['steps']
        color = EMOTION_CYCLES[emo]['color']
        
        win = tk.Toplevel(self.master); win.title("Therapeutic Cycle"); win.geometry("450x550"); win.configure(bg="#050505")
        tk.Label(win, text=f"{emo.upper()} PROCESSING PATH", font=("Orbitron", 14, "bold"), bg="#050505", fg=color).pack(pady=15)
        
        for i, s in enumerate(steps):
            f = tk.Frame(win, bg="#111", padx=10, pady=10, highlightbackground=color, highlightthickness=1)
            f.pack(fill=tk.X, padx=20, pady=5)
            tk.Label(f, text=f"STEP {i+1}: {s['name']}", font=("Arial", 10, "bold"), bg="#111", fg=color).pack(anchor="w")
            tk.Label(f, text=s['description'], bg="#111", fg="white", font=("Arial", 9)).pack(anchor="w")
            tk.Label(f, text=f"Action: {s['action']}", bg="#111", fg=THEME["accent"], font=("Arial", 8, "italic")).pack(anchor="w")

    def _popup(self, title, txt):
        w = tk.Toplevel(self.master); w.title(title); w.geometry("400x350"); w.configure(bg="#0A0A0A")
        tk.Label(w, text=txt, bg="#0A0A0A", fg="white", font=("Arial", 11), wraplength=350, justify="left", pady=20).pack()
        tk.Button(w, text="CLOSE", command=w.destroy, bg=THEME["danger"], fg="white", width=10).pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = EmotionTrackerApp(root)
    root.mainloop()
