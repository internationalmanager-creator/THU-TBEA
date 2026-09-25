import pymupdf
import os
import glob

source_dir = 'paper/thu/src/figures'
output_dir = 'paper/thu/figures'
os.makedirs(output_dir, exist_ok=True)

pdf_files = glob.glob(os.path.join(source_dir, '*.pdf'))
print(f"Encontrados {len(pdf_files)} archivos PDF.")

for pdf_path in pdf_files:
    name = os.path.splitext(os.path.basename(pdf_path))[0]
    output_path = os.path.join(output_dir, f"{name}.png")
    try:
        doc = pymupdf.open(pdf_path)
        page = doc.load_page(0)
        pix = page.get_pixmap(dpi=150)
        pix.save(output_path)
        doc.close()
        print(f"[OK] Convertido: {name}.png")
    except Exception as e:
        print(f"[ERROR] No se pudo convertir {name}: {e}")

print("\n¡Listo! Los PNGs estan en paper/thu/figures/")
