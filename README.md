# SFU Campus Pathfinder

An A* pathfinding application for navigating SFU's Burnaby campus.

## Features
- A* search algorithm for finding optimal routes through the campus
- Weather-aware routing with adjustable tolerance (Clear, Rain, Snow)
- Simulated construction with penalties
- Adaptive edge cost learning based on real walk times
- Interactive User Interface with Campus Map Visualization

## Requirements
- Python 3.10+
- pip

## Setup
1. Clone the repository (SSH) 

`git clone git@github.com:KaiHikichi/SFUPathFinder.git`

2. Install dependencies

`pip install -r requirements.txt`

3. Run the application

`python main.py`

## How It Works
1. Select a start and destination node from the dropdowns
2. Set weather conditions and your tolerance for being outdoors
3. Adjust construction chance and penalty
4. Press **FIND PATH** to run A* algorithm
5. You will see the optimal route to walk, as well as distance and time estimates. You can view your route on a map by clicking the **VIEW ON MAP** button
6. After walking the route, you may enter how long it took. The app will learn and improve future estimates


## Authors
- Kian Athari
- Bryan Dela Cruz
- Kai Hikichi
- Mohid Rashid