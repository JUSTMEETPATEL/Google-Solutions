import pytest
from faircheck.algorithms import FairlearnWrapper, AIF360Wrapper

def test_fairlearn_wrapper_fit_raises_not_implemented():
    wrapper = FairlearnWrapper()
    with pytest.raises(NotImplementedError, match="To be implemented in Phase 3"):
        wrapper.fit(None, None, None)

def test_aif360_wrapper_fit_raises_not_implemented():
    wrapper = AIF360Wrapper()
    with pytest.raises(NotImplementedError, match="To be implemented in Phase 3"):
        wrapper.fit(None, None, None)
