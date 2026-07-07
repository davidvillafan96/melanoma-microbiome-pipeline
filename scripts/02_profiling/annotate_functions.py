import os
import subprocess

# Rutas
PROTEIN_DIR = "/Users/davidvillafan96/Documents/melanoma_microbiome_project/data/features/predicted_proteins"
ANNOTATION_DIR = "/Users/davidvillafan96/Documents/melanoma_microbiome_project/data/features/functional_annotations"
os.makedirs(ANNOTATION_DIR, exist_ok=True)

protein_files = [f for f in os.listdir(PROTEIN_DIR) if f.endswith(".faa")]

print(f"🧬 Iniciando anotación funcional para {len(protein_files)} muestras...")

for f in protein_files:
    input_faa = os.path.join(PROTEIN_DIR, f)
    output_prefix = os.path.join(ANNOTATION_DIR, f.replace(".faa", ""))
    
    # Comando emapper: usa --meta porque tus muestras son metagenómicas
    cmd = [
        "emapper.py",
        "-i", input_faa,
        "-o", output_prefix,
        "--meta",  # Modo metagenómico
        "--no_annot", # Opcional: solo si quieres velocidad
        "--cpu", "4"
    ]
    
    print(f"📊 Anotando {f}...")
    subprocess.run(cmd, check=True)