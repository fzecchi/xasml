"""Multi-seed check of the CNN energy-shift asymmetry.

Retrains the CNN architecture from multiple random seeds, keeping the stratified
data split fixed, and reports balanced accuracy and per-class recall across all five
rigid energy shifts (-1.0, -0.5, 0.0, +0.5, +1.0 eV).
"""

import os

os.environ["KERAS_BACKEND"] = "torch"
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "0"

import keras
import numpy as np
from keras import callbacks, layers, models
from sklearn.preprocessing import LabelEncoder
from sklearn.utils import class_weight

from xasml import resource_path
from xasml.models.data import Processor
from xasml.models.io import read_from_h5
from xasml.models.metrics import calculate_accuracies

SPLIT_SEED = 42
SEEDS = [42, 0, 1, 2, 3, 4, 5, 6, 7, 8, 81, 13]
SHIFTS = [-1.0, -0.5, 0.0, 0.5, 1.0]
ENERGY_SHIFT = 7112
ENERGY_MIN, ENERGY_MAX = -10 + ENERGY_SHIFT, 60 + ENERGY_SHIFT
LABELS = ["O:6", "T:4"]
OUTLIER_THRESHOLD = 4

X, y, metas = read_from_h5(
    resource_path("xasml:datasets/fdmnes/materials.h5"), "Fe", "job15"
)
label_encoder = LabelEncoder().fit(np.array(LABELS))


def prepare(shift=0.0):
    """Prepare processor for a given shift with stratified splitting."""
    p = Processor(X, y, metas=metas)
    p.reset()
    p.select_labels(LABELS, randomize=True, random_seed=SPLIT_SEED)
    p.y = np.array(label_encoder.transform(p.y))
    energies = p.metas[0]["energies"] + ENERGY_SHIFT
    if shift:
        p.shift(shift, reference=energies)
    mask = p.trim(ENERGY_MIN, ENERGY_MAX, reference=energies)
    p.remove_outliers(threshold=OUTLIER_THRESHOLD)
    p.normalize(method="area", reference=energies[mask])
    p.split(
        test_size=0.15,
        val_size=0.15,
        random_seed=SPLIT_SEED,
        shuffle=True,
        stratify=True,
    )
    return p


def build_model(input_dim):
    """Build the standard 4-block CNN classifier architecture."""
    conv_kw = {
        "activation": "relu",
        "padding": "same",
        "kernel_initializer": "he_normal",
    }
    dense_kw = {"activation": "relu", "kernel_initializer": "he_normal"}
    model = models.Sequential(name="cnn_seed_eval")
    model.add(layers.Input(shape=(input_dim,)))
    model.add(layers.Reshape((input_dim, 1)))
    for filters in (8, 16, 32, 64):
        model.add(layers.Conv1D(filters, 3, **conv_kw))
        model.add(layers.Conv1D(filters, 3, **conv_kw))
        model.add(layers.MaxPooling1D(2))
    model.add(layers.Flatten())
    model.add(layers.Dense(64, **dense_kw))
    model.add(layers.Dropout(0.2))
    model.add(layers.Dense(32, **dense_kw))
    model.add(layers.Dropout(0.2))
    model.add(layers.Dense(1, activation="sigmoid"))
    return model


def evaluate_model_on_shifts(model, shift_processors):
    """Evaluate a trained model across all pre-computed shift test sets."""
    results = {}
    for s, proc in shift_processors.items():
        probs = model.predict(proc.X_test, verbose=0).ravel()
        preds = (probs >= 0.5).astype(int)
        y_true = label_encoder.inverse_transform(proc.y_test)
        y_pred = label_encoder.inverse_transform(preds)
        accs = calculate_accuracies(y_true, y_pred)
        results[s] = {
            "balanced": accs["balanced"] * 100,
            "O:6": accs["O:6"] * 100,
            "T:4": accs["T:4"] * 100,
        }
    return results


def is_one_class_prediction(results):
    """Return whether the clean test predictions contain only one class."""
    clean_recalls = (results[0.0]["O:6"], results[0.0]["T:4"])
    return sorted(clean_recalls) == [0.0, 100.0]


