import re
import dns.resolver
import smtplib
from socket import gaierror
import threading
from collections import defaultdict
import time
import pandas as pd
from ExportData.ExcelExport import exportar_a_excel
from ExportData.ConsoleMetrics import generar_reporte_consola

from VerifyEmail.VerifyEmail import verificar_email

ARCHIVO_EMAILS = "emails.txt"
NUM_THREADS = 10


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





# Ejecución
if __name__ == "__main__":
    start_time = time.perf_counter()  # Inicia cronómetro

    print(f"Leyendo emails desde {ARCHIVO_EMAILS}...")
    emails = leer_emails(ARCHIVO_EMAILS)
    print(f"Validando {len(emails)} emails con {NUM_THREADS} hilos...")

    resultados = [(email, *verificar_email(email.strip())) for email in emails]
    generar_reporte_consola(resultados)
    exportar_a_excel(resultados)
    end_time = time.perf_counter()
    elapsed = end_time - start_time
    print(f"\n⏱️ Tiempo total: {elapsed:.2f} segundos")
