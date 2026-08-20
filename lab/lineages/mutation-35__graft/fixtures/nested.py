"""Ugly nested control flow for when(1)."""


def delete_user(user, db, audit):
    if user is None:
        audit.warn("missing")
        return None
    if user.locked:
        try:
            db.flush()
            if user.role == "admin":
                if not user.can_delete:
                    return "denied"
                raise RuntimeError("admin locked")
            return None
        except RuntimeError as exc:
            audit.error(exc)
            if getattr(exc, "retry", False):
                return "retry"
            return "fail"
        else:
            audit.ok("unlocked path")
        finally:
            db.release()
    elif user.pending:
        for item in user.queue:
            if item.kind == "invite":
                continue
            try:
                db.apply(item)
            except ValueError:
                return "bad-item"
        else:
            return "drained"
    else:
        match user.status:
            case "active" if user.age > 18:
                return db.delete(user)
            case "active":
                return "minor"
            case "gone":
                return None
            case _:
                return "unknown"
    return "fallthrough"


def decorating(fn):
    return fn


@decorating
def top(x):
    return [n for n in x if n > 0 if n % 2 == 0]
