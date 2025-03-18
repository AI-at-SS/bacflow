from datetime import date


def DoB_to_age(DoB: date) -> int:
    """https://stackoverflow.com/a/9754466"""
    T = date.today()
    offset = int((T.month, T.day) < (DoB.month, DoB.day))
    return T.year - DoB.year - offset
