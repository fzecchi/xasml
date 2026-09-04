import copy
import logging

import numpy as np
from sklearn.model_selection import train_test_split

logger = logging.getLogger(__name__)


def shift_features(X: np.ndarray, nids: int) -> np.ndarray:
    """Shift a 2-D features array by *nids* indices.

    Positive *nids* shifts to the right; negative shifts to the left.
    Edge values are repeated to fill the vacated positions.
    """
    _, ncols = X.shape
    X_shifted = np.empty_like(X)
    if nids > 0:
        X_shifted[:, :nids] = X[:, 0][:, np.newaxis]
        X_shifted[:, nids:] = X[:, : (ncols - nids)]
    else:
        X_shifted[:, : (ncols + nids)] = X[:, -nids:]
        X_shifted[:, (ncols + nids) :] = X[:, -1][:, np.newaxis]
    return X_shifted


def add_poisson_noise(
    X: np.ndarray,
    rng: np.random.Generator,
    *,
    snr: float | None = None,
    counts_per_intensity: float | None = None,
    reference_intensity: float | None = None,
) -> np.ndarray:
    """Add Poisson noise to a features array.

    Exactly one of *snr* or *counts_per_intensity* must be provided. When
    *snr* is given, *reference_intensity* defines where that SNR is achieved.
    """
    if (snr is None) == (counts_per_intensity is None):
        raise ValueError(
            "Exactly one of 'snr' or 'counts_per_intensity' must be provided."
        )
    if snr is not None:
        if snr <= 0:
            raise ValueError("The SNR must be positive.")
        if reference_intensity is None or reference_intensity <= 0:
            raise ValueError("The reference intensity must be positive.")
        counts_per_intensity = snr**2 / reference_intensity
    if counts_per_intensity is None or counts_per_intensity <= 0:
        raise ValueError("Counts per intensity must be positive.")
    return rng.poisson(X * counts_per_intensity) / counts_per_intensity


def normalize_features(
    X: np.ndarray, method: str, reference: np.ndarray | None = None
) -> np.ndarray:
    """Normalize a 2-D features array.

    Args:
        X: Features array of shape ``(n_samples, n_features)``.
        method: ``"min-max"``, ``"z-score"``, or ``"area"``.
        reference: Energy axis required for ``"area"`` normalization.
    """
    if method == "min-max":
        xmin = np.min(X, axis=1, keepdims=True)
        return (X - xmin) / (np.max(X, axis=1, keepdims=True) - xmin)
    elif method == "z-score":
        return (X - np.mean(X, axis=1, keepdims=True)) / np.std(
            X, axis=1, keepdims=True
        )
    elif method == "area":
        return X / np.trapezoid(X, reference, axis=1)[:, np.newaxis]
    raise ValueError(f"Invalid normalization method: {method}")


