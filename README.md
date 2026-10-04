# 🧩 Maze Agent

A small AI agent that looks at a maze, **predicts how hard it is** with a neural network, and then **chooses the search algorithm** (BFS or A\*) it expects to work best. Everything is visualized in a web UI.

## ✨ Features
- 🎲 Random maze generation (recursive backtracker / DFS) in 5 sizes
- 🧠 Difficulty classifier (EASY / MEDIUM / HARD): scikit-learn `MLPClassifier`, trained on synthetic mazes at startup
- 🤖 Agent that picks BFS or A\* from the prediction and explains why
- 🔍 Manual BFS and A\* runs to compare explored nodes and path length
- 📊 Training log and model evaluation shown in the UI

## 🚀 Quick Start
```bash
git clone https://github.com/hxnx444/Maze-Agent.git
cd Maze-Agent
pip install -r requirements.txt
python app.py
```
Then open **http://localhost:5000**. The model trains when the server starts, so the first launch takes a few seconds.

## 🔌 API
| Method | Route | Purpose |
|--------|-------|---------|
| `GET` | `/api/state` | Current maze, features, prediction, training log |
| `POST` | `/api/new-maze` | Generate a new maze |
| `POST` | `/api/run/<bfs\|astar>` | Run one algorithm |
| `POST` | `/api/run-agent` | Predict difficulty, let the agent pick, run it |

## 📁 Structure
```
Maze-Agent/
├── app.py            # Flask server + API
├── agent.py          # picks BFS or A* from the prediction
├── algorithms.py     # BFS and A* implementations
├── maze.py           # maze generation + feature extraction
├── ml_model.py       # synthetic data, MLP training, prediction
├── templates/        # index.html
├── static/           # script.js, style.css
└── requirements.txt
```

## 🛠️ Stack
Python · Flask · scikit-learn · NumPy · vanilla JS

## 📄 License
MIT
