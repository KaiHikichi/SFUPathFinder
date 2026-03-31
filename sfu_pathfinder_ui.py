import customtkinter as ctk
import json
import math
import sys
import os

# ── Appearance ──────────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# ── Colours ──────────────────────────────────────────────────────────────────
SFU_RED      = "#CC0633"
SFU_RED_DIM  = "#8B0422"
SFU_RED_GLOW = "#FF1744"
BG_DARK      = "#0D0D0D"
BG_PANEL     = "#141414"
BG_CARD      = "#1A1A1A"
BG_HOVER     = "#222222"
TEXT_PRIMARY = "#F0F0F0"
TEXT_DIM     = "#888888"
TEXT_MUTED   = "#555555"
ACCENT_GOLD  = "#FFB81C"
INDOOR_COL   = "#4FC3F7"
OUTDOOR_COL  = "#81C784"
BORDER_COL   = "#2A2A2A"

# ── Inline graph / search (no external imports needed) ────────────────────────
from enum import Enum

class Weather(Enum):
    CLEAR  = 1.00
    RAINING = 1.25
    SNOWY   = 1.75

class Node:
    def __init__(self, name, lon, lat):
        self.name  = name
        self.edges = []
        self.h     = 0.0
        self.lon   = lon
        self.lat   = lat

    def __str__(self):
        return self.name

    def calc_heuristic(self, goal):
        self.h = math.sqrt((self.lon - goal.lon)**2 + (self.lat - goal.lat)**2)

class Edge:
    def __init__(self, home, dest, cost, is_indoor):
        self.homeNode = home
        self.destNode = dest
        self.cost     = cost
        self.is_indoor = is_indoor

class NodeMap:
    def __init__(self):
        self.nodes = {}

    def add_node(self, node):
        self.nodes[node.name] = node
        for edge in node.edges[:]:
            if edge.destNode.name in self.nodes:
                target = self.nodes[edge.destNode.name]
                rev = Edge(target, node, edge.cost, edge.is_indoor)
                target.edges.append(rev)
            else:
                node.edges.remove(edge)

class FE:
    def __init__(self, node, parent, cost):
        self.node   = node
        self.parent = parent
        self.cost   = cost

def load_map(json_path):
    with open(json_path, "r") as f:
        data = json.load(f)
    node_map = NodeMap()
    # First pass: create all nodes
    tmp = {}
    for nd in data["nodes"]:
        n = Node(nd["name"], nd["long"], nd["lat"])
        tmp[nd["name"]] = n
    # Second pass: add edges then insert into map in order
    for nd in data["nodes"]:
        n = tmp[nd["name"]]
        for e in nd["edges"]:
            if e["name"] in tmp:
                edge = Edge(n, tmp[e["name"]], e["cost"], e["isIndoor"])
                n.edges.append(edge)
        node_map.nodes[n.name] = n
    # Third pass: wire reverse edges
    for name, node in node_map.nodes.items():
        for edge in node.edges:
            dest = edge.destNode
            exists = any(e.destNode == node for e in dest.edges)
            if not exists:
                rev = Edge(dest, node, edge.cost, edge.is_indoor)
                dest.edges.append(rev)
    return node_map

def apply_weather(node_map, tolerance, weather):
    for node in node_map.nodes.values():
        for edge in node.edges:
            if not edge.is_indoor:
                edge.cost = edge.cost + (1 - tolerance) * weather.value

def a_star(start, goal):
    for node in [start, goal]:
        node.calc_heuristic(goal)

    fringe  = [FE(start, None, 0)]
    visited = set()

    # Pre-compute heuristics for all nodes reachable (lazy)
    def get_h(node):
        node.calc_heuristic(goal)
        return node.h

    while fringe:
        current = min(fringe, key=lambda fe: fe.cost)
        fringe.remove(current)

        if current.node == goal:
            # Reconstruct path
            path, edges_used = [], []
            fe = current
            while fe:
                path.append(fe.node)
                fe = fe.parent
            path.reverse()
            return path, current.cost

        if current.node.name in visited:
            continue
        visited.add(current.node.name)

        for edge in current.node.edges:
            if edge.destNode.name in visited:
                continue
            new_cost = current.cost - current.node.h + edge.cost + get_h(edge.destNode)
            fringe.append(FE(edge.destNode, current, new_cost))

    return None, None

