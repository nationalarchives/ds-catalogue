import base64


def base64_encode(s):
    s = bytes(s, "utf-8")
    s = base64.urlsafe_b64encode(s)
    return s.decode("utf-8", "ignore")


def base64_decode(s):
    if not s:
        return ""
    try:
        raw = s.encode("utf-8")
        padding = (-len(raw)) % 4
        if padding:
            raw += b"=" * padding
        decoded = base64.urlsafe_b64decode(raw)
    except Exception:
        return ""
    return decoded.decode("utf-8", "ignore")