def print_summary(all_results, title):
    """Print absolute metrics, paired losses, and shift asymmetry."""
    count = len(all_results)
    seed_label = "SEED" if count == 1 else "SEEDS"
    print(f"\n=== {title} ACROSS {count} {seed_label} ===")
    for s in SHIFTS:
        bals = [r[s]["balanced"] for _, r in all_results]
        o6s = [r[s]["O:6"] for _, r in all_results]
        t4s = [r[s]["T:4"] for _, r in all_results]
        print(
            f"Shift {s:+4.1f} eV: Balanced = {np.mean(bals):5.1f} +/- {np.std(bals):4.1f}% | "
            f"O:6 = {np.mean(o6s):5.1f} +/- {np.std(o6s):4.1f}% | "
            f"T:4 = {np.mean(t4s):5.1f} +/- {np.std(t4s):4.1f}%"
        )

    print("\n=== PAIRED LOSS RELATIVE TO THE CLEAN TEST SET ===")
    for s in (shift for shift in SHIFTS if shift != 0.0):
        balanced_losses = [
            r[0.0]["balanced"] - r[s]["balanced"] for _, r in all_results
        ]
        t4_losses = [r[0.0]["T:4"] - r[s]["T:4"] for _, r in all_results]
        print(
            f"Shift {s:+4.1f} eV: Balanced loss = "
            f"{np.mean(balanced_losses):5.1f} +/- {np.std(balanced_losses):4.1f} points | "
            f"T:4 loss = {np.mean(t4_losses):5.1f} +/- {np.std(t4_losses):4.1f} points"
        )

    worse_at_neg = sum(
        1 for _, r in all_results if r[-1.0]["balanced"] < r[1.0]["balanced"]
    )
    t4_worse_at_neg = sum(1 for _, r in all_results if r[-1.0]["T:4"] < r[1.0]["T:4"])
    print(f"\n-1.0 eV yields lower Balanced Accuracy in {worse_at_neg}/{count} seeds")
    print(f"-1.0 eV yields lower T:4 Recall in {t4_worse_at_neg}/{count} seeds")


def main():
    print(f"Preparing datasets for shifts: {SHIFTS}")
    base_proc = prepare(0.0)
    shift_procs = {s: prepare(s) for s in SHIFTS}

    classes = np.unique(base_proc.y_train)
    weights = class_weight.compute_class_weight(
        "balanced", classes=classes, y=base_proc.y_train
    )
    class_weights = dict(zip(classes, weights))

    all_results = []
    table_width = 132
    print("\n" + "=" * table_width)
    print(
        f"{'Seed':>5} | {'-1.0 eV (Bal / T:4)':>20} | {'-0.5 eV (Bal / T:4)':>20} |"
        f" {'0.0 eV (Bal / T:4)':>20} | {'+0.5 eV (Bal / T:4)':>20} |"
        f" {'+1.0 eV (Bal / T:4)':>20}"
    )
    print("-" * table_width)

    for seed in SEEDS:
        keras.backend.clear_session()
        keras.utils.set_random_seed(seed)
        print(f"Training seed {seed}...", end=" ", flush=True)
        model = build_model(base_proc.X_train.shape[1])
        model.compile(
            loss="binary_crossentropy",
            optimizer=keras.optimizers.Adam(learning_rate=1e-4),
            metrics=["accuracy"],
        )
        early_stopping = callbacks.EarlyStopping(
            monitor="val_loss", patience=32, restore_best_weights=True
        )
        reduce_lr = callbacks.ReduceLROnPlateau(
            monitor="val_loss", factor=0.5, patience=16, min_lr=1e-6
        )

        history = model.fit(
            base_proc.X_train,
            base_proc.y_train,
            validation_data=(base_proc.X_val, base_proc.y_val),
            epochs=512,
            batch_size=32,
            callbacks=[early_stopping, reduce_lr],
            class_weight=class_weights,
            verbose=0,
        )
        print(f"{len(history.history['loss'])} epochs", flush=True)

        res = evaluate_model_on_shifts(model, shift_procs)
        all_results.append((seed, res))

        m10_b, m10_t = res[-1.0]["balanced"], res[-1.0]["T:4"]
        m05_b, m05_t = res[-0.5]["balanced"], res[-0.5]["T:4"]
        z00_b, z00_t = res[0.0]["balanced"], res[0.0]["T:4"]
        p05_b, p05_t = res[0.5]["balanced"], res[0.5]["T:4"]
        p10_b, p10_t = res[1.0]["balanced"], res[1.0]["T:4"]

        print(
            f"{seed:5d} | {m10_b:5.1f}% / {m10_t:5.1f}%     |"
            f" {m05_b:5.1f}% / {m05_t:5.1f}%     |"
            f" {z00_b:5.1f}% / {z00_t:5.1f}%     |"
            f" {p05_b:5.1f}% / {p05_t:5.1f}%     |"
            f" {p10_b:5.1f}% / {p10_t:5.1f}%"
        )

    print("=" * table_width)
    collapsed_seeds = [
        seed for seed, results in all_results if is_one_class_prediction(results)
    ]
    print_summary(all_results, "SUMMARY STATISTICS")
    if collapsed_seeds:
        non_collapsed_results = [
            item for item in all_results if item[0] not in collapsed_seeds
        ]
        print_summary(non_collapsed_results, "NON-COLLAPSED MODEL STATISTICS")
    print(f"Clean-set one-class predictions: {collapsed_seeds or 'none'}")

    return all_results


if __name__ == "__main__":
    main()
