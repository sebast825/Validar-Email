import sys
import os

# Agrega la raíz del proyecto al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from VerifyEmail.SyntaxValidation import SyntaxValidation
from VerifyEmail.MxVerify import MxVerify
from VerifyEmail.SmtpVerify import SmtpVerify
from VerifyEmail.isCatchAll import isCatchAll

if __name__ == "__main__":
    print("=== TESTS SIMPLES ===\n")

    # 1️⃣ Test SyntaxValidation
    emails = [
        "usuario@gmail.com",
        "invalido@@gmail.com",
        "info@empresa.com",           # role_based
        "fake@mailinator.com"         # disposable
    ]
    for e in emails:
        print(f"Test sintaxis: {e}")
        print(SyntaxValidation(e))
        print()

    # 2️⃣ Test MxVerify
    dominios = ["gmail.com", "dominioinexistente123123.com"]
    for d in dominios:
        print(f"Test MX: {d}")
        print(MxVerify(d, dns_timeout=5))
        print()

    # 3️⃣ Test isCatchAll (usa dominios reales)
    status, reason, mx_servers = MxVerify("gmail.com", dns_timeout=5)
    if mx_servers:
        print("Test Catch-All gmail.com")
        print(isCatchAll(mx_servers, "gmail.com", "test@midominio.com", smtp_timeout=5))
        print()

    # 4️⃣ Test SmtpVerify
    if mx_servers:
        print("Test SMTP (falso email)")
        print(SmtpVerify("noexiste@gmail.com", mx_servers, "test@midominio.com", smtp_timeout=5, smtp_retries=1, retry_delay=1))
        print()

    # 5️⃣ Test flujo completo
    print("=== Test completo ===")
   
    print()
