import numpy as np
from sklearn.ensemble import VotingClassifier
from .model_training import train_tabular_model

def create_ensemble_model(X: np.ndarray, y: np.ndarray, target_type: str) -> VotingClassifier:
    """Create ensemble model from individual classifiers"""
    from xgboost import XGBClassifier
    from lightgbm import LGBMClassifier
    from sklearn.ensemble import RandomForestClassifier
    
    estimators = [
        ('xgboost', XGBClassifier(
            n_estimators=150,
            max_depth=4,
            learning_rate=0.1,
            use_label_encoder=False,
            eval_metric='logloss'
        )),
        ('lightgbm', LGBMClassifier(
            n_estimators=150,
            max_depth=4,
            learning_rate=0.1
        )),
        ('randomforest', RandomForestClassifier(
            n_estimators=150,
            max_depth=5
        ))
    ]
    
    ensemble = VotingClassifier(
        estimators=estimators,
        voting='soft' if len(np.unique(y)) > 2 else 'hard'
    )
    
    ensemble.fit(X, y)
    return ensemble