import socket
import smtplib
import time

def verifySMTP(email, mx_servers, sender, smtp_timeout, smtp_retries, retry_delay):
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