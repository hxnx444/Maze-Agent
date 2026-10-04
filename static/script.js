/* script.js
 * Thin client: no algorithm or ML logic here, only fetch() calls to the
 * Flask API and DOM rendering / animation for a single maze grid.
 */

const els = {
  statusDot: document.getElementById("agentStatusDot"),
  statusText: document.getElementById("agentStatusText"),
  mazeGrid: document.getElementById("mazeGrid"),
  mazePanelTitle: document.getElementById("mazePanelTitle"),

  btnGenerate: document.getElementById("btnGenerate"),
  btnBFS: document.getElementById("btnBFS"),
  btnAstar: document.getElementById("btnAstar"),
  btnAgent: document.getElementById("btnAgent"),
  btnReset: document.getElementById("btnReset"),

  difficultyValue: document.getElementById("difficultyValue"),
  confidenceValue: document.getElementById("confidenceValue"),
  currentAlgoValue: document.getElementById("currentAlgoValue"),
  modelStatusValue: document.getElementById("modelStatusValue"),

  barEasy: document.getElementById("barEasy"),
  barMedium: document.getElementById("barMedium"),
  barHard: document.getElementById("barHard"),
  pctEasy: document.getElementById("pctEasy"),
  pctMedium: document.getElementById("pctMedium"),
  pctHard: document.getElementById("pctHard"),

  featSize: document.getElementById("featSize"),
  featDensity: document.getElementById("featDensity"),
  featDistance: document.getElementById("featDistance"),
  featOpen: document.getElementById("featOpen"),
  featDeadEnds: document.getElementById("featDeadEnds"),

  agentReason: document.getElementById("agentReason"),

  tblBfsPath: document.getElementById("tblBfsPath"),
  tblAstarPath: document.getElementById("tblAstarPath"),
  tblBfsExpanded: document.getElementById("tblBfsExpanded"),
  tblAstarExpanded: document.getElementById("tblAstarExpanded"),
  tblBfsTime: document.getElementById("tblBfsTime"),
  tblAstarTime: document.getElementById("tblAstarTime"),
  tblBfsFound: document.getElementById("tblBfsFound"),
  tblAstarFound: document.getElementById("tblAstarFound"),
  conclusionBox: document.getElementById("conclusionBox"),

  trainingLog: document.getElementById("trainingLog"),
  trainingProgress: document.getElementById("trainingProgress"),
  nnResultLabel: document.getElementById("nnResultLabel"),
  nnResultSub: document.getElementById("nnResultSub"),

  testAccValue: document.getElementById("testAccValue"),
  testSetInfo: document.getElementById("testSetInfo"),
  confusionBody: document.getElementById("confusionBody"),
};

let currentMaze = null;
let cellEls = [];
let animating = false;
let lastBfs = null;
let lastAstar = null;

const allButtons = () => [els.btnGenerate, els.btnBFS, els.btnAstar, els.btnAgent, els.btnReset];

function setBusy(isBusy, label) {
  animating = isBusy;
  allButtons().forEach((b) => (b.disabled = isBusy));
  els.statusDot.className = "status-dot" + (isBusy ? " status-busy" : " status-done");
  els.statusText.textContent = label || (isBusy ? "Working…" : "Idle");
}

/* ---------------- Grid rendering ---------------- */

function buildGrid(maze) {
  currentMaze = maze;
  const { grid, rows, cols, start, goal } = maze;

  els.mazeGrid.style.aspectRatio = `${cols} / ${rows}`;
  els.mazeGrid.style.gridTemplateColumns = `repeat(${cols}, 1fr)`;
  els.mazeGrid.style.gridTemplateRows = `repeat(${rows}, 1fr)`;
  els.mazeGrid.innerHTML = "";

  cellEls = [];
  for (let r = 0; r < rows; r++) {
    const row = [];
    for (let c = 0; c < cols; c++) {
      const div = document.createElement("div");
      div.className = "cell";
      if (grid[r][c] === 1) div.classList.add("wall");
      if (r === start.r && c === start.c) div.classList.add("start");
      if (r === goal.r && c === goal.c) div.classList.add("goal");
      els.mazeGrid.appendChild(div);
      row.push(div);
    }
    cellEls.push(row);
  }
}

function clearOverlays() {
  if (!cellEls.length) return;
  for (const row of cellEls) {
    for (const cell of row) {
      cell.classList.remove("visited", "path");
    }
  }
}

function isStartOrGoal(r, c) {
  const { start, goal } = currentMaze;
  return (r === start.r && c === start.c) || (r === goal.r && c === goal.c);
}

