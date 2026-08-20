"""Several early returns. A bag of locators, not one stack."""


def bag(user):
    if user is None:
        return None
    if user.locked:
        return None
    if user.pending:
        return "wait"
    return user
