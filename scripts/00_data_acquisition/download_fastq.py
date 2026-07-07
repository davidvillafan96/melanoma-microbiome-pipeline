import os
import requests
import time

# ⚙️ CONFIGURACIÓN DEL SCRIPT
TEST_MODE = False      # 🔓 ¡Ya vimos que funciona! Ponlo en False para que baje todo de corrido.
LIMIT_SAMPLES = 2     
MAX_RETRIES = 3        # Número de veces que reintentará si el servidor se cuelga
TIMEOUT_SECONDS = 30   # Si el servidor no envía datos en 30 segundos, rompe el bucle y reintenta

INPUT_IDS_PATH = "data/clinical/samples_ids.txt"
OUTPUT_DIR = "data/raw"

os.makedirs(OUTPUT_DIR, exist_ok=True)

print("🌐 Leyendo la lista de códigos de muestras...")
try:
    with open(INPUT_IDS_PATH, "r") as f:
        run_ids = [line.strip() for line in f if line.strip()]
except FileNotFoundError:
    print(f"❌ Error: No se encontró el archivo '{INPUT_IDS_PATH}'.")
    exit()

if TEST_MODE:
    print(f"⚠️ MODO DE PRUEBA ACTIVADO. Solo procesaremos las primeras {LIMIT_SAMPLES} muestras.")
    run_ids = run_ids[:LIMIT_SAMPLES]

print(f"🧬 Total de muestras a procesar: {len(run_ids)}")

for idx, run_id in enumerate(run_ids, 1):
    print(f"\n⚡ [{idx}/{len(run_ids)}] Buscando enlaces para: {run_id}...")
    
    ena_api_url = f"https://www.ebi.ac.uk/ena/portal/api/filereport?accession={run_id}&result=read_run&fields=fastq_ftp&format=tsv"
    
    try:
        response = requests.get(ena_api_url, timeout=15)
        if response.status_code != 200 or len(response.text.strip().split("\n")) <= 1:
            print(f"❌ La API de la ENA no devolvió datos válidos para {run_id}. Saltando...")
            continue
            
        lines = response.text.strip().split("\n")
        data_row = lines[1].split("\t")
        
        fastq_links_str = ""
        for item in data_row:
            if "fastq" in item or ".gz" in item:
                fastq_links_str = item
                break
        
        if not fastq_links_str:
            print(f"❌ No se encontró un enlace FASTQ válido para {run_id}")
            continue
            
        links = fastq_links_str.split(";")
        
        for link in links:
            download_url = f"http://{link}" if not link.startswith("http") else link
            file_name = os.path.basename(download_url)
            dest_path = os.path.join(OUTPUT_DIR, file_name)
            
            if os.path.exists(dest_path):
                print(f"⏩ El archivo {file_name} ya existe. Saltando...")
                continue
            
            # --- BUCLE DE REINTENTOS CON TOLERANCIA A CORTE DE RED ---
            success = False
            for attempt in range(1, MAX_RETRIES + 1):
                print(f"⬇️ Descargando {file_name} (Intento {attempt}/{MAX_RETRIES})...")
                try:
                    # Agregamos timeout para que no se quede colgado eternamente
                    with requests.get(download_url, stream=True, timeout=TIMEOUT_SECONDS) as r:
                        r.raise_for_status()
                        with open(dest_path, 'wb') as f_out:
                            for chunk in r.iter_content(chunk_size=1024 * 1024): # Bloques de 1MB para mayor velocidad
                                if chunk:
                                    f_out.write(chunk)
                    print(f"✅ Descarga completada con éxito: {file_name}")
                    success = True
                    break # Rompe el bucle de reintentos porque fue exitoso
                    
                except (requests.exceptions.RequestException, Exception) as e:
                    print(f"⚠️ Alerta: El intento {attempt} falló o se congeló. Motivo: {e}")
                    if os.path.exists(dest_path):
                        os.remove(dest_path) # Limpia el archivo parcial corrupto para el próximo intento
                    if attempt < MAX_RETRIES:
                        print("⏳ Esperando 10 segundos antes de volver a intentar...")
                        time.sleep(10)
            
            if not success:
                print(f"❌ Fallaron todos los intentos para descargar {file_name}. Se procesará en la siguiente ejecución general.")

    except Exception as e:
        print(f"❌ Ocurrió un problema de conexión con la API para {run_id}: {e}")

print("\n🏁 Proceso de descargas finalizado.")