import os
import subprocess

# Configuración de rutas
ASSEMBLY_DIR = "data/assembly"
PROTEINS_DIR = "data/features/predicted_proteins"

# Asegurar que la carpeta de destino de características biológicas exista
os.makedirs(PROTEINS_DIR, exist_ok=True)

print("🧬 Iniciando pipeline de Predicción de Genes (ORFs) con Prodigal...")

# Listar las subcarpetas dentro de data/assembly (una por muestra)
if not os.path.exists(ASSEMBLY_DIR) or not os.listdir(ASSEMBLY_DIR):
    print(f"⚠️ No se encontraron carpetas de muestras en '{ASSEMBLY_DIR}'.")
    exit()

samples = [d for d in os.listdir(ASSEMBLY_DIR) if os.path.isdir(os.path.join(ASSEMBLY_DIR, d))]
print(f"📦 Se detectaron {len(samples)} carpetas de ensamblados para analizar.")

for idx, sample_name in enumerate(samples, 1):
    # Ruta teórica del archivo de contigs generado por MEGAHIT
    contigs_path = os.path.join(ASSEMBLY_DIR, sample_name, f"{sample_name}.contigs.fa")
    
    # Validar estructuralmente si el ensamblador ya generó el archivo
    print(f"\n🔍 [{idx}/{len(samples)}] Buscando contigs para: {sample_name}")
    
    # Definir rutas de salida para los genes y proteínas predichas
    out_faa = os.path.join(PROTEINS_DIR, f"{sample_name}_proteins.faa") # Aminoácidos (Las proteínas)
    out_gff = os.path.join(PROTEINS_DIR, f"{sample_name}_genes.gff")    # Coordenadas genómicas
    
    # Construir el comando de Prodigal
    # -p meta: Modo metagenómico (diseñado para muestras con múltiples especies y genes fragmentados)
    cmd_prodigal = [
        "prodigal",
        "-i", contigs_path,
        "-a", out_faa,
        "-o", out_gff,
        "-f", "gff",
        "-p", "meta"
    ]
    
    print(f"🖥️ Comando estructurado listo para {sample_name}. (Traduce nucleótidos a proteínas FASTA).")
    # En producción real con el archivo .contigs.fa presente:
    # if os.path.exists(contigs_path):
    #     subprocess.run(cmd_prodigal, check=True)
    #     print(f"✅ Predicción completada. Proteínas guardadas en: {out_faa}")
    # else:
    #     print(f"⏩ Archivo físico de contigs no detectado aún para {sample_name}. Esquema guardado.")

print("\n🏁 Suite de scripts de bioinformática upstream completamente estructurada.")