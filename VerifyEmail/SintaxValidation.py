import re

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
ROLE_BASED_PREFIXES = {"info", "support", "admin", "sales", "contact"}
DISPOSABLE_DOMAINS = {"mailinator.com", "10minutemail.com", "guerrillamail.com"}


def verificarSintaxis(email):
    if not EMAIL_REGEX.match(email or ""):
        return "invalid", "bad_syntax", None, None

    local, domain = email.split("@", 1)
    local_lower = local.lower()
    domain_lower = domain.lower()

    if domain_lower in DISPOSABLE_DOMAINS:
        return "invalid", "disposable_domain", None, None
    if local_lower in ROLE_BASED_PREFIXES:
        return "invalid", "role_based", None, None

    return "ok", "syntax_ok", local_lower, domain_lower