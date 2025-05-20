import re
import dns.resolver
import smtplib
from socket import gaierror
import threading
from collections import defaultdict
import time
import pandas as pd

ARCHIVO_EMAILS = "emails.txt"
NUM_THREADS = 10
DELAY_ENTRE_EMAILS = 1  # Segundos

def verificar_email(email):
    try:
        # Validación sintáctica
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return (email, "❌ Sintaxis inválida")

        dominio = email.split('@')[1]
        
        # DNS - MX con reintentos
        try:
            mx_records = dns.resolver.resolve(dominio, 'MX', lifetime=10)
            mx_servers = [mx.exchange.to_text() for mx in mx_records]
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
            return (email, "❌ Dominio no existe")
        except dns.resolver.Timeout:
            return (email, "⚠️ Timeout DNS")
        except dns.resolver.NoNameservers:
            return (email, "⚠️ Servidores DNS no responden")

        # Intentar todos los MX
        for mx in mx_servers:
            try:
                with smtplib.SMTP(mx, timeout=10) as server:
                    server.helo('mi-dominio.com')
                    server.mail('sender@mi-dominio.com')
                    code, _ = server.rcpt(email)
                    server.quit()  # Cierre limpio

                    if code == 250:
                        return (email, "✅ Válido")
                    elif 400 <= code < 500:
                        return (email, f"⚠️ Error temporal ({code})")
                    else:
                        continue  # Próximo MX

            except smtplib.SMTPConnectError:
                continue  # Falló este MX, probar siguiente
            except Exception as e:
                return (email, f"⚠️ Error SMTP: {str(e)}")

        return (email, "⚠️ Todos los MX fallaron")

    except Exception as e:
        return (email, f"⚠️ Error inesperado: {str(e)}")

def validar_emails(emails):
    resultados = []
    lock = threading.Lock()

    def worker(batch):
        for email in batch:
            with lock:
                resultado = verificar_email(email.strip())
                resultados.append(resultado)
            time.sleep(DELAY_ENTRE_EMAILS)

    # Distribución exacta de emails
    batch_size = (len(emails) // NUM_THREADS) + 1
    batches = [emails[i:i + batch_size] for i in range(0, len(emails), batch_size)]

    threads = []
    for batch in batches:
        if batch:
            thread = threading.Thread(target=worker, args=(batch,))
            threads.append(thread)
            thread.start()

    for thread in threads:
        thread.join()

    return resultados

# Resto del código se mantiene igual (leer_emails, generar_reporte, main)
# Leer emails desde archivo .txt
def leer_emails(archivo):
    with open(archivo, 'r') as f:
        return [line.strip() for line in f if line.strip()]

# Estadísticas y resultados
def generar_reporte(resultados):
    estadisticas = defaultdict(list)
    for email, estado in resultados:
        estadisticas[estado].append(email)
    
    print("\n--- REPORTE FINAL ---")
    for estado, emails in estadisticas.items():
        print(f"\n{estado} ({len(emails)}):")
        for email in emails[:3]:  # Muestra solo 3 ejemplos por categoría
            print(f"  - {email}")
        if len(emails) > 3:
            print(f"  ... y {len(emails) - 3} más")
    
    print("\n📊 RESUMEN:")
    for estado, emails in estadisticas.items():
        print(f"{estado}: {len(emails)} emails")


def exportar_a_excel(resultados):
    # Limpia caracteres inválidos en nombres de hojas
    def clean_sheet_name(name):
        invalid_chars = [':', '\\', '/', '?', '*', '[', ']']
        for char in invalid_chars:
            name = name.replace(char, ' ')
        return name.strip()[:31]  # Corta a 31 caracteres

    df = pd.DataFrame(resultados, columns=["Email", "Estado"])
    
    # Crear Excel
    with pd.ExcelWriter("reporte.xlsx") as writer:
        # Hoja resumen
        summary = df["Estado"].value_counts().reset_index()
        summary.columns = ["Estado", "Cantidad"]
        summary.to_excel(writer, sheet_name="Resumen", index=False)
        
        # Hojas por estado
        for estado in df["Estado"].unique():
            sheet_name = clean_sheet_name(estado)
            df[df["Estado"] == estado].to_excel(
                writer, 
                sheet_name=sheet_name, 
                index=False
            )
    
    print("✔ Reporte exportado a 'reporte.xlsx'")

# Ejecución
if __name__ == "__main__":
    start_time = time.perf_counter()  # Inicia cronómetro

    print(f"Leyendo emails desde {ARCHIVO_EMAILS}...")
    emails = leer_emails(ARCHIVO_EMAILS)
    print(f"Validando {len(emails)} emails con {NUM_THREADS} hilos...")
    resultados = validar_emails(emails)
    generar_reporte(resultados)
    exportar_a_excel(resultados)

    end_time = time.perf_counter()
    elapsed = end_time - start_time
    print(f"\n⏱️ Tiempo total: {elapsed:.2f} segundos")
