

from SintaxValidation import verificarSintaxis
from VerifyMx import verifyMX
from verifySmpt import verifySMTP
from isCatchAll import isCatchAll

def verificar_email(email, sender="verifier@mi-dominio.com", helo_domain="mi-dominio.com",
                              dns_timeout=10, smtp_timeout=10, smtp_retries=1, retry_delay=5):
    """Llama a las funciones de verificación en orden"""
    
    # 1️⃣ Verificar sintaxis y dominios básicos
    status, reason, local_lower, domain_lower = verificarSintaxis(email)
    if status != "ok":
        return status, reason

    # 2️⃣ Verificar registros MX
    status, reason, mx_servers = verifyMX(domain_lower, dns_timeout)
    if status != "ok":
        return status, reason

    # 3️⃣ Verificar si es catch-all
    status, reason = isCatchAll(mx_servers, domain_lower, sender, smtp_timeout)
    if status != "ok":
        return status, reason

    # 4️⃣ Verificación SMTP
    return verifySMTP(email, mx_servers, sender, smtp_timeout, smtp_retries, retry_delay)


verificar_email("buenusamedicos@hotmail.com")