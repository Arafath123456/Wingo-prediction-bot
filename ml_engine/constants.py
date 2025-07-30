# Mapping for game outcomes
COLOR_MAPPING = {
    5: "Green",
    1: "Red",
    3: "Red",
    7: "Red",
    9: "Red",
    0: "Violet",
    2: "Violet",
    4: "Violet",
    6: "Violet",
    8: "Violet"
}

SIZE_MAPPING = {
    0: "Small",
    1: "Small",
    2: "Small",
    3: "Small",
    4: "Small",
    5: "Big",
    6: "Big",
    7: "Big",
    8: "Big",
    9: "Big"
}

# Model configuration
MODEL_CONFIG = {
    "n_lags": 10,
    "rolling_windows": [5, 10, 20, 50],
    "sequence_length": 30,
    "test_size": 0.2,
    "validation_split": 0.15
}