import re
import dns.resolver
import smtplib
from socket import gaierror
import threading
from collections import defaultdict
import time
import pandas as pd
from verificarEmail import verificar_email
from newVerificarEmail import verificar_email_combinado
from ExportData.ExcelExport import exportar_a_excel

ARCHIVO_EMAILS = "emails.txt"
NUM_THREADS = 10
DELAY_ENTRE_EMAILS = 1  # Segundos


def validar_emails(emails):
    resultados = []
    lock = threading.Lock()

    def worker(batch):
        for email in batch:
            with lock:
                resultado = verificar_email_combinado(email.strip())
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
    emails = []
    with open(archivo, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                # Dividir por ";" y luego limpiar cada segmento
                for segment in line.split(';'):
                    cleaned_segment = segment.strip()
                    if cleaned_segment:  # Ignorar segmentos vacíos
                        emails.append(cleaned_segment)
    return emails

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




# Ejecución
if __name__ == "__main__":
    start_time = time.perf_counter()  # Inicia cronómetro

    print(f"Leyendo emails desde {ARCHIVO_EMAILS}...")
    emails = leer_emails(ARCHIVO_EMAILS)
    print(f"Validando {len(emails)} emails con {NUM_THREADS} hilos...")

    resultados = [(email, *verificar_email_combinado(email.strip())) for email in emails]
    #generar_reporte(resultados)
    exportar_a_excel(resultados)
    end_time = time.perf_counter()
    elapsed = end_time - start_time
    print(f"\n⏱️ Tiempo total: {elapsed:.2f} segundos")
