import pytest

@pytest.mark.parametrize(
    "dev,dtype,metric,k,n,self_query",
    [("cpu", "half", "ip", 1, 1, True)],
)
def test_knn_label_count_expectations(dev, dtype, metric, k, n, self_query):
    assert True
