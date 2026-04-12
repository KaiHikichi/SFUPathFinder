import customtkinter as ctk
import tkinter as tk
import os, sys

# Setup Paths
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from util.graph import NodeMap, Weather, simulateConstruction
from util.setup import setUp
from util.search import A_Star
from util.edge_operations import update_edge_costs_in_path, estimate_time_per_edge, METERS_PER_MIN

MAP_JSON = os.path.join(ROOT, "maps", "mapNodes.json")
METERS_PER_DEGREE = 111139 

# Initialize Map
node_map = NodeMap()
setUp(node_map, MAP_JSON)
node_names = sorted(node_map.nodes.keys())

# ── Palette ───────────────────────────────────────────────────────────────────
RED      = "#CC0633"
RED_HOV  = "#e8073a"
BG       = "#111318"
BG_CARD  = "#1c1f26"
BG_ROW   = "#22262f"
BG_INPUT = "#2a2e38"
BORDER   = "#2e3340"
WHITE    = "#f0f2f5"
DIM      = "#6b7280"
GOLD     = "#f5a623"
GREEN    = "#34d399"
BLUE     = "#60a5fa"
ORANGE   = "#fb923c"

ctk.set_appearance_mode("dark")

root = ctk.CTk()
root.title("SFU Campus Pathfinder")
root.geometry("1100x850")
root.configure(fg_color=BG)

FONT = "Segoe UI"
FB = lambda sz: ctk.CTkFont(family=FONT, size=sz, weight="bold")
FR = lambda sz: ctk.CTkFont(family=FONT, size=sz)

# ── Header ────────────────────────────────────────────────────────────────────
header = ctk.CTkFrame(root, fg_color=BG_CARD, corner_radius=0, height=84)
header.pack(fill="x")
tk.Frame(header, bg=RED, width=5).place(x=0, y=0, relheight=1)

title_block = ctk.CTkFrame(header, fg_color="transparent")
title_block.place(x=24, y=18)
ctk.CTkLabel(title_block, text="PATHFINDER", font=FB(22), text_color=WHITE).pack(anchor="w")
ctk.CTkLabel(title_block, text="Burnaby Campus  ·  Weather & Construction Simulation", font=FR(11), text_color=DIM).pack(anchor="w")

tk.Frame(root, bg=RED, height=3).pack(fill="x")

body = ctk.CTkFrame(root, fg_color="transparent")
body.pack(fill="both", expand=True, padx=20, pady=16)
body.grid_columnconfigure(0, weight=0, minsize=320)
body.grid_columnconfigure(1, weight=1)
body.grid_rowconfigure(0, weight=1)

# ── Left Panel ────────────────────────────────────────────────────────────────
left = ctk.CTkFrame(body, fg_color=BG_CARD, corner_radius=12)
left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

def sec_label(parent, text):
    ctk.CTkLabel(parent, text=text, font=FB(10), text_color=DIM).pack(anchor="w", padx=20, pady=(18, 6))

sec_label(left, "ROUTE")
start_var = ctk.StringVar(value="ASB Entrance")
end_var   = ctk.StringVar(value="CS Common Room")

for var in [start_var, end_var]:
    f = ctk.CTkFrame(left, fg_color="transparent")
    f.pack(fill="x", padx=20, pady=(0, 8))
    ctk.CTkOptionMenu(f, values=node_names, variable=var, height=38, corner_radius=8, fg_color=BG_INPUT, button_color=RED).pack(fill="x")

sec_label(left, "WEATHER CONDITIONS")
wx_var = ctk.StringVar(value="CLEAR")
for val, icon, label in [("CLEAR","☀","Clear"), ("RAINING","🌧","Rain"), ("SNOWY","❄","Snow")]:
    btn = ctk.CTkFrame(left, fg_color=BG_INPUT, corner_radius=8)
    btn.pack(fill="x", padx=20, pady=(0, 6))
    ctk.CTkRadioButton(btn, text=f"{icon}  {label}", variable=wx_var, value=val, fg_color=RED, font=FR(13)).pack(anchor="w", padx=14, pady=8)

tol_var = ctk.DoubleVar(value=0.5)
sec_label(left, "WEATHER TOLERANCE")
ctk.CTkSlider(left, from_=0, to=1, variable=tol_var, progress_color=RED, button_color=RED).pack(fill="x", padx=20, pady=(0, 5))
ctk.CTkLabel(left, text="Low (Avoid)  ← →  High (Ignore)", font=FR(10), text_color=DIM).pack(padx=20)

