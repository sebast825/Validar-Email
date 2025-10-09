import re
import dns.resolver
import smtplib
import socket
import random

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
ROLE_BASED_PREFIXES = {"info", "support", "admin", "sales", "contact"}
DISPOSABLE_DOMAINS = {"mailinator.com", "10minutemail.com", "guerrillamail.com"}

def verificar_email_combinado(email, sender="verifier@mi-dominio.com", helo_domain="mi-dominio.com",
                              dns_timeout=10, smtp_timeout=10,smtp_retries=2, retry_delay=5):
    """
    Verifica un email combinando validaciones DNS y SMTP.
    Retorna: (status, reason)
      status: "valid", "invalid", "risky"
      reason: texto corto explicando la causa
    """

    # 1️⃣ Validación básica
    if not EMAIL_REGEX.match(email or ""):
        return "invalid", "bad_syntax"

    local, domain = email.split("@", 1)
    local_lower = local.lower()
    domain_lower = domain.lower()

    if domain_lower in DISPOSABLE_DOMAINS:
        return "invalid", "disposable_domain"
    if local_lower in ROLE_BASED_PREFIXES:
        return "invalid", "role_based"

    # 2️⃣ Resolver MX del dominio
    try:
        mx_records = dns.resolver.resolve(domain_lower, "MX", lifetime=dns_timeout)
        mx_servers = sorted([r.exchange.to_text().rstrip(".") for r in mx_records])
        if not mx_servers:
            return "invalid", "no_mx_records"
    except dns.resolver.NXDOMAIN:
        return "invalid", "domain_not_found"
    except dns.resolver.NoAnswer:
        return "invalid", "no_mx_records"
    except dns.resolver.Timeout:
        return "risky", "dns_timeout"
    except dns.resolver.NoNameservers:
        return "risky", "no_nameservers"
    except Exception as e:
        return "risky", f"dns_error_{type(e).__name__}"

    # 3️⃣ Detectar catch-all
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

   # Verificación SMTP con reintentos simples
    last_error = None
    for mx in mx_servers:
        attempt = 1
        while attempt <= smtp_retries:
            try:
                with smtplib.SMTP(mx, timeout=smtp_timeout) as server:
                    server.ehlo_or_helo_if_needed()
                    server.mail(sender)
                    code, _ = server.rcpt(email)

                    if code == 250:
                        return "valid", "smtp_ok"
                    elif code == 550:
                        return "invalid", "smtp_reject"
                    elif 400 <= code < 500:
                        last_error = f"smtp_soft_fail_{code}"
                        attempt += 1
                        time.sleep(retry_delay)
                        continue
                    else:
                        last_error = f"smtp_unexpected_{code}"
                        break

            except (socket.timeout, smtplib.SMTPConnectError):
                last_error = "smtp_connect_timeout"
                attempt += 1
                time.sleep(retry_delay)
                continue
            except smtplib.SMTPServerDisconnected:
                last_error = "smtp_disconnected"
                attempt += 1
                time.sleep(retry_delay)
                continue
            except Exception as e:
                last_error = f"smtp_error_{type(e).__name__}"
                break
            break  # salir del while si no hay soft fail

    if last_error:
        return "risky", last_error
    return "risky", "unverified"
