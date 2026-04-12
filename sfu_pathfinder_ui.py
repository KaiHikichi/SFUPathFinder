import customtkinter as ctk
import tkinter as tk
import os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from util.graph import NodeMap, Weather, simulateConstruction, Node
from util.setup import setUp
from util.search import A_Star
from util.edge_operations import estimate_time_per_edge, update_edge_costs_in_path

MAP_JSON = os.path.join(ROOT, "maps", "mapNodes.json")
METERS_PER_DEGREE = 111139
METERS_PER_MIN = 85

# ── Persistent map — built once, never rebuilt ────────────────────────────────
shared_map = NodeMap()
setUp(shared_map, MAP_JSON)
node_names = sorted(shared_map.nodes.keys())

last_path = []
last_cost = 0.0

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

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

root = ctk.CTk()
root.title("SFU Campus Pathfinder")
root.geometry("640x900")
root.minsize(580, 760)
root.configure(fg_color=BG)

FONT = "Nunito"
FB = lambda sz: ctk.CTkFont(family=FONT, size=sz, weight="bold")
FR = lambda sz: ctk.CTkFont(family=FONT, size=sz)
FM = lambda sz: ctk.CTkFont(family=FONT, size=sz)

# ── Header ────────────────────────────────────────────────────────────────────
LOGO_W, LOGO_H = 120, 60
HEADER_H = LOGO_H + 24

header = ctk.CTkFrame(root, fg_color=BG_CARD, corner_radius=0, height=HEADER_H, border_width=0)
header.pack(fill="x")
header.pack_propagate(False)

accent = tk.Frame(header, bg=RED, width=5)
accent.place(x=0, y=0, relheight=1)

LOGO_PATH = os.path.join(ROOT, "assets", "sfu_logo.png")
try:
    from PIL import Image, ImageTk
    logo_img = Image.open(LOGO_PATH).resize((LOGO_W, LOGO_H), Image.LANCZOS)
    logo_photo = ImageTk.PhotoImage(logo_img)
    logo_lbl = ctk.CTkLabel(header, image=logo_photo, text="", fg_color="transparent")
    logo_lbl.image = logo_photo
    logo_lbl.place(x=18, y=12)
    title_x = LOGO_W + 30
except Exception:
    title_x = 24

title_block = ctk.CTkFrame(header, fg_color="transparent")
title_block.place(x=title_x, y=18)
ctk.CTkLabel(title_block, text="PATHFINDER",
             font=FB(22), text_color=WHITE, fg_color="transparent").pack(anchor="w")
ctk.CTkLabel(title_block, text="Burnaby Campus  ·  A★ Navigation",
             font=FR(11), text_color=DIM, fg_color="transparent").pack(anchor="w")

badge = ctk.CTkLabel(header, text="  LIVE  ",
                     font=FB(10), text_color=WHITE,
                     fg_color=RED, corner_radius=8)
badge.place(x=548, y=28)

sep = tk.Frame(root, bg=RED, height=3)
sep.pack(fill="x")

# ── Scrollable main area ──────────────────────────────────────────────────────
main_scroll = ctk.CTkScrollableFrame(root, fg_color=BG, corner_radius=0,
                                      scrollbar_button_color=BG_ROW,
                                      scrollbar_button_hover_color=RED)
main_scroll.pack(fill="both", expand=True)
main_scroll.grid_columnconfigure(0, weight=1)

def section_label(parent, text):
    ctk.CTkLabel(parent, text=text, font=FB(10), text_color=DIM,
                 fg_color="transparent").pack(anchor="w", padx=20, pady=(14, 4))

def divider(parent):
    tk.Frame(parent, bg=BORDER, height=1).pack(fill="x", padx=20, pady=6)

# ── Controls card ─────────────────────────────────────────────────────────────
ctrl = ctk.CTkFrame(main_scroll, fg_color=BG_CARD, corner_radius=12)
ctrl.pack(fill="x", padx=20, pady=(18, 0))

# ── Node selectors
section_label(ctrl, "ROUTE")

