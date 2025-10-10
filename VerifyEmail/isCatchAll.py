import random
import smtplib
import socket

def isCatchAll(mx_servers, domain_lower, sender, smtp_timeout):
    probe_email = f"random{random.randint(100000,999999)}@{domain_lower}"
    for mx in mx_servers:
        try:
            with smtplib.SMTP(mx, timeout=smtp_timeout) as server:
                server.ehlo_or_helo_if_needed()
                server.mail(sender)
                code, _ = server.rcpt(probe_email)
                if code == 250:
                    return "risky", "domain_accepts_all"
        except (socket.timeout, smtplib.SMTPConnectError):
            continue
        except Exception:
            continue
    return "ok", "no_catch_all"