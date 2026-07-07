import os
import glob
import subprocess

# Configuración de rutas
TRIMMED_DIR = "data/trimmed"
BACTERIAL_DIR = "data/bacterial_pure"
INDEX_HUMAN = "data/reference/GRCh38_noalt_as" # Ruta al índice hg38

# Asegurar que la carpeta de salida exista
os.makedirs(BACTERIAL_DIR, exist_ok=True)

print("🧬 Iniciando pipeline de remoción de ADN del hospedador (Humano)...")

# Buscar los archivos que limpió fastp
r1_files = glob.glob(os.path.join(TRIMMED_DIR, "*_clean_1.fastq.gz"))
r1_files.sort() # Ordenar alfabéticamente para mantener un control limpio

if not r1_files:
    print("⚠️ No se encontraron archivos '_clean_1.fastq.gz' en data/trimmed. ¡Espera a que corra fastp!")
    exit()

for idx, r1_path in enumerate(r1_files, 1):
    filename_r1 = os.path.basename(r1_path)
    sample_name = filename_r1.replace("_clean_1.fastq.gz", "")
    r2_path = os.path.join(TRIMMED_DIR, f"{sample_name}_clean_2.fastq.gz")
    
    # Definir archivos de salida esperados (Puros bacterianos)
    out_bact_r1 = os.path.join(BACTERIAL_DIR, f"{sample_name}_bact_1.fastq.gz")
    out_bact_r2 = os.path.join(BACTERIAL_DIR, f"{sample_name}_bact_2.fastq.gz")
    
    # --- OPTIMIZACIÓN 1: El "Checkpoint" ---
    # Si ambos archivos de salida ya existen, saltamos esta muestra.
    if os.path.exists(out_bact_r1) and os.path.exists(out_bact_r2):
        print(f"⏩ [{idx}/{len(r1_files)}] Saltando {sample_name}: Ya procesada anteriormente.")
        continue
        
    # Verificar que el par R2 exista antes de largar Bowtie
    if not os.path.exists(r2_path):
        print(f"⚠️ Error: No se encontró el R2 para {sample_name}. Saltando...")
        continue
    
    print(f"🏹 [{idx}/{len(r1_files)}] Filtrando trazas humanas de: {sample_name}")
    
    cmd_bowtie = [
        "bowtie2",
        "-x", INDEX_HUMAN,
        "-1", r1_path,
        "-2", r2_path,
        "--un-conc-gz", os.path.join(BACTERIAL_DIR, f"{sample_name}_bact_%.fastq.gz"),
        "-p", "4", # Hilos de procesamiento
        "--very-sensitive" 
    ]
    
    try:
        # --- OPTIMIZACIÓN 2: Evitar el cuelgue de la terminal ---
        # stdout=subprocess.DEVNULL tira el SAM gigante a la basura en lugar de imprimirlo.
        # stderr=None permite que las estadísticas de mapeo de bowtie2 se sigan viendo.
        subprocess.run(cmd_bowtie, stdout=subprocess.DEVNULL, check=True)
        print(f"✅ {sample_name} filtrada correctamente.\n")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al procesar {sample_name}. Detalle: {e}\n")

print("🏁 Pipeline finalizado.")