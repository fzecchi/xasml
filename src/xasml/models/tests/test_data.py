import numpy as np
import pytest
from pymatgen.core import Lattice, Structure

from xasml.models.data import (
    Processor,
    add_poisson_noise,
    normalize_features,
    shift_features,
)
from xasml.models.fluorescence import create_binder

test_size = 0.2
random_seed = 13


# ---------------------------------------------------------------------------
# shift_features
# ---------------------------------------------------------------------------


def test_shift_features_right():
    X = np.array([[1, 2, 3, 4, 5]])
    result = shift_features(X, 2)
    expected = np.array([[1, 1, 1, 2, 3]])
    assert np.array_equal(result, expected)


def test_shift_features_left():
    X = np.array([[1, 2, 3, 4, 5]])
    result = shift_features(X, -2)
    expected = np.array([[3, 4, 5, 5, 5]])
    assert np.array_equal(result, expected)


def test_shift_features_preserves_shape():
    X = np.random.default_rng(42).random((10, 50))
    for nids in [-5, -1, 1, 5]:
        result = shift_features(X, nids)
        assert result.shape == X.shape


def test_shift_features_does_not_modify_input():
    X = np.array([[1.0, 2.0, 3.0, 4.0]])
    X_copy = X.copy()
    shift_features(X, 2)
    assert np.array_equal(X, X_copy)


def test_shift_features_by_one_right():
    X = np.array([[10, 20, 30]])
    result = shift_features(X, 1)
    expected = np.array([[10, 10, 20]])
    assert np.array_equal(result, expected)


def test_shift_features_by_one_left():
    X = np.array([[10, 20, 30]])
    result = shift_features(X, -1)
    expected = np.array([[20, 30, 30]])
    assert np.array_equal(result, expected)


def test_shift_features_multiple_rows():
    X = np.array([[1, 2, 3, 4], [5, 6, 7, 8]])
    result = shift_features(X, 1)
    expected = np.array([[1, 1, 2, 3], [5, 5, 6, 7]])
    assert np.array_equal(result, expected)


# ---------------------------------------------------------------------------
# add_poisson_noise
# ---------------------------------------------------------------------------


def test_add_poisson_noise_preserves_shape():
    X = np.ones((5, 20))
    rng = np.random.default_rng(42)
    result = add_poisson_noise(X, rng, counts_per_intensity=10000)
    assert result.shape == X.shape


def test_add_poisson_noise_achieves_reference_snr():
    snr = 20
    reference_intensity = 0.03
    X = np.full((2000, 1000), reference_intensity)
    noisy = add_poisson_noise(
        X,
        np.random.default_rng(42),
        snr=snr,
        reference_intensity=reference_intensity,
    )
    achieved_snr = reference_intensity / np.std(noisy - X)
    assert achieved_snr == pytest.approx(snr, rel=0.01)


def test_add_poisson_noise_high_counts_close_to_original():
    X = np.ones((3, 100))
    rng = np.random.default_rng(42)
    result = add_poisson_noise(X, rng, counts_per_intensity=1e8)
    assert np.allclose(result, X, atol=0.01)


def test_add_poisson_noise_reproducible():
    X = np.ones((3, 50))
    r1 = add_poisson_noise(X, np.random.default_rng(0), counts_per_intensity=100)
    r2 = add_poisson_noise(X, np.random.default_rng(0), counts_per_intensity=100)
    assert np.array_equal(r1, r2)


def test_add_poisson_noise_does_not_modify_input():
    X = np.ones((2, 10))
    X_copy = X.copy()
    add_poisson_noise(X, np.random.default_rng(0), counts_per_intensity=100)
    assert np.array_equal(X, X_copy)


def test_add_poisson_noise_non_negative():
    X = np.ones((5, 30))
    result = add_poisson_noise(X, np.random.default_rng(42), counts_per_intensity=100)
    assert np.all(result >= 0)


# ---------------------------------------------------------------------------
# normalize_features
# ---------------------------------------------------------------------------


def test_normalize_features_min_max():
    X = np.array([[1.0, 2.0, 3.0, 4.0, 5.0]])
    result = normalize_features(X, "min-max")
    assert np.isclose(result.min(), 0.0)
    assert np.isclose(result.max(), 1.0)


