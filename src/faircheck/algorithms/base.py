from abc import ABC, abstractmethod

class FairnessWrapper(ABC):
    """Abstract Base Class for algorithm wrappers."""
    
    @abstractmethod
    def fit(self, X, y, protected_attribute):
        pass

    @abstractmethod
    def predict(self, X):
        pass

    @abstractmethod
    def evaluate_fairness(self, dataset):
        pass
