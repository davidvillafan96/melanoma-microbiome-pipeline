import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

# --- Configuración ---
INPUT_FILE = "data/features/taxonomy_matrix.tsv"
OUTPUT_DIR = "results/figures"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 1. Carga inteligente
df = pd.read_csv(INPUT_FILE, sep='\t', comment='#')
df.rename(columns={df.columns[0]: 'clade_name'}, inplace=True)

# 2. Conversión forzada a numérico
# Convertimos todas las columnas (excepto clade_name) a números, si hay errores los vuelve NaN
for col in df.columns[1:]:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

# 3. Filtrado y Limpieza de nombres
# Solo especies (s__), sin subespecies (t__)
df_species = df[df['clade_name'].str.contains(r's__') & ~df['clade_name'].str.contains(r't__')].copy()
df_species['species'] = df_species['clade_name'].str.split('|').str[-1].str.replace('s__', '')

# 4. Preparación para graficar
# Seleccionamos las 15 más abundantes
df_species['mean_abundance'] = df_species.iloc[:, 1:-1].mean(axis=1)
top_15 = df_species.nlargest(15, 'mean_abundance')

# Creamos el dataframe de ploteo
df_plot = top_15.set_index('species').drop(columns=['clade_name', 'mean_abundance']).T

# --- 5. Generación de Gráficos ---

# Gráfico de Barras Apiladas
plt.figure(figsize=(14, 8))
df_plot.plot(kind='bar', stacked=True, cmap='Paired', width=0.8, ax=plt.gca())
plt.title('Microbiota Composition (Top 15 Species)', fontsize=16, fontweight='bold')
plt.ylabel('Relative Abundance', fontsize=12)
plt.xlabel('Sample ID', fontsize=12)
plt.legend(title="Species", bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "composicion_clean.png"), dpi=300)
print("✅ Gráfico de composición guardado.")

# Gráfico de Cajas (Boxplot)
df_melted = df_plot.reset_index().melt(id_vars='index', var_name='Species', value_name='Abundance')
plt.figure(figsize=(12, 8))
sns.boxplot(data=df_melted, x='Abundance', y='Species', palette='Set2', orient='h')
plt.title('Abundance Distribution (Top 15 Species)', fontsize=16, fontweight='bold')
plt.xlabel('Relative Abundance', fontsize=12)
plt.ylabel('Species', fontsize=12)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "distribucion_clean.png"), dpi=300)
print("✅ Gráfico de distribución guardado.")

plt.show()