/* Animates visitedOrder then the final path over the single grid. */
function animateResult(result) {
  const panel = document.getElementById("panelMaze");
  return new Promise((resolve) => {
    clearOverlays();
    panel.classList.add("is-running");
    const visited = result.visitedOrder || [];
    const path = result.path || [];

    // Scale animation speed to maze size so a 50x50 maze doesn't take forever.
    const stepMs = visited.length > 600 ? 2 : visited.length > 250 ? 5 : 12;
    let i = 0;

    function stepVisited() {
      if (i >= visited.length) {
        animatePath();
        return;
      }
      const { r, c } = visited[i];
      if (!isStartOrGoal(r, c)) cellEls[r][c].classList.add("visited");
      i++;
      setTimeout(stepVisited, stepMs);
    }

    function animatePath() {
      let j = 0;
      function stepPath() {
        if (j >= path.length) {
          panel.classList.remove("is-running");
          resolve();
          return;
        }
        const { r, c } = path[j];
        if (!isStartOrGoal(r, c)) cellEls[r][c].classList.add("path");
        j++;
        setTimeout(stepPath, Math.max(stepMs, 10));
      }
      stepPath();
    }

    stepVisited();
  });
}

/* ---------------- Stat panel rendering ---------------- */

function renderFeatures(features) {
  if (!features) return;
  els.featSize.textContent = features.size;
  els.featDensity.textContent = (features.wallDensity * 100).toFixed(1) + "%";
  els.featDistance.textContent = features.distance;
  els.featOpen.textContent = features.openCells;
  els.featDeadEnds.textContent = features.deadEnds;
}

function renderPrediction(prediction) {
  if (!prediction) return;
  const label = prediction.label;
  els.difficultyValue.textContent = label;
  els.difficultyValue.className =
    "stat-value diff-" + label.toLowerCase();
  els.confidenceValue.textContent = (prediction.confidence * 100).toFixed(1) + "%";

  const p = prediction.probabilities;
  els.barEasy.style.width = (p.EASY * 100).toFixed(1) + "%";
  els.barMedium.style.width = (p.MEDIUM * 100).toFixed(1) + "%";
  els.barHard.style.width = (p.HARD * 100).toFixed(1) + "%";
  els.pctEasy.textContent = (p.EASY * 100).toFixed(0) + "%";
  els.pctMedium.textContent = (p.MEDIUM * 100).toFixed(0) + "%";
  els.pctHard.textContent = (p.HARD * 100).toFixed(0) + "%";

  els.nnResultLabel.textContent = "Maze Difficulty: " + label;
  els.nnResultSub.textContent =
    `Confidence ${(prediction.confidence * 100).toFixed(1)}% · ` +
    `EASY ${(p.EASY * 100).toFixed(0)}% / MEDIUM ${(p.MEDIUM * 100).toFixed(0)}% / HARD ${(p.HARD * 100).toFixed(0)}%`;
}

function renderTrainingLog(log) {
  if (!log || !log.length) return;
  const last = log[log.length - 1];
  els.trainingProgress.style.width = (last.epoch / last.totalEpochs) * 100 + "%";
  const tail = log.slice(-5);
  els.trainingLog.textContent = tail
    .map((e) => `epoch ${e.epoch}/${e.totalEpochs}  loss=${e.loss.toFixed(4)}  acc=${(e.acc * 100).toFixed(1)}%`)
    .join("\n");
}

function renderModelEval(evalData) {
  if (!evalData) return;
  els.testAccValue.textContent = `Test Accuracy: ${(evalData.testAccuracy * 100).toFixed(1)}%`;
  els.testSetInfo.textContent =
    `Held out ${evalData.testSetSize} of ${evalData.testSetSize + evalData.trainSetSize} samples ` +
    `(never seen during training)`;

  const labels = evalData.labels;
  const cm = evalData.confusionMatrix;
  els.confusionBody.innerHTML = "";
  labels.forEach((rowLabel, r) => {
    const tr = document.createElement("tr");
    const rowLabelTd = document.createElement("td");
    rowLabelTd.textContent = rowLabel;
    tr.appendChild(rowLabelTd);
    labels.forEach((_, c) => {
      const td = document.createElement("td");
      td.textContent = cm[r][c];
      if (c === r) td.classList.add("diag-cell");
      tr.appendChild(td);
    });
    els.confusionBody.appendChild(tr);
  });
}

function fmtTime(ms) {
  return ms.toFixed(2) + " ms";
}

