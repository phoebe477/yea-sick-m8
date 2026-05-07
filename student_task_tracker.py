"""
student_task_tracker.py - Student Task Tracker

Tkinter-based GUI for managing student coursework tasks.
Features: add/edit/delete tasks, deadline-proximity colour coding,
clickable dashboard filter cards, column-header sorting, calendar view,
Flappy Book gamified deletion, dark mode, confetti celebration, trash/restore.

Dependencies: tkinter, json, os, datetime, random, calendar (all standard library).
Data is persisted to 'student_tasks.json' and 'deleted_tasks.json'.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta
import json
import os
import random
import calendar

# =========================
# EXAMPLE DATA TEMPLATES
# =========================

EXAMPLE_SUBJECTS = [
    "General", "Maths", "English", "History", "Physics",
    "Chemistry", "Biology", "Computer Sci", "Geography", "French", "Art", "Music", "Psychology"
]

EXAMPLE_TASK_TEMPLATES = [
    ("Essay: Causes of WW1", "History", "High"),
    ("Calculus Problem Set 4", "Maths", "High"),
    ("Lab Report: Titration", "Chemistry", "Medium"),
    ("Read: Of Mice and Men Ch.5-7", "English", "Low"),
    ("Waves Revision Notes", "Physics", "Medium"),
    ("French Oral Presentation", "French", "High"),
    ("Binary Trees Assignment", "Computer Sci", "High"),
    ("River Erosion Essay", "Geography", "Medium"),
    ("Sketchbook Submission", "Art", "Low"),
    ("Cell Division Quiz Prep", "Biology", "High"),
    ("Statistics Coursework", "Maths", "High"),
    ("Poetry Analysis: Ozymandias", "English", "Medium"),
    ("Source Evaluation: Cold War", "History", "Low"),
    ("Python Sorting Algorithms", "Computer Sci", "Medium"),
    ("Organic Chemistry Notes", "Chemistry", "Low"),
    ("Mock Exam Revision: Mechanics", "Physics", "High"),
    ("Grammar Exercises p.34-40", "French", "Low"),
    ("Map Skills Test Revision", "Geography", "Medium"),
    ("Genetics Past Papers", "Biology", "High"),
    ("Final Piece Planning", "Art", "Medium"),
    ("Trigonometry Worksheet", "Maths", "Low"),
    ("Macbeth Essay Draft", "English", "High"),
    ("Flowchart for Game Project", "Computer Sci", "Low"),
    ("Timeline Poster: Industrial Revolution", "History", "Low"),
    ("Electricity & Circuits Lab", "Physics", "Medium"),
    ("Composition: String Quartet", "Music", "Medium"),
    ("Listening Exam Practice", "Music", "Low"),
    ("Memory & Cognition Essay", "Psychology", "High"),
    ("Research: Milgram Experiment", "Psychology", "Medium"),
    ("Reaction Rates Experiment Write-up", "Chemistry", "High"),
    ("Ecosystems Case Study", "Geography", "Low"),
    ("Comparative Essay: 1984 vs BNW", "English", "High"),
    ("Database Design ERD", "Computer Sci", "Medium"),
    ("Calculus: Integration by Parts", "Maths", "Medium"),
    ("Photosynthesis Diagram & Notes", "Biology", "Low"),
    ("Cold War Timeline", "History", "Medium"),
    ("Refraction & Lenses Worksheet", "Physics", "Low"),
    ("French Writing Coursework Draft", "French", "High"),
    ("Lino Print Final Design", "Art", "High"),
    ("Attachment Theory Summary", "Psychology", "Low"),
]

DUE_TIMES = ["09:00", "10:00", "11:00", "12:00", "14:00", "15:00", "16:00", "17:00", "18:00", "23:59"]


def generate_example_tasks():
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    tasks = []
    templates = EXAMPLE_TASK_TEMPLATES[:]
    random.shuffle(templates)
    for i, (title, subject, priority) in enumerate(templates, start=1):
        days_ahead = random.randint(-10, 60)
        due_time = random.choice(DUE_TIMES)
        due_date = today + timedelta(days=days_ahead)
        due_str = due_date.strftime("%d/%m/%Y") + " " + due_time
        done = random.random() < 0.15
        tasks.append({
            "id": i, "title": title, "subject": subject,
            "priority": priority, "due": due_str, "done": done
        })
    return tasks


# =========================
# FLAPPY BOOK MINI-GAME
# =========================

class FlappyBookGame:
    def __init__(self, parent, task_title, on_success):
        self.parent = parent
        self.task_title = task_title
        self.on_success = on_success
        self.score = 0
        self.game_running = False
        self.game_started = False
        self.target_score = 5
        self._game_loop_id = None

        self.window = tk.Toplevel(parent)
        self.window.title(f"Flappy Book - Delete: {task_title}")
        self.window.geometry("400x620")
        self.window.resizable(False, False)
        self.window.configure(bg="#87CEEB")

        self.book_y = 250
        self.book_velocity = 0
        self.gravity = 0.5
        self.jump_strength = -8

        self.pipes = []
        self.pipe_width = 60
        self.pipe_gap = 150
        self.pipe_spacing = 250
        self.pipe_speed = 3

        self.canvas = tk.Canvas(self.window, width=400, height=500, bg="skyblue",
                                highlightthickness=0)
        self.canvas.pack()

        bottom = tk.Frame(self.window, bg="#1E3A8A", height=120)
        bottom.pack(fill=tk.X)
        bottom.pack_propagate(False)

        self.score_label = tk.Label(bottom, text=f"Score: 0 / {self.target_score}",
                                    font=("Segoe UI", 16, "bold"), bg="#1E3A8A", fg="white")
        self.score_label.pack(pady=(10, 2))

        self.status_label = tk.Label(bottom, text="Press SPACE or click the game to jump",
                                     font=("Segoe UI", 10), bg="#1E3A8A", fg="#93C5FD")
        self.status_label.pack()

        self.btn_frame = tk.Frame(bottom, bg="#1E3A8A")
        self.btn_frame.pack(pady=6)

        self._draw_book()

        self.start_msg = self.canvas.create_text(
            200, 200,
            text="PRESS SPACE OR CLICK\nTO START!\n\nScore 5 to delete this task.",
            font=("Segoe UI", 14, "bold"), fill="white", justify="center"
        )

        self.window.bind("<KeyPress-space>", self._on_space)
        self.canvas.bind("<Button-1>", self._on_click)
        self.window.after(50, lambda: self.window.focus_force())
        self._idle_animation()

    def _draw_book(self):
        y = self.book_y
        self.b_body  = self.canvas.create_rectangle(80, y, 110, y+30,
                                                    fill="#8B4513", outline="#5C2E0B", width=2)
        self.b_spine = self.canvas.create_line(95, y, 95, y+30, fill="#FFD700", width=2)
        self.b_cover = self.canvas.create_rectangle(82, y+5, 108, y+25,
                                                    fill="#F5DEB3", outline="")
        self.b_icon  = self.canvas.create_text(95, y+15, text="B",
                                               font=("Segoe UI", 9, "bold"), fill="#8B4513")

    def _move_book_to(self, y):
        self.book_y = y
        self.canvas.coords(self.b_body,  80, y,   110, y+30)
        self.canvas.coords(self.b_spine, 95, y,   95,  y+30)
        self.canvas.coords(self.b_cover, 82, y+5, 108, y+25)
        self.canvas.coords(self.b_icon,  95, y+15)

    def _on_space(self, event):
        if not self.game_started:
            self._start_game()
        elif self.game_running:
            self._jump()
        self.window.focus_force()

    def _on_click(self, event):
        if not self.game_started:
            self._start_game()
        elif self.game_running:
            self._jump()
        self.window.focus_force()

    def _start_game(self):
        self.game_started = True
        self.game_running = True
        self.canvas.delete(self.start_msg)
        self.status_label.config(text="SPACE or click to jump!")
        self._clear_btn_frame()
        self._create_pipe()
        self._loop()

    def _jump(self):
        self.book_velocity = self.jump_strength

    def _idle_animation(self):
        if not self.game_started and self.window.winfo_exists():
            import math, time
            offset = math.sin(time.time() * 2) * 8
            self._move_book_to(250 + offset)
            self.window.after(40, self._idle_animation)

    def _create_pipe(self):
        h = random.randint(80, 340)
        top = self.canvas.create_rectangle(400, 0, 400+self.pipe_width, h,
                                           fill="#2E7D32", outline="#1B5E20", width=2)
        bot = self.canvas.create_rectangle(400, h+self.pipe_gap, 400+self.pipe_width, 500,
                                           fill="#2E7D32", outline="#1B5E20", width=2)
        self.pipes.append({"x": 400, "top": top, "bot": bot, "h": h, "scored": False})

    def _clear_pipes(self):
        for p in self.pipes:
            self.canvas.delete(p["top"])
            self.canvas.delete(p["bot"])
        self.pipes.clear()

    def _loop(self):
        if not self.game_running:
            return
        self.book_velocity += self.gravity
        new_y = self.book_y + self.book_velocity
        self._move_book_to(new_y)
        if new_y <= 0 or new_y + 30 >= 500:
            self._game_over()
            return
        to_del = []
        for p in self.pipes:
            p["x"] -= self.pipe_speed
            self.canvas.coords(p["top"], p["x"], 0, p["x"]+self.pipe_width, p["h"])
            self.canvas.coords(p["bot"], p["x"], p["h"]+self.pipe_gap,
                               p["x"]+self.pipe_width, 500)
            if not p["scored"] and p["x"] + self.pipe_width < 80:
                p["scored"] = True
                self.score += 1
                self.score_label.config(text=f"Score: {self.score} / {self.target_score}")
                if self.score >= self.target_score:
                    self._win()
                    return
            if p["x"] + self.pipe_width < 0:
                to_del.append(p)
        for p in to_del:
            self.canvas.delete(p["top"])
            self.canvas.delete(p["bot"])
            self.pipes.remove(p)
        if not self.pipes or self.pipes[-1]["x"] < 400 - self.pipe_spacing:
            self._create_pipe()
        bx1, by1, bx2, by2 = 82, self.book_y + 2, 108, self.book_y + 28
        for p in self.pipes:
            px1, px2 = p["x"], p["x"] + self.pipe_width
            if bx2 > px1 and bx1 < px2:
                if by1 < p["h"] or by2 > p["h"] + self.pipe_gap:
                    self._game_over()
                    return
        self._game_loop_id = self.window.after(20, self._loop)

    def _game_over(self):
        self.game_running = False
        self.status_label.config(text=f"Game over!  Score: {self.score} / {self.target_score}",
                                 fg="#FCA5A5")
        self.canvas.create_rectangle(0, 0, 400, 500, fill="black", stipple="gray50", outline="")
        self._clear_btn_frame()
        tk.Button(self.btn_frame, text="Try Again", command=self._restart,
                  bg="#F59E0B", fg="white", font=("Segoe UI", 11, "bold"),
                  padx=18, pady=4, relief=tk.FLAT).pack(side=tk.LEFT, padx=8)
        tk.Button(self.btn_frame, text="Give Up", command=self.window.destroy,
                  bg="#EF4444", fg="white", font=("Segoe UI", 11, "bold"),
                  padx=18, pady=4, relief=tk.FLAT).pack(side=tk.LEFT, padx=8)

    def _restart(self):
        if self._game_loop_id:
            self.window.after_cancel(self._game_loop_id)
            self._game_loop_id = None
        self.score = 0
        self.book_velocity = 0
        self.game_running = True
        self.game_started = True
        self.canvas.delete("all")
        self._draw_book()
        self._move_book_to(250)
        self.score_label.config(text=f"Score: 0 / {self.target_score}")
        self.status_label.config(text="SPACE or click to jump!", fg="#93C5FD")
        self._clear_btn_frame()
        self._clear_pipes()
        self._create_pipe()
        self.window.focus_force()
        self._loop()

    def _win(self):
        self.game_running = False
        self.canvas.create_rectangle(0, 0, 400, 500, fill="#052e16", stipple="gray50", outline="")
        self.canvas.create_text(200, 220, text="WELL DONE!",
                                font=("Segoe UI", 28, "bold"), fill="#4ADE80")
        self.canvas.create_text(200, 265, text="Moving task to trash...",
                                font=("Segoe UI", 13), fill="#86EFAC")
        self.score_label.config(text=f"Score: {self.score} / {self.target_score}", fg="#4ADE80")
        self.status_label.config(text="Task deleted! Window closing...", fg="#86EFAC")
        self._clear_btn_frame()

        def _finish():
            self.window.destroy()
            self.on_success()
        self.window.after(1800, _finish)

    def _clear_btn_frame(self):
        for w in self.btn_frame.winfo_children():
            w.destroy()


# =========================
# CALENDAR VIEW
# =========================

class CalendarView:
    PRIORITY_COLOURS = {"High": "#EF4444", "Medium": "#F59E0B", "Low": "#10B981"}
    DONE_COLOUR = "#6B7280"

    def __init__(self, parent, tasks, dark_mode=False):
        self.parent = parent
        self.tasks = tasks
        self.dark_mode = dark_mode
        now = datetime.now()
        self.year = now.year
        self.month = now.month
        self.window = tk.Toplevel(parent)
        self.window.title("📅 Calendar View")
        self.window.geometry("1100x700")
        self.window.resizable(True, True)
        self._build_ui()
        self._render()

    def _build_ui(self):
        bg = "#111827" if self.dark_mode else "#F8FAFC"
        fg = "#F9FAFB" if self.dark_mode else "#1E3A8A"
        self.window.configure(bg=bg)
        nav = tk.Frame(self.window, bg=bg)
        nav.pack(fill=tk.X, pady=6, padx=10)
        tk.Button(nav, text="◀ Prev", command=self._prev_month,
                  bg="#1E3A8A", fg="white", font=("Segoe UI", 10, "bold"),
                  relief=tk.FLAT, padx=10).pack(side=tk.LEFT)
        self.nav_label = tk.Label(nav, text="", font=("Segoe UI", 16, "bold"), bg=bg, fg=fg)
        self.nav_label.pack(side=tk.LEFT, expand=True)
        tk.Button(nav, text="Next ▶", command=self._next_month,
                  bg="#1E3A8A", fg="white", font=("Segoe UI", 10, "bold"),
                  relief=tk.FLAT, padx=10).pack(side=tk.RIGHT)
        tk.Button(nav, text="Today", command=self._go_today,
                  bg="#10B981", fg="white", font=("Segoe UI", 10, "bold"),
                  relief=tk.FLAT, padx=10).pack(side=tk.RIGHT, padx=6)
        legend = tk.Frame(self.window, bg=bg)
        legend.pack(fill=tk.X, padx=10, pady=(0, 4))
        for label, colour in [("High", "#EF4444"), ("Medium", "#F59E0B"),
                               ("Low", "#10B981"), ("Done", "#6B7280")]:
            tk.Label(legend, text="●", fg=colour, bg=bg, font=("Segoe UI", 12)).pack(side=tk.LEFT)
            tk.Label(legend, text=f" {label}   ", bg=bg,
                     fg="#F9FAFB" if self.dark_mode else "#374151",
                     font=("Segoe UI", 9)).pack(side=tk.LEFT)
        outer = tk.Frame(self.window, bg=bg)
        outer.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        self.canvas_scroll = tk.Canvas(outer, bg=bg, highlightthickness=0)
        vsb = ttk.Scrollbar(outer, orient="vertical", command=self.canvas_scroll.yview)
        self.canvas_scroll.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas_scroll.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.grid_frame = tk.Frame(self.canvas_scroll, bg=bg)
        self._grid_window = self.canvas_scroll.create_window(
            (0, 0), window=self.grid_frame, anchor="nw")
        self.grid_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas_scroll.bind("<Configure>", self._on_canvas_configure)
        self.canvas_scroll.bind_all(
            "<MouseWheel>",
            lambda e: self.canvas_scroll.yview_scroll(-1 * (e.delta // 120), "units"))

    def _on_frame_configure(self, event):
        self.canvas_scroll.configure(scrollregion=self.canvas_scroll.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas_scroll.itemconfig(self._grid_window, width=event.width)

    def _tasks_for_month(self):
        result = {}
        for t in self.tasks:
            try:
                d = datetime.strptime(t["due"], "%d/%m/%Y %H:%M")
            except ValueError:
                continue
            if d.year == self.year and d.month == self.month:
                result.setdefault(d.day, []).append(t)
        return result

    def _render(self):
        bg       = "#111827" if self.dark_mode else "#F8FAFC"
        cell_bg  = "#1F2937" if self.dark_mode else "#FFFFFF"
        today    = datetime.now()
        for w in self.grid_frame.winfo_children():
            w.destroy()
        self.nav_label.config(text=calendar.month_name[self.month] + " " + str(self.year))
        for col, name in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
            tk.Label(self.grid_frame, text=name, font=("Segoe UI", 10, "bold"),
                     bg="#1E3A8A", fg="white", width=15, anchor="center", pady=4
                     ).grid(row=0, column=col, sticky="nsew", padx=1, pady=1)
        month_tasks = self._tasks_for_month()
        first_weekday, num_days = calendar.monthrange(self.year, self.month)
        row, col = 1, first_weekday
        for day in range(1, num_days + 1):
            is_today = (self.year == today.year and self.month == today.month and day == today.day)
            outline  = "#F59E0B" if is_today else ("#374151" if self.dark_mode else "#E5E7EB")
            cell = tk.Frame(self.grid_frame, bg=cell_bg,
                            highlightbackground=outline,
                            highlightthickness=2 if is_today else 1)
            cell.grid(row=row, column=col, sticky="nsew", padx=2, pady=2)
            self.grid_frame.columnconfigure(col, weight=1, uniform="cal")
            self.grid_frame.rowconfigure(row, weight=1)
            day_fg = "#F59E0B" if is_today else ("#F9FAFB" if self.dark_mode else "#1E3A8A")
            tk.Label(cell, text=str(day), font=("Segoe UI", 9, "bold"),
                     bg=cell_bg, fg=day_fg, anchor="ne").pack(fill=tk.X, padx=4, pady=(3, 1))
            day_tasks = month_tasks.get(day, [])
            for t in day_tasks[:4]:
                colour = (self.DONE_COLOUR if t["done"]
                          else self.PRIORITY_COLOURS.get(t["priority"], "#6B7280"))
                short = (t["title"][:18] + "…") if len(t["title"]) > 18 else t["title"]
                tk.Label(cell, text=f"● {short}", font=("Segoe UI", 7),
                         bg=cell_bg, fg=colour, anchor="w", cursor="hand2").pack(fill=tk.X, padx=4)
            if len(day_tasks) > 4:
                tk.Label(cell, text=f"+{len(day_tasks)-4} more…",
                         font=("Segoe UI", 7, "italic"), bg=cell_bg, fg="#9CA3AF",
                         anchor="w").pack(fill=tk.X, padx=4)
            if day_tasks:
                cell.bind("<Button-1>",
                    lambda e, d=day, dt=day_tasks: self._show_day_detail(d, dt))
                for child in cell.winfo_children():
                    child.bind("<Button-1>",
                        lambda e, d=day, dt=day_tasks: self._show_day_detail(d, dt))
            col += 1
            if col > 6:
                col = 0
                row += 1
        while col != 0:
            tk.Frame(self.grid_frame, bg=bg).grid(
                row=row, column=col, sticky="nsew", padx=2, pady=2)
            col += 1
            if col > 6:
                break

    def _show_day_detail(self, day, day_tasks):
        bg = "#111827" if self.dark_mode else "#F8FAFC"
        fg = "#F9FAFB" if self.dark_mode else "#1E3A8A"
        popup = tk.Toplevel(self.window)
        popup.title(f"Tasks for {day} {calendar.month_name[self.month]} {self.year}")
        popup.geometry("420x360")
        popup.configure(bg=bg)
        popup.grab_set()
        tk.Label(popup, text=f"📅  {day} {calendar.month_name[self.month]} {self.year}",
                 font=("Segoe UI", 13, "bold"), bg=bg, fg=fg).pack(pady=(12, 6))
        frame = tk.Frame(popup, bg=bg)
        frame.pack(fill=tk.BOTH, expand=True, padx=14)
        for t in day_tasks:
            colour  = (self.DONE_COLOUR if t["done"]
                       else self.PRIORITY_COLOURS.get(t["priority"], "#6B7280"))
            row_bg  = "#1F2937" if self.dark_mode else "#F1F5F9"
            card    = tk.Frame(frame, bg=row_bg, pady=5, padx=8)
            card.pack(fill=tk.X, pady=3)
            status  = "✓ Done" if t["done"] else "⏳ Pending"
            tk.Label(card, text=f"● {t['title']}", font=("Segoe UI", 10, "bold"),
                     fg=colour, bg=row_bg, anchor="w").pack(fill=tk.X)
            tk.Label(card, text=f"{t['subject']}  |  {t['priority']} priority  |  "
                                 f"Due {t['due']}  |  {status}",
                     font=("Segoe UI", 8), fg="#9CA3AF", bg=row_bg, anchor="w").pack(fill=tk.X)
        tk.Button(popup, text="Close", command=popup.destroy,
                  bg="#1E3A8A", fg="white", font=("Segoe UI", 10),
                  relief=tk.FLAT, padx=12).pack(pady=12)

    def _prev_month(self):
        if self.month == 1:
            self.month, self.year = 12, self.year - 1
        else:
            self.month -= 1
        self._render()

    def _next_month(self):
        if self.month == 12:
            self.month, self.year = 1, self.year + 1
        else:
            self.month += 1
        self._render()

    def _go_today(self):
        now = datetime.now()
        self.year, self.month = now.year, now.month
        self._render()


# =========================
# POMODORO TIMER
# =========================

class PomodoroTimer:
    """
    A Pomodoro timer window with work/short-break/long-break sessions,
    session counter, and optional task association.

    Modes:
        Work       — 25 min (default), configurable
        Short Break — 5 min
        Long Break  — 15 min (auto after every 4 work sessions)
    """

    MODES = {
        "work":        ("🍅 Work",         25 * 60, "#DC2626"),
        "short_break": ("☕ Short Break",   5  * 60, "#059669"),
        "long_break":  ("🌿 Long Break",   15 * 60, "#1E3A8A"),
    }

    def __init__(self, parent, dark_mode=False):
        self.parent    = parent
        self.dark_mode = dark_mode

        self.mode           = "work"
        self.time_left      = self.MODES["work"][1]
        self.running        = False
        self.session_count  = 0   # completed work sessions
        self._after_id      = None

        self.window = tk.Toplevel(parent)
        self.window.title("🍅 Pomodoro Timer")
        self.window.geometry("420x520")
        self.window.resizable(False, False)
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)

        bg = "#111827" if dark_mode else "#F8FAFC"
        self.window.configure(bg=bg)

        self._build_ui(bg)
        self._refresh_display()

    # ── UI ───────────────────────────────────────────────────────────────

    def _build_ui(self, bg):
        fg      = "white" if self.dark_mode else "#1E3A8A"
        sub_fg  = "#9CA3AF" if self.dark_mode else "#6B7280"
        card_bg = "#1F2937" if self.dark_mode else "#FFFFFF"

        # Mode label
        self.mode_label = tk.Label(self.window, text="",
                                   font=("Segoe UI", 13, "bold"), bg=bg, fg=fg)
        self.mode_label.pack(pady=(18, 2))

        # Session dots  ● ● ● ●
        self.dots_label = tk.Label(self.window, text="",
                                   font=("Segoe UI", 14), bg=bg, fg=sub_fg)
        self.dots_label.pack()

        # Big clock face
        clock_card = tk.Frame(self.window, bg=card_bg, padx=30, pady=20,
                              highlightbackground="#E5E7EB" if not self.dark_mode else "#374151",
                              highlightthickness=2)
        clock_card.pack(pady=14)

        self.time_label = tk.Label(clock_card, text="25:00",
                                   font=("Consolas", 54, "bold"),
                                   bg=card_bg, fg="#DC2626")
        self.time_label.pack()

        self.phase_label = tk.Label(clock_card, text="Ready to focus",
                                    font=("Segoe UI", 10), bg=card_bg, fg=sub_fg)
        self.phase_label.pack()

        # Progress bar (canvas)
        self.progress_canvas = tk.Canvas(self.window, width=360, height=10,
                                         bg=card_bg, highlightthickness=0)
        self.progress_canvas.pack(pady=(0, 14))
        self.progress_bg  = self.progress_canvas.create_rectangle(0, 0, 360, 10,
                                                                   fill="#E5E7EB", outline="")
        self.progress_bar = self.progress_canvas.create_rectangle(0, 0, 0, 10,
                                                                   fill="#DC2626", outline="")

        # Mode selector buttons
        mode_frame = tk.Frame(self.window, bg=bg)
        mode_frame.pack(pady=4)
        mode_btn = dict(font=("Segoe UI", 9, "bold"), relief=tk.FLAT, padx=10, pady=4)
        for key, (label, _, colour) in self.MODES.items():
            tk.Button(mode_frame, text=label, bg=colour, fg="white",
                      command=lambda k=key: self._set_mode(k),
                      **mode_btn).pack(side=tk.LEFT, padx=4)

        # Control buttons
        ctrl_frame = tk.Frame(self.window, bg=bg)
        ctrl_frame.pack(pady=10)
        ctrl_btn = dict(font=("Segoe UI", 11, "bold"), relief=tk.FLAT, padx=20, pady=8)

        self.start_btn = tk.Button(ctrl_frame, text="▶  Start",
                                   bg="#059669", fg="white",
                                   command=self._toggle, **ctrl_btn)
        self.start_btn.pack(side=tk.LEFT, padx=6)

        tk.Button(ctrl_frame, text="↺  Reset",
                  bg="#6B7280", fg="white",
                  command=self._reset, **ctrl_btn).pack(side=tk.LEFT, padx=6)

        # Custom duration row
        dur_frame = tk.Frame(self.window, bg=bg)
        dur_frame.pack(pady=6)
        tk.Label(dur_frame, text="Custom work mins:",
                 font=("Segoe UI", 9), bg=bg,
                 fg="white" if self.dark_mode else "#374151").pack(side=tk.LEFT, padx=(0, 6))
        self.custom_var = tk.StringVar(value="25")
        tk.Entry(dur_frame, textvariable=self.custom_var,
                 font=("Segoe UI", 10), width=4).pack(side=tk.LEFT)
        tk.Button(dur_frame, text="Set", command=self._apply_custom,
                  bg="#6366F1", fg="white",
                  font=("Segoe UI", 9, "bold"), relief=tk.FLAT, padx=8).pack(side=tk.LEFT, padx=6)

        # Sessions completed counter
        self.sessions_label = tk.Label(self.window, text="Sessions today: 0",
                                       font=("Segoe UI", 9), bg=bg, fg=sub_fg)
        self.sessions_label.pack(pady=(4, 0))

    # ── Timer logic ──────────────────────────────────────────────────────

    def _toggle(self):
        if self.running:
            self._pause()
        else:
            self._start()

    def _start(self):
        self.running = True
        self.start_btn.config(text="⏸  Pause", bg="#D97706")
        self.phase_label.config(text="Focusing…" if self.mode == "work" else "Resting…")
        self._tick()

    def _pause(self):
        self.running = False
        if self._after_id:
            self.window.after_cancel(self._after_id)
            self._after_id = None
        self.start_btn.config(text="▶  Resume", bg="#059669")
        self.phase_label.config(text="Paused")

    def _reset(self):
        self.running = False
        if self._after_id:
            self.window.after_cancel(self._after_id)
            self._after_id = None
        self.time_left = self.MODES[self.mode][1]
        self.start_btn.config(text="▶  Start", bg="#059669")
        self.phase_label.config(text="Ready to focus")
        self._refresh_display()

    def _tick(self):
        if not self.running:
            return
        if self.time_left <= 0:
            self._session_complete()
            return
        self.time_left -= 1
        self._refresh_display()
        self._after_id = self.window.after(1000, self._tick)

    def _session_complete(self):
        self.running = False
        self.start_btn.config(text="▶  Start", bg="#059669")

        if self.mode == "work":
            self.session_count += 1
            self.sessions_label.config(text=f"Sessions today: {self.session_count}")
            # Every 4 work sessions → long break, otherwise short break
            next_mode = "long_break" if self.session_count % 4 == 0 else "short_break"
            label, _, colour = self.MODES[next_mode]
            self.window.bell()
            messagebox.showinfo("🍅 Pomodoro Complete!",
                f"Great work! Session {self.session_count} done.\n\n"
                f"Time for a {'long' if next_mode == 'long_break' else 'short'} break.",
                parent=self.window)
            self._set_mode(next_mode)
        else:
            self.window.bell()
            messagebox.showinfo("☕ Break Over!",
                "Break finished — ready for the next session!",
                parent=self.window)
            self._set_mode("work")

    def _set_mode(self, mode):
        self.running = False
        if self._after_id:
            self.window.after_cancel(self._after_id)
            self._after_id = None
        self.mode      = mode
        self.time_left = self.MODES[mode][1]
        self.start_btn.config(text="▶  Start", bg="#059669")
        self.phase_label.config(text="Ready to focus" if mode == "work" else "Ready for break")
        self._refresh_display()

    def _apply_custom(self):
        try:
            mins = int(self.custom_var.get())
            if not 1 <= mins <= 120:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid", "Please enter a number between 1 and 120.",
                                 parent=self.window)
            return
        # Update the work mode duration and reset if currently in work mode
        self.MODES = dict(self.MODES)   # make a copy so we don't mutate the class-level dict
        label, _, colour = self.MODES["work"]
        self.MODES["work"] = (label, mins * 60, colour)
        if self.mode == "work":
            self._reset()

    def _refresh_display(self):
        label, total, colour = self.MODES[self.mode]
        mins, secs = divmod(self.time_left, 60)

        self.mode_label.config(text=label, fg=colour)
        self.time_label.config(text=f"{mins:02}:{secs:02}", fg=colour)

        # Session dots — filled for completed, empty for remaining (up to next 4-block)
        block_pos  = self.session_count % 4
        dots = "●" * block_pos + "○" * (4 - block_pos)
        self.dots_label.config(text=f"  {dots}  — {self.session_count} session{'s' if self.session_count != 1 else ''} completed")

        # Progress bar
        fraction = self.time_left / total if total > 0 else 0
        filled   = int((1 - fraction) * 360)
        self.progress_canvas.itemconfig(self.progress_bar,
                                        x2=max(filled, 0), fill=colour)

    def _on_close(self):
        self.running = False
        if self._after_id:
            self.window.after_cancel(self._after_id)
        self.window.destroy()


# =========================
# MAIN APPLICATION
# =========================

class StudentTaskTracker:

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Student Task Tracker")
        self.root.geometry("1500x900")
        self.tasks = []
        self.deleted_tasks = []
        self.subjects = ["General"]
        self.data_file = "student_tasks.json"
        self.trash_file = "deleted_tasks.json"
        self.dark_mode = False
        self._sort_col = None
        self._sort_asc = True
        self._active_filter = None  # "total"|"pending"|"done"|"overdue"|"due_soon"|None
        self.load_data()
        self.create_gui()
        self.populate_task_list()
        self.tree.bind("<Double-1>", lambda e: self.show_clock())
        self.root.after(60000, self.refresh_all)

    # ── Data persistence ────────────────────────────────────────────────

    def load_data(self):
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, "r") as f:
                    data = json.load(f)
                    self.tasks    = data.get("tasks", [])
                    self.subjects = data.get("subjects", ["General"])
            if os.path.exists(self.trash_file):
                with open(self.trash_file, "r") as f:
                    data = json.load(f)
                    self.deleted_tasks = data.get("deleted_tasks", [])
            else:
                self.deleted_tasks = []
        except Exception:
            self.tasks, self.deleted_tasks = [], []

    def save_data(self):
        with open(self.data_file, "w") as f:
            json.dump({"tasks": self.tasks, "subjects": self.subjects}, f, indent=4)
        with open(self.trash_file, "w") as f:
            json.dump({"deleted_tasks": self.deleted_tasks}, f, indent=4)

    # ── GUI setup ───────────────────────────────────────────────────────

    def create_gui(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.main = tk.Frame(self.root, bg="#F8FAFC")
        self.main.pack(fill=tk.BOTH, expand=True)

        # Scrollable canvas wrapper
        self.main_canvas = tk.Canvas(self.main, bg="#F8FAFC", highlightthickness=0)
        self.main_scrollbar = ttk.Scrollbar(self.main, orient="vertical",
                                            command=self.main_canvas.yview)
        self.main_canvas.configure(yscrollcommand=self.main_scrollbar.set)
        self.main_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.content_frame = tk.Frame(self.main_canvas, bg="#F8FAFC")
        self.canvas_window = self.main_canvas.create_window(
            (0, 0), window=self.content_frame, anchor="nw")
        self.content_frame.bind("<Configure>", self._on_content_configure)
        self.main_canvas.bind("<Configure>", self._on_canvas_configure)
        self._bind_mousewheel(self.main_canvas)

        # ── Header ──────────────────────────────────────────────────────
        self.header_frame = tk.Frame(self.content_frame, bg="#1E3A8A", pady=12)
        self.header_frame.pack(fill=tk.X)
        self.title_label = tk.Label(self.header_frame, text="📚 Student Task Tracker",
                                    font=("Segoe UI", 26, "bold"), bg="#1E3A8A", fg="white")
        self.title_label.pack(side=tk.LEFT, padx=16)
        hdr_btn = dict(font=("Segoe UI", 10, "bold"), relief=tk.FLAT, padx=12, pady=6)
        tk.Button(self.header_frame, text="+ Task", command=self.add_task,
                  bg="#10B981", fg="white", **hdr_btn).pack(side=tk.RIGHT, padx=6)
        tk.Button(self.header_frame, text="+ Subject", command=self.add_subject,
                  bg="#6366F1", fg="white", **hdr_btn).pack(side=tk.RIGHT)

        # ── Dashboard filter cards ───────────────────────────────────────
        self.dash_frame = tk.Frame(self.content_frame, bg="#F8FAFC", pady=10)
        self.dash_frame.pack(fill=tk.X, padx=12)

        card_defs = [
            ("total",    "📋 Total",    "#1E3A8A", "#3B5ECC"),
            ("pending",  "⏳ Pending",  "#DC2626", "#FF4444"),
            ("done",     "✅ Done",     "#059669", "#07C47E"),
            ("overdue",  "🔥 Overdue",  "#B91C1C", "#E33232"),
            ("due_soon", "⚠️ Due Soon", "#D97706", "#F59E0B"),
        ]

        self._dash_cards       = {}
        self._dash_card_frames = {}
        self._card_normal_bg   = {}
        self._card_active_bg   = {}

        for key, label, normal_bg, active_bg in card_defs:
            self._card_normal_bg[key] = normal_bg
            self._card_active_bg[key] = active_bg

            card = tk.Frame(self.dash_frame, bg=normal_bg, padx=18, pady=10,
                            relief=tk.FLAT, bd=0, cursor="hand2")
            card.pack(side=tk.LEFT, padx=6)
            self._dash_card_frames[key] = card

            title_lbl = tk.Label(card, text=label, font=("Segoe UI", 9, "bold"),
                                 bg=normal_bg, fg="white", cursor="hand2")
            title_lbl.pack()

            val_lbl = tk.Label(card, text="–", font=("Segoe UI", 22, "bold"),
                               bg=normal_bg, fg="white", cursor="hand2")
            val_lbl.pack()
            self._dash_cards[key] = val_lbl

            hint_lbl = tk.Label(card, text="click to filter",
                                font=("Segoe UI", 7, "italic"),
                                bg=normal_bg, fg="white", cursor="hand2")
            hint_lbl.pack()

            for widget in (card, title_lbl, val_lbl, hint_lbl):
                widget.bind("<Button-1>", lambda e, k=key: self._toggle_card_filter(k))

        # Next-due info card (not a filter)
        self.next_task_frame = tk.Frame(self.dash_frame, bg="#312E81",
                                        padx=18, pady=6, relief=tk.FLAT)
        self.next_task_frame.pack(side=tk.LEFT, padx=12, fill=tk.Y, expand=True)
        tk.Label(self.next_task_frame, text="🚀 Next Due",
                 font=("Segoe UI", 9, "bold"), bg="#312E81", fg="#C7D2FE").pack(anchor="w")
        self.next_task_title = tk.Label(self.next_task_frame, text="–",
                                        font=("Segoe UI", 13, "bold"),
                                        bg="#312E81", fg="white", anchor="w")
        self.next_task_title.pack(anchor="w")
        self.next_task_sub = tk.Label(self.next_task_frame, text="",
                                      font=("Segoe UI", 9),
                                      bg="#312E81", fg="#A5B4FC", anchor="w")
        self.next_task_sub.pack(anchor="w")

        # Active-filter banner (hidden until a card is clicked)
        self.filter_banner_frame = tk.Frame(self.content_frame, bg="#1D4ED8", pady=5)
        self.filter_banner_label = tk.Label(self.filter_banner_frame, text="",
                                            font=("Segoe UI", 9, "bold"),
                                            bg="#1D4ED8", fg="white")
        self.filter_banner_label.pack(side=tk.LEFT, padx=10)
        tk.Button(self.filter_banner_frame, text="✕ Clear filter",
                  font=("Segoe UI", 9, "bold"), relief=tk.FLAT, padx=8, pady=2,
                  bg="#2563EB", fg="white",
                  command=self._clear_card_filter).pack(side=tk.RIGHT, padx=10)

        # ── Colour legend ────────────────────────────────────────────────
        legend_frame = tk.Frame(self.content_frame, bg="#F8FAFC", pady=4)
        legend_frame.pack(fill=tk.X, padx=12)
        legend_items = [
            ("🔴 Overdue", "#DC2626"), ("🟠 ≤ 1 day",  "#EA580C"),
            ("🟡 ≤ 3 days", "#D97706"), ("🔵 ≤ 7 days", "#2563EB"),
            ("🟢 On track", "#059669"), ("⚫ Done",     "#6B7280"),
        ]
        tk.Label(legend_frame, text="Deadline colours:", font=("Segoe UI", 9, "bold"),
                 bg="#F8FAFC", fg="#374151").pack(side=tk.LEFT, padx=(0, 6))
        for text, colour in legend_items:
            tk.Label(legend_frame, text=text, font=("Segoe UI", 9),
                     bg="#F8FAFC", fg=colour).pack(side=tk.LEFT, padx=6)

        # ── Search bar ───────────────────────────────────────────────────
        self.filter_frame = tk.Frame(self.content_frame, bg="#F8FAFC")
        self.filter_frame.pack(fill=tk.X, pady=5, padx=12)
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(self.filter_frame, textvariable=self.search_var,
                                font=("Segoe UI", 11), width=28)
        search_entry.pack(side=tk.LEFT)
        search_entry.bind("<KeyRelease>", lambda e: self.apply_filters())
        flt_btn = dict(font=("Segoe UI", 9, "bold"), relief=tk.FLAT, padx=10, pady=4)
        tk.Button(self.filter_frame, text="🔍 Search", command=self.apply_filters,
                  bg="#6366F1", fg="white", **flt_btn).pack(side=tk.LEFT, padx=6)
        tk.Label(self.filter_frame, text="Click column headers to sort  ↑↓",
                 font=("Segoe UI", 9, "italic"), bg="#F8FAFC", fg="#9CA3AF").pack(side=tk.LEFT, padx=10)

        # ── Treeview ─────────────────────────────────────────────────────
        tree_frame = tk.Frame(self.content_frame, bg="#F8FAFC")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=(4, 0))
        cols = ("id", "title", "subject", "priority", "due", "countdown", "status")
        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings",
                                 height=14, selectmode="extended")
        tree_vsb = ttk.Scrollbar(tree_frame, orient="vertical",   command=self.tree.yview)
        tree_hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=tree_vsb.set, xscrollcommand=tree_hsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        tree_vsb.grid(row=0, column=1, sticky="ns")
        tree_hsb.grid(row=1, column=0, sticky="ew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        col_widths  = {"id": 40, "title": 280, "subject": 110, "priority": 80,
                       "due": 130, "countdown": 100, "status": 90}
        col_labels  = {"id": "ID", "title": "Title", "subject": "Subject",
                       "priority": "Priority", "due": "Due", "countdown": "Countdown",
                       "status": "Status"}

        def make_sort_cmd(col):
            return lambda: self._sort_by_col(col)

        for col in cols:
            self.tree.heading(col, text=col_labels[col], command=make_sort_cmd(col))
            self.tree.column(col, anchor="center", width=col_widths.get(col, 100))

        # ── Action buttons ───────────────────────────────────────────────
        self.btn_frame = tk.Frame(self.content_frame, bg="#F8FAFC", pady=12)
        self.btn_frame.pack(fill=tk.X, padx=12, pady=(8, 20))
        act_btn = dict(font=("Segoe UI", 10, "bold"), relief=tk.FLAT, padx=14, pady=6)
        btn_row1 = tk.Frame(self.btn_frame, bg="#F8FAFC")
        btn_row1.pack(pady=4)
        tk.Button(btn_row1, text="✏️ Edit",         command=self.edit_task,
                  bg="#6366F1", fg="white", **act_btn).pack(side=tk.LEFT, padx=4)
        tk.Button(btn_row1, text="🗑 Bin Selected",  command=self.delete_task,
                  bg="#DC2626", fg="white", **act_btn).pack(side=tk.LEFT, padx=4)
        tk.Button(btn_row1, text="📚 Fun Trash",     command=self.fun_trash_game,
                  bg="#F59E0B", fg="white", **act_btn).pack(side=tk.LEFT, padx=4)
        tk.Button(btn_row1, text="✨ Mark Done",     command=self.toggle_done,
                  bg="#059669", fg="white", **act_btn).pack(side=tk.LEFT, padx=4)
        btn_row2 = tk.Frame(self.btn_frame, bg="#F8FAFC")
        btn_row2.pack(pady=4)
        tk.Button(btn_row2, text="📅 Calendar",      command=self.show_calendar,
                  bg="#1E3A8A", fg="white", **act_btn).pack(side=tk.LEFT, padx=4)
        tk.Button(btn_row2, text="📁 View Trash",    command=self.view_trash,
                  bg="#4B5563", fg="white", **act_btn).pack(side=tk.LEFT, padx=4)
        tk.Button(btn_row2, text="🔄 Load Examples", command=self.load_examples,
                  bg="#9CA3AF", fg="white", **act_btn).pack(side=tk.LEFT, padx=4)
        tk.Button(btn_row2, text="🍅 Pomodoro",      command=self.show_pomodoro,
                  bg="#DC2626", fg="white", **act_btn).pack(side=tk.LEFT, padx=4)

        self.sel_label = tk.Label(self.btn_frame, text="",
                                  font=("Segoe UI", 9, "italic"), bg="#F8FAFC", fg="#6B7280")
        self.sel_label.pack(pady=4)
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

        self.dark_btn = tk.Button(self.root, text="🌙 DARK MODE",
                                  font=("Segoe UI", 11, "bold"), bg="#111827", fg="white",
                                  command=self.toggle_dark_mode, padx=15, pady=8)
        self.dark_btn.place(relx=0.98, rely=0.97, anchor="se")

    def _on_content_configure(self, event):
        self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.main_canvas.itemconfig(self.canvas_window, width=event.width)

    def _bind_mousewheel(self, widget):
        def _scroll(event):
            widget.yview_scroll(int(-1 * (event.delta / 120)), "units")
        widget.bind("<MouseWheel>", _scroll)
        self.content_frame.bind("<MouseWheel>", _scroll)

    # ── Dashboard card filter logic ──────────────────────────────────────

    def _get_filtered_tasks(self, key):
        now = datetime.now()
        if key == "total":
            return list(self.tasks)
        elif key == "pending":
            return [t for t in self.tasks if not t["done"]]
        elif key == "done":
            return [t for t in self.tasks if t["done"]]
        elif key == "overdue":
            result = []
            for t in self.tasks:
                if t["done"]:
                    continue
                try:
                    if datetime.strptime(t["due"], "%d/%m/%Y %H:%M") < now:
                        result.append(t)
                except ValueError:
                    pass
            return result
        elif key == "due_soon":
            result = []
            for t in self.tasks:
                if t["done"]:
                    continue
                try:
                    diff = (datetime.strptime(t["due"], "%d/%m/%Y %H:%M") - now).total_seconds()
                    if 0 <= diff <= 86400:
                        result.append(t)
                except ValueError:
                    pass
            return result
        return list(self.tasks)

    def _toggle_card_filter(self, key):
        if self._active_filter == key:
            self._clear_card_filter()
            return
        self._active_filter = key
        self._update_card_visuals()
        filtered = self._get_filtered_tasks(key)
        search = self.search_var.get().lower()
        if search:
            filtered = [t for t in filtered
                        if search in t["title"].lower() or search in t["subject"].lower()]
        card_names = {"total": "All Tasks", "pending": "Pending",
                      "done": "Completed", "overdue": "Overdue", "due_soon": "Due Within 24h"}
        count = len(filtered)
        self.filter_banner_label.config(
            text=f"  Filtered: {card_names.get(key, key)}  —  {count} task{'s' if count != 1 else ''}")
        self.filter_banner_frame.pack(fill=tk.X, padx=12, before=self.filter_frame)
        self._populate_raw(filtered)

    def _clear_card_filter(self):
        self._active_filter = None
        self._update_card_visuals()
        self.filter_banner_frame.pack_forget()
        self.apply_filters()

    def _update_card_visuals(self):
        for key, frame in self._dash_card_frames.items():
            if key == self._active_filter:
                bg = self._card_active_bg[key]
                frame.config(bg=bg, highlightbackground="white",
                             highlightthickness=3, relief=tk.RAISED, bd=2)
            else:
                bg = self._card_normal_bg[key]
                frame.config(bg=bg, highlightbackground=bg,
                             highlightthickness=0, relief=tk.FLAT, bd=0)
            for child in frame.winfo_children():
                try:
                    child.config(bg=bg)
                except Exception:
                    pass

    # ── Calendar / selection ────────────────────────────────────────────

    def show_calendar(self):
        CalendarView(self.root, self.tasks, self.dark_mode)

    def show_pomodoro(self):
        PomodoroTimer(self.root, self.dark_mode)

    def _on_tree_select(self, event):
        n = len(self.tree.selection())
        if n == 0:
            self.sel_label.config(text="")
        elif n == 1:
            self.sel_label.config(text="1 task selected")
        else:
            self.sel_label.config(text=f"{n} tasks selected")

    # ── Fun Trash ────────────────────────────────────────────────────────

    def fun_trash_game(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("📚 Fun Time!", "Please select a task to have some fun!")
            return
        tasks_to_play = []
        for item in selection:
            tid  = int(self.tree.item(item)["values"][0])
            task = next((t for t in self.tasks if t["id"] == tid), None)
            if task:
                tasks_to_play.append(task)
        if not tasks_to_play:
            return
        count  = len(tasks_to_play)
        plural = f"{count} tasks" if count > 1 else f"'{tasks_to_play[0]['title']}'"
        if not messagebox.askyesno("Fun Trash",
                f"📚 Play Flappy Book to delete:\n\n📝 {plural}\n\n"
                f"{'You will play one game per task! ' if count > 1 else ''}"
                f"📖 Score 5 points to permanently delete each task!\n\nReady? 📚"):
            return
        self._launch_next_fun_game(tasks_to_play, 0)

    def _launch_next_fun_game(self, task_list, index):
        if index >= len(task_list):
            return
        task = task_list[index]
        if task not in self.tasks:
            self._launch_next_fun_game(task_list, index + 1)
            return

        def delete_after_win():
            t_copy = task.copy()
            t_copy["deleted_at"]      = datetime.now().strftime("%d/%m/%Y %H:%M")
            t_copy["deleted_by_game"] = True
            self.deleted_tasks.append(t_copy)
            if task in self.tasks:
                self.tasks.remove(task)
            self.save_data()
            self.populate_task_list()
            remaining = len(task_list) - index - 1
            msg = f"🎉 '{task['title']}' trashed!"
            if remaining > 0:
                msg += f"\n\n{remaining} more task(s) to go — get ready!"
            messagebox.showinfo("Deleted!", msg)
            self._launch_next_fun_game(task_list, index + 1)

        FlappyBookGame(self.root, task["title"], delete_after_win)

    # ── Celebration ──────────────────────────────────────────────────────

    def celebrate(self):
        canvas = tk.Canvas(self.root, width=1400, height=820,
                           highlightthickness=0, bg="#F8FAFC")
        canvas.place(x=0, y=0, relwidth=1, relheight=1)
        colors = ['#FFC107', '#FF5722', '#E91E63', '#9C27B0',
                  '#3F51B5', '#00BCD4', '#4CAF50']
        particles = []
        for _ in range(100):
            x    = random.randint(0, 1400)
            y    = random.randint(-200, 0)
            size = random.randint(5, 12)
            p    = canvas.create_rectangle(x, y, x+size, y+size,
                                           fill=random.choice(colors), outline="")
            particles.append([p, random.randint(5, 15)])

        def animate():
            still = False
            for p_data in particles:
                canvas.move(p_data[0], random.randint(-2, 2), p_data[1])
                pos = canvas.coords(p_data[0])
                if pos and pos[1] < 820:
                    still = True
            if still:
                self.root.after(20, animate)
            else:
                canvas.destroy()
        animate()
        messagebox.showinfo("Well Done!", "🌟 Amazing work! You've completed a task! 🌟")

    def toggle_done(self):
        selection = self.tree.selection()
        if not selection:
            return
        triggered = False
        for item in selection:
            tid = int(self.tree.item(item)["values"][0])
            for t in self.tasks:
                if t["id"] == tid:
                    t["done"] = not t["done"]
                    if t["done"]:
                        triggered = True
        self.save_data()
        self.populate_task_list()
        if triggered:
            self.celebrate()

    # ── Task CRUD ────────────────────────────────────────────────────────

    def task_form(self, task=None):
        win = tk.Toplevel(self.root)
        win.title("Edit Task" if task else "Add Task")
        win.geometry("420x450")
        title    = tk.StringVar(value=task["title"]    if task else "")
        subject  = tk.StringVar(value=task["subject"]  if task else self.subjects[0])
        priority = tk.StringVar(value=task["priority"] if task else "Medium")
        due      = tk.StringVar(value=task["due"]      if task else
                                datetime.now().strftime("%d/%m/%Y %H:%M"))
        tk.Label(win, text="Title").pack(pady=(10, 0))
        tk.Entry(win, textvariable=title, width=30).pack()
        tk.Label(win, text="Subject").pack(pady=(10, 0))
        ttk.Combobox(win, textvariable=subject, values=self.subjects).pack()
        tk.Label(win, text="Priority").pack(pady=(10, 0))
        ttk.Combobox(win, textvariable=priority, values=["High", "Medium", "Low"]).pack()
        tk.Label(win, text="Due (DD/MM/YYYY HH:MM)").pack(pady=(10, 0))
        tk.Entry(win, textvariable=due).pack()

        def save():
            if not title.get():
                messagebox.showerror("Error", "Task title required")
                return
            try:
                due_dt = datetime.strptime(due.get(), "%d/%m/%Y %H:%M")
            except ValueError:
                messagebox.showerror("Error", "Invalid date format.\nPlease use DD/MM/YYYY HH:MM")
                return

            now = datetime.now()

            # Warn if date is in the past
            if due_dt < now:
                delta = now - due_dt
                days  = delta.days
                if days == 0:
                    ago = f"{delta.seconds // 3600} hour(s) ago"
                elif days < 7:
                    ago = f"{days} day(s) ago"
                elif days < 31:
                    ago = f"{days // 7} week(s) ago"
                else:
                    ago = f"{days // 30} month(s) ago"
                if not messagebox.askyesno(
                        "⚠️ Date in the Past",
                        f"The due date you entered is in the past ({ago}):\n\n"
                        f"  📅  {due.get()}\n\n"
                        f"Are you sure you want to set this date?"):
                    return

            # Warn if date is more than 1 year in the future
            elif due_dt > now + timedelta(days=365):
                months_away = int((due_dt - now).days / 30)
                if not messagebox.askyesno(
                        "⚠️ Date Far in the Future",
                        f"The due date you entered is over a year away "
                        f"(~{months_away} months from now):\n\n"
                        f"  📅  {due.get()}\n\n"
                        f"Are you sure you want to set this date?"):
                    return

            if task:
                task.update({"title": title.get(), "subject": subject.get(),
                             "priority": priority.get(), "due": due.get()})
            else:
                new_id = max([t["id"] for t in self.tasks], default=0) + 1
                self.tasks.append({"id": new_id, "title": title.get(),
                                   "subject": subject.get(), "priority": priority.get(),
                                   "due": due.get(), "done": False})
            self.save_data()
            self.populate_task_list()
            win.destroy()

        tk.Button(win, text="Save Task", command=save, bg="#10B981", fg="white").pack(pady=20)

    def add_task(self):
        self.task_form()

    def edit_task(self):
        sel = self.tree.selection()
        if not sel:
            return
        tid  = int(self.tree.item(sel[0])["values"][0])
        task = next((t for t in self.tasks if t["id"] == tid), None)
        if task:
            self.task_form(task)

    def delete_task(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Trash", "Please select task(s) to move to trash.")
            return
        count = len(sel)
        msg   = (f"Move '{self.tree.item(sel[0])['values'][1]}' to trash?"
                 if count == 1 else f"Move {count} selected tasks to trash?")
        if not messagebox.askyesno("Trash", msg):
            return
        moved = 0
        for item in sel:
            tid = int(self.tree.item(item)["values"][0])
            for t in self.tasks[:]:
                if t["id"] == tid:
                    t_copy = t.copy()
                    t_copy["deleted_at"]      = datetime.now().strftime("%d/%m/%Y %H:%M")
                    t_copy["deleted_by_game"] = False
                    self.deleted_tasks.append(t_copy)
                    self.tasks.remove(t)
                    moved += 1
                    break
        self.save_data()
        self.populate_task_list()
        if moved:
            messagebox.showinfo("Trash",
                f"✅ Moved {moved} task(s) to trash.\n\n📁 Restore via 'View Trash' if needed.")

    def load_examples(self):
        if self.tasks and not messagebox.askyesno("Load Examples",
                "Replace current tasks with example data?"):
            return
        self.tasks    = generate_example_tasks()
        self.subjects = EXAMPLE_SUBJECTS[:]
        self.save_data()
        self.populate_task_list()
        messagebox.showinfo("Done", f"Loaded {len(self.tasks)} example tasks!")

    # ── Display helpers ──────────────────────────────────────────────────

    def get_countdown(self, due):
        try:
            d    = datetime.strptime(due, "%d/%m/%Y %H:%M")
            diff = d - datetime.now()
            if diff.total_seconds() < 0:
                return "OVERDUE"
            return f"{diff.days}d {diff.seconds // 3600}h"
        except ValueError:
            return "Invalid"

    def _populate_raw(self, tasks):
        for item in self.tree.get_children():
            self.tree.delete(item)
        now = datetime.now()
        COLOUR_MAP = {
            "done":    "#6B7280", "overdue": "#DC2626",
            "day1":    "#EA580C", "day3":    "#D97706",
            "day7":    "#2563EB", "ontrack": "#059669",
        }
        for t in tasks:
            cd = self.get_countdown(t["due"])
            if t["done"]:
                prox = "done"
            elif cd == "OVERDUE":
                prox = "overdue"
            else:
                try:
                    diff_h = (datetime.strptime(t["due"], "%d/%m/%Y %H:%M") - now).total_seconds() / 3600
                    prox = "day1" if diff_h <= 24 else "day3" if diff_h <= 72 else "day7" if diff_h <= 168 else "ontrack"
                except ValueError:
                    prox = "ontrack"
            self.tree.insert("", tk.END,
                values=(t["id"], t["title"], t["subject"], t["priority"],
                        t["due"], cd, "Done ✓" if t["done"] else "Pending"),
                tags=(prox,))
        tree_bg = "#1F2937" if self.dark_mode else "white"
        for tag, colour in COLOUR_MAP.items():
            self.tree.tag_configure(tag, foreground=colour, background=tree_bg,
                                    font=("Segoe UI", 10, "bold" if tag != "done" else "normal"))
        self.update_dashboard()

    def populate_task_list(self, tasks=None):
        if tasks is None:
            if self._active_filter is not None:
                base     = self._get_filtered_tasks(self._active_filter)
                search   = self.search_var.get().lower()
                filtered = ([t for t in base
                             if search in t["title"].lower() or search in t["subject"].lower()]
                            if search else base)
                count = len(filtered)
                card_names = {"total": "All Tasks", "pending": "Pending",
                              "done": "Completed", "overdue": "Overdue", "due_soon": "Due Within 24h"}
                self.filter_banner_label.config(
                    text=f"  Filtered: {card_names.get(self._active_filter, '')}  —  "
                         f"{count} task{'s' if count != 1 else ''}")
                self._populate_raw(filtered)
                return
            tasks = self.tasks
        self._populate_raw(tasks)

    def update_dashboard(self):
        now        = datetime.now()
        total      = len(self.tasks)
        done_count = sum(t["done"] for t in self.tasks)
        pending    = [t for t in self.tasks if not t["done"]]
        overdue_count  = 0
        due_soon_count = 0
        for t in pending:
            try:
                diff = (datetime.strptime(t["due"], "%d/%m/%Y %H:%M") - now).total_seconds()
                if diff < 0:
                    overdue_count += 1
                elif diff <= 86400:
                    due_soon_count += 1
            except ValueError:
                pass
        self._dash_cards["total"].config(text=str(total))
        self._dash_cards["pending"].config(text=str(len(pending)))
        self._dash_cards["done"].config(text=str(done_count))
        self._dash_cards["overdue"].config(text=str(overdue_count))
        self._dash_cards["due_soon"].config(text=str(due_soon_count))
        if pending:
            nxt = min(pending, key=lambda x: datetime.strptime(x["due"], "%d/%m/%Y %H:%M"))
            self.next_task_title.config(text=nxt["title"][:55])
            cd = self.get_countdown(nxt["due"])
            self.next_task_sub.config(
                text=f"{nxt['subject']}  ·  {nxt['priority']} priority  ·  Due: {nxt['due']}  ·  {cd}")
        else:
            self.next_task_title.config(text="All tasks complete! 🎉")
            self.next_task_sub.config(text="")

    # ── Sorting ──────────────────────────────────────────────────────────

    def _sort_by_col(self, col):
        PRIORITY_ORDER = {"High": 1, "Medium": 2, "Low": 3}
        COL_LABELS     = {"id": "ID", "title": "Title", "subject": "Subject",
                          "priority": "Priority", "due": "Due",
                          "countdown": "Countdown", "status": "Status"}
        if self._sort_col == col:
            self._sort_asc = not self._sort_asc
        else:
            self._sort_col = col
            self._sort_asc = True
        asc = self._sort_asc
        if col in ("due", "countdown"):
            self.tasks.sort(key=lambda t: datetime.strptime(t["due"], "%d/%m/%Y %H:%M"),
                            reverse=not asc)
        elif col == "priority":
            self.tasks.sort(key=lambda t: PRIORITY_ORDER.get(t["priority"], 9), reverse=not asc)
        elif col == "status":
            self.tasks.sort(key=lambda t: t["done"], reverse=not asc)
        elif col == "id":
            self.tasks.sort(key=lambda t: t["id"], reverse=not asc)
        else:
            self.tasks.sort(key=lambda t: t.get(col, "").lower(), reverse=not asc)
        arrow = " ▲" if asc else " ▼"
        for c, label in COL_LABELS.items():
            self.tree.heading(c, text=label + (arrow if c == col else ""))
        self.populate_task_list()

    def sort_deadline(self):
        self._sort_by_col("due")

    def sort_priority(self):
        self._sort_by_col("priority")

    def apply_filters(self):
        search = self.search_var.get().lower()
        if self._active_filter is not None:
            base     = self._get_filtered_tasks(self._active_filter)
            filtered = ([t for t in base
                         if search in t["title"].lower() or search in t["subject"].lower()]
                        if search else base)
            self._populate_raw(filtered)
            return
        if not search:
            self._populate_raw(self.tasks)
            return
        filtered = [t for t in self.tasks
                    if search in t["title"].lower() or search in t["subject"].lower()]
        self._populate_raw(filtered)

    # ── Trash view ───────────────────────────────────────────────────────

    def view_trash(self):
        if not self.deleted_tasks:
            messagebox.showinfo("Trash", "Trash is empty.")
            return
        tw  = tk.Toplevel(self.root)
        tw.title("Trash Bin")
        tw.geometry("900x600")
        bg  = "#F8FAFC" if not self.dark_mode else "#111827"
        fg  = "#1E3A8A" if not self.dark_mode else "#F9FAFB"
        tw.configure(bg=bg)
        mf  = tk.Frame(tw, bg=bg)
        mf.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        tk.Label(mf, text=f"📁 Trash contains {len(self.deleted_tasks)} deleted task(s)",
                 font=("Segoe UI", 11, "bold"), bg=bg, fg=fg).pack(pady=(0, 10))
        tf  = tk.Frame(mf, bg=bg)
        tf.pack(fill=tk.BOTH, expand=True)
        cols = ("id", "title", "subject", "due", "deleted_at")
        tt   = ttk.Treeview(tf, columns=cols, show="headings", selectmode="extended")
        vsb  = ttk.Scrollbar(tf, orient="vertical",   command=tt.yview)
        hsb  = ttk.Scrollbar(tf, orient="horizontal", command=tt.xview)
        tt.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        tt.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tf.grid_rowconfigure(0, weight=1)
        tf.grid_columnconfigure(0, weight=1)
        col_widths = {"id": 60, "title": 300, "subject": 120, "due": 130, "deleted_at": 150}
        for c in cols:
            tt.heading(c, text=c.replace("_", " ").title())
            tt.column(c, anchor="center", width=col_widths.get(c, 100))
        for t in self.deleted_tasks:
            tt.insert("", tk.END, values=(t["id"], t["title"], t["subject"],
                                          t["due"], t.get("deleted_at", "N/A")))
        bf  = tk.Frame(mf, bg=bg, pady=10)
        bf.pack(fill=tk.X)
        sel_lbl = tk.Label(bf, text="", font=("Segoe UI", 9, "italic"), bg=bg, fg="#6B7280")

        def upd_sel():
            n = len(tt.selection())
            sel_lbl.config(text=f"{n} item(s) selected" if n else "")

        def sel_all():
            for item in tt.get_children():
                tt.selection_add(item)
            upd_sel()

        def restore():
            sel = tt.selection()
            if not sel:
                messagebox.showwarning("No Selection", "Select tasks to restore.")
                return
            done = 0
            for item in sel:
                v = tt.item(item)["values"]
                for t in self.deleted_tasks[:]:
                    if t["id"] == v[0] and t["title"] == v[1]:
                        self.deleted_tasks.remove(t)
                        t["id"] = max([x["id"] for x in self.tasks], default=0) + 1
                        t.pop("deleted_at", None)
                        t.pop("deleted_by_game", None)
                        self.tasks.append(t)
                        done += 1
                        break
            if done:
                self.save_data()
                self.populate_task_list()
                messagebox.showinfo("Restored", f"✅ Restored {done} task(s).")
                tw.destroy()
                self.view_trash()

        def perm_del():
            sel = tt.selection()
            if not sel:
                messagebox.showwarning("No Selection", "Select tasks to permanently delete.")
                return
            if not messagebox.askyesno("Permanently Delete",
                    f"⚠️ Permanently delete {len(sel)} task(s)? This cannot be undone!"):
                return
            to_del = []
            for item in sel:
                v = tt.item(item)["values"]
                for t in self.deleted_tasks[:]:
                    if t["id"] == v[0] and t["title"] == v[1]:
                        to_del.append(t)
                        break
            for t in to_del:
                self.deleted_tasks.remove(t)
            self.save_data()
            tw.destroy()
            self.view_trash()
            messagebox.showinfo("Deleted", f"✅ Permanently deleted {len(to_del)} task(s).")

        bs = dict(font=("Segoe UI", 10, "bold"), relief=tk.FLAT, padx=15, pady=6)
        r1 = tk.Frame(bf, bg=bg)
        r1.pack(pady=5)
        tk.Button(r1, text="↩️ Restore Selected",           command=restore,  bg="#10B981", fg="white", **bs).pack(side=tk.LEFT, padx=5)
        tk.Button(r1, text="✅ Select All",                  command=sel_all,  bg="#3B82F6", fg="white", **bs).pack(side=tk.LEFT, padx=5)
        tk.Button(r1, text="🗑️ Permanently Delete Selected", command=perm_del, bg="#DC2626", fg="white", **bs).pack(side=tk.LEFT, padx=5)
        r2 = tk.Frame(bf, bg=bg)
        r2.pack(pady=5)
        sel_lbl.pack(side=tk.LEFT, padx=10)
        tk.Button(r2, text="Close", command=tw.destroy, bg="#6B7280", fg="white", **bs).pack(side=tk.RIGHT, padx=5)
        tt.bind("<<TreeviewSelect>>", lambda e: upd_sel())
        tw.transient(self.root)
        tw.grab_set()
        self.root.wait_window(tw)

    # ── Dark mode ────────────────────────────────────────────────────────

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        bg      = "#111827" if self.dark_mode else "#F8FAFC"
        tree_bg = "#1F2937" if self.dark_mode else "white"
        hdr_bg  = "#0F172A" if self.dark_mode else "#1E3A8A"

        self.root.configure(bg=bg)
        self.main.configure(bg=bg)
        self.main_canvas.configure(bg=bg)
        self.content_frame.configure(bg=bg)
        self.header_frame.configure(bg=hdr_bg)
        self.title_label.configure(bg=hdr_bg)
        self.dash_frame.configure(bg=bg)
        self.filter_frame.configure(bg=bg)
        self.btn_frame.configure(bg=bg)
        self.sel_label.configure(bg=bg)

        for row in self.btn_frame.winfo_children():
            if isinstance(row, tk.Frame):
                row.configure(bg=bg)

        self.style.configure("Treeview", background=tree_bg,
                             foreground="white" if self.dark_mode else "black",
                             fieldbackground=tree_bg)
        self.style.configure("Treeview.Heading",
                             background="#374151" if self.dark_mode else "#E5E7EB",
                             foreground="white" if self.dark_mode else "black")
        self.dark_btn.config(
            text="☀️ LIGHT MODE" if self.dark_mode else "🌙 DARK MODE",
            bg="white" if self.dark_mode else "#111827",
            fg="black" if self.dark_mode else "white")
        self.populate_task_list()

    # ── Utilities ────────────────────────────────────────────────────────

    def add_subject(self):
        s = simpledialog.askstring("Subject", "New subject:")
        if s and s not in self.subjects:
            self.subjects.append(s)
            self.save_data()

    def show_clock(self):
        sel = self.tree.selection()
        if not sel:
            return
        tid  = int(self.tree.item(sel[0])["values"][0])
        task = next((t for t in self.tasks if t["id"] == tid), None)
        if not task:
            return
        cw = tk.Toplevel(self.root)
        cw.title("Countdown")
        cw.geometry("400x200")
        cw.configure(bg="#111827")
        lbl = tk.Label(cw, text="", font=("Consolas", 32, "bold"), bg="#111827", fg="#10B981")
        lbl.pack(expand=True)

        def upd():
            if not cw.winfo_exists():
                return
            diff = datetime.strptime(task["due"], "%d/%m/%Y %H:%M") - datetime.now()
            if diff.total_seconds() <= 0:
                lbl.config(text="OVERDUE", fg="red")
            else:
                h, r = divmod(int(diff.total_seconds()), 3600)
                m, s = divmod(r, 60)
                lbl.config(text=f"{h//24}d {h%24:02}:{m:02}:{s:02}")
                cw.after(1000, upd)
        upd()

    def refresh_all(self):
        self.populate_task_list()
        self.root.after(60000, self.refresh_all)


# =========================
# ENTRY POINT
# =========================

if __name__ == "__main__":
    app = StudentTaskTracker()
    app.root.mainloop()
