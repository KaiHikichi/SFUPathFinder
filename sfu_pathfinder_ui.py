import customtkinter as ctk
import tkinter as tk
import os, sys, math
from PIL import Image, ImageTk

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from util.graph import NodeMap, Weather
from util.setup import setUp
from util.search import A_Star


MAP_JSON = os.path.join(ROOT, "maps", "mapNodes.json")

node_map = NodeMap()
setUp(node_map, MAP_JSON)
node_names = sorted(node_map.nodes.keys())

def haversine(n1, n2):
    lat1, lat2 = math.radians(n1.lat), math.radians(n2.lat)
    lon1, lon2 = math.radians(n1.long), math.radians(n2.long)
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return 6_371_000 * 2 * math.asin(math.sqrt(a))

# ── Palette ───────────────────────────────────────────────────────────────────
RED       = "#CC0633"
RED_HOV   = "#e8073a"
RED_DIM   = "#7a0420"
BG        = "#111318"
BG_CARD   = "#1c1f26"
BG_ROW    = "#22262f"
BG_INPUT  = "#2a2e38"
BORDER    = "#2e3340"
WHITE     = "#f0f2f5"
DIM       = "#6b7280"
GOLD      = "#f5a623"
GREEN     = "#34d399"
BLUE      = "#60a5fa"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

root = ctk.CTk()
root.title("SFU Campus Pathfinder")
root.geometry("620x820")
root.minsize(580, 700)
root.configure(fg_color=BG)

# Nunito is warm and friendly — install via: brew install --cask font-nunito
# Falls back to Trebuchet MS if not installed
FONT = "Nunito"
FB = lambda sz: ctk.CTkFont(family=FONT, size=sz, weight="bold")
FR = lambda sz: ctk.CTkFont(family=FONT, size=sz)
FM = lambda sz: ctk.CTkFont(family=FONT, size=sz)

# ── Header ────────────────────────────────────────────────────────────────────
# Logo is 1280x640 (2:1 ratio) — display at 120x60 to preserve ratio and fit header
LOGO_W, LOGO_H = 120, 60
HEADER_H = LOGO_H + 24  # padding above and below

header = ctk.CTkFrame(root, fg_color=BG_CARD, corner_radius=0, height=HEADER_H,
                      border_width=0)
header.pack(fill="x")
header.pack_propagate(False)

# left red accent bar
accent = tk.Frame(header, bg=RED, width=5)
accent.place(x=0, y=0, relheight=1)

# SFU logo — place sfu_logo.png in assets/
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

# red pill badge top-right
badge = ctk.CTkLabel(header, text="  LIVE  ",
                     font=FB(10), text_color=WHITE,
                     fg_color=RED, corner_radius=8)
badge.place(x=548, y=28)

sep = tk.Frame(root, bg=RED, height=3)
sep.pack(fill="x")

# ── Controls card ─────────────────────────────────────────────────────────────
ctrl = ctk.CTkFrame(root, fg_color=BG_CARD, corner_radius=12)
ctrl.pack(fill="x", padx=20, pady=(18, 0))

def section_label(parent, text):
    ctk.CTkLabel(parent, text=text, font=FB(10), text_color=DIM,
                 fg_color="transparent").pack(anchor="w", padx=20, pady=(14, 4))

def divider(parent):
    tk.Frame(parent, bg=BORDER, height=1).pack(fill="x", padx=20, pady=6)

# ── Node selectors
section_label(ctrl, "ROUTE")

nodes_frame = ctk.CTkFrame(ctrl, fg_color="transparent")
nodes_frame.pack(fill="x", padx=20, pady=(0, 4))
nodes_frame.grid_columnconfigure((0, 1), weight=1)

for col, (lbl, var_name) in enumerate([("From", "start_var"), ("To", "end_var")]):
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

WX_OPTIONS = [
    ("CLEAR",    "☀",  "Clear",   WHITE),
    ("RAINING",  "🌧", "Rain",    BLUE),
    ("SNOWY",    "❄",  "Snow",    "#a5f3fc"),
]
for val, icon, label, col in WX_OPTIONS:
    btn_frame = ctk.CTkFrame(wx_frame, fg_color=BG_INPUT, corner_radius=8)
    btn_frame.pack(side="left", padx=(0, 8), ipadx=4, ipady=4)
    ctk.CTkRadioButton(btn_frame, text=f"{icon}  {label}", variable=wx_var, value=val,
                       fg_color=RED, hover_color=RED_HOV,
                       text_color=col, font=FR(13),
                       border_color=BORDER).pack(padx=10, pady=6)

divider(ctrl)

# ── Tolerance
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
tol_row.pack(fill="x", padx=20, pady=(4, 16))
ctk.CTkSlider(tol_row, from_=0, to=1, variable=tol_var,
              progress_color=RED, button_color=WHITE, button_hover_color=RED_HOV,
              fg_color=BG_INPUT,
              command=lambda v: tol_lbl.configure(text=f"{int(float(v)*100)}%")).pack(fill="x")

# ── Find button ───────────────────────────────────────────────────────────────
ctk.CTkButton(root, text="FIND PATH",
              command=lambda: find(),
              height=52, corner_radius=10,
              fg_color=RED, hover_color=RED_HOV,
              text_color=WHITE, font=FB(16)).pack(fill="x", padx=20, pady=14)