sec_label(left, "LIVE DATA")
constr_var = ctk.BooleanVar(value=True)
ctk.CTkCheckBox(left, text="Simulate Construction", variable=constr_var, font=FR(13), fg_color=RED, hover_color=RED_HOV).pack(padx=20, pady=5, anchor="w")

sec_label(left, "JOURNEY FEEDBACK")
time_entry = ctk.CTkEntry(left, placeholder_text="Minutes taken", height=38, corner_radius=8, fg_color=BG_INPUT, border_width=0)
time_entry.pack(fill="x", padx=20, pady=(0, 8))
fb_status = ctk.CTkLabel(left, text="", font=FR(11))
fb_status.pack(padx=20)

btn_frame = ctk.CTkFrame(left, fg_color="transparent")
btn_frame.pack(side="bottom", fill="x", padx=20, pady=16)

# ── Right Panel ───────────────────────────────────────────────────────────────
right = ctk.CTkFrame(body, fg_color=BG_CARD, corner_radius=12)
right.grid(row=0, column=1, sticky="nsew")
right.grid_rowconfigure(1, weight=1)
right.grid_columnconfigure(0, weight=1)

res_hdr = ctk.CTkFrame(right, fg_color=BG_ROW, corner_radius=0, height=50)
res_hdr.grid(row=0, column=0, sticky="ew")
summary_lbl = ctk.CTkLabel(res_hdr, text="READY", font=FB(12), text_color=GOLD)
summary_lbl.pack(side="right", padx=16)

scroll = ctk.CTkScrollableFrame(right, fg_color="transparent")
scroll.grid(row=1, column=0, sticky="nsew")
scroll.grid_columnconfigure(0, weight=1)

# Logic State
current_path = []
current_cost = 0

def find():
    global current_path, current_cost
    
    # 1. Update weather based on UI toggles (main.py logic)
    weather_map = {"CLEAR": Weather.CLEAR, "RAINING": Weather.RAINING, "SNOWY": Weather.SNOWY}
    node_map.updateWeatherCosts(tol_var.get(), weather_map[wx_var.get()])
    
    # 2. Simulate construction if checked
    if constr_var.get():
        simulateConstruction(node_map, 0.001, 2)
    
    start_node = node_map.nodes[start_var.get()]
    dest_node = node_map.nodes[end_var.get()]
    
    # 3. Search
    path, cost = A_Star(start_node, dest_node)
    current_path = path
    current_cost = cost
    
    # 4. Total Display Calculation (main.py formula)
    total_mins = cost * METERS_PER_DEGREE / METERS_PER_MIN
    summary_lbl.configure(text=f"TOTAL EST: {total_mins:.2f} MINS")
    
    for w in scroll.winfo_children(): w.destroy()
    
    for i in range(len(path)):
        node = path[i]
        n_card = ctk.CTkFrame(scroll, fg_color=BG_ROW, corner_radius=8)
        n_card.pack(fill="x", padx=40, pady=2)
        ctk.CTkLabel(n_card, text=node.name, font=FB(13), text_color=WHITE).pack(side="left", padx=15, pady=10)

        # Show segment distance and indoor/outdoor status
        if i < len(path) - 1:
            next_node = path[i+1]
            edge = next((e for e in node.edges if e.destNode == next_node), None)
            
            if edge:
                dist_m = edge.cost * METERS_PER_DEGREE
                env_text = "🏠 Indoors" if edge.isIndoor else "🌳 Outdoors"
                
                e_frame = ctk.CTkFrame(scroll, fg_color="transparent")
                e_frame.pack(fill="x", padx=60)
                tk.Frame(e_frame, bg=BORDER, width=2, height=20).pack(side="left", padx=(15, 10))
                
                info_text = f"{dist_m:.1f}m  ·  {env_text}"
                ctk.CTkLabel(e_frame, text=info_text, font=FR(11), text_color=DIM).pack(side="left")

def submit_feedback():
    if not current_path: return
    try:
        user_time = float(time_entry.get())
        # Passing raw cost exactly as in main.py
        times = estimate_time_per_edge(current_path, user_time, current_cost)
        update_edge_costs_in_path(current_path, times)
        fb_status.configure(text="✓ Map updated.", text_color=GREEN)
    except:
        fb_status.configure(text="⚠ Invalid input.", text_color=ORANGE)

ctk.CTkButton(btn_frame, text="FIND PATH", command=find, height=50, corner_radius=10, fg_color=RED, hover_color=RED_HOV, font=FB(14)).pack(fill="x", pady=5)
ctk.CTkButton(btn_frame, text="SUBMIT FEEDBACK", command=submit_feedback, height=35, corner_radius=10, fg_color=BG_INPUT, font=FB(12)).pack(fill="x")

root.mainloop()