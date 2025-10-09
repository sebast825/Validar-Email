import re
import dns.resolver
import smtplib
from socket import gaierror
import threading
from collections import defaultdict
import time
import pandas as pd
from verificarEmail import verificar_email

ARCHIVO_EMAILS = "emails.txt"
NUM_THREADS = 10
DELAY_ENTRE_EMAILS = 1  # Segundos


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
        used_sheets = set()  # Para evitar nombres repetidos
        for estado in df["Estado"].unique():
            sheet_name = clean_sheet_name(estado)
            original_name = sheet_name
            counter = 1
            # Si ya existe, agregamos un sufijo incremental
            while sheet_name in used_sheets:
                sheet_name = f"{original_name}_{counter}"
                counter += 1
            used_sheets.add(sheet_name)

            df[df["Estado"] == estado].to_excel(
                writer, 
                sheet_name=sheet_name, 
                index=False
            )
    
    print("✔ Reporte exportado a 'reporte.xlsx'")
def exportar_todo_en_una_hoja(resultados):
    """
    Exporta todos los emails con su estado en una sola hoja de Excel llamada 'Todos los Emails'.
    """
    df = pd.DataFrame(resultados, columns=["Email", "Estado"])
    
    with pd.ExcelWriter("reporte.xlsx", engine="openpyxl", mode="a") as writer:
        df.to_excel(writer, sheet_name="Todos los Emails", index=False)
    print("✔ Reporte exportado a 'reporte_todos.xlsx'")


# Ejecución
if __name__ == "__main__":
    start_time = time.perf_counter()  # Inicia cronómetro

    print(f"Leyendo emails desde {ARCHIVO_EMAILS}...")
    emails = leer_emails(ARCHIVO_EMAILS)
    print(f"Validando {len(emails)} emails con {NUM_THREADS} hilos...")
    resultados = validar_emails(emails)
    generar_reporte(resultados)
    exportar_a_excel(resultados)
    exportar_todo_en_una_hoja(resultados)
    end_time = time.perf_counter()
    elapsed = end_time - start_time
    print(f"\n⏱️ Tiempo total: {elapsed:.2f} segundos")
