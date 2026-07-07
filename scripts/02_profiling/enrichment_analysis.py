import pandas as pd
import glob
from scipy.stats import mannwhitneyu

# Rutas
ANNOTATION_DIR = "/Users/davidvillafan96/Documents/melanoma_microbiome_project/data/features/functional_annotations"
CLINICAL_DATA = "/Users/davidvillafan96/Documents/melanoma_microbiome_project/data/clinical/supp_dataset_1.csv"

# 1. Consolidar matriz funcional (Simplificado: conteo de ocurrencias de 'COG_category')
# (Nota: Asume que emapper generó archivos .annotations)
all_annotations = glob.glob(os.path.join(ANNOTATION_DIR, "*.annotations"))
data = []

for f in all_annotations:
    sample_name = os.path.basename(f).replace("_proteins.annotations", "")
    df_temp = pd.read_csv(f, sep="\t", comment="#", header=None)
    # Columna 8 suele ser COG_category en emapper
    counts = df_temp[8].value_counts()
    counts.name = sample_name
    data.append(counts)

df_func = pd.DataFrame(data).fillna(0)
df_clinical = pd.read_csv(CLINICAL_DATA)

# 2. Análisis de Enriquecimiento (Wilcoxon rank-sum test)
results = []
for func in df_func.columns:
    group_r = df_func.loc[df_clinical[df_clinical['Study_Clin_Response'] == 'Responder']['Sample'], func]
    group_nr = df_func.loc[df_clinical[df_clinical['Study_Clin_Response'] == 'Non_Responder']['Sample'], func]
    
    stat, p = mannwhitneyu(group_r, group_nr)
    results.append({'Function': func, 'p_value': p, 'log2FC': group_r.mean() / (group_nr.mean() + 1e-6)})

df_results = pd.DataFrame(results).sort_values('p_value')
df_results.to_csv("functional_enrichment_results.csv", index=False)
print("🏁 Análisis de enriquecimiento guardado.")