def get_edge_between(node_a, node_b):
    for e in node_a.edges:
        if e.destNode == node_b:
            return e
    return None

# ── GUI ───────────────────────────────────────────────────────────────────────
MAP_FILE = os.path.join(os.path.dirname(__file__), "maps", "mapNodes.json")

class PathfinderApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("SFU Campus Pathfinder")
        self.geometry("780x820")
        self.minsize(700, 700)
        self.configure(fg_color=BG_DARK)

        # Load map
        try:
            self.node_map = load_map(MAP_FILE)
        except FileNotFoundError:
            self.node_map = None

        self.node_names = sorted(self.node_map.nodes.keys()) if self.node_map else []
        self._build_ui()

    # ── Layout ────────────────────────────────────────────────────────────────
    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_header()
        self._build_controls()
        self._build_results()
        self._build_footer()

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color=BG_PANEL, corner_radius=0, height=80)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(1, weight=1)
        header.grid_propagate(False)

        # Red accent bar
        bar = ctk.CTkFrame(header, fg_color=SFU_RED, width=5, corner_radius=0)
        bar.grid(row=0, column=0, sticky="ns", padx=(0, 16), pady=0)

        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.grid(row=0, column=1, sticky="w", pady=16)

        ctk.CTkLabel(
            title_frame, text="SFU CAMPUS PATHFINDER",
            font=ctk.CTkFont(family="Courier New", size=20, weight="bold"),
            text_color=TEXT_PRIMARY
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_frame, text="A★ Navigation  ·  Burnaby Mountain",
            font=ctk.CTkFont(family="Courier New", size=11),
            text_color=TEXT_DIM
        ).pack(anchor="w")

        # SFU logo text badge
        badge = ctk.CTkLabel(
            header, text=" SFU ",
            font=ctk.CTkFont(family="Courier New", size=13, weight="bold"),
            text_color="white",
            fg_color=SFU_RED,
            corner_radius=4,
            width=44, height=28
        )
        badge.grid(row=0, column=2, padx=20, pady=20)

    def _build_controls(self):
        ctrl = ctk.CTkFrame(self, fg_color=BG_PANEL, corner_radius=10)
        ctrl.grid(row=1, column=0, sticky="ew", padx=16, pady=(12, 6))
        ctrl.grid_columnconfigure((0, 1), weight=1)

        # ── Node selectors ────────────────────────────────────────────────────
        node_frame = ctk.CTkFrame(ctrl, fg_color="transparent")
        node_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=(16, 8))
        node_frame.grid_columnconfigure((0, 1), weight=1)

        self._label(node_frame, "START NODE", 0, 0)
        self._label(node_frame, "END NODE",   0, 1)

        self.start_var = ctk.StringVar(value=self.node_names[0] if self.node_names else "")
        self.end_var   = ctk.StringVar(value=self.node_names[-1] if self.node_names else "")

        self.start_menu = ctk.CTkOptionMenu(
            node_frame, values=self.node_names, variable=self.start_var,
            fg_color=BG_CARD, button_color=SFU_RED_DIM, button_hover_color=SFU_RED,
            dropdown_fg_color=BG_CARD, dropdown_hover_color=BG_HOVER,
            text_color=TEXT_PRIMARY, dropdown_text_color=TEXT_PRIMARY,
            font=ctk.CTkFont(family="Courier New", size=12),
            corner_radius=6, anchor="w"
        )
        self.start_menu.grid(row=1, column=0, sticky="ew", padx=(0, 8))

        ctk.CTkLabel(
            node_frame, text="→",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=SFU_RED, fg_color="transparent"
        ).grid(row=1, column=0, columnspan=2)   # centred between menus

        self.end_menu = ctk.CTkOptionMenu(
            node_frame, values=self.node_names, variable=self.end_var,
            fg_color=BG_CARD, button_color=SFU_RED_DIM, button_hover_color=SFU_RED,
            dropdown_fg_color=BG_CARD, dropdown_hover_color=BG_HOVER,
            text_color=TEXT_PRIMARY, dropdown_text_color=TEXT_PRIMARY,
            font=ctk.CTkFont(family="Courier New", size=12),
            corner_radius=6, anchor="w"
        )
        self.end_menu.grid(row=1, column=1, sticky="ew", padx=(8, 0))

        # ── Divider ───────────────────────────────────────────────────────────
        div = ctk.CTkFrame(ctrl, fg_color=BORDER_COL, height=1, corner_radius=0)
        div.grid(row=1, column=0, columnspan=2, sticky="ew", padx=20, pady=8)

        # ── Weather controls ──────────────────────────────────────────────────
        wx_frame = ctk.CTkFrame(ctrl, fg_color="transparent")
        wx_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 6))
        wx_frame.grid_columnconfigure(1, weight=1)

        self._label(wx_frame, "WEATHER", 0, 0, span=2)

        # Weather type
        self.weather_var = ctk.StringVar(value="CLEAR")
        wx_type_frame = ctk.CTkFrame(wx_frame, fg_color="transparent")
        wx_type_frame.grid(row=1, column=0, sticky="w", pady=(4, 0))

        for label, val in [("☀ Clear", "CLEAR"), ("🌧 Rain", "RAINING"), ("❄ Snow", "SNOWY")]:
            btn = ctk.CTkRadioButton(
                wx_type_frame, text=label, variable=self.weather_var, value=val,
                fg_color=SFU_RED, hover_color=SFU_RED_DIM,
                text_color=TEXT_PRIMARY,
                font=ctk.CTkFont(family="Courier New", size=12),
                border_color=TEXT_MUTED
            )
            btn.pack(side="left", padx=(0, 16))

        # Tolerance slider
        tol_frame = ctk.CTkFrame(wx_frame, fg_color="transparent")
        tol_frame.grid(row=1, column=1, sticky="ew", padx=(20, 0), pady=(4, 0))
        tol_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            tol_frame, text="WEATHER TOLERANCE",
            font=ctk.CTkFont(family="Courier New", size=10),
            text_color=TEXT_DIM
        ).grid(row=0, column=0, columnspan=3, sticky="w")

        ctk.CTkLabel(
            tol_frame, text="AVOIDS",
            font=ctk.CTkFont(family="Courier New", size=9),
            text_color=TEXT_MUTED
        ).grid(row=1, column=0, padx=(0, 6))

        self.tolerance_var = ctk.DoubleVar(value=0.5)
        self.tol_slider = ctk.CTkSlider(
            tol_frame, from_=0.0, to=1.0, variable=self.tolerance_var,
            progress_color=SFU_RED, button_color=SFU_RED, button_hover_color=SFU_RED_GLOW,
            fg_color=BG_CARD, width=160
        )
        self.tol_slider.grid(row=1, column=1, sticky="ew", padx=4)

        ctk.CTkLabel(
            tol_frame, text="IGNORES",
            font=ctk.CTkFont(family="Courier New", size=9),
            text_color=TEXT_MUTED
        ).grid(row=1, column=2, padx=(6, 0))

        self.tol_label = ctk.CTkLabel(
            tol_frame, text="0.50",
            font=ctk.CTkFont(family="Courier New", size=10, weight="bold"),
            text_color=SFU_RED
        )
        self.tol_label.grid(row=1, column=3, padx=(8, 0))
        self.tol_slider.configure(command=self._update_tol_label)

        # ── Find Path button ──────────────────────────────────────────────────
        self.find_btn = ctk.CTkButton(
            ctrl, text="FIND OPTIMAL PATH  ▶",
            command=self._find_path,
            fg_color=SFU_RED, hover_color=SFU_RED_GLOW,
            text_color="white",
            font=ctk.CTkFont(family="Courier New", size=14, weight="bold"),
            corner_radius=6, height=44,
            border_width=0
        )
        self.find_btn.grid(row=3, column=0, columnspan=2, sticky="ew", padx=20, pady=(10, 18))

    def _build_results(self):
        outer = ctk.CTkFrame(self, fg_color=BG_PANEL, corner_radius=10)
        outer.grid(row=2, column=0, sticky="nsew", padx=16, pady=(0, 6))
        outer.grid_columnconfigure(0, weight=1)
        outer.grid_rowconfigure(1, weight=1)

        # Header bar
        hdr = ctk.CTkFrame(outer, fg_color=BG_CARD, corner_radius=0, height=36)
        hdr.grid(row=0, column=0, sticky="ew")
        hdr.grid_columnconfigure(0, weight=1)
        hdr.grid_propagate(False)

        ctk.CTkLabel(
            hdr, text="ROUTE OUTPUT",
            font=ctk.CTkFont(family="Courier New", size=11, weight="bold"),
            text_color=TEXT_DIM
        ).grid(row=0, column=0, sticky="w", padx=16)

        self.cost_badge = ctk.CTkLabel(
            hdr, text="",
            font=ctk.CTkFont(family="Courier New", size=11, weight="bold"),
            text_color=ACCENT_GOLD, fg_color="transparent"
        )
        self.cost_badge.grid(row=0, column=1, sticky="e", padx=16)

        # Scrollable result area
        self.result_scroll = ctk.CTkScrollableFrame(
            outer, fg_color="transparent", corner_radius=0,
            scrollbar_button_color=SFU_RED_DIM,
            scrollbar_button_hover_color=SFU_RED
        )
        self.result_scroll.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        self.result_scroll.grid_columnconfigure(0, weight=1)

        self.result_placeholder = ctk.CTkLabel(
            self.result_scroll,
            text="Select start and end nodes, then press\nFIND OPTIMAL PATH to calculate a route.",
            font=ctk.CTkFont(family="Courier New", size=13),
            text_color=TEXT_MUTED,
            justify="center"
        )
        self.result_placeholder.grid(row=0, column=0, pady=60)

    def _build_footer(self):
        footer = ctk.CTkFrame(self, fg_color="transparent", height=28)
        footer.grid(row=3, column=0, sticky="ew", padx=16, pady=(0, 8))
        footer.grid_columnconfigure(0, weight=1)
        footer.grid_propagate(False)

        legend = ctk.CTkFrame(footer, fg_color="transparent")
        legend.grid(row=0, column=0, sticky="w")

        for colour, label in [(INDOOR_COL, "Indoor"), (OUTDOOR_COL, "Outdoor")]:
            dot = ctk.CTkLabel(legend, text="●", text_color=colour,
                               font=ctk.CTkFont(size=10), fg_color="transparent")
            dot.pack(side="left", padx=(0, 3))
            ctk.CTkLabel(legend, text=label, text_color=TEXT_MUTED,
                         font=ctk.CTkFont(family="Courier New", size=10),
                         fg_color="transparent").pack(side="left", padx=(0, 12))

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _label(self, parent, text, row, col, span=1):
        ctk.CTkLabel(
            parent, text=text,
            font=ctk.CTkFont(family="Courier New", size=10, weight="bold"),
            text_color=TEXT_DIM
        ).grid(row=row, column=col, columnspan=span, sticky="w", pady=(0, 4))

    def _update_tol_label(self, val):
        self.tol_label.configure(text=f"{float(val):.2f}")

    # ── Path finding ──────────────────────────────────────────────────────────
    def _find_path(self):
        if not self.node_map:
            self._show_error("Could not load map file.")
            return

        start_name = self.start_var.get()
        end_name   = self.end_var.get()

        if start_name == end_name:
            self._show_error("Start and end nodes must be different.")
            return

        # Deep-copy costs before applying weather (reload fresh each time)
        try:
            fresh_map = load_map(MAP_FILE)
        except Exception as e:
            self._show_error(f"Map load error: {e}")
            return

        # Apply weather
        weather_key = self.weather_var.get()
        weather     = Weather[weather_key]
        tolerance   = self.tolerance_var.get()
        if weather != Weather.CLEAR:
            apply_weather(fresh_map, tolerance, weather)

        start = fresh_map.nodes.get(start_name)
        goal  = fresh_map.nodes.get(end_name)

        if not start or not goal:
            self._show_error("Unknown node selected.")
            return

        path, cost = a_star(start, goal)

        if path is None:
            self._show_error("No path found between these nodes.")
            return

        self._render_results(path, cost, fresh_map)

    def _clear_results(self):
        for widget in self.result_scroll.winfo_children():
            widget.destroy()

    def _show_error(self, msg):
        self._clear_results()
        self.cost_badge.configure(text="")
        ctk.CTkLabel(
            self.result_scroll, text=f"⚠  {msg}",
            font=ctk.CTkFont(family="Courier New", size=12),
            text_color=SFU_RED_GLOW
        ).grid(row=0, column=0, pady=40)

    def _render_results(self, path, cost, fresh_map):
        self._clear_results()
        self.cost_badge.configure(text=f"TOTAL COST  {cost:.3f}")

        for i, node in enumerate(path):
            row_frame = ctk.CTkFrame(
                self.result_scroll, fg_color=BG_CARD, corner_radius=8
            )
            row_frame.grid(row=i, column=0, sticky="ew", padx=12, pady=3)
            row_frame.grid_columnconfigure(1, weight=1)

            # Step number
            ctk.CTkLabel(
                row_frame,
                text=f"{i+1:02d}",
                font=ctk.CTkFont(family="Courier New", size=11, weight="bold"),
                text_color=TEXT_MUTED,
                width=28
            ).grid(row=0, column=0, padx=(12, 8), pady=10, sticky="w")

            # Node name
            ctk.CTkLabel(
                row_frame, text=node.name,
                font=ctk.CTkFont(family="Courier New", size=13, weight="bold"),
                text_color=TEXT_PRIMARY, anchor="w"
            ).grid(row=0, column=1, sticky="w", pady=10)

            # Edge info (if not last node)
            if i < len(path) - 1:
                next_node = path[i + 1]
                edge = get_edge_between(node, next_node)
                if edge:
                    is_in   = edge.is_indoor
                    tag_col = INDOOR_COL if is_in else OUTDOOR_COL
                    tag_txt = "INDOOR" if is_in else "OUTDOOR"
                    icon    = "🏠" if is_in else "🌿"

                    info_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
                    info_frame.grid(row=0, column=2, padx=(0, 12), sticky="e")

                    ctk.CTkLabel(
                        info_frame, text=f"{icon} {tag_txt}",
                        font=ctk.CTkFont(family="Courier New", size=10, weight="bold"),
                        text_color=tag_col, fg_color="transparent"
                    ).pack(side="left", padx=(0, 10))

                    ctk.CTkLabel(
                        info_frame,
                        text=f"cost  {edge.cost:.3f}",
                        font=ctk.CTkFont(family="Courier New", size=10),
                        text_color=ACCENT_GOLD, fg_color="transparent"
                    ).pack(side="left")

                # Arrow connector
                arrow = ctk.CTkLabel(
                    self.result_scroll, text="│",
                    font=ctk.CTkFont(family="Courier New", size=10),
                    text_color=TEXT_MUTED, fg_color="transparent"
                )
                arrow.grid(row=i, column=0, sticky="s", pady=0)

            else:
                # Destination badge
                ctk.CTkLabel(
                    row_frame, text="⬛ DESTINATION",
                    font=ctk.CTkFont(family="Courier New", size=10, weight="bold"),
                    text_color=SFU_RED, fg_color="transparent"
                ).grid(row=0, column=2, padx=(0, 12), sticky="e")


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = PathfinderApp()
    app.mainloop()