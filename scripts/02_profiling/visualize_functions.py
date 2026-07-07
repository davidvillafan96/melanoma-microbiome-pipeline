import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Cargar resultados del script anterior
df = pd.read_csv("functional_enrichment_results.csv")
# Filtrar top 20 funciones significativas
top_functions = df[df['p_value'] < 0.05].head(20)

plt.figure(figsize=(10, 8))
sns.barplot(data=top_functions, x='log2FC', y='Function', palette='viridis')
plt.title('Funciones Enriquecidas: Respondedores vs No Respondedores')
plt.xlabel('Log2 Fold Change')
plt.savefig("functional_enrichment_plot.png", dpi=300)
plt.show()