#

- [ ] Does the normalization of the spectra affect the accuracies?
  - Date: 2024-09-12
  - The accuracy of the model improves only slightly when the spectra are normalized. Below are the results of the model trained with and without min-max normalization.
  - Model trained **without** normalization:
  
    ```log
    2024-09-12 15:36:13,599 - xasml.utils - INFO - Accuracy: 95.7 %.
    2024-09-12 15:36:13,601 - xasml.utils - INFO - Balanced accuracy: 95.1 %.
    2024-09-12 15:36:13,603 - xasml.utils - INFO - F1 score: 95.7 %.
    ```

  - Model trained **with min-max** normalization:

    ```log
    2024-09-12 15:36:19,111 - xasml.utils - INFO - Accuracy: 95.9 %.
    2024-09-12 15:36:19,112 - xasml.utils - INFO - Balanced accuracy: 95.5 %.
    2024-09-12 15:36:19,114 - xasml.utils - INFO - F1 score: 95.9 %.
    ```

    - Model trained **with area** normalization:

    ```log
    2024-09-12 15:36:19,111 - xasml.utils - INFO - Accuracy: 95.7 %.
    2024-09-12 15:36:19,112 - xasml.utils - INFO - Balanced accuracy: 95.7 %.
    2024-09-12 15:36:19,114 - xasml.utils - INFO - F1 score: 95.8 %.
    ```  

- [ ] Test the use of descriptors compared to the full spectrum.
