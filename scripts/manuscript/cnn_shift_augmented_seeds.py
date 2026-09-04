"""Test CNN shift augmentation across model initialization seeds."""

import argparse
import os

os.environ["KERAS_BACKEND"] = "torch"
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "0"

import keras
import numpy as np
from cnn_shift_seeds import (
    ENERGY_MAX,
    ENERGY_MIN,
    ENERGY_SHIFT,
    LABELS,
    OUTLIER_THRESHOLD,
    SEEDS,
    SHIFTS,
    SPLIT_SEED,
    X,
    build_model,
    evaluate_model_on_shifts,
    label_encoder,
    metas,
    prepare,
    print_summary,
    y,
)
from keras import callbacks
from sklearn.utils import class_weight

from xasml.models.data import Processor

AUGMENT_FRACTION = 2 / 3
AUGMENT_SHIFT_RANGE = (-1.5, 1.5)
AUGMENT_TRAIN_SEED = 42
AUGMENT_VAL_SEED = 43


def prepare_augmented():
    """Reproduce the shift-augmented data pipeline from the current notebook."""
    processor = Processor(X, y, metas=metas)
    processor.reset()
    processor.select_labels(LABELS, randomize=True, random_seed=SPLIT_SEED)
    processor.y = np.array(label_encoder.transform(processor.y))

    energies_full = np.copy(processor.metas[0]["energies"]) + ENERGY_SHIFT
    features_full = np.copy(processor.X)
    mask = processor.trim(ENERGY_MIN, ENERGY_MAX, reference=energies_full)
    energies = energies_full[mask]
    keep = processor.remove_outliers(threshold=OUTLIER_THRESHOLD)
    processor.set_features("all", features_full[keep])

    processor.split(
        test_size=0.15,
        val_size=0.15,
        random_seed=SPLIT_SEED,
        shuffle=True,
        stratify=True,
    )

    processor.trim(ENERGY_MIN, ENERGY_MAX, reference=energies_full, subset="test")
    processor.normalize(method="area", reference=energies, subset="test")

    augment_kwargs = {
        "fraction": AUGMENT_FRACTION,
        "shift_range": AUGMENT_SHIFT_RANGE,
        "snr_range": None,
        "normalization": None,
    }
    processor.augment(
        energies=energies_full,
        random_seed=AUGMENT_TRAIN_SEED,
        **augment_kwargs,
    )
    processor.augment(
        energies=energies_full,
        random_seed=AUGMENT_VAL_SEED,
        subset="val",
        **augment_kwargs,
    )

    for subset in ("train", "val"):
        processor.trim(
            ENERGY_MIN,
            ENERGY_MAX,
            reference=energies_full,
            subset=subset,
        )
        processor.normalize(method="area", reference=energies, subset=subset)

    return processor


def run(seeds):
    """Train and evaluate the augmented CNN for each requested seed."""
    print("Preparing the fixed augmented training and validation sets", flush=True)
    processor = prepare_augmented()
    shift_processors = {shift: prepare(shift) for shift in SHIFTS}

    classes = np.unique(processor.y_train)
    weights = class_weight.compute_class_weight(
        "balanced", classes=classes, y=processor.y_train
    )
    class_weights = dict(zip(classes, weights))

    print(f"Training shape: {processor.X_train.shape}")
    print(f"Validation shape: {processor.X_val.shape}")
    print(f"Class weights: {class_weights}")

    all_results = []
    for seed in seeds:
        keras.backend.clear_session()
        keras.utils.set_random_seed(seed)
        print(f"Training augmented seed {seed}...", end=" ", flush=True)

        model = build_model(processor.X_train.shape[1])
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
            processor.X_train,
            processor.y_train,
            validation_data=(processor.X_val, processor.y_val),
            epochs=512,
            batch_size=32,
            callbacks=[early_stopping, reduce_lr],
            class_weight=class_weights,
            verbose=0,
        )
        print(f"{len(history.history['loss'])} epochs")

        results = evaluate_model_on_shifts(model, shift_processors)
        all_results.append((seed, results))
        values = " | ".join(
            f"{shift:+.1f}: {results[shift]['balanced']:.1f}% / "
            f"{results[shift]['T:4']:.1f}%"
            for shift in SHIFTS
        )
        print(f"Seed {seed}: {values}", flush=True)

    print_summary(all_results, "AUGMENTED MODEL STATISTICS")
    return all_results


def parse_args():
    """Parse model seeds from the command line."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--seeds",
        nargs="+",
        type=int,
        default=SEEDS,
        help="Model initialization seeds. Defaults to the baseline seed list.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run(args.seeds)
