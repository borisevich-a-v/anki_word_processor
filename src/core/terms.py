"""When two terms are the same term."""


def term_key(term: str) -> str:
    """What terms are compared by: the text without surrounding spaces, in Unicode case folding."""
    return term.strip().casefold()
