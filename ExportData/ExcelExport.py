import pandas as pd
import os
# --- Función de utilidad ---
def clean_sheet_name(name: str) -> str:
    """
    Limpia caracteres inválidos y limita el nombre a 31 caracteres para Excel.
    """
    invalid_chars = [':', '\\', '/', '?', '*', '[', ']']
    for char in invalid_chars:
        name = name.replace(char, ' ')
    return name.strip()[:31]

# --- Generar hoja resumen ---
def generar_resumen(df: pd.DataFrame) -> pd.DataFrame:
    """
    Genera un resumen agrupando por Estado, contando y concatenando emails.
    """
    summary = df.groupby("Estado").agg(
        Cantidad=("Email", "count"),
        Emails=("Email", lambda x: ", ".join(x))
    ).reset_index()
    return summary

# --- Crear hojas individuales por estado ---
def crear_hojas_por_estado(df: pd.DataFrame, writer: pd.ExcelWriter):
    """
    Crea una hoja por cada estado con emails y detalle.
    Evita nombres duplicados de hojas.
    """
    used_sheets = set()
    for estado in df["Estado"].unique():
        sheet_name = clean_sheet_name(estado)
        original_name = sheet_name
        counter = 1
        while sheet_name in used_sheets:
            sheet_name = f"{original_name}_{counter}"
            counter += 1
        used_sheets.add(sheet_name)

        df[df["Estado"] == estado][["Email", "Estado","Detalle"]].to_excel(
            writer,
            sheet_name=sheet_name,
            index=False
        )

# --- Función principal ---
def exportar_a_excel(resultados):
    """
    Exporta resultados de emails a Excel con hoja resumen y hojas por estado.
    """
      # Obtener la carpeta del script actual
    script_dir = os.path.dirname(os.path.abspath(__file__))
    archivo = "reports/reporte.xlsx"
    # Crear carpeta 'Reports' dentro de la raíz del proyecto (una carpeta arriba del script)
    carpeta = os.path.join(script_dir, "..", "Reports")
    os.makedirs(carpeta, exist_ok=True)
    df = pd.DataFrame(resultados, columns=["Email", "Estado", "Detalle"])
    
    with pd.ExcelWriter(archivo, engine="openpyxl") as writer:
        # Hoja Resumen
        resumen = generar_resumen(df)
        resumen.to_excel(writer, sheet_name="Resumen", index=False)

        # Hojas por estado
        crear_hojas_por_estado(df, writer)

    print(f"✔ Reporte exportado a '{archivo}'")

resultadosTest = [
   ("a@x.com", "smtp_ok", "smtp_ok"),
   ("b@x.com", "smtp_ok", "smtp_ok"),
   ("c@x.com", "smtp_reject", "smtp_reject"),
   ("d@x.com", "smtp_disconnected", "smtp_disconnected"),
]

#exportar_a_excel(resultadosTest)
