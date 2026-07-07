import os
import glob
import subprocess

# --- CONFIGURACIÓN ---
BASE_PATH = "/Users/davidvillafan96/Documents/melanoma_microbiome_project"
BACTERIAL_DIR = os.path.join(BASE_PATH, "data/bacterial_pure")
PROFILE_OUT_DIR = os.path.join(BASE_PATH, "data/features/metaphlan_outputs")
MERGED_MATRIX_DIR = os.path.join(BASE_PATH, "data/features")
DB_PATH = "/Users/davidvillafan96/Documents/metaphlan_db/"
DB_NAME = "mpa_vJan25_CHOCOPhlAnSGB_202503"

# AJUSTE DE RENDIMIENTO: 
# Si tu Mac tiene 8 núcleos, usa 4. Si tiene más, puedes intentar con 6.
# Nunca uses el total de núcleos, o la máquina se congelará.
THREADS = "4" 

os.makedirs(PROFILE_OUT_DIR, exist_ok=True)

r1_files = sorted(glob.glob(os.path.join(BACTERIAL_DIR, "*_bact_1.fastq.gz")))

if not r1_files:
    print("⚠️ No se encontraron archivos FASTQ.")
    exit()

print(f"🚀 Iniciando MetaPhlAn con {THREADS} hilos por muestra.")

for idx, r1_path in enumerate(r1_files, 1):
    sample_name = os.path.basename(r1_path).replace("_bact_1.fastq.gz", "")
    r2_path = r1_path.replace("_bact_1.fastq.gz", "_bact_2.fastq.gz")
    
    sample_output = os.path.join(PROFILE_OUT_DIR, f"{sample_name}_profile.txt")
    map_output = os.path.join(PROFILE_OUT_DIR, f"{sample_name}.map.bz2")
    
    if os.path.exists(sample_output):
        continue

    print(f"\n📊 [{idx}/{len(r1_files)}] Procesando: {sample_name}")
    
    # Comando optimizado
    cmd_metaphlan = [
        "metaphlan",
        f"{r1_path},{r2_path}",
        "--input_type", "fastq",
        "--db_dir", DB_PATH,
        "-x", DB_NAME,
        "-o", sample_output,
        "--mapout", map_output,
        "--nproc", THREADS, # Aquí está el acelerador
        "--offline"         # Agregado para evitar llamadas innecesarias a internet
    ]
    
    try:
        subprocess.run(cmd_metaphlan, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en {sample_name}: {e}")

# --- CONSOLIDACIÓN ---
print("\n🔗 Generando matriz maestra...")
output_matrix = os.path.join(MERGED_MATRIX_DIR, "taxonomy_matrix.tsv")

try:
    merge_cmd = f"merge_metaphlan_tables.py {PROFILE_OUT_DIR}/*_profile.txt > {output_matrix}"
    subprocess.run(merge_cmd, shell=True, check=True)
    print(f"🏁 ¡Finalizado! Matriz guardada en: {output_matrix}")
except subprocess.CalledProcessError as e:
    print(f"❌ Error al consolidar la matriz: {e}")