nodes_frame = ctk.CTkFrame(ctrl, fg_color="transparent")
nodes_frame.pack(fill="x", padx=20, pady=(0, 4))
nodes_frame.grid_columnconfigure((0, 1), weight=1)

for col, lbl in enumerate(["From", "To"]):
    cell = ctk.CTkFrame(nodes_frame, fg_color="transparent")
    cell.grid(row=0, column=col, sticky="ew", padx=(0, 8) if col==0 else (8, 0))
    ctk.CTkLabel(cell, text=lbl, font=FB(11), text_color=WHITE,
                 fg_color="transparent").pack(anchor="w", pady=(0, 4))
    var = ctk.StringVar(value=node_names[0] if col==0 else node_names[-1])
    if col == 0: start_var = var
    else:        end_var   = var
    ctk.CTkOptionMenu(cell, values=node_names, variable=var,
                      height=38, corner_radius=8,
                      fg_color=BG_INPUT, button_color=BG_ROW, button_hover_color=BORDER,
                      dropdown_fg_color=BG_CARD, dropdown_hover_color=BG_ROW,
                      text_color=WHITE, dropdown_text_color=WHITE,
                      font=FR(13)).pack(fill="x")

divider(ctrl)

# ── Weather
section_label(ctrl, "CONDITIONS")

wx_frame = ctk.CTkFrame(ctrl, fg_color="transparent")
wx_frame.pack(fill="x", padx=20, pady=(0, 4))
wx_var = ctk.StringVar(value="CLEAR")

for val, icon, label, col in [("CLEAR","☀","Clear",WHITE),("RAINING","🌧","Rain",BLUE),("SNOWY","❄","Snow","#a5f3fc")]:
    btn_frame = ctk.CTkFrame(wx_frame, fg_color=BG_INPUT, corner_radius=8)
    btn_frame.pack(side="left", padx=(0, 8), ipadx=4, ipady=4)
    ctk.CTkRadioButton(btn_frame, text=f"{icon}  {label}", variable=wx_var, value=val,
                       fg_color=RED, hover_color=RED_HOV, text_color=col,
                       font=FR(13), border_color=BORDER).pack(padx=10, pady=6)

divider(ctrl)

# ── Weather tolerance
section_label(ctrl, "WEATHER TOLERANCE")

tol_frame = ctk.CTkFrame(ctrl, fg_color="transparent")
tol_frame.pack(fill="x", padx=20, pady=(0, 4))
ctk.CTkLabel(tol_frame, text="Prefers indoors", font=FR(11), text_color=DIM,
             fg_color="transparent").pack(side="left")
tol_var = ctk.DoubleVar(value=0.5)
tol_lbl = ctk.CTkLabel(tol_frame, text="50%", font=FB(13), text_color=RED,
                        fg_color="transparent", width=44)
tol_lbl.pack(side="right")
ctk.CTkLabel(tol_frame, text="Doesn't mind", font=FR(11), text_color=DIM,
             fg_color="transparent").pack(side="right", padx=(0, 8))

tol_row = ctk.CTkFrame(ctrl, fg_color="transparent")
tol_row.pack(fill="x", padx=20, pady=(4, 8))
ctk.CTkSlider(tol_row, from_=0, to=1, variable=tol_var,
              progress_color=RED, button_color=WHITE, button_hover_color=RED_HOV,
              fg_color=BG_INPUT,
              command=lambda v: tol_lbl.configure(text=f"{int(float(v)*100)}%")).pack(fill="x")

divider(ctrl)

# ── Construction settings
section_label(ctrl, "CONSTRUCTION")

con_frame = ctk.CTkFrame(ctrl, fg_color="transparent")
con_frame.pack(fill="x", padx=20, pady=(0, 16))
con_frame.grid_columnconfigure((0, 1), weight=1)

chance_cell = ctk.CTkFrame(con_frame, fg_color="transparent")
chance_cell.grid(row=0, column=0, sticky="ew", padx=(0, 8))
ctk.CTkLabel(chance_cell, text="Chance", font=FB(11), text_color=WHITE,
             fg_color="transparent").pack(anchor="w", pady=(0, 4))
