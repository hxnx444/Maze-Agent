

import random

from flask import Flask, jsonify, render_template

import agent
import maze as maze_mod
import ml_model
from algorithms import run_astar, run_bfs

app = Flask(__name__)

MAZE_SIZE_OPTIONS = [(15, 19), (19, 25), (25, 35), (31, 45), (41, 55)]


STATE = {
    "maze": None,
    "features": None,
    "model": None,
    "training_log": [],
    "model_eval": None,
}


def _train_model_once():
    def on_progress(entry):
        STATE["training_log"].append(entry)

    model, log, evaluation = ml_model.build_and_train(on_progress=on_progress)
    STATE["model"] = model
    STATE["training_log"] = log
    STATE["model_eval"] = evaluation


def _new_maze():
    rows, cols = random.choice(MAZE_SIZE_OPTIONS)
    m = maze_mod.generate_maze(rows=rows, cols=cols)
    STATE["maze"] = m
    STATE["features"] = maze_mod.extract_features(m)
    return m


def _prediction_payload():
    if STATE["model"] is None or STATE["features"] is None:
        return None
    return ml_model.predict(STATE["model"], STATE["features"])


_train_model_once()
_new_maze()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/state")
def api_state():
    """Everything the page needs on first load: current maze, its
    features, and a prediction if the model is trained."""
    return jsonify(
        {
            "maze": STATE["maze"],
            "features": STATE["features"],
            "prediction": _prediction_payload(),
            "modelTrained": STATE["model"] is not None,
            "trainingLog": STATE["training_log"],
            "modelEval": STATE["model_eval"],
        }
    )


@app.route("/api/new-maze", methods=["POST"])
def api_new_maze():
    _new_maze()
    return jsonify(
        {
            "maze": STATE["maze"],
            "features": STATE["features"],
            "prediction": _prediction_payload(),
        }
    )


@app.route("/api/run/<algo>", methods=["POST"])
def api_run(algo):
    if STATE["maze"] is None:
        return jsonify({"error": "no maze generated yet"}), 400

    if algo == "bfs":
        result = run_bfs(STATE["maze"])
    elif algo == "astar":
        result = run_astar(STATE["maze"])
    else:
        return jsonify({"error": f"unknown algorithm '{algo}'"}), 400

    return jsonify(result)


@app.route("/api/run-agent", methods=["POST"])
def api_run_agent():
 
    if STATE["maze"] is None or STATE["model"] is None:
        return jsonify({"error": "maze or model not ready"}), 400

    prediction = ml_model.predict(STATE["model"], STATE["features"])
    decision = agent.decide(prediction)

    if decision["algorithmKey"] == "bfs":
        result = run_bfs(STATE["maze"])
    else:
        result = run_astar(STATE["maze"])

    return jsonify({"prediction": prediction, "decision": decision, "result": result})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