def test_normalize_features_z_score():
    X = np.array([[10.0, 20.0, 30.0, 40.0, 50.0]])
    result = normalize_features(X, "z-score")
    assert np.isclose(result.mean(), 0.0, atol=1e-10)
    assert np.isclose(result.std(), 1.0, atol=1e-10)


def test_normalize_features_area():
    energies = np.array([0.0, 1.0, 2.0, 3.0])
    X = np.array([[2.0, 2.0, 2.0, 2.0]])
    result = normalize_features(X, "area", energies)
    area = np.trapezoid(result[0], energies)
    assert np.isclose(area, 1.0)


def test_normalize_features_invalid_method():
    X = np.array([[1.0, 2.0]])
    with pytest.raises(ValueError, match="Invalid normalization method"):
        normalize_features(X, "invalid")


def test_normalize_features_preserves_shape():
    X = np.random.default_rng(42).random((5, 20)) + 0.1
    for method in ["min-max", "z-score"]:
        assert normalize_features(X, method).shape == X.shape


def test_normalize_features_does_not_modify_input():
    X = np.array([[1.0, 2.0, 3.0]])
    X_copy = X.copy()
    normalize_features(X, "min-max")
    assert np.array_equal(X, X_copy)


def test_normalize_features_multiple_rows_min_max():
    X = np.array([[1.0, 5.0], [10.0, 20.0]])
    result = normalize_features(X, "min-max")
    assert np.allclose(result, [[0.0, 1.0], [0.0, 1.0]])


# ---------------------------------------------------------------------------
# Processor.split / Processor.trim (existing tests)
# ---------------------------------------------------------------------------


def test_split():
    X = np.array([[1, 2, 3, 4, 5], [6, 7, 8, 9, 10], [11, 12, 13, 14, 15]])
    y = np.array([0, 1, 0])

    processor = Processor(X, y)
    processor.split(test_size, stratify=False, random_seed=random_seed)

    X_train, X_test = processor.X_train, processor.X_test
    y_train, y_test = processor.y_train, processor.y_test

    assert X_train.shape == (2, 5)
    assert np.all(X_train == np.array([[1, 2, 3, 4, 5], [11, 12, 13, 14, 15]]))
    assert X_test.shape == (1, 5)
    assert np.all(X_test == np.array([[6, 7, 8, 9, 10]]))
    assert y_train.shape == (2,)
    assert np.all(y_train == np.array([0, 0]))
    assert y_test.shape == (1,)
    assert np.all(y_test == np.array([1]))


def test_split_validation_size_is_fraction_of_complete_dataset():
    X = np.arange(500).reshape(100, 5)
    y = np.array([0] * 70 + [1] * 30)

    processor = Processor(X, y)
    processor.split(test_size=0.15, val_size=0.15, random_seed=random_seed)

    assert processor.X_train.shape == (70, 5)
    assert processor.X_val.shape == (15, 5)
    assert processor.X_test.shape == (15, 5)


def test_split_can_stratify_validation_and_test_sets():
    X = np.arange(500).reshape(100, 5)
    y = np.array([0] * 70 + [1] * 30)

    processor = Processor(X, y)
    processor.split(
        test_size=0.15,
        val_size=0.15,
        stratify=True,
        random_seed=random_seed,
    )

    assert np.mean(processor.y_train) == pytest.approx(0.3)
    assert np.mean(processor.y_val) == pytest.approx(0.3, abs=0.04)
    assert np.mean(processor.y_test) == pytest.approx(0.3, abs=0.04)


def test_trim():
    X = np.array([[1, 2, 3, 4, 5], [6, 7, 8, 9, 10], [11, 12, 13, 14, 15]])
    y = np.array([0, 1, 0])

    processor = Processor(X, y)
    processor.split(test_size, stratify=False, random_seed=random_seed)

    processor.trim(left=1, right=3, subset="all")

    X_trimmed = processor.X
    assert X_trimmed.shape == (3, 2)
    assert np.all(X_trimmed == np.array([[2, 3], [7, 8], [12, 13]]))


