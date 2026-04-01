import customtkinter as ctk
import json, math, os
from enum import Enum

class Weather(Enum):
    CLEAR=1.0; RAINING=1.25; SNOWY=1.75

class Node:
    def __init__(self, name, lon, lat):
        self.name=name; self.edges=[]; self.h=0.0; self.lon=lon; self.lat=lat

class Edge:
    def __init__(self, home, dest, cost, indoor):
        self.homeNode=home; self.destNode=dest; self.cost=cost; self.is_indoor=indoor

class FE:
    def __init__(self, node, parent, cost):
        self.node=node; self.parent=parent; self.cost=cost

def load_map(path):
    data = json.load(open(path))
    tmp = {n["name"]: Node(n["name"], n["long"], n["lat"]) for n in data["nodes"]}
    for n in data["nodes"]:
        for e in n["edges"]:
            if e["name"] in tmp:
                tmp[n["name"]].edges.append(Edge(tmp[n["name"]], tmp[e["name"]], e["cost"], e["isIndoor"]))
    for node in tmp.values():
        for e in node.edges:
            if not any(x.destNode==node for x in e.destNode.edges):
                e.destNode.edges.append(Edge(e.destNode, node, e.cost, e.is_indoor))
    return tmp

def a_star(start, goal):
    def h(n): n.h=math.sqrt((n.lon-goal.lon)**2+(n.lat-goal.lat)**2); return n.h
    fringe=[FE(start,None,0)]; visited=set()
    while fringe:
        cur=min(fringe,key=lambda f:f.cost); fringe.remove(cur)
        if cur.node==goal:
            path,f=[],cur
            while f: path.append(f.node); f=f.parent
            return list(reversed(path)),cur.cost
        if cur.node.name in visited: continue
        visited.add(cur.node.name)
        for e in cur.node.edges:
            if e.destNode.name not in visited:
                fringe.append(FE(e.destNode,cur,cur.cost-cur.node.h+e.cost+h(e.destNode)))
    return None,None

MAP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "maps", "mapNodes.json")
node_map   = load_map(MAP)
node_names = sorted(node_map.keys())

ctk.set_appearance_mode("dark")
root = ctk.CTk()
root.title("SFU Pathfinder")
root.geometry("500x600")

ctk.CTkLabel(root, text="SFU Pathfinder", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=16)

ctk.CTkLabel(root, text="Start").pack()
start_var = ctk.StringVar(value=node_names[0])
ctk.CTkOptionMenu(root, values=node_names, variable=start_var, width=340).pack()

ctk.CTkLabel(root, text="End").pack(pady=(10,0))
end_var = ctk.StringVar(value=node_names[-1])
ctk.CTkOptionMenu(root, values=node_names, variable=end_var, width=340).pack()

ctk.CTkLabel(root, text="Weather").pack(pady=(10,0))
wx_var = ctk.StringVar(value="CLEAR")
f = ctk.CTkFrame(root, fg_color="transparent"); f.pack()
for t,v in [("Clear","CLEAR"),("Rain","RAINING"),("Snow","SNOWY")]:
    ctk.CTkRadioButton(f, text=t, variable=wx_var, value=v).pack(side="left", padx=8)

ctk.CTkLabel(root, text="Tolerance (0=avoids outdoors, 1=ignores)").pack(pady=(10,0))
tol_var = ctk.DoubleVar(value=0.5)
tol_lbl = ctk.CTkLabel(root, text="0.50")
ctk.CTkSlider(root, from_=0, to=1, variable=tol_var, width=340,
              command=lambda v: tol_lbl.configure(text=f"{v:.2f}")).pack()
tol_lbl.pack()

out = ctk.CTkTextbox(root, width=460, height=220, font=ctk.CTkFont(family="Courier New", size=12))
out.pack(pady=12)
out.insert("end", "Pick nodes and click Find Path.\n")
out.configure(state="disabled")

def find():
    fresh = load_map(MAP)
    wx = Weather[wx_var.get()]
    if wx != Weather.CLEAR:
        for node in fresh.values():
            for e in node.edges:
                if not e.is_indoor: e.cost += (1-tol_var.get()) * wx.value

    path, cost = a_star(fresh[start_var.get()], fresh[end_var.get()])
    out.configure(state="normal"); out.delete("1.0","end")
    if not path:
        out.insert("end","No path found.\n")
    else:
        out.insert("end", f"{len(path)} stops — cost: {cost:.3f}\n" + "─"*40+"\n")
        for i,node in enumerate(path):
            if i<len(path)-1:
                e = next((x for x in node.edges if x.destNode==path[i+1]),None)
                tag = "[in]" if e and e.is_indoor else "[out]"
                out.insert("end", f"{i+1:02d}. {node.name}  →{tag} {e.cost:.2f}\n" if e else f"{i+1:02d}. {node.name}\n")
            else:
                out.insert("end", f"{i+1:02d}. {node.name} ★\n")
    out.configure(state="disabled")

ctk.CTkButton(root, text="Find Path", command=find, width=340,
              fg_color="#CC0633", hover_color="#ff1744").pack()

root.mainloop()