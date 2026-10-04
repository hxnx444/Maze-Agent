# 🧩 Maze Agent

An AI agent that learns to navigate and solve mazes.

![demo](assets/demo.gif)

## ✨ Features
- 🧠 Solves mazes with **[A* / BFS / Q-learning, pick yours]**
- 🎲 Random maze generation (DFS / Prim's)
- 📊 Visualization of the agent's path and training progress
- ⚙️ Configurable maze size and difficulty

## 🚀 Quick Start
```bash
git clone https://github.com/<username>/maze-agent.git
cd maze-agent
pip install -r requirements.txt
python main.py
```

## 🕹️ Usage
```bash
python main.py --size 20 --algo qlearning --render
```

| Flag | Description | Default |
|------|-------------|---------|
| `--size` | Maze dimensions | `10` |
| `--algo` | Agent algorithm | `astar` |
| `--render` | Show visualization | `false` |

## 📁 Structure
```
maze-agent/
├── agent/       # agent logic
├── maze/        # maze generation
├── main.py
└── requirements.txt
```

## 🛣️ Roadmap
- [ ] Add reinforcement learning agent
- [ ] Compare algorithms with benchmarks
- [ ] Web demo

## 📄 License
MIT