def test_add_incident_beam_self_absorption(fe2o3):
    energies = np.array([7000.0, 7100.0, 7200.0, 7300.0])
    X = np.ones((2, len(energies)))
    y = np.array([0, 1])

    metas = [
        {"energies": energies, "structure": fe2o3},
        {"energies": energies, "structure": fe2o3},
    ]
    processor = Processor(X, y, metas=metas)

    X_before = np.copy(processor.X)

    processor.add_incident_beam_self_absorption(
        binder=create_binder("boron nitride"),
        absorbing_element="Fe",
        compound_weight_fraction=0.1,
        phi=45.0,
        theta=45.0,
        thickness=0.1,
    )

    assert processor.X.shape == X_before.shape
    assert np.all(processor.X > 0)
    assert not np.allclose(processor.X, X_before)


def test_split_preserves_metas():
    X = np.array(
        [[1, 2, 3, 4, 5], [6, 7, 8, 9, 10], [11, 12, 13, 14, 15], [16, 17, 18, 19, 20]]
    )
    y = np.array([0, 1, 0, 1])

    metas = []
    for i in range(4):
        metas.append(
            {
                "structure": Structure(
                    Lattice.cubic(3.0 + i),
                    ["Fe"],
                    [[0.0, 0.0, 0.0]],
                ),
                "material_id": f"mp-{i}",
            }
        )

    processor = Processor(X, y, metas=metas)
    processor.split(test_size=0.5, random_seed=random_seed)

    m_train = processor.metas_train
    m_test = processor.metas_test

    assert len(m_train) + len(m_test) == len(metas)

    original_params = [m["structure"].lattice.a for m in metas]
    split_params = [m["structure"].lattice.a for m in m_train] + [
        m["structure"].lattice.a for m in m_test
    ]
    assert sorted(split_params) == sorted(original_params)


# ---------------------------------------------------------------------------
# Processor.shift
# ---------------------------------------------------------------------------


def test_processor_shift_right_by_index():
    X = np.array([[1.0, 2.0, 3.0, 4.0, 5.0]])
    processor = Processor(X, np.array([0]))
    processor.shift(2)
    expected = np.array([[1.0, 1.0, 1.0, 2.0, 3.0]])
    assert np.array_equal(processor.X, expected)


def test_processor_shift_left_by_index():
    X = np.array([[1.0, 2.0, 3.0, 4.0, 5.0]])
    processor = Processor(X, np.array([0]))
    processor.shift(-2)
    expected = np.array([[3.0, 4.0, 5.0, 5.0, 5.0]])
    assert np.array_equal(processor.X, expected)


def test_processor_shift_zero():
    X = np.array([[1.0, 2.0, 3.0]])
    processor = Processor(X, np.array([0]))
    processor.shift(0)
    assert np.array_equal(processor.X, X)


def test_processor_shift_with_reference():
    X = np.array([[1.0, 2.0, 3.0, 4.0, 5.0]])
    reference = np.array([0.0, 1.0, 2.0, 3.0, 4.0])
    processor = Processor(X, np.array([0]))
    processor.shift(1.0, reference=reference)
    expected = np.array([[1.0, 1.0, 2.0, 3.0, 4.0]])
    assert np.array_equal(processor.X, expected)


def test_processor_shift_on_subset():
    X = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]])
    y = np.array([0, 1, 0])
    processor = Processor(X, y)
    processor.split(test_size=0.34, stratify=False, random_seed=random_seed)
    X_test_before = processor.X_test.copy()
    processor.shift(1, subset="train")
    assert np.array_equal(processor.X_test, X_test_before)


def test_processor_shift_reference_length_mismatch():
    X = np.array([[1.0, 2.0, 3.0]])
    reference = np.array([0.0, 1.0])
    processor = Processor(X, np.array([0]))
    with pytest.raises(ValueError, match="reference length"):
        processor.shift(1.0, reference=reference)


# ---------------------------------------------------------------------------
# Processor.normalize
# ---------------------------------------------------------------------------


