import json

def enc_a(obj):
    return json.dumps({k: v for k, v in obj.items() if v is not False})

def enc_b(obj):
    return json.dumps(obj)

def main():
    rec = {"flag": False, "name": "x"}
    a = enc_a(rec)
    b = enc_b(rec)
    print("A", a)
    print("B", b)
    print("A_has_flag", "flag" in json.loads(a))
    print("B_has_flag", "flag" in json.loads(b))

if __name__ == "__main__":
    main()
