from .base import FairnessWrapper

class AIF360Wrapper(FairnessWrapper):
    """Wrapper for AIF360 algorithms."""
    
    def fit(self, X, y, protected_attribute):
        raise NotImplementedError("To be implemented in Phase 3")

    def predict(self, X):
        raise NotImplementedError("To be implemented in Phase 3")

    def evaluate_fairness(self, dataset):
        raise NotImplementedError("To be implemented in Phase 3")