def test_processor_normalize_min_max():
    X = np.array([[1.0, 3.0, 5.0], [2.0, 4.0, 8.0]])
    processor = Processor(X, np.array([0, 1]))
    processor.normalize(method="min-max")
    assert np.isclose(processor.X[0].min(), 0.0)
    assert np.isclose(processor.X[0].max(), 1.0)
    assert np.isclose(processor.X[1].min(), 0.0)
    assert np.isclose(processor.X[1].max(), 1.0)


def test_processor_normalize_z_score():
    X = np.array([[10.0, 20.0, 30.0]])
    processor = Processor(X, np.array([0]))
    processor.normalize(method="z-score")
    assert np.isclose(processor.X[0].mean(), 0.0, atol=1e-10)
    assert np.isclose(processor.X[0].std(), 1.0, atol=1e-10)


def test_processor_normalize_area():
    energies = np.array([0.0, 1.0, 2.0, 3.0])
    X = np.array([[2.0, 2.0, 2.0, 2.0]])
    processor = Processor(X, np.array([0]))
    processor.normalize(method="area", reference=energies)
    area = np.trapezoid(processor.X[0], energies)
    assert np.isclose(area, 1.0)


def test_processor_normalize_none():
    X = np.array([[1.0, 2.0, 3.0]])
    processor = Processor(X, np.array([0]))
    processor.normalize(method=None)
    assert np.array_equal(processor.X, X)


def test_processor_normalize_area_without_reference():
    X = np.array([[1.0, 2.0, 3.0]])
    processor = Processor(X, np.array([0]))
    with pytest.raises(ValueError, match="reference must be provided"):
        processor.normalize(method="area")


def test_processor_normalize_invalid_method():
    X = np.array([[1.0, 2.0, 3.0]])
    processor = Processor(X, np.array([0]))
    with pytest.raises(ValueError, match="Invalid normalization method"):
        processor.normalize(method="invalid")


def test_processor_normalize_subset():
    X = np.array([[1.0, 3.0, 5.0], [2.0, 4.0, 8.0], [3.0, 6.0, 9.0]])
    y = np.array([0, 1, 0])
    processor = Processor(X, y)
    processor.split(test_size=0.34, stratify=False, random_seed=random_seed)
    X_test_before = processor.X_test.copy()
    processor.normalize(method="min-max", subset="train")
    assert np.array_equal(processor.X_test, X_test_before)


# ---------------------------------------------------------------------------
# Processor.add_poisson_noise
# ---------------------------------------------------------------------------


def test_processor_add_poisson_noise_shape():
    X = np.ones((3, 20))
    processor = Processor(X, np.array([0, 1, 0]))
    processor.add_poisson_noise(counts_per_intensity=1000, random_seed=42)
    assert processor.X.shape == (3, 20)


def test_processor_add_poisson_noise_snr_shape():
    X = np.ones((3, 20))
    processor = Processor(X, np.array([0, 1, 0]))
    processor.add_poisson_noise(snr=100, reference_intensity=1.0, random_seed=42)
    assert processor.X.shape == (3, 20)


def test_processor_add_poisson_noise_snr_changes_data():
    X = np.ones((3, 50))
    processor = Processor(X, np.array([0, 1, 0]))
    X_before = processor.X.copy()
    processor.add_poisson_noise(snr=10, reference_intensity=1.0, random_seed=42)
    assert not np.array_equal(processor.X, X_before)


def test_processor_high_snr_close_to_original():
    X = np.ones((3, 100))
    processor = Processor(X, np.array([0, 1, 0]))
    processor.add_poisson_noise(snr=10000, reference_intensity=1.0, random_seed=42)
    assert np.allclose(processor.X, X, atol=0.01)


def test_processor_noise_on_subset():
    X = np.ones((6, 20))
    y = np.array([0, 1, 0, 1, 0, 1])
    processor = Processor(X, y)
    processor.split(test_size=0.34, stratify=False, random_seed=random_seed)
    X_train_before = processor.X_train.copy()
    processor.add_poisson_noise(
        snr=10, reference_intensity=1.0, subset="test", random_seed=42
    )
    assert np.array_equal(processor.X_train, X_train_before)


