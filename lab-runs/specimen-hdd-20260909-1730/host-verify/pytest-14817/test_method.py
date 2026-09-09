class Obj:
    def compute(self):
        return 42

def test_method_call():
    assert Obj().compute() == 100
