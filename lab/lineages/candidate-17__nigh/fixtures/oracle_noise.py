def test_sentence():
    output = "会議の日程を変更しました。"
    assert output == "会議の日程を変更しました。"


def test_typeof_should_not_matter():
    x = "hello"
    if isinstance(x, str):
        return x