def test_processor_noise_methods_use_same_helper():
    """Both methods should produce the same result for equivalent params."""
    X = np.ones((3, 20))
    p1 = Processor(X.copy(), np.array([0, 1, 0]))
    p2 = Processor(X.copy(), np.array([0, 1, 0]))
    snr = 50
    p1.add_poisson_noise(snr=snr, reference_intensity=1.0, random_seed=7)
    p2.add_poisson_noise(counts_per_intensity=snr**2, random_seed=7)
    assert np.array_equal(p1.X, p2.X)


def test_processor_normalizes_after_noise():
    energies = np.linspace(-10, 60, 50)
    X = np.full((3, 50), 0.03)
    processor = Processor(X, np.array([0, 1, 0]))
    processor.add_poisson_noise(
        snr=20,
        reference_intensity=0.03,
        normalization="area",
        reference=energies,
        random_seed=42,
    )
    assert np.allclose(np.trapezoid(processor.X, energies, axis=1), 1.0)


# ---------------------------------------------------------------------------
# Processor.select_labels
# ---------------------------------------------------------------------------


def test_select_labels_basic():
    X = np.arange(20).reshape(4, 5).astype(float)
    y = np.array(["A", "B", "A", "C"])
    processor = Processor(X, y)
    processor.select_labels(["A", "B"])
    assert len(processor.y) == 3
    assert set(processor.y) == {"A", "B"}


def test_select_labels_with_ratios():
    X = np.arange(50).reshape(10, 5).astype(float)
    y = np.array(["A"] * 6 + ["B"] * 4)
    processor = Processor(X, y)
    processor.select_labels(["A", "B"], ratios=[1, 1])
    assert np.sum(processor.y == "A") == 4
    assert np.sum(processor.y == "B") == 4


def test_select_labels_on_subset():
    X = np.arange(30).reshape(6, 5).astype(float)
    y = np.array(["A", "B", "A", "B", "A", "B"])
    processor = Processor(X, y)
    processor.split(test_size=0.34, random_seed=random_seed)
    n_test_before = len(processor.y_test)
    processor.select_labels(["A"], subset="train")
    assert len(processor.y_test) == n_test_before


# ---------------------------------------------------------------------------
# Processor.reset
# ---------------------------------------------------------------------------


def test_reset_restores_original():
    X = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
    y = np.array([0, 1])
    processor = Processor(X, y)
    processor.normalize(method="min-max")
    assert not np.array_equal(processor.X, X)
    processor.reset()
    assert np.array_equal(processor.X, X)


def test_reset_train_subset():
    X = np.arange(15).reshape(3, 5).astype(float)
    y = np.array([0, 1, 0])
    processor = Processor(X, y)
    processor.split(test_size=0.34, stratify=False, random_seed=random_seed)
    X_train_orig = processor.X_train.copy()
    processor.normalize(method="min-max", subset="train")
    processor.reset(subset="train")
    assert np.array_equal(processor.X_train, X_train_orig)


# ---------------------------------------------------------------------------
# Processor.augment
# ---------------------------------------------------------------------------


@pytest.fixture()
def processor_with_split():
    """A processor with enough samples to augment, already split."""
    rng = np.random.default_rng(42)
    n_samples, n_features = 30, 50
    X = rng.random((n_samples, n_features)) + 0.1
    y = np.array(["A"] * 15 + ["B"] * 15)
    energies = np.linspace(7100, 7200, n_features)
    metas = [{"id": i} for i in range(n_samples)]
    processor = Processor(X, y, metas=metas)
    processor.split(test_size=0.2, random_seed=42)
    return processor, energies


def test_augment_increases_training_size(processor_with_split):
    processor, energies = processor_with_split
    n_train_before = len(processor.y_train)
    processor.augment(
        energies=energies,
        fraction=1 / 3,
        noise_reference_intensity=1.0,
        normalization="area",
        random_seed=42,
    )
    n_augmented = int(n_train_before * (1 / 3))
    assert len(processor.y_train) == n_train_before + n_augmented


def test_augment_validation_subset(processor_with_split):
    processor, energies = processor_with_split
    # Re-split to create a validation set, then augment only that subset.
    processor.split(test_size=0.2, val_size=0.2, random_seed=42)
    n_train_before = len(processor.y_train)
    n_val_before = len(processor.y_val)
    processor.augment(
        energies=energies,
        fraction=1 / 3,
        noise_reference_intensity=1.0,
        normalization="area",
        random_seed=42,
        subset="val",
    )
    # The validation set grows while the training set is left untouched.
    assert len(processor.y_val) == n_val_before + int(n_val_before * (1 / 3))
    assert len(processor.y_train) == n_train_before