chance_row = ctk.CTkFrame(chance_cell, fg_color="transparent")
chance_row.pack(fill="x")
chance_var = ctk.DoubleVar(value=0.001)
chance_lbl = ctk.CTkLabel(chance_row, text="0.1%", font=FB(12), text_color=GOLD,
                            fg_color="transparent", width=44)
chance_lbl.pack(side="right")
ctk.CTkSlider(chance_row, from_=0, to=1, variable=chance_var,
              progress_color=GOLD, button_color=WHITE, button_hover_color=GOLD,
              fg_color=BG_INPUT,
              command=lambda v: chance_lbl.configure(text=f"{float(v)*100:.1f}%")).pack(
              side="left", fill="x", expand=True)

penalty_cell = ctk.CTkFrame(con_frame, fg_color="transparent")
penalty_cell.grid(row=0, column=1, sticky="ew", padx=(8, 0))
ctk.CTkLabel(penalty_cell, text="Penalty", font=FB(11), text_color=WHITE,
             fg_color="transparent").pack(anchor="w", pady=(0, 4))
penalty_row = ctk.CTkFrame(penalty_cell, fg_color="transparent")
penalty_row.pack(fill="x")
penalty_var = ctk.DoubleVar(value=2.0)
penalty_lbl = ctk.CTkLabel(penalty_row, text="2.0×", font=FB(12), text_color=GOLD,
                             fg_color="transparent", width=44)
penalty_lbl.pack(side="right")
ctk.CTkSlider(penalty_row, from_=1, to=5, variable=penalty_var,
              progress_color=GOLD, button_color=WHITE, button_hover_color=GOLD,
              fg_color=BG_INPUT,
              command=lambda v: penalty_lbl.configure(text=f"{float(v):.1f}×")).pack(
              side="left", fill="x", expand=True)

# ── Find button ───────────────────────────────────────────────────────────────
ctk.CTkButton(main_scroll, text="FIND PATH",
              command=lambda: find(),
              height=52, corner_radius=10,
              fg_color=RED, hover_color=RED_HOV,
              text_color=WHITE, font=FB(16)).pack(fill="x", padx=20, pady=14)

# ── Results card ──────────────────────────────────────────────────────────────
res_outer = ctk.CTkFrame(main_scroll, fg_color=BG_CARD, corner_radius=12)
res_outer.pack(fill="x", padx=20, pady=(0, 8))

res_hdr = ctk.CTkFrame(res_outer, fg_color=BG_ROW, corner_radius=0, height=40)
res_hdr.pack(fill="x")
res_hdr.pack_propagate(False)

ctk.CTkLabel(res_hdr, text="ROUTE", font=FB(11), text_color=DIM,
             fg_color="transparent", anchor="w").pack(side="left", padx=16)

summary_lbl = ctk.CTkLabel(res_hdr, text="", font=FB(12), text_color=GOLD,
                             fg_color="transparent", anchor="e")
summary_lbl.pack(side="right", padx=16)

map_btn = ctk.CTkButton(
    res_hdr,
    text="VIEW ON MAP",
    command=lambda: show_map(last_path),
    state="disabled",
    text_color=WHITE,
    height=28,
    corner_radius=6,
    fg_color="#97b7ec",
    hover_color="#5491f3",
    font=FB(10)
)
map_btn.pack(side="right", padx=(0, 8))

steps_frame = ctk.CTkFrame(res_outer, fg_color="transparent")
steps_frame.pack(fill="x")
steps_frame.grid_columnconfigure(0, weight=1)

placeholder = ctk.CTkLabel(steps_frame,
    text="Select a start and destination,\nthen press FIND PATH.",
    font=FR(14), text_color=DIM, justify="center", fg_color="transparent")
placeholder.grid(row=0, column=0, pady=40)

