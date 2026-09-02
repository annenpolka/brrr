def test_item():
    try:
        print('helper', helper)
    except NameError:
        print('helper', 'MISSING')