def test_augment_shift_only(processor_with_split):
    processor, energies = processor_with_split
    n_train_before = len(processor.y_train)
    # Disabling noise and self-absorption leaves shift-only augmentation.
    processor.augment(
        energies=energies,
        fraction=1 / 3,
        snr_range=None,
        normalization="area",
        random_seed=42,
    )
    assert len(processor.y_train) == n_train_before + int(n_train_before * (1 / 3))


def test_augment_no_perturbation_enabled_raises(processor_with_split):
    processor, energies = processor_with_split
    with pytest.raises(ValueError, match="At least one perturbation"):
        processor.augment(energies=energies, shift_range=None, snr_range=None)


def test_augment_preserves_test_set(processor_with_split):
    processor, energies = processor_with_split
    X_test_before = processor.X_test.copy()
    y_test_before = processor.y_test.copy()
    processor.augment(energies=energies, noise_reference_intensity=1.0, random_seed=42)
    assert np.array_equal(processor.X_test, X_test_before)
    assert np.array_equal(processor.y_test, y_test_before)


def test_augment_labels_match(processor_with_split):
    processor, energies = processor_with_split
    processor.augment(energies=energies, noise_reference_intensity=1.0, random_seed=42)
    assert set(processor.y_train) <= {"A", "B"}


def test_augment_metas_length(processor_with_split):
    processor, energies = processor_with_split
    processor.augment(energies=energies, noise_reference_intensity=1.0, random_seed=42)
    assert len(processor.metas_train) == len(processor.y_train)


def test_augment_feature_columns_unchanged(processor_with_split):
    processor, energies = processor_with_split
    n_cols = processor.X_train.shape[1]
    processor.augment(energies=energies, noise_reference_intensity=1.0, random_seed=42)
    assert processor.X_train.shape[1] == n_cols


def test_augment_without_self_absorption(processor_with_split):
    processor, energies = processor_with_split
    n_train_before = len(processor.y_train)
    processor.augment(
        energies=energies,
        noise_reference_intensity=1.0,
        self_absorption_kwargs=None,
        random_seed=42,
    )
    n_augmented = int(n_train_before * (1 / 3))
    assert len(processor.y_train) == n_train_before + n_augmented


def test_augment_no_normalization(processor_with_split):
    processor, energies = processor_with_split
    processor.augment(
        energies=energies,
        noise_reference_intensity=1.0,
        normalization=None,
        random_seed=42,
    )
    assert processor.X_train.shape[0] > 0


def test_augment_reproducible(processor_with_split):
    processor, energies = processor_with_split
    X_train_orig = processor.X_train.copy()
    y_train_orig = processor.y_train.copy()

    processor.augment(energies=energies, noise_reference_intensity=1.0, random_seed=99)
    X_after_1 = processor.X_train.copy()

    # Reset train to original and augment again.
    processor.X_train = X_train_orig.copy()
    processor.y_train = y_train_orig.copy()
    processor.metas_train = [{"id": i} for i in range(len(y_train_orig))]
    processor.augment(energies=energies, noise_reference_intensity=1.0, random_seed=99)
    X_after_2 = processor.X_train.copy()

    assert np.array_equal(X_after_1, X_after_2)


def test_augment_fraction(processor_with_split):
    processor, energies = processor_with_split
    n_train = len(processor.y_train)
    fraction = 0.5
    processor.augment(
        energies=energies,
        fraction=fraction,
        noise_reference_intensity=1.0,
        random_seed=42,
    )
    expected = n_train + int(n_train * fraction)
    assert len(processor.y_train) == expected


