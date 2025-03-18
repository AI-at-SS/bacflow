from datetime import date


def DoB_to_age(DoB: date) -> int:
    """https://stackoverflow.com/a/9754466"""
    now = date.today()
    offset = int((now.month, now.day) < (DoB.month, DoB.day))
    age = now.year - DoB.year - offset

    return age