# ── Feedback card ─────────────────────────────────────────────────────────────
feedback_card = ctk.CTkFrame(main_scroll, fg_color=BG_CARD, corner_radius=12)
submitted_lbl = ctk.CTkLabel(main_scroll, text="", font=FR(12),
                              text_color=GREEN, fg_color="transparent")

def show_feedback():
    for w in feedback_card.winfo_children():
        w.destroy()
    feedback_card.pack(fill="x", padx=20, pady=(0, 8))
    submitted_lbl.pack_forget()

    ctk.CTkLabel(feedback_card, text="HOW LONG DID IT TAKE?",
                 font=FB(10), text_color=DIM,
                 fg_color="transparent").pack(anchor="w", padx=20, pady=(14, 4))

    row = ctk.CTkFrame(feedback_card, fg_color="transparent")
    row.pack(fill="x", padx=20, pady=(0, 16))

    time_entry = ctk.CTkEntry(row, placeholder_text="Minutes walked (e.g. 7.5)",
                               height=40, corner_radius=8,
                               fg_color=BG_INPUT, border_color=BORDER,
                               text_color=WHITE, font=FR(13))
    time_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

    def submit():
        try:
            t = float(time_entry.get())
        except ValueError:
            time_entry.configure(border_color=RED)
            return
        times = estimate_time_per_edge(last_path, t, last_cost)
        expectedTimes = estimate_time_per_edge(last_path, last_cost  * METERS_PER_DEGREE / METERS_PER_MIN, last_cost)
        update_edge_costs_in_path(last_path, times, expectedTimes)
        feedback_card.pack_forget()
        submitted_lbl.configure(text=f"✓ Costs updated with {t:.1f} min walk")
        submitted_lbl.pack(padx=20, pady=(0, 12))

    ctk.CTkButton(row, text="UPDATE", command=submit,
                  height=40, width=90, corner_radius=8,
                  fg_color=RED, hover_color=RED_HOV,
                  text_color=WHITE, font=FB(13)).pack(side="left")

# ── Find logic ────────────────────────────────────────────────────────────────
def clear_steps():
    for w in steps_frame.winfo_children():
        w.destroy()

def find():
    global last_path, last_cost

    wx  = Weather[wx_var.get()]
    tol = tol_var.get()

    shared_map.updateWeatherCosts(tol, wx)
    simulateConstruction(shared_map, chance_var.get(), penalty_var.get())

    start = shared_map.nodes[start_var.get()]
    goal  = shared_map.nodes[end_var.get()]
    
    for node in shared_map.nodes.values():
        node:Node
        node.h = node.calcHeuristic(goal)

    path, cost = A_Star(start, goal)
    last_path = path
    last_cost = cost

    clear_steps()
    feedback_card.pack_forget()
    submitted_lbl.pack_forget()

    if not path:
        ctk.CTkLabel(steps_frame, text="No path found.", font=FR(14),
                     text_color=DIM, fg_color="transparent").grid(row=0, column=0, pady=40)
        summary_lbl.configure(text="")
        map_btn.configure(state="disabled", fg_color="#97b7ec")
        return
    else:
        map_btn.configure(state="normal", fg_color=BLUE, hover_color="#5491f3", text_color=WHITE)

    est_mins = cost * METERS_PER_DEGREE / METERS_PER_MIN
    summary_lbl.configure(text=f"~{est_mins:.1f} min  ·  {len(path)} stops")

    for i, node in enumerate(path):
        is_last = (i == len(path) - 1)

        card = ctk.CTkFrame(steps_frame, fg_color=BG_ROW, corner_radius=10)
        card.grid(row=i*2, column=0, sticky="ew", padx=12, pady=(6, 0))
        card.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(card,
            text=f"{i+1}" if not is_last else "★",
            font=FB(13), text_color=WHITE,
            fg_color=RED if not is_last else GOLD,
            corner_radius=16, width=32, height=32).grid(row=0, column=0, padx=(14, 12), pady=14)

        ctk.CTkLabel(card, text=node.name, font=FB(14), text_color=WHITE,
                     fg_color="transparent", anchor="w").grid(row=0, column=1, sticky="w", pady=14)

        if not is_last:
            nxt_edge = next((e for e in node.edges if e.destNode.name == path[i+1].name), None)
            is_in    = nxt_edge and nxt_edge.isIndoor
            tag_txt  = "Indoor" if is_in else "Outdoor"
            tag_col  = GREEN    if is_in else GOLD
            tag_bg   = "#0d2b1f" if is_in else "#2b1f0d"
            edge_mins = (nxt_edge.cost * METERS_PER_DEGREE / METERS_PER_MIN) if nxt_edge else 0

            badge_frame = ctk.CTkFrame(card, fg_color="transparent")
            badge_frame.grid(row=0, column=2, padx=(0, 14), pady=14)
            ctk.CTkLabel(badge_frame, text=tag_txt, font=FB(10), text_color=tag_col,
                         fg_color=tag_bg, corner_radius=6, width=60, height=22).pack(anchor="e")
            ctk.CTkLabel(badge_frame, text=f"~{edge_mins:.1f} min", font=FM(11), text_color=DIM,
                         fg_color="transparent").pack(anchor="e", pady=(2, 0))

            ctk.CTkLabel(steps_frame, text="↓", font=ctk.CTkFont(size=16),
                         text_color=BORDER, fg_color="transparent").grid(row=i*2+1, column=0, pady=0)

    show_feedback()


