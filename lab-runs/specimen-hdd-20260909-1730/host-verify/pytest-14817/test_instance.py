class Obj:
    def compute(self):
        return 42

def test_instance_method():
    obj = Obj()
    assert obj.compute() == 100
