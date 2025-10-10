from SintaxValidation import verificarSintaxis
from VerifyMx import verifyMX
from VerifyEmail import verifySMTP
from isCatchAll import isCatchAll

if __name__ == "__main__":
    print("=== TESTS SIMPLES ===\n")

    # 1️⃣ Test verificarSintaxis
    emails = [
        "usuario@gmail.com",
        "invalido@@gmail.com",
        "info@empresa.com",           # role_based
        "fake@mailinator.com"         # disposable
    ]
    for e in emails:
        print(f"Test sintaxis: {e}")
        print(verificarSintaxis(e))
        print()

    # 2️⃣ Test verifyMX
    dominios = ["gmail.com", "dominioinexistente123123.com"]
    for d in dominios:
        print(f"Test MX: {d}")
        print(verifyMX(d, dns_timeout=5))
        print()

    # 3️⃣ Test isCatchAll (usa dominios reales)
    status, reason, mx_servers = verifyMX("gmail.com", dns_timeout=5)
    if mx_servers:
        print("Test Catch-All gmail.com")
        print(isCatchAll(mx_servers, "gmail.com", "test@midominio.com", smtp_timeout=5))
        print()

    # 4️⃣ Test verifySMTP
    if mx_servers:
        print("Test SMTP (falso email)")
        print(verifySMTP("noexiste@gmail.com", mx_servers, "test@midominio.com", smtp_timeout=5, smtp_retries=1, retry_delay=1))
        print()

    # 5️⃣ Test flujo completo
    print("=== Test completo ===")
    print(verificar_email_combinado("usuario@gmail.com"))
    print(verificar_email_combinado("noexiste@dominiofalso123123.com"))
    print()