def test_augment_with_self_absorption(fe2o3):
    n_features = 50
    energies = np.linspace(7000, 7200, n_features)
    rng = np.random.default_rng(42)
    X = rng.random((10, n_features)) + 0.1
    y = np.array(["A"] * 5 + ["B"] * 5)
    metas = [{"structure": fe2o3} for _ in range(10)]

    processor = Processor(X, y, metas=metas)
    processor.split(test_size=0.2, random_seed=42)
    n_train_before = len(processor.y_train)

    processor.augment(
        energies=energies,
        fraction=1 / 3,
        noise_reference_intensity=1.0,
        self_absorption_kwargs={
            "binder": "boron nitride",
            "absorbing_element": "Fe",
            "compound_weight_fraction": (0.05, 0.2),
            "phi": 45,
            "theta": 45,
            "thickness": (0.05, 0.2),
        },
        normalization="area",
        random_seed=42,
    )

    n_augmented = int(n_train_before * (1 / 3))
    assert len(processor.y_train) == n_train_before + n_augmented
    assert processor.X_train.shape[1] == n_features
    assert np.all(np.isfinite(processor.X_train))


# ---------------------------------------------------------------------------
# Processor.remove_outliers
# ---------------------------------------------------------------------------


def test_remove_outliers_removes_extreme_spectrum():
    # Many similar spectra plus one clear outlier so that the outlier
    # exceeds the mean ± threshold * std envelope.
    n = 20
    X_normal = np.tile([1.0, 2.0, 3.0], (n, 1))
    X_outlier = np.array([[1.0, 2.0, 300.0]])
    X = np.vstack([X_normal, X_outlier])
    y = np.array(["A"] * n + ["B"])
    processor = Processor(X, y)
    keep = processor.remove_outliers(threshold=2.5)
    assert keep.sum() == n
    assert processor.X.shape[0] == n
    assert len(processor.y) == n


def test_remove_outliers_keeps_all_when_no_outlier():
    rng = np.random.default_rng(42)
    X = rng.normal(loc=5.0, scale=0.01, size=(20, 10))
    y = np.array(["A"] * 10 + ["B"] * 10)
    processor = Processor(X, y)
    keep = processor.remove_outliers(threshold=5.0)
    assert keep.all()
    assert processor.X.shape[0] == 20


def test_remove_outliers_updates_metas():
    n = 20
    X_normal = np.tile([1.0, 2.0], (n, 1))
    X_outlier = np.array([[1.0, 500.0]])
    X = np.vstack([X_normal, X_outlier])
    y = np.array(["A"] * n + ["B"])
    metas = [{"id": i} for i in range(n + 1)]
    processor = Processor(X, y, metas=metas)
    processor.remove_outliers(threshold=2.0)
    assert len(processor.metas) == n
    assert all(m["id"] != n for m in processor.metas)


def test_remove_outliers_on_subset():
    X = np.arange(30).reshape(6, 5).astype(float)
    y = np.array(["A", "B", "A", "B", "A", "B"])
    processor = Processor(X, y)
    processor.split(test_size=0.34, random_seed=random_seed)
    X_test_before = processor.X_test.copy()
    processor.remove_outliers(threshold=2.5, subset="train")
    assert np.array_equal(processor.X_test, X_test_before)


def test_remove_outliers_returns_boolean_mask():
    X = np.ones((5, 3))
    y = np.array(["A"] * 5)
    processor = Processor(X, y)
    keep = processor.remove_outliers(threshold=2.5)
    assert keep.dtype == bool
    assert len(keep) == 5


def test_augment_with_scalar_sa_params(fe2o3):
    n_features = 50
    energies = np.linspace(7000, 7200, n_features)
    rng = np.random.default_rng(42)
    X = rng.random((10, n_features)) + 0.1
    y = np.array(["A"] * 5 + ["B"] * 5)
    metas = [{"structure": fe2o3} for _ in range(10)]

    processor = Processor(X, y, metas=metas)
    processor.split(test_size=0.2, random_seed=42)

    processor.augment(
        energies=energies,
        fraction=1 / 3,
        noise_reference_intensity=1.0,
        self_absorption_kwargs={
            "binder": "boron nitride",
            "absorbing_element": "Fe",
            "compound_weight_fraction": 0.1,
            "phi": 45,
            "theta": 45,
            "thickness": 0.1,
        },
        normalization="area",
        random_seed=42,
    )
    assert np.all(np.isfinite(processor.X_train))