# ── Results ───────────────────────────────────────────────────────────────────
res_outer = ctk.CTkFrame(root, fg_color=BG_CARD, corner_radius=12)
res_outer.pack(fill="both", expand=True, padx=20, pady=(0, 20))

# results header bar
res_hdr = ctk.CTkFrame(res_outer, fg_color=BG_ROW, corner_radius=0, height=40)
res_hdr.pack(fill="x")
res_hdr.pack_propagate(False)
res_hdr.grid_columnconfigure(0, weight=1)

res_title = ctk.CTkLabel(res_hdr, text="ROUTE", font=FB(11), text_color=DIM,
                          fg_color="transparent", anchor="w")
res_title.pack(side="left", padx=16)

summary_lbl = ctk.CTkLabel(res_hdr, text="", font=FB(12), text_color=GOLD,
                             fg_color="transparent", anchor="e")
summary_lbl.pack(side="right", padx=16)

# scrollable steps
scroll = ctk.CTkScrollableFrame(res_outer, fg_color="transparent",
                                 scrollbar_button_color=BG_ROW,
                                 scrollbar_button_hover_color=RED)
scroll.pack(fill="both", expand=True, padx=0, pady=0)
scroll.grid_columnconfigure(0, weight=1)

placeholder = ctk.CTkLabel(scroll,
    text="Select a start and destination,\nthen press FIND PATH.",
    font=FR(14), text_color=DIM, justify="center", fg_color="transparent")
placeholder.grid(row=0, column=0, pady=40)

# ── Find logic ────────────────────────────────────────────────────────────────
def clear_results():
    for w in scroll.winfo_children():
        w.destroy()

def find():
    fresh = NodeMap()
    setUp(fresh, MAP_JSON)
    wx = Weather[wx_var.get()]
    if wx != Weather.CLEAR:
        fresh.updateWeatherCosts(tol_var.get(), wx)
    start = fresh.nodes[start_var.get()]
    goal  = fresh.nodes[end_var.get()]
    for node in fresh.nodes.values():
        node.calcHeuristic(goal)
    path, _ = A_Star(start, goal)

    clear_results()

    if not path:
        ctk.CTkLabel(scroll, text="No path found.", font=FR(14),
                     text_color=DIM, fg_color="transparent").grid(row=0, column=0, pady=40)
        summary_lbl.configure(text="")
        return

    total_m = sum(haversine(path[i], path[i+1]) for i in range(len(path)-1))
    total_str = f"{total_m:.0f} m" if total_m < 1000 else f"{total_m/1000:.2f} km"
    summary_lbl.configure(text=f"{total_str}  ·  {len(path)} stops")

    for i, node in enumerate(path):
        is_last = (i == len(path) - 1)

        # step card
        card = ctk.CTkFrame(scroll, fg_color=BG_ROW, corner_radius=10)
        card.grid(row=i*2, column=0, sticky="ew", padx=12, pady=(6, 0))
        card.grid_columnconfigure(1, weight=1)

        # step number circle
        num_lbl = ctk.CTkLabel(card,
            text=f"{i+1}" if not is_last else "★",
            font=FB(13), text_color=WHITE,
            fg_color=RED if not is_last else GOLD,
            corner_radius=16, width=32, height=32)
        num_lbl.grid(row=0, column=0, padx=(14, 12), pady=14)

        # node name
        ctk.CTkLabel(card, text=node.name,
                     font=FB(14), text_color=WHITE,
                     fg_color="transparent", anchor="w").grid(
            row=0, column=1, sticky="w", pady=14)

        # edge info badge (not last)
        if not is_last:
            dist    = haversine(node, path[i+1])
            nxt_edge = next((e for e in node.edges if e.destNode.name == path[i+1].name), None)
            is_in   = nxt_edge and nxt_edge.isIndoor
            tag_txt = "Indoor" if is_in else "Outdoor"
            tag_col = GREEN   if is_in else GOLD
            tag_bg  = "#0d2b1f" if is_in else "#2b1f0d"

            badge_frame = ctk.CTkFrame(card, fg_color="transparent")
            badge_frame.grid(row=0, column=2, padx=(0, 14), pady=14)

            ctk.CTkLabel(badge_frame, text=tag_txt,
                         font=FB(10), text_color=tag_col,
                         fg_color=tag_bg, corner_radius=6,
                         width=60, height=22).pack(anchor="e")
            ctk.CTkLabel(badge_frame, text=f"{dist:.0f} m",
                         font=FM(11), text_color=DIM,
                         fg_color="transparent").pack(anchor="e", pady=(2,0))

        # connector arrow between cards
        if not is_last:
            connector = ctk.CTkLabel(scroll, text="↓",
                                     font=ctk.CTkFont(size=16), text_color=BORDER,
                                     fg_color="transparent")
            connector.grid(row=i*2+1, column=0, pady=0)
        
    # Render path on map
    show_map(path)

# ── Map display ─────────────────────────────────────────────────────────────

# Bounds of the SFU map to help normalize lat/lon of nodes to pixel coordinates 
MAP_TOP_LAT = 49.281381
MAP_BOTTOM_LAT = 49.275921
MAP_LEFT_LON = -122.932051
MAP_RIGHT_LON = -122.911654

def show_map(path):
    # Define tk window for map display
    map_window = tk.Toplevel(root)
    map_window.title("Route Map")
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