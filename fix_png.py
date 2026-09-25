import re
import os

file_path = 'data/background/run_figures.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Busca todas las llamadas a savefig que guarden como .pdf
pattern = re.compile(r"savefig\((['\"])(.*?)\.pdf\1\)")

def replacer(match):
    quote = match.group(1)
    path = match.group(2)
    # Extrae el nombre del archivo sin extension
    filename = os.path.basename(path)
    # Construye la ruta para el PNG en la carpeta correcta
    png_path = f"paper/thu/figures/{filename}.png"
    # Devuelve el guardado original en PDF y agrega el guardado en PNG
    return f"savefig({quote}{path}.pdf{quote})\n    plt.savefig({quote}{png_path}{quote}, dpi=150, bbox_inches='tight')"

# Reemplaza en todo el archivo
new_content = pattern.sub(replacer, content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Archivo run_figures.py modificado con exito para guardar PNGs.")
