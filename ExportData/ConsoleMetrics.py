from collections import defaultdict


# Estadísticas y resultados
def generar_reporte_consola(resultados):
    estadisticas = defaultdict(list)
    for email, estado, *_  in resultados:
        estadisticas[estado].append(email)
    
    print("\n--- REPORTE FINAL ---")
    for estado, emails, *_  in estadisticas.items():
        print(f"\n{estado} ({len(emails)}):")
        for email in emails[:3]:  # Muestra solo 3 ejemplos por categoría
            print(f"  - {email}")
        if len(emails) > 3:
            print(f"  ... y {len(emails) - 3} más")
    
    print("\n📊 RESUMEN:")
    for estado, emails, *_  in estadisticas.items():
        print(f"{estado}: {len(emails)} emails")