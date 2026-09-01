def login(user, password):
    return issue_token(user)


def issue_token(user):
    return f"token-for-{user}"
