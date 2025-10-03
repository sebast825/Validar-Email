import re
import dns.resolver
import smtplib
from socket import gaierror

def verificar_email(email, sender="sender@mi-dominio.com", helo_domain="mi-dominio.com"):
    """
    Verifica un email de manera más robusta:
    - Valida sintaxis
    - Comprueba MX
    - Intenta conexión SMTP a varios MX
    - Diferencia errores de red de emails inexistentes
    """
    try:
        # 1️⃣ Validación de sintaxis
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return (email, "❌ Sintaxis inválida")

        dominio = email.split('@')[1]

        # 2️⃣ Resolver MX del dominio
        try:
            mx_records = dns.resolver.resolve(dominio, 'MX', lifetime=10)
            mx_servers = sorted([mx.exchange.to_text() for mx in mx_records])
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
            return (email, "❌ Dominio no existe")
        except dns.resolver.Timeout:
            return (email, "⚠️ Timeout DNS")
        except dns.resolver.NoNameservers:
            return (email, "⚠️ Servidores DNS no responden")

        # 3️⃣ Intentar todos los MX
        last_error = None
        for mx in mx_servers:
            try:
                with smtplib.SMTP(mx, timeout=5) as server:
                    server.helo(helo_domain)
                    server.mail(sender)
                    code, _ = server.rcpt(email)

                    if code == 250:
                        return (email, "✅ Válido")
                    elif code == 550:
                        return (email, "❌ No existe")
                    elif 400 <= code < 500:
                        last_error = f"⚠️ Error temporal ({code})"
                        continue  # Intentar siguiente MX
                    else:
                        last_error = f"⚠️ Código SMTP inesperado ({code})"
                        continue

            except smtplib.SMTPConnectError:
                last_error = "⚠️ Conexión SMTP fallida"
                continue
            except smtplib.SMTPServerDisconnected:
                last_error = "⚠️ Servidor desconectado"
                continue
            except smtplib.SMTPRecipientsRefused:
                return (email, "❌ No existe")
            except Exception as e:
                last_error = f"⚠️ Error SMTP: {str(e)}"
                continue

        # Si ningún MX devolvió 250 ni 550
        if last_error:
            return (email, last_error)
        else:
            return (email, "⚠️ No se pudo verificar")

    except Exception as e:
        return (email, f"⚠️ Error inesperado: {str(e)}")