"""
Emotion Tracker & Recommendation System — Aurora Gradient Edition
Powered by CustomTkinter with Aurora Theme
Restructured by: Gemini AI | Enhanced by: GitHub Copilot
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
    import customtkinter as ctk
    import tkinter as tk
    from tkinter import ttk, messagebox
    from PIL import Image, ImageTk, ImageDraw
    import pyttsx3
except Exception as e:
    print(f"Missing Library Error: {e}")
    sys.exit(1)

# =========================
# AURORA GRADIENT THEME CONFIGURATION
# =========================
# CustomTkinter appearance settings
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Aurora gradient colors (purple, blue, pink, cyan)
AURORA_THEME = {
    "bg_dark": "#0D0D1A",           # Deep space dark
    "bg_card": "#1A1A2E",           # Card background
    "bg_secondary": "#16213E",      # Secondary background
    "aurora_purple": "#9D4EDD",     # Aurora purple
    "aurora_blue": "#7B2CBF",       # Aurora blue-purple
    "aurora_pink": "#E040FB",       # Aurora pink
    "aurora_cyan": "#00E5FF",       # Aurora cyan
    "aurora_magenta": "#C77DFF",    # Aurora light purple
    "text_primary": "#FFFFFF",      # White text
    "text_secondary": "#B8B8D1",    # Light gray text
    "gradient_start": "#667eea",    # Gradient start (indigo)
    "gradient_end": "#764ba2",      # Gradient end (purple)
    "success": "#00E676",           # Success green
    "danger": "#FF5252",            # Danger red
    "warning": "#FFD740",           # Warning yellow
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
    "happy": {"emoji": "😊", "color": AURORA_THEME["success"], "reason": "Positive vibes! Share your joy.", "book": "The Alchemist", "summary": "A journey to find your destiny."},
    "sad": {"emoji": "😢", "color": AURORA_THEME["aurora_blue"], "reason": "Low energy detected. Take it easy.", "book": "Peer-e-Kamil", "summary": "A path of spiritual discovery."},
    "angry": {"emoji": "😡", "color": AURORA_THEME["danger"], "reason": "Tension detected. Take deep breaths.", "book": "The Power of Now", "summary": "Living in the present moment."},
    "fear": {"emoji": "😨", "color": AURORA_THEME["aurora_purple"], "reason": "Anxiety detected. You are safe.", "book": "Atomic Habits", "summary": "Tiny changes, big results."},
    "surprise": {"emoji": "😲", "color": AURORA_THEME["warning"], "reason": "Shock detected. Adapt and learn.", "book": "Who Moved My Cheese", "summary": "Dealing with change."},
    "neutral": {"emoji": "😐", "color": AURORA_THEME["aurora_cyan"], "reason": "Balanced state. Keep focusing.", "book": "Think Like a Monk", "summary": "Purpose and clarity."}
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
# MAIN APPLICATION (CustomTkinter Aurora Edition)
# =========================

class EmotionTrackerApp:
    face_rect = None

    def __init__(self, master):
        self.master = master
        self.master.title("NEURAL MOOD PRO — AURORA EDITION")
        self.master.geometry("1280x900")
        self.master.configure(fg_color=AURORA_THEME["bg_dark"])
        
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

        self._build_interface()
        self._apply_tree_styles()

    def _apply_tree_styles(self):
        """Apply styles to ttk Treeview for consistency with Aurora theme"""
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Aurora.Treeview", 
                       background=AURORA_THEME["bg_card"], 
                       foreground=AURORA_THEME["text_primary"], 
                       fieldbackground=AURORA_THEME["bg_card"], 
                       rowheight=28,
                       font=("Segoe UI", 10))
        style.map("Aurora.Treeview", 
                 background=[('selected', AURORA_THEME['aurora_purple'])], 
                 foreground=[('selected', 'white')])
        style.configure("Aurora.Treeview.Heading", 
                       background=AURORA_THEME["bg_secondary"], 
                       foreground=AURORA_THEME["aurora_cyan"], 
                       font=("Segoe UI", 10, "bold"))

    def _build_interface(self):
        # Main container
        main_container = ctk.CTkFrame(self.master, fg_color=AURORA_THEME["bg_dark"])
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header with Aurora gradient effect
        self._create_header(main_container)
        
        # Content area with two panels
        content_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, pady=10)
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)
        
        # Left Panel - Video Feed & Controls
        self._create_left_panel(content_frame)
        
        # Right Panel - Dashboard & Logs
        self._create_right_panel(content_frame)

    def _create_header(self, parent):
        """Create Aurora-styled header"""
        header_frame = ctk.CTkFrame(parent, fg_color=AURORA_THEME["bg_card"], corner_radius=15, height=100)
        header_frame.pack(fill="x", pady=(0, 10))
        header_frame.pack_propagate(False)
        
        # Aurora accent line at top
        accent_frame = ctk.CTkFrame(header_frame, fg_color=AURORA_THEME["aurora_purple"], height=3, corner_radius=0)
        accent_frame.pack(fill="x")
        
        # Title
        title_label = ctk.CTkLabel(
            header_frame, 
            text="✨ NEURAL MOOD PRO",
            font=ctk.CTkFont(family="Segoe UI", size=32, weight="bold"),
            text_color=AURORA_THEME["aurora_cyan"]
        )
        title_label.pack(pady=(15, 5))
        
        # Subtitle with gradient-like effect (using multiple colors in description)
        subtitle_label = ctk.CTkLabel(
            header_frame, 
            text="Advanced Emotion Intelligence System | Aurora Edition",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=AURORA_THEME["aurora_magenta"]
        )
        subtitle_label.pack()

    def _create_left_panel(self, parent):
        """Create left panel with video feed and controls"""
        left_panel = ctk.CTkFrame(parent, fg_color=AURORA_THEME["bg_card"], corner_radius=15)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        # Video Preview Frame
        preview_frame = ctk.CTkFrame(left_panel, fg_color=AURORA_THEME["bg_secondary"], corner_radius=10)
        preview_frame.pack(fill="x", padx=15, pady=15)
        
        # Aurora border effect around video
        self.preview = ctk.CTkLabel(preview_frame, text="", fg_color="#000000", corner_radius=8)
        self.preview.pack(padx=3, pady=3)
        self._placeholder()
        
        # System Controls Card
        controls_frame = ctk.CTkFrame(left_panel, fg_color=AURORA_THEME["bg_secondary"], corner_radius=10)
        controls_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        controls_label = ctk.CTkLabel(
            controls_frame, 
            text="🎮 SYSTEM CONTROLS",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=AURORA_THEME["aurora_cyan"]
        )
        controls_label.pack(pady=(15, 10))
        
        # Button container
        btn_container = ctk.CTkFrame(controls_frame, fg_color="transparent")
        btn_container.pack(fill="x", padx=15, pady=(0, 15))
        
        # Start Button with Aurora gradient colors
        start_btn = ctk.CTkButton(
            btn_container,
            text="▶ START AI SCAN",
            command=self.start,
            fg_color=AURORA_THEME["aurora_purple"],
            hover_color=AURORA_THEME["aurora_blue"],
            font=ctk.CTkFont(size=13, weight="bold"),
            height=45,
            corner_radius=10
        )
        start_btn.pack(side="left", expand=True, fill="x", padx=(0, 5))
        
        # Stop Button
        stop_btn = ctk.CTkButton(
            btn_container,
            text="⏹ STOP",
            command=self.stop,
            fg_color=AURORA_THEME["danger"],
            hover_color="#FF1744",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=45,
            corner_radius=10
        )
        stop_btn.pack(side="left", expand=True, fill="x", padx=(5, 0))
        
        # Voice toggle
        self.voice_var = ctk.BooleanVar(value=True)
        voice_switch = ctk.CTkSwitch(
            controls_frame,
            text="AI Voice Feedback",
            variable=self.voice_var,
            font=ctk.CTkFont(size=12),
            text_color=AURORA_THEME["text_secondary"],
            progress_color=AURORA_THEME["aurora_pink"],
            button_color=AURORA_THEME["aurora_cyan"]
        )
        voice_switch.pack(pady=(0, 15))
        
        # Camera Settings
        settings_frame = ctk.CTkFrame(left_panel, fg_color=AURORA_THEME["bg_secondary"], corner_radius=10)
        settings_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        settings_label = ctk.CTkLabel(
            settings_frame, 
            text="⚙️ CAMERA SETTINGS",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=AURORA_THEME["aurora_cyan"]
        )
        settings_label.pack(pady=(15, 10))
        
        cam_container = ctk.CTkFrame(settings_frame, fg_color="transparent")
        cam_container.pack(fill="x", padx=15, pady=(0, 15))
        
        ctk.CTkLabel(
            cam_container, 
            text="Camera Index:",
            font=ctk.CTkFont(size=12),
            text_color=AURORA_THEME["text_secondary"]
        ).pack(side="left")
        
        self.cam_entry = ctk.CTkEntry(
            cam_container, 
            width=60, 
            fg_color=AURORA_THEME["bg_card"],
            border_color=AURORA_THEME["aurora_purple"],
            text_color=AURORA_THEME["text_primary"]
        )
        self.cam_entry.insert(0, "0")
        self.cam_entry.pack(side="left", padx=10)

    def _create_right_panel(self, parent):
        """Create right panel with dashboard and logs"""
        right_panel = ctk.CTkFrame(parent, fg_color=AURORA_THEME["bg_card"], corner_radius=15)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        
        # Create scrollable frame for right panel content
        scroll_frame = ctk.CTkScrollableFrame(right_panel, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Live Status Dashboard
        self._create_status_dashboard(scroll_frame)
        
        # Media Cycle Info
        self._create_cycle_info(scroll_frame)
        
        # Recommendation Hub
        self._create_recommendation_hub(scroll_frame)
        
        # Detection History
        self._create_history_section(scroll_frame)
        
        # Action Buttons
        self._create_action_buttons(scroll_frame)
        
        # Feature Buttons
        self._create_feature_buttons(scroll_frame)

    def _create_status_dashboard(self, parent):
        """Create the live emotion status display"""
        dashboard = ctk.CTkFrame(parent, fg_color=AURORA_THEME["bg_secondary"], corner_radius=12)
        dashboard.pack(fill="x", padx=10, pady=10)
        
        # Inner container for horizontal layout
        inner = ctk.CTkFrame(dashboard, fg_color="transparent")
        inner.pack(fill="x", padx=20, pady=20)
        
        # Emoji display
        self.lbl_emoji = ctk.CTkLabel(
            inner, 
            text="❓",
            font=ctk.CTkFont(size=70),
            text_color=AURORA_THEME["text_primary"]
        )
        self.lbl_emoji.pack(side="left", padx=(0, 20))
        
        # Info container
        info_frame = ctk.CTkFrame(inner, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True)
        
        self.lbl_emo = ctk.CTkLabel(
            info_frame,
            text="AWAITING DATA",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=AURORA_THEME["aurora_cyan"]
        )
        self.lbl_emo.pack(anchor="w")
        
        self.lbl_adv = ctk.CTkLabel(
            info_frame,
            text="System ready for facial analysis...",
            font=ctk.CTkFont(size=12),
            text_color=AURORA_THEME["text_secondary"],
            wraplength=300
        )
        self.lbl_adv.pack(anchor="w", pady=(5, 0))

    def _create_cycle_info(self, parent):
        """Create media cycle information display"""
        cycle_frame = ctk.CTkFrame(parent, fg_color=AURORA_THEME["bg_secondary"], corner_radius=10)
        cycle_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.lbl_cycle = ctk.CTkLabel(
            cycle_frame,
            text="📊 Cycle: 0/3 | Streak: 0 detections",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=AURORA_THEME["aurora_magenta"]
        )
        self.lbl_cycle.pack(pady=12)

    def _create_recommendation_hub(self, parent):
        """Create recommendation buttons"""
        hub_frame = ctk.CTkFrame(parent, fg_color=AURORA_THEME["bg_secondary"], corner_radius=10)
        hub_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        hub_label = ctk.CTkLabel(
            hub_frame,
            text="🎯 RECOMMENDATION HUB",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=AURORA_THEME["aurora_cyan"]
        )
        hub_label.pack(pady=(15, 10))
        
        btn_container = ctk.CTkFrame(hub_frame, fg_color="transparent")
        btn_container.pack(fill="x", padx=15, pady=(0, 15))
        
        buttons = [
            ("🎵 SONG", self.open_song, AURORA_THEME["aurora_purple"]),
            ("📝 POETRY", self.open_poetry, AURORA_THEME["aurora_blue"]),
            ("📚 NOVEL", self.open_novel, AURORA_THEME["aurora_pink"]),
            ("🔥 ALT", self.open_alt, AURORA_THEME["aurora_magenta"])
        ]
        
        for text, cmd, color in buttons:
            btn = ctk.CTkButton(
                btn_container,
                text=text,
                command=cmd,
                fg_color=color,
                hover_color=AURORA_THEME["aurora_cyan"],
                font=ctk.CTkFont(size=11, weight="bold"),
                height=40,
                corner_radius=8
            )
            btn.pack(side="left", expand=True, fill="x", padx=2)

    def _create_history_section(self, parent):
        """Create detection history section with Treeview"""
        history_frame = ctk.CTkFrame(parent, fg_color=AURORA_THEME["bg_secondary"], corner_radius=10)
        history_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        history_label = ctk.CTkLabel(
            history_frame,
            text="📋 DETECTION HISTORY",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=AURORA_THEME["aurora_cyan"]
        )
        history_label.pack(pady=(15, 10))
        
        # Treeview container (using tk.Frame for ttk compatibility)
        tree_container = tk.Frame(history_frame, bg=AURORA_THEME["bg_card"])
        tree_container.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        self.tree = ttk.Treeview(
            tree_container, 
            columns=("T", "E", "C"), 
            show="headings", 
            height=8,
            style="Aurora.Treeview"
        )
        self.tree.heading("T", text="TIME")
        self.tree.heading("E", text="EMOTION")
        self.tree.heading("C", text="COMMENT")
        self.tree.column("T", width=90)
        self.tree.column("E", width=110)
        self.tree.column("C", width=200)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _create_action_buttons(self, parent):
        """Create data action buttons"""
        action_frame = ctk.CTkFrame(parent, fg_color="transparent")
        action_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        actions = [
            ("💬 ADD COMMENT", self.add_comment, AURORA_THEME["bg_secondary"]),
            ("🗑️ CLEAR LOG", self.clear_history, AURORA_THEME["danger"]),
            ("💾 EXPORT CSV", self.export_csv, AURORA_THEME["success"])
        ]
        
        for text, cmd, color in actions:
            btn = ctk.CTkButton(
                action_frame,
                text=text,
                command=cmd,
                fg_color=color,
                hover_color=AURORA_THEME["aurora_purple"],
                font=ctk.CTkFont(size=11),
                height=35,
                corner_radius=8
            )
            btn.pack(side="left", expand=True, fill="x", padx=2)

    def _create_feature_buttons(self, parent):
        """Create feature buttons"""
        feature_frame = ctk.CTkFrame(parent, fg_color="transparent")
        feature_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # AI Report button with Aurora gradient colors
        ai_btn = ctk.CTkButton(
            feature_frame,
            text="🤖 AI WELLNESS REPORT",
            command=self.ai_report,
            fg_color=AURORA_THEME["aurora_cyan"],
            hover_color=AURORA_THEME["aurora_purple"],
            font=ctk.CTkFont(size=12, weight="bold"),
            height=40,
            corner_radius=10
        )
        ai_btn.pack(side="left", expand=True, fill="x", padx=2)
        
        cycle_btn = ctk.CTkButton(
            feature_frame,
            text="🔄 4-STEP CYCLE",
            command=self.show_4_step,
            fg_color=AURORA_THEME["bg_secondary"],
            hover_color=AURORA_THEME["aurora_blue"],
            font=ctk.CTkFont(size=11),
            height=40,
            corner_radius=10
        )
        cycle_btn.pack(side="left", expand=True, fill="x", padx=2)
        
        snap_btn = ctk.CTkButton(
            feature_frame,
            text="📸 SNAPSHOT",
            command=self.take_snapshot,
            fg_color=AURORA_THEME["bg_secondary"],
            hover_color=AURORA_THEME["aurora_pink"],
            font=ctk.CTkFont(size=11),
            height=40,
            corner_radius=10
        )
        snap_btn.pack(side="left", expand=True, fill="x", padx=2)

    # --- FUNCTIONAL LOGIC ---

    def _placeholder(self):
        """Create placeholder image for video preview"""
        img = Image.new('RGB', (530, 380), color=AURORA_THEME["bg_dark"])
        # Add Aurora-styled border effect
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, 529, 379], outline=AURORA_THEME["aurora_purple"], width=2)
        tk_img = ImageTk.PhotoImage(img)
        self.preview.configure(image=tk_img)
        self.preview.image = tk_img

    def start(self):
        if self.running: return
        try:
            idx = int(self.cam_entry.get())
        except ValueError:
            idx = 0
        self.cap = cv2.VideoCapture(idx)
        if not self.cap.isOpened(): 
            messagebox.showerror("Error", "Camera Not Found")
            return
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
                # Aurora-styled face rectangle
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 230), 2)  # Purple/Pink color

            if time.time() - self.last_analysis > 1.5:  # Analysis interval
                self.last_analysis = time.time()
                threading.Thread(target=self._ai_analysis, args=(frame.copy(),), daemon=True).start()

            img = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img).resize((530, 380))
            tk_img = ImageTk.PhotoImage(img)
            self.master.after(0, self._update_video, tk_img)
            time.sleep(0.01)

    def _update_video(self, img):
        self.preview.configure(image=img)
        self.preview.image = img

    def _ai_analysis(self, frame):
        try:
            # Enhanced detection with RetinaFace for better accuracy
            res = DeepFace.analyze(
                frame, 
                actions=['emotion'], 
                enforce_detection=False,  # Allow graceful handling when no face detected
                detector_backend='retinaface',  # More accurate face detection
                silent=True
            )[0]
            dom = res['dominant_emotion']
            r = res['region']
            EmotionTrackerApp.face_rect = (r['x'], r['y'], r['w'], r['h'])
            self.smoother.add(dom)
            smoothed = self.smoother.get()
            self.master.after(0, lambda: self._process_result(smoothed))
        except Exception:
            # Try alternative detection if RetinaFace fails
            try:
                res = DeepFace.analyze(
                    frame, 
                    actions=['emotion'], 
                    enforce_detection=False,
                    detector_backend='opencv',
                    silent=True
                )[0]
                dom = res['dominant_emotion']
                r = res['region']
                EmotionTrackerApp.face_rect = (r['x'], r['y'], r['w'], r['h'])
                self.smoother.add(dom)
                smoothed = self.smoother.get()
                self.master.after(0, lambda: self._process_result(smoothed))
            except:
                EmotionTrackerApp.face_rect = None

    def _process_result(self, emo):
        self.current_emo_key = emo
        data = EMOTION_DATA.get(emo, EMOTION_DATA["neutral"])
        media, pos, streak = self.media_mgr.get_media(emo)
        
        # UI Updates with Aurora colors
        self.lbl_emoji.configure(text=data['emoji'])
        self.lbl_emo.configure(text=emo.upper(), text_color=data['color'])
        self.lbl_adv.configure(text=data['reason'])
        self.lbl_cycle.configure(text=f"📊 Cycle: {pos+1}/3 | Streak: {streak} detections")
        
        # History
        t = datetime.now().strftime("%H:%M:%S")
        self.tree.insert("", 0, values=(t, emo.upper(), ""), tags=(emo,))
        self.history.appendleft({"time": t, "emo": emo, "media": media, "comment": ""})

        if self.voice_var.get() and self.tts:
            threading.Thread(target=lambda: (self.tts.say(f"{emo}"), self.tts.runAndWait()), daemon=True).start()

    # --- ACTION METHODS ---

    def add_comment(self):
        sel = self.tree.selection()
        if not sel: 
            messagebox.showinfo("Tip", "Select a history row first")
            return
        
        # Create custom dialog with Aurora theme
        dialog = ctk.CTkInputDialog(
            text="Add a personal note:",
            title="Log Comment"
        )
        comment = dialog.get_input()
        
        if comment:
            curr = list(self.tree.item(sel[0], 'values'))
            curr[2] = comment
            self.tree.item(sel[0], values=curr)
            # Sync with history list
            for h in self.history:
                if h["time"] == curr[0]: 
                    h["comment"] = comment
                    break

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
            cv2.imwrite(fn, self.frame)
            messagebox.showinfo("Saved", f"Snapshot saved: {fn}")

    def export_csv(self):
        if not self.history: 
            messagebox.showinfo("Info", "No data to export")
            return
        with open("emotion_pro_report.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["Time", "Emotion", "Comment"])
            for h in self.history: 
                w.writerow([h['time'], h['emo'], h['comment']])
        messagebox.showinfo("Export", "CSV Saved: emotion_pro_report.csv")

    def ai_report(self):
        emo = self.current_emo_key
        data = EMOTION_DATA[emo]
        
        # Create Aurora-styled report popup
        report_win = ctk.CTkToplevel(self.master)
        report_win.title("AI Wellness Report")
        report_win.geometry("450x400")
        report_win.configure(fg_color=AURORA_THEME["bg_dark"])
        
        # Header
        header = ctk.CTkLabel(
            report_win,
            text="🤖 NEURAL ANALYSIS REPORT",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=AURORA_THEME["aurora_cyan"]
        )
        header.pack(pady=20)
        
        # Content frame
        content = ctk.CTkFrame(report_win, fg_color=AURORA_THEME["bg_card"], corner_radius=15)
        content.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Report details
        details = [
            ("Detected State:", emo.upper(), data['color']),
            ("Intelligence Advice:", data['reason'], AURORA_THEME["text_secondary"]),
            ("Suggested Reading:", data['book'], AURORA_THEME["aurora_magenta"]),
            ("Summary:", data['summary'], AURORA_THEME["text_secondary"])
        ]
        
        for label, value, color in details:
            row = ctk.CTkFrame(content, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=8)
            
            ctk.CTkLabel(
                row,
                text=label,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=AURORA_THEME["aurora_cyan"]
            ).pack(anchor="w")
            
            ctk.CTkLabel(
                row,
                text=value,
                font=ctk.CTkFont(size=14),
                text_color=color,
                wraplength=350
            ).pack(anchor="w")
        
        # Close button
        close_btn = ctk.CTkButton(
            report_win,
            text="CLOSE",
            command=report_win.destroy,
            fg_color=AURORA_THEME["danger"],
            hover_color="#FF1744",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=120
        )
        close_btn.pack(pady=10)

    def show_4_step(self):
        emo = self.current_emo_key
        steps = EMOTION_CYCLES[emo]['steps']
        color = EMOTION_CYCLES[emo]['color']
        
        # Aurora-styled 4-step cycle window
        cycle_win = ctk.CTkToplevel(self.master)
        cycle_win.title("Therapeutic Cycle")
        cycle_win.geometry("500x650")
        cycle_win.configure(fg_color=AURORA_THEME["bg_dark"])
        
        # Header
        header = ctk.CTkLabel(
            cycle_win,
            text=f"✨ {emo.upper()} PROCESSING PATH",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=AURORA_THEME["aurora_cyan"]
        )
        header.pack(pady=20)
        
        # Scrollable frame for steps
        scroll = ctk.CTkScrollableFrame(cycle_win, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        aurora_colors = [
            AURORA_THEME["aurora_purple"],
            AURORA_THEME["aurora_blue"],
            AURORA_THEME["aurora_pink"],
            AURORA_THEME["aurora_magenta"]
        ]
        
        for i, s in enumerate(steps):
            step_color = aurora_colors[i % len(aurora_colors)]
            
            step_frame = ctk.CTkFrame(scroll, fg_color=AURORA_THEME["bg_card"], corner_radius=12)
            step_frame.pack(fill="x", pady=8)
            
            # Step header
            step_header = ctk.CTkLabel(
                step_frame,
                text=f"STEP {i+1}: {s['name'].upper()}",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=step_color
            )
            step_header.pack(anchor="w", padx=15, pady=(15, 5))
            
            # Description
            desc_label = ctk.CTkLabel(
                step_frame,
                text=s['description'],
                font=ctk.CTkFont(size=11),
                text_color=AURORA_THEME["text_primary"]
            )
            desc_label.pack(anchor="w", padx=15)
            
            # Action
            action_label = ctk.CTkLabel(
                step_frame,
                text=f"Action: {s['action']}",
                font=ctk.CTkFont(size=10),
                text_color=AURORA_THEME["aurora_cyan"]
            )
            action_label.pack(anchor="w", padx=15, pady=(5, 15))

    def _popup(self, title, txt):
        """Create Aurora-styled popup"""
        popup = ctk.CTkToplevel(self.master)
        popup.title(title)
        popup.geometry("400x350")
        popup.configure(fg_color=AURORA_THEME["bg_dark"])
        
        content = ctk.CTkLabel(
            popup,
            text=txt,
            font=ctk.CTkFont(size=12),
            text_color=AURORA_THEME["text_primary"],
            wraplength=350,
            justify="left"
        )
        content.pack(pady=30, padx=20)
        
        close_btn = ctk.CTkButton(
            popup,
            text="CLOSE",
            command=popup.destroy,
            fg_color=AURORA_THEME["danger"],
            hover_color="#FF1744",
            width=100
        )
        close_btn.pack(pady=10)

if __name__ == "__main__":
    root = ctk.CTk()
    app = EmotionTrackerApp(root)
    root.mainloop()
