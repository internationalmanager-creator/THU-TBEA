import json
import pymupdf  # Usamos pymupdf en lugar de fitz (que esta deprecado)
import os

manifest_path = 'data/inventory/figuras_manifest.json'
output_dir = 'paper/thu/figures'

os.makedirs(output_dir, exist_ok=True)

try:
    with open(manifest_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    # Detectar si el JSON es una lista directa o un diccionario con una lista adentro
    if isinstance(data, list):
        manifest = data
    elif isinstance(data, dict):
        # Buscar la lista dentro del diccionario (puede llamarse 'figuras', 'items', 'data', etc.)
        manifest = data.get('figuras', data.get('items', data.get('data', [])))
        if not manifest and len(data) > 0:
            for value in data.values():
                if isinstance(value, list):
                    manifest = value
                    break
    else:
        print("Error: Formato de JSON no reconocido.")
        exit(1)

    for item in manifest:
        # Manejar caso donde el item sea un string (solo el nombre)
        if isinstance(item, str):
            name = item
            pdf_path = f"paper/thu/src/figures/{name}.pdf"
        elif isinstance(item, dict):
            pdf_path = item.get('pdf_path')
            name = item.get('name')
        else:
            continue
            
        if pdf_path and os.path.exists(pdf_path) and name:
            doc = pymupdf.open(pdf_path)
            page = doc.load_page(0)
            pix = page.get_pixmap(dpi=150)
            
            output_path = os.path.join(output_dir, f"{name}.png")
            pix.save(output_path)
            print(f"[OK] Convertido: {name}.png")
            doc.close()
        else:
            print(f"[FALTA] No se encontro PDF para: {name}")

    print("\n¡Listo! Todas las figuras deberian estar en paper/thu/figures/")
    
except Exception as e:
    print(f"Error: {e}")
