
import random
import warnings

import numpy as np
from sklearn.exceptions import ConvergenceWarning
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier


warnings.filterwarnings("ignore", category=ConvergenceWarning)

LABELS = ["EASY", "MEDIUM", "HARD"]

RANGES = {
    "size": (100, 2000),
    "wallDensity": (0, 1),
    "distance": (0, 100),
    "openCells": (50, 1600),
    "deadEnds": (0, 400),
}


def _norm(v, bounds):
    lo, hi = bounds
    x = (v - lo) / (hi - lo)
    return min(1.0, max(0.0, x))


def to_input_vector(features):
    return [
        _norm(features["size"], RANGES["size"]),
        _norm(features["wallDensity"], RANGES["wallDensity"]),
        _norm(features["distance"], RANGES["distance"]),
        _norm(features["openCells"], RANGES["openCells"]),
        _norm(features["deadEnds"], RANGES["deadEnds"]),
    ]


def _generate_sample():
    """Generates a plausible random maze-feature sample and an oracle
    label used ONLY to create ground truth for supervised training."""
    size = 100 + random.random() * 1900
    wall_density = 0.15 + random.random() * 0.55
    open_cells = size * (1 - wall_density)
    distance = random.random() * min(100, (size ** 0.5) * 4)
    dead_end_ratio = random.random() * 0.45
    dead_ends = open_cells * dead_end_ratio

    features = {
        "size": size,
        "wallDensity": wall_density,
        "distance": distance,
        "openCells": open_cells,
        "deadEnds": dead_ends,
    }

    score = (
        0.32 * _norm(size, RANGES["size"])
        + 0.16 * wall_density
        + 0.30 * _norm(distance, RANGES["distance"])
        + 0.22 * dead_end_ratio
        + (random.random() * 0.1 - 0.05)  # small label noise
    )


    if score < 0.35:
        label = 0
    elif score < 0.62:
        label = 1
    else:
        label = 2

    return features, label


def _generate_balanced_samples(sample_count):
  
    target_per_label = sample_count // len(LABELS)
    counts = {0: 0, 1: 0, 2: 0}
    samples = []

    while len(samples) < target_per_label * len(LABELS):
        features, label = _generate_sample()
        if counts[label] >= target_per_label:
            continue
        counts[label] += 1
        samples.append((features, label))

    random.shuffle(samples)
    return samples
  

def build_and_train(on_progress=None, sample_count=900, epochs=60, test_size=0.2):
    samples = _generate_balanced_samples(sample_count)
    xs = np.array([to_input_vector(f) for f, _ in samples])
    ys = np.array([label for _, label in samples])

    xs_train, xs_test, ys_train, ys_test = train_test_split(
        xs, ys, test_size=test_size, random_state=42, stratify=ys
    )

    model = MLPClassifier(
        hidden_layer_sizes=(16, 8),
        activation="relu",
        solver="adam",
        learning_rate_init=0.01,
        max_iter=1,
        warm_start=True,
        random_state=42,
    )

    log = []
    for epoch in range(1, epochs + 1):
        model.fit(xs_train, ys_train)
        loss = model.loss_
        train_acc = float((model.predict(xs_train) == ys_train).mean())
        entry = {"epoch": epoch, "totalEpochs": epochs, "loss": loss, "acc": train_acc}
        log.append(entry)
        if on_progress:
            on_progress(entry)
    test_preds = model.predict(xs_test)
    test_accuracy = float((test_preds == ys_test).mean())
    cm = confusion_matrix(ys_test, test_preds, labels=[0, 1, 2]).tolist()

    evaluation = {
        "testAccuracy": test_accuracy,
        "testSetSize": int(len(ys_test)),
        "trainSetSize": int(len(ys_train)),
        "labels": LABELS,
        "confusionMatrix": cm,  
    }

    return model, log, evaluation


def predict(model, features):
    x = np.array([to_input_vector(features)])
    probs = model.predict_proba(x)[0]
    max_idx = int(np.argmax(probs))

    return {
        "label": LABELS[max_idx],
        "confidence": float(probs[max_idx]),
        "probabilities": {
            "EASY": float(probs[0]),
            "MEDIUM": float(probs[1]),
            "HARD": float(probs[2]),
        },
    }
