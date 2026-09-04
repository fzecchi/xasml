import logging

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
)

logger = logging.getLogger(__name__)

# Sequential colormap that matches the violet line-plot colour (#832db6).
DEFAULT_CM_CMAP = LinearSegmentedColormap.from_list(
    "white_violet", ["#ffffff", "#832db6"]
)


def calculate_accuracies(y_test, y_pred):
    unique_classes = sorted(set(y_test))
    accuracies = {}
    accuracies["accuracy"] = accuracy_score(y_test, y_pred)
    accuracies["balanced"] = balanced_accuracy_score(y_test, y_pred)
    for unique_class in unique_classes:
        accuracies[unique_class] = accuracy_score(
            y_test[y_test == unique_class], y_pred[y_test == unique_class]
        )

    logger.info(f"Balanced accuracy: {accuracies['balanced'] * 100:.1f}%")
    for cls in unique_classes:
        logger.info(f"  {cls}: {accuracies[cls] * 100:.1f}%")
    return accuracies


def display_metrics(
    y_test: np.ndarray,
    y_pred: np.ndarray,
    display_labels: list[str] | None = None,
    cm_name: str | list[str] | tuple[str, ...] | None = None,
    normalize: str | None = None,
    cmap=DEFAULT_CM_CMAP,
    **kwargs,
):
    """Compute classification metrics and (optionally) save a confusion matrix.

    Args:
        y_test: True labels.
        y_pred: Predicted labels.
        display_labels: Labels used to annotate the confusion matrix axes.
        cm_name: Output path for the confusion-matrix figure. A single string
            saves one file; an iterable of strings saves to each path, so
            ``cm_name=["cm.png", "cm.pdf"]`` writes both a raster and a vector
            copy in one call.
        normalize: Normalization mode forwarded to
            :func:`sklearn.metrics.confusion_matrix`. Defaults to ``None``
            (raw counts). Pass ``"true"`` for row-normalised fractions.
        cmap: Colormap used for the confusion-matrix cells. Defaults to a
            sequential white-to-violet colormap that matches the line-plot
            palette used elsewhere in the manuscript.
        **kwargs: Forwarded to :meth:`matplotlib.figure.Figure.savefig`.
    """
    n_test = len(y_test)
    n_classes = len(set(y_test))
    logger.debug(
        f"Evaluating predictions on {n_test} samples across {n_classes} classes."
    )

    accuracies = calculate_accuracies(y_test, y_pred)

    f1 = f1_score(y_test, y_pred, average="weighted")

    logger.info(f"Accuracy: {accuracies['accuracy'] * 100:.1f}%")
    logger.info(f"F1 score: {f1 * 100:.1f}%")

    cm = confusion_matrix(y_test, y_pred, normalize=normalize)
    cmd = ConfusionMatrixDisplay(cm, display_labels=display_labels)
    values_format = ".1%" if normalize is not None else "d"

    fig, ax = plt.subplots(figsize=(3.5, 3.5))
    cmd.plot(
        ax=ax, colorbar=False, values_format=values_format, cmap=cmap,
    )
    ax.set(ylabel="True coordination", xlabel="Predicted coordination")
    ax.tick_params(length=0)
    fig.tight_layout()
    if cm_name is not None:
        # Save at the exact 3.5x3.5 figure size for a consistent CM footprint
        # across the manuscript. Callers may pass bbox_inches="tight" to override.
        bbox_inches = kwargs.pop("bbox_inches", None)
        paths = [cm_name] if isinstance(cm_name, str) else list(cm_name)
        for path in paths:
            fig.savefig(path, bbox_inches=bbox_inches, **kwargs)
            logger.debug(f"Confusion matrix saved to {path}.")

    return accuracies