class Processor:
    """A class to process data for machine learning."""

    def __init__(
        self,
        X: np.ndarray,
        y: np.ndarray,
        *,
        metas: list[dict] | None = None,
        storage: dict | None = None,
    ):
        """Initialize the data processor.

        Args:
            X: The features of the data.
            y: The labels of the data.
            metas: A list of dictionaries, one per spectrum. Each dictionary
                can contain per-spectrum information such as the pymatgen
                Structure, material ID, or site ID.
            storage: A dictionary containing shared data to store. The keys are
                the names of the data and the values are the data themselves.
        """
        self.X = X
        self.y = y
        self.metas = metas if metas is not None else [{} for _ in range(len(y))]
        self.storage = {} if storage is None else storage

        # Copy the features and labels to the storage dictionary.
        for key in ["X", "y", "metas"]:
            self.copy_to_storage(key)

        self.X_train: np.ndarray = np.array([])
        self.y_train: np.ndarray = np.array([])
        self.metas_train: list[dict] = []

        self.X_test: np.ndarray = np.array([])
        self.y_test: np.ndarray = np.array([])
        self.metas_test: list[dict] = []

        self.X_val: np.ndarray = np.array([])
        self.y_val: np.ndarray = np.array([])
        self.metas_val: list[dict] = []

        # In the methods below, specifying "all" modifies the X and y attributes
        # only, so the `split` method should be called right after.

    def set_features(self, subset: str, X: np.ndarray):
        """Set the features for the specified subset.

        Args:
            subset: The subset of the data to set.
            X: The features to set.
        """
        if subset == "all":
            self.X = X
        else:
            setattr(self, f"X_{subset}", X)

    def set_labels(self, subset: str, y: np.ndarray):
        """Set the labels for the specified subset.

        Args:
            subset: The subset of the data to set.
            y: The labels to set.
        """
        if subset == "all":
            self.y = y
        else:
            setattr(self, f"y_{subset}", y)

    def set_metas(self, subset: str, metas: list[dict]):
        """Set the metas for the specified subset.

        Args:
            subset: The subset of the data to set.
            metas: The metas to set.
        """
        if subset == "all":
            self.metas = metas
        else:
            setattr(self, f"metas_{subset}", metas)

    def copy_to_storage(self, key: str, force: bool = False):
        """Copy the attribute specified by the key argument to the storage.

        Args:
            key: The key of the attribute to copy to the storage dictionary.
            force: Whether or not to overwrite the storage dictionary if the key
                already exists.
        """
        if key in self.storage and not force:
            raise ValueError(f"The storage dictionary already contains the {key}.")
        self.storage[key] = copy.deepcopy(getattr(self, key))

    def copy_from_storage(self, key: str):
        """Copy the data specified by the key from the storage to the attribute.

        Args:
            key: The key of the data to copy from the storage dictionary.
        """
        try:
            setattr(self, key, copy.deepcopy(self.storage[key]))
            logger.info(f"Copied '{key}' from storage.")
        except KeyError:
            setattr(self, key, np.array([]))
            logger.debug(f"'{key}' not found in storage.")

    def select_subset(self, subset: str):
        """Select the subset of the data specified by the ``subset`` argument.

        Args:
            subset: The subset of the data to select.

        Returns:
            A tuple of (X, y, metas) for the selected subset.
        """
        X: np.ndarray = np.array([])
        y: np.ndarray = np.array([])

        if subset in ["train", "test", "val"]:
            X = getattr(self, f"X_{subset}")
            y = getattr(self, f"y_{subset}")
            metas = getattr(self, f"metas_{subset}")
        elif subset == "all":
            X, y, metas = self.X, self.y, self.metas
        else:
            raise ValueError(f"Invalid subset: {subset}")

        if X.size == 0 or y.size == 0:
            raise ValueError(
                f"The {subset} subset is not defined. Did you forget to call `split`?"
            )

        return X, y, metas

    def shift(
        self,
        value: float,
        reference: np.ndarray | None = None,
        subset: str = "all",
    ):
        """Shift the features using the value argument.

        Args:
            value: The number of indices to shift the features. A positive value shifts
                these to the right, while a negative value shifts them to the left.
            reference: The reference used to calculate the number of indices to shift.
                If None, the value is used as the number of indices to shift.
            subset: The subset of the data to which the shift is applied.
        """
        if value == 0:
            logger.info("No shift applied.")
            return

        # If a reference is provided, calculate the number of points to shift.
        if reference is not None:
            if len(reference) != self.X.shape[1]:
                raise ValueError(
                    "The reference length must be the same as the features length."
                )
            if value > 0:
                ids = np.where(reference > reference[-1] - value)[0]
                nids = len(ids)
            else:
                ids = np.where(reference < reference[0] - value)[0]
                nids = -len(ids)
        else:
            nids = int(value)

        X, *_ = self.select_subset(subset)
        direction = "right" if nids > 0 else "left"
        logger.info(f"Shifting the features to the {direction} by {abs(nids)} indices.")
        self.set_features(subset, shift_features(X, nids))

    def trim(
        self,
        left: float | None,
        right: float | None,
        reference: np.ndarray | None = None,
        subset: str = "all",
    ):
        """Trim the features to the range specified by the left and right arguments.

        Args:
            left: The left limit of the range determining the features to keep.
            right: The right limit of the range determining the features to keep.
            reference: The reference used to calculate the range to keep. If None, the
                left and right arguments are used as integer indices.
            subset: The subset of the data to which the trim is applied.
        """
        if left is None or right is None:
            raise ValueError("The left and right limits must be provided.")

        X, *_ = self.select_subset(subset)
        logger.debug(f"Initial features size: {X.shape}")

        # Create a mask to select the features within the specified range.
        mask = np.zeros_like(X[0, :], dtype=bool)
        if reference is not None:
            if len(reference) != self.X.shape[1]:
                raise ValueError(
                    "The reference length must be the same as the features length."
                )
            mask[(left <= reference) & (reference <= right)] = True
        else:
            mask[int(left) : int(right)] = True

        X_trimmed = X[:, mask]
        logger.debug(f"Final features size: {X_trimmed.shape}")

        self.set_features(subset, X_trimmed)
        logger.info(
            f"Trimmed features in the '{subset}' subset to the range {left} to {right}."
        )
        return mask

    def normalize(
        self,
        subset: str = "all",
        *,
        method: str | None,
        reference: np.ndarray | None = None,
    ):
        """Normalize the features.

        Args:
            subset: The subset of the data to normalize.
            method: The normalization method. The valid options are "min-max",
                "z-score", and "area". Pass ``None`` to skip normalization.
            reference: The reference array (e.g. energy axis) required for the "area"
                normalization method.
        """
        if method is None:
            logger.info("No normalization applied.")
            return
        if method == "area" and reference is None:
            raise ValueError("The reference must be provided for the area method.")

        X, *_ = self.select_subset(subset)
        self.set_features(subset, normalize_features(X, method, reference))
        logger.info(f"Normalized the '{subset}' subset using the '{method}' method.")

    def add_poisson_noise(
        self,
        *,
        snr: float | None = None,
        counts_per_intensity: float | None = None,
        reference_intensity: float | None = None,
        normalization: str | None = None,
        reference: np.ndarray | None = None,
        subset: str = "all",
        random_seed: int = 42,
    ):
        """Add Poisson noise to the features.

        Exactly one of *snr* or *counts_per_intensity* must be provided. When
        *snr* is given, *reference_intensity* defines where that SNR is achieved.

        Args:
            snr: The signal-to-noise ratio.
            counts_per_intensity: Factor that converts intensity into expected counts.
            reference_intensity: Intensity at which *snr* is defined.
            normalization: Normalization method applied after adding noise.
            reference: Energy axis used for area normalization.
            subset: The subset of the data to which the noise is added.
            random_seed: The seed used by the random number generator.
        """
        if normalization == "area" and reference is None:
            raise ValueError("Area normalization requires a reference array.")

        X, *_ = self.select_subset(subset)
        rng = np.random.default_rng(random_seed)
        X_noisy = add_poisson_noise(
            X,
            rng,
            snr=snr,
            counts_per_intensity=counts_per_intensity,
            reference_intensity=reference_intensity,
        )
        if normalization is not None:
            X_noisy = normalize_features(X_noisy, normalization, reference)
        self.set_features(subset, X_noisy)

        if snr is not None:
            logger.info(
                f"Added Poisson noise to the '{subset}' subset using an SNR of {snr} "
                f"at a reference intensity of {reference_intensity}."
            )
        else:
            logger.info(
                f"Added Poisson noise to the '{subset}' subset using "
                f"{counts_per_intensity} counts per intensity."
            )

    def add_incident_beam_self_absorption(
        self, subset: str = "all", energies: np.ndarray | None = None, **kwargs
    ):
        """Apply incident beam self-absorption to the features.

        Transforms the calculated absorption spectra into fluorescence detected
        spectra using ``fluorescence.calculate_spectrum``. The compound for each
        spectrum is read from the ``"structure"`` key of its metas dictionary.

        Args:
            subset: The subset of the data to which the transformation is applied.
            energies: The incident photon energies in eV. If None, the energies are
                read from the metas dictionary.
            **kwargs: Parameters forwarded to function doing the transformation.
                Required: ``binder``, ``absorbing_element``,
                ``compound_weight_fraction``, ``phi``, ``theta``, ``thickness``.
                Optional: ``solid_angle``, ``edge``, ``emission_line``.
        """
        from xasml.models.fluorescence import calculate_spectrum

        X, _, metas = self.select_subset(subset)
        X_transformed = np.empty_like(X)
        for i in range(X.shape[0]):
            if energies is None:
                spectrum_energies = np.asarray(metas[i].get("energies"))
            else:
                spectrum_energies = energies
            X_transformed[i] = calculate_spectrum(
                energies=spectrum_energies,
                intensity=X[i],
                compound=metas[i]["structure"],
                **kwargs,
            )
        logger.info(f"Applied incident beam self-absorption to the '{subset}' subset.")
        self.set_features(subset, X_transformed)

    def augment(
        self,
        energies: np.ndarray,
        fraction: float = 1 / 3,
        shift_range: tuple[float, float] | None = (-1, 1),
        snr_range: tuple[float, float] | None = (100, 500),
        noise_reference_intensity: float | None = None,
        self_absorption_kwargs: dict | None = None,
        normalization: str | None = "area",
        random_seed: int = 42,
        subset: str = "train",
    ):
        """Augment a data subset with perturbed spectra.

        Randomly selects a fraction of the subset samples and applies one of
        the enabled perturbation types to each: energy shift, Poisson noise, or
        incident beam self-absorption. A perturbation is enabled when its
        parameters are not None, so passing ``snr_range=None`` and
        ``self_absorption_kwargs=None`` augments with shifts only. The perturbed
        spectra are re-normalized
        and appended to the subset. Augmenting the validation set as well as
        the training set lets early stopping select for robustness rather than
        for clean-data performance.

        Must be called after :meth:`split`.

        Args:
            energies: Energy axis in eV, used as shift reference, for
                self-absorption calculation, and for area normalization.
            fraction: Fraction of training samples to augment.
            shift_range: Range of random energy shifts in eV ``(min, max)``,
                or None to disable shift augmentation.
            snr_range: Range of signal-to-noise ratios for Poisson noise
                ``(min, max)``, or None to disable noise augmentation.
            noise_reference_intensity: Intensity at which values in *snr_range*
                are defined. Required when noise augmentation is enabled.
            self_absorption_kwargs: Keyword arguments forwarded to
                :func:`~xasml.models.fluorescence.calculate_spectrum`.
                Required keys: ``binder``, ``absorbing_element``, ``phi``,
                ``theta``. The ``compound_weight_fraction`` and ``thickness``
                keys accept either a scalar or a ``(min, max)`` tuple; tuples
                are sampled uniformly per spectrum. If *None*, self-absorption
                augmentation is disabled and samples are split between shift
                and noise only.
            normalization: Normalization method applied to augmented spectra
                before appending. Passed to :meth:`normalize`.
            random_seed: Seed for the random number generator.
            subset: The subset to augment (for example ``"train"`` or ``"val"``).
        """
        # A perturbation is enabled when its parameters are not None.
        enabled = []
        if shift_range is not None:
            enabled.append("shift")
        if snr_range is not None:
            if noise_reference_intensity is None:
                raise ValueError("Noise augmentation requires a reference intensity.")
            enabled.append("noise")
        if self_absorption_kwargs is not None:
            enabled.append("self_absorption")
        if not enabled:
            raise ValueError("At least one perturbation must be enabled.")

        X_train, y_train, metas_train = self.select_subset(subset)

        n_train = len(y_train)
        n_augment = int(n_train * fraction)
        rng = np.random.default_rng(random_seed)

        # Select samples and assign a perturbation type to each.
        augment_indices = rng.choice(n_train, size=n_augment, replace=False)
        type_names = np.array(enabled)[rng.choice(len(enabled), n_augment)]

        X_augmented = np.copy(X_train[augment_indices])
        y_augmented = np.copy(y_train[augment_indices])

        # --- Shift ---
        if shift_range is not None:
            energy_step = energies[1] - energies[0]
            for i in np.where(type_names == "shift")[0]:
                shift_val = rng.uniform(*shift_range)
                nids = round(shift_val / energy_step)
                if nids == 0:
                    continue
                X_augmented[i : i + 1] = shift_features(X_augmented[i : i + 1], nids)

        # --- Noise ---
        if snr_range is not None:
            noise_rng = np.random.default_rng(random_seed)
            for i in np.where(type_names == "noise")[0]:
                snr = rng.uniform(*snr_range)
                X_augmented[i : i + 1] = add_poisson_noise(
                    X_augmented[i : i + 1],
                    noise_rng,
                    snr=snr,
                    reference_intensity=noise_reference_intensity,
                )

        # --- Self-absorption ---
        if self_absorption_kwargs is not None:
            from xasml.models.fluorescence import calculate_spectrum

            self_absorption_kwargs = dict(self_absorption_kwargs)
            thickness_kwarg = self_absorption_kwargs.pop("thickness", None)
            weight_fraction_cfg = self_absorption_kwargs.pop(
                "compound_weight_fraction", None
            )

            for i in np.where(type_names == "self_absorption")[0]:
                idx = augment_indices[i]
                structure = metas_train[idx].get("structure")
                if structure is None:
                    continue
                thickness = (
                    rng.uniform(*thickness_kwarg)
                    if isinstance(thickness_kwarg, tuple)
                    else thickness_kwarg
                )
                weight_fraction = (
                    rng.uniform(*weight_fraction_cfg)
                    if isinstance(weight_fraction_cfg, tuple)
                    else weight_fraction_cfg
                )
                X_augmented[i] = calculate_spectrum(
                    energies=energies,
                    intensity=X_augmented[i],
                    compound=structure,
                    compound_weight_fraction=weight_fraction,
                    thickness=thickness,
                    **self_absorption_kwargs,
                )

        # Normalize the original and augmented spectra after perturbation.
        if normalization is not None:
            X_train = normalize_features(X_train, normalization, energies)
            X_augmented = normalize_features(X_augmented, normalization, energies)

        # Append augmented data to the subset.
        self.set_features(subset, np.vstack([X_train, X_augmented]))
        self.set_labels(subset, np.concatenate([y_train, y_augmented]))
        self.set_metas(
            subset, list(metas_train) + [metas_train[i] for i in augment_indices]
        )

        n_shift = int((type_names == "shift").sum())
        n_noise = int((type_names == "noise").sum())
        n_sa = int((type_names == "self_absorption").sum())
        logger.info(
            f"Augmented '{subset}' subset with {n_augment} samples "
            f"(shift: {n_shift}, noise: {n_noise}, self-absorption: {n_sa}). "
            f"Total: {len(self.select_subset(subset)[1])} samples."
        )

    def split(
        self,
        test_size: float = 0.2,
        val_size: float | None = None,
        shuffle: bool = True,
        stratify: bool = True,
        random_seed: int = 42,
    ):
        """Split the data into training, testing, and validation sets.

        Args:
            test_size: The proportion of the data to include in the testing set.
            val_size: The proportion of the data to include in the validation set.
                If None, the validation set is not created.
            shuffle: Whether or not to shuffle the data before splitting it.
            stratify: Whether to preserve label proportions in each subset.
            random_seed: The seed used by the random number generator.
        """
        split_size = test_size + val_size if val_size is not None else test_size
        X_train, X_test, y_train, y_test, metas_train, metas_test = train_test_split(
            self.X,
            self.y,
            self.metas,
            test_size=split_size,
            random_state=random_seed,
            shuffle=shuffle,
            stratify=self.y if stratify else None,
        )

        if val_size is not None:
            X_val, X_test, y_val, y_test, metas_val, metas_test = train_test_split(
                X_test,
                y_test,
                metas_test,
                test_size=test_size / split_size,
                random_state=random_seed,
                shuffle=shuffle,
                stratify=y_test if stratify else None,
            )
            logger.info("Split data into training, testing, and validation sets.")
            X_val, y_val = np.array(X_val), np.array(y_val)
        else:
            X_val, y_val, metas_val = np.array([]), np.array([]), []
            logger.info("Split data into training and testing sets.")

        X_train, X_test = np.array(X_train), np.array(X_test)
        y_train, y_test = np.array(y_train), np.array(y_test)

        self.X_train, self.X_test, self.X_val = X_train, X_test, X_val
        self.y_train, self.y_test, self.y_val = y_train, y_test, y_val
        self.metas_train = metas_train
        self.metas_test = metas_test
        self.metas_val = metas_val

        # Copy the split data to the storage dictionary.
        for subset in ["train", "test", "val"]:
            for key in ["X", "y", "metas"]:
                self.copy_to_storage(f"{key}_{subset}", force=True)

        subsets = (
            ["train", "test", "val"] if val_size is not None else ["train", "test"]
        )
        subset_names = ", ".join(subsets)
        logger.debug(f"Subset sizes ({subset_names}):")
        for subset in subsets:
            for key in ["X", "y"]:
                logger.debug(
                    f"{key}_{subset}: {getattr(self, f'{key}_{subset}').shape}"
                )
            logger.debug(f"metas_{subset}: {len(getattr(self, f'metas_{subset}'))}")

    def select_labels(
        self,
        labels: list[str],
        ratios: list[float] | None = None,
        randomize: bool = False,
        subset: str = "all",
        random_seed: int = 42,
    ):
        """Select the labels (Y-values) specified by the ``labels`` argument.

        Args:
            labels: The labels to select.
            ratios: The ratios of the labels to select. If None, the labels are
                selected uniformly.
            randomize: Whether or not to randomize the selected labels.
            subset: The subset of the data of which the labels are selected. The valid
                options are "train", "test", "val", and "all".
            random_seed: The seed used by the random number generator when
                ``randomize`` is True.
        """
        # Select the subset from the data.
        X, y, metas = self.select_subset(subset)

        # Determine the number of occurrences of each label.
        n_occurrences = np.array([np.sum(y == label) for label in labels])

        # Determine the indices of each label.
        indices = [np.where(y == label)[0] for label in labels]

        # If the ratios are provided, use them to calculate the number of occurrences
        # for each label.
        if ratios is not None:
            # Normalize the ratios to maximum of 1.
            ratios = list(np.array(ratios) / np.max(ratios))

            # Determine the minimum number of occurrences.
            n_occurrences_min = np.min(n_occurrences)

            # Calculate the number of occurrences for each label.
            n_occurrences = np.array([
                int(n_occurrences_min * ratio) for ratio in ratios
            ])

        # Select indices according to the ratios.
        rng = np.random.default_rng(random_seed)
        selected_indices = []
        for i, (label, n_occ) in enumerate(zip(labels, n_occurrences)):
            if randomize:
                selected_indices.append(
                    rng.choice(indices[i], size=n_occ, replace=False)
                )
            else:
                selected_indices.append(indices[i][:n_occ])

        logger.debug("Number of occurrences for each label:")
        for label, selected_index in zip(labels, selected_indices):
            logger.debug(f"{label}: {len(selected_index)}")

        # Concatenate the selected indices.
        selected_indices = np.concatenate(selected_indices)

        # Convert the selected indices to a boolean mask.
        mask = np.zeros(len(y), dtype=bool)
        mask[selected_indices] = True

        # Apply the mask to the features, labels, and metas.
        self.set_features(subset, X[mask, :])
        self.set_labels(subset, y[mask])
        self.set_metas(subset, [m for m, keep in zip(metas, mask) if keep])

        logger.info(f"Selected {np.sum(mask):d} out of {len(mask):d} labels.")

        return mask

    def remove_outliers(
        self,
        threshold: float = 2.5,
        min_std: float = 0.01,
        subset: str = "all",
    ) -> np.ndarray:
        """Remove spectra that deviate from the mean by more than *threshold* standard deviations.

        For each energy grid point *j*, the mean and population standard
        deviation are computed over all spectra.  A spectrum is removed if
        ``|X[i, j] - mean[j]| > threshold * effective_std[j]`` for **any** grid point.

        To avoid flagging spectra as outliers where the signal is very small,
        the effective standard deviation is floored at ``min_std`` times the
        maximum absolute mean signal.

        Args:
            threshold: Number of standard deviations beyond which a spectrum
                is considered an outlier.
            min_std: Minimum standard deviation as a fraction of the peak mean
                signal. Prevents spurious rejection where the signal is near zero.
            subset: The subset of the data to filter.

        Returns:
            A boolean mask of shape ``(n_samples,)`` where ``True`` marks the
            spectra that were **kept**.
        """
        X, y, metas = self.select_subset(subset)

        mean = np.mean(X, axis=0)
        std = np.std(X, axis=0, ddof=0)

        # Floor the std to avoid spurious outlier detection where signal is near zero.
        std_floor = min_std * np.max(np.abs(mean))
        effective_std = np.maximum(std, std_floor)

        # A spectrum is an outlier if any point exceeds the envelope.
        within_envelope = np.abs(X - mean) <= threshold * effective_std
        keep = np.all(within_envelope, axis=1)
        n_removed = int(np.sum(~keep))

        self.set_features(subset, X[keep])
        self.set_labels(subset, y[keep])
        self.set_metas(subset, [m for m, k in zip(metas, keep) if k])

        logger.info(
            f"Removed {n_removed} outlier(s) out of {len(keep)} spectra "
            f"(threshold={threshold}, min_std={min_std})."
        )
        return keep

    def reset(self, subset: str = "all", values: str = "original"):
        """Reset the features and labels for the specified subset.

        Args:
            subset: The subset of the data to reset.
            values: The values to reset the features and labels to. The valid options
                are `original` and `empty`.
        """
        keys = (
            ["X", "y", "metas"]
            if subset == "all"
            else [f"X_{subset}", f"y_{subset}", f"metas_{subset}"]
        )

        for key in keys:
            if values == "original":
                self.copy_from_storage(key)
            elif values == "empty":
                setattr(self, key, np.array([]))
            else:
                raise ValueError(f"Invalid values: {values}")
