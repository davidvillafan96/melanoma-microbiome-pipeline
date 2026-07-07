import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
from sklearn.decomposition import PCA

# Asegurar que el directorio existe
os.makedirs("results/figures", exist_ok=True)

# 1. Cargar datos
df = pd.read_csv("data/processed/final_ml_ready_dataset.csv", index_col="Sample")

# 2. Definir metadata y especies
metadata_cols = ['Study_Clin_Response', 'Age', 'Sex', 'Alpha_Diversity_Shannon', 
                 'Alpha_Diversity_InvSimpson', 'Age_Scaled']
species_cols = [c for c in df.columns if c not in metadata_cols]

print(f"Generando visualizaciones para {len(species_cols)} especies...")

# --- A) HEATMAP (Con escala horizontal superior) ---
g = sns.clustermap(
    df[species_cols].T, 
    cmap="RdBu_r", 
    standard_scale=0, 
    figsize=(14, 12), 
    row_cluster=True, 
    col_cluster=True,
    # Ajuste de posición: (left, bottom, width, height)
    cbar_pos=(0.05, 0.95, 0.2, 0.03), 
    cbar_kws={"orientation": "horizontal"}
)
g.fig.suptitle("Perfiles bacterianos (CLR)", y=1.05)
g.savefig("results/figures/clustered_heatmap.png", dpi=300, bbox_inches='tight')
plt.close()

# --- B) ALPHA DIVERSITY (Boxplots) ---
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
sns.boxplot(data=df, x='Study_Clin_Response', y='Alpha_Diversity_Shannon', ax=axes[0], palette="viridis")
sns.boxplot(data=df, x='Study_Clin_Response', y='Alpha_Diversity_InvSimpson', ax=axes[1], palette="magma")
axes[0].set_title("Shannon Index")
axes[1].set_title("InvSimpson Index")
plt.tight_layout()
plt.savefig("results/figures/alpha_diversity.png", dpi=300, bbox_inches='tight')
plt.close()

# --- C) PCA (Beta Diversity) ---
pca = PCA(n_components=2)
pca_results = pca.fit_transform(df[species_cols])
df_pca = pd.DataFrame(data=pca_results, columns=['PC1', 'PC2'], index=df.index)
df_pca['Response'] = df['Study_Clin_Response']

plt.figure(figsize=(8, 6))
sns.scatterplot(data=df_pca, x='PC1', y='PC2', hue='Response', s=100, style='Response')
plt.title(f"PCA Taxonómico (PC1: {pca.explained_variance_ratio_[0]*100:.1f}%, PC2: {pca.explained_variance_ratio_[1]*100:.1f}%)")
plt.savefig("results/figures/pca_beta_diversity.png", dpi=300, bbox_inches='tight')
plt.close()

print("🏁 Visualizaciones guardadas exitosamente en 'results/figures/'")