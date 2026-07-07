import os
import glob
import subprocess
import shutil

# Configuración de rutas
BACTERIAL_DIR = "data/bacterial_pure"
ASSEMBLY_DIR = "data/assembly"

# Buscar el ejecutable de megahit automáticamente
megahit_path = shutil.which("megahit")

if not megahit_path:
    print("❌ ERROR: No se encuentra el ejecutable 'megahit'.")
    print("Asegúrate de estar en el entorno 'bioinfo' (conda activate bioinfo) y de tenerlo instalado.")
    exit()

# Asegurar que la carpeta raíz de ensamblados exista
os.makedirs(ASSEMBLY_DIR, exist_ok=True)

print(f"🧩 Iniciando pipeline de Ensamblado Metagenómico con MEGAHIT en: {megahit_path}")

# Buscar los archivos R1 puramente bacterianos
r1_files = glob.glob(os.path.join(BACTERIAL_DIR, "*_bact_1.fastq.gz"))

if not r1_files:
    print("⚠️ No se encontraron archivos '_bact_1.fastq.gz' en data/bacterial_pure. ¡Espera a que corra remove_host!")
    exit()

print(f"📦 Se encontraron {len(r1_files)} muestras listas para ensamblar.")

for idx, r1_path in enumerate(r1_files, 1):
    filename_r1 = os.path.basename(r1_path)
    sample_name = filename_r1.replace("_bact_1.fastq.gz", "")
    r2_path = os.path.join(BACTERIAL_DIR, f"{sample_name}_bact_2.fastq.gz")
    
    if not os.path.exists(r2_path):
        print(f"⚠️ Alerta: No se encontró el par R2 para {sample_name}. Saltando...")
        continue
        
    print(f"\n🧵 [{idx}/{len(r1_files)}] Ensamblando contigs para la muestra: {sample_name}")
    
    # MEGAHIT requiere una carpeta de salida específica por cada muestra
    sample_out_dir = os.path.join(ASSEMBLY_DIR, sample_name)
    
    # Construir el comando usando la ruta absoluta encontrada
    # Construir el comando usando la ruta absoluta encontrada
    cmd_megahit = [
        megahit_path,
        "-1", r1_path,
        "-2", r2_path,
        "-o", sample_out_dir,
        "--out-prefix", sample_name,
        "-t", "2",          # Usa 2 hilos para evitar que la MacBook se sobrecaliente
        "--force"           # Asegúrate de tener '--force' y no '--clobber'
    ]
    
    print(f"🖥️ Ejecutando MEGAHIT para {sample_name}...")
    
    try:
        # Ejecución del comando
        subprocess.run(cmd_megahit, check=True)
        print(f"✅ Archivo '{sample_name}.contigs.fa' generado exitosamente en {sample_out_dir}.")
    except subprocess.CalledProcessError as e:
        print(f"❌ ERROR al ensamblar {sample_name}. Código de error: {e}")
        continue

print("\n🏁 Proceso de ensamblado metagenómico finalizado.")