# ── Map display ─────────────────────────────────────────────────────────────

# Bounds of the SFU map to help normalize lat/lon of nodes to pixel coordinates 
MAP_TOP_LAT = 49.281381
MAP_BOTTOM_LAT = 49.275921
MAP_LEFT_LON = -122.932051
MAP_RIGHT_LON = -122.911654

def show_map(path):
    # Define tk window for map display
    map_window = tk.Toplevel(root)
    map_window.title(f"Route Map ({path[0].name} → {path[-1].name})")
    map_window.geometry("1852x757")

    # Load map image and convert it to a Tkinter-compatible format
    img = Image.open("maps/baseMap.png")
    tk_img = ImageTk.PhotoImage(img)

    # Create a canvas to display / fit the map in the tk window and allow drawing
    canvas = tk.Canvas(map_window, width=img.width, height=img.height)
    canvas.pack(fill="both", expand=True)

    # Display the map image on the canvas
    canvas.create_image(0, 0, anchor="nw", image=tk_img)

    # Keep a reference to the image to keep it rendered on the canvas
    canvas.image = tk_img 

    # Function to convert lat/lon coordinates to x,y pixel coordinates on the map image
    def latlon_to_xy(lat, lon):
        x = (lon - MAP_LEFT_LON) / (MAP_RIGHT_LON - MAP_LEFT_LON) * img.width
        y = (MAP_TOP_LAT - lat) / (MAP_TOP_LAT - MAP_BOTTOM_LAT) * img.height
        return x, y

    # Draw the path of nodes on the canvas
    for i in range(len(path)-1):
        n1, n2 = path[i], path[i+1]
        x1, y1 = latlon_to_xy(n1.lat, n1.long)
        x2, y2 = latlon_to_xy(n2.lat, n2.long)
        canvas.create_line(x1, y1, x2, y2, fill=BLUE, width=4)

    # Draw a green circle to represent start node
    node = path[0]
    x, y = latlon_to_xy(node.lat, node.long)
    canvas.create_oval(x-5, y-5, x+5, y+5, fill=GREEN)

    # Draw blue circles for intermediate nodes
    for i in range(1, len(path)-1):
        node = path[i]
        x, y = latlon_to_xy(node.lat, node.long)
        canvas.create_oval(x-5, y-5, x+5, y+5, fill=BLUE)
    
    # Draw a red circle to represent destination node
    node = path[len(path)-1]
    x, y = latlon_to_xy(node.lat, node.long)
    canvas.create_oval(x-5, y-5, x+5, y+5, fill=RED)


root.mainloop()