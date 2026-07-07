import os
import glob
import subprocess

# Configuración de rutas
RAW_DIR = "data/raw"
TRIMMED_DIR = "data/trimmed"
REPORTS_DIR = "results/qc_reports"

# Asegurar que las carpetas de salida existan
os.makedirs(TRIMMED_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

print("🧼 Buscando muestras en data/raw para control de calidad...")

# Buscar todos los archivos R1 (Forward)
r1_files = glob.glob(os.path.join(RAW_DIR, "*_1.fastq.gz"))

if not r1_files:
    print("⚠️ No se encontraron archivos comprimidos con el sufijo '_1.fastq.gz' en data/raw.")
    exit()

print(f"📦 Se encontraron {len(r1_files)} muestras listas para procesar.")

for idx, r1_path in enumerate(r1_files, 1):
    # Derivar el nombre base de la muestra y la ruta de R2 (Reverse)
    filename_r1 = os.path.basename(r1_path)
    sample_name = filename_r1.replace("_1.fastq.gz", "")
    r2_path = os.path.join(RAW_DIR, f"{sample_name}_2.fastq.gz")
    
    # Verificar que exista su par R2
    if not os.path.exists(r2_path):
        print(f"⚠️ Alerta: No se encontró el par R2 para la muestra {sample_name}. Saltando...")
        continue
        
    print(f"\n⚡ [{idx}/{len(r1_files)}] Procesando calidad de: {sample_name}")
    
    # Definir rutas de salida limpias
    out_r1 = os.path.join(TRIMMED_DIR, f"{sample_name}_clean_1.fastq.gz")
    out_r2 = os.path.join(TRIMMED_DIR, f"{sample_name}_clean_2.fastq.gz")
    
    # Definir rutas de los reportes
    report_html = os.path.join(REPORTS_DIR, f"{sample_name}_report.html")
    report_json = os.path.join(REPORTS_DIR, f"{sample_name}_report.json")
    
    # Construir el comando de fastp
    # -q 20: Filtra bases con calidad Phred menor a 20 (99% de precisión)
    # --detect_adapter_for_pe: Detecta automáticamente adaptadores en lecturas pareadas
    cmd = [
        "fastp",
        "-i", r1_path,
        "-I", r2_path,
        "-o", out_r1,
        "-O", out_r2,
        "-h", report_html,
        "-j", report_json,
        "-q", "20",
        "--detect_adapter_for_pe",
        "--thread", "4"  # Ajusta según los núcleos de tu Mac
    ]
    
    # Ejecutar el comando en el sistema operativo
    try:
        result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(f"✅ Muestra {sample_name} limpiada con éxito.")
        print(f"📊 Reporte visual generado en: {report_html}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al procesar la muestra {sample_name}:")
        print(e.stderr)

print("\n🏁 Pipeline de control de calidad finalizado para las muestras disponibles.")