function updateComparisonTable() {
  if (lastBfs) {
    els.tblBfsPath.textContent = lastBfs.found ? lastBfs.path.length : "—";
    els.tblBfsExpanded.textContent = lastBfs.expanded;
    els.tblBfsTime.textContent = fmtTime(lastBfs.timeMs);
    els.tblBfsFound.textContent = lastBfs.found ? "Yes" : "No";
  }
  if (lastAstar) {
    els.tblAstarPath.textContent = lastAstar.found ? lastAstar.path.length : "—";
    els.tblAstarExpanded.textContent = lastAstar.expanded;
    els.tblAstarTime.textContent = fmtTime(lastAstar.timeMs);
    els.tblAstarFound.textContent = lastAstar.found ? "Yes" : "No";
  }

  if (lastBfs && lastAstar) {
    if (!lastBfs.found || !lastAstar.found) {
      els.conclusionBox.innerHTML = "One of the runs didn't find a path — generate a new maze and try again.";
      return;
    }
    const diff = lastBfs.expanded - lastAstar.expanded;
    if (diff > 0) {
      const pct = ((diff / lastBfs.expanded) * 100).toFixed(1);
      els.conclusionBox.innerHTML =
        `<strong>A* wins.</strong> It expanded ${pct}% fewer nodes than BFS (${lastAstar.expanded} vs ${lastBfs.expanded}) ` +
        `by using the Manhattan-distance heuristic to stay focused on the goal, while both found a path of the same length.`;
    } else if (diff < 0) {
      els.conclusionBox.innerHTML =
        `<strong>BFS matched or beat A*</strong> on this maze (${lastBfs.expanded} vs ${lastAstar.expanded} nodes expanded) — ` +
        `this can happen on small or sparse mazes where the heuristic has little room to help.`;
    } else {
      els.conclusionBox.innerHTML = `<strong>Tie.</strong> Both algorithms expanded the same number of nodes (${lastBfs.expanded}).`;
    }
  }
}

function resetComparisonTable() {
  lastBfs = null;
  lastAstar = null;
  [
    els.tblBfsPath, els.tblAstarPath, els.tblBfsExpanded, els.tblAstarExpanded,
    els.tblBfsTime, els.tblAstarTime, els.tblBfsFound, els.tblAstarFound,
  ].forEach((el) => (el.textContent = "—"));
  els.conclusionBox.textContent = "Run both algorithms to generate a comparison conclusion.";
}

/* ---------------- API calls ---------------- */

async function loadState() {
  setBusy(true, "Loading…");
  const res = await fetch("/api/state");
  const data = await res.json();
  buildGrid(data.maze);
  renderFeatures(data.features);
  if (data.prediction) renderPrediction(data.prediction);
  els.modelStatusValue.textContent = data.modelTrained ? "Trained" : "Training…";
  renderTrainingLog(data.trainingLog);
  renderModelEval(data.modelEval);
  setBusy(false);
}

async function newMaze() {
  setBusy(true, "Generating maze…");
  resetComparisonTable();
  els.currentAlgoValue.textContent = "—";
  els.agentReason.textContent = 'Run "Let Agent Decide" to see why the agent picked an algorithm.';
  const res = await fetch("/api/new-maze", { method: "POST" });
  const data = await res.json();
  buildGrid(data.maze);
  renderFeatures(data.features);
  if (data.prediction) renderPrediction(data.prediction);
  setBusy(false);
}

async function runAlgo(algo) {
  setBusy(true, algo === "bfs" ? "Running BFS…" : "Running A*…");
  const res = await fetch(`/api/run/${algo}`, { method: "POST" });
  const result = await res.json();

  if (algo === "bfs") lastBfs = result;
  else lastAstar = result;

  els.currentAlgoValue.textContent = result.algorithm;
  await animateResult(result);
  updateComparisonTable();
  setBusy(false);
}

async function runAgent() {
  setBusy(true, "Agent deciding…");
  const res = await fetch("/api/run-agent", { method: "POST" });
  const data = await res.json();

  renderPrediction(data.prediction);
  els.currentAlgoValue.textContent = data.decision.algorithm;
  els.agentReason.textContent = data.decision.reason;

  if (data.decision.algorithmKey === "bfs") lastBfs = data.result;
  else lastAstar = data.result;

  await animateResult(data.result);
  updateComparisonTable();
  setBusy(false);
}

function resetView() {
  clearOverlays();
  resetComparisonTable();
  els.currentAlgoValue.textContent = "—";
  els.agentReason.textContent = 'Run "Let Agent Decide" to see why the agent picked an algorithm.';
}

/* ---------------- Wire up ---------------- */

els.btnGenerate.addEventListener("click", () => { if (!animating) newMaze(); });
els.btnBFS.addEventListener("click", () => { if (!animating) runAlgo("bfs"); });
els.btnAstar.addEventListener("click", () => { if (!animating) runAlgo("astar"); });
els.btnAgent.addEventListener("click", () => { if (!animating) runAgent(); });
els.btnReset.addEventListener("click", () => { if (!animating) resetView(); });

loadState();
