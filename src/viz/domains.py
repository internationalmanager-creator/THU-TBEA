"""Definicion canonica de dominios.

Fuente unica: cualquier dominio nuevo se anade aqui y aparece
automaticamente en todos los idiomas y en todas las vistas.
"""

DOMAINS = {
    "cosmologia": {
        "es": "Cosmologia", "en": "Cosmology", "de": "Kosmologie",
        "color": "#6C5CE7",
    },
    "geofisica": {
        "es": "Geofisica", "en": "Geophysics", "de": "Geophysik",
        "color": "#00B894",
    },
    "biologia": {
        "es": "Biologia", "en": "Biology", "de": "Biologie",
        "color": "#E17055",
    },
    "neurofisiologia": {
        "es": "Neurofisiologia", "en": "Neurophysiology",
        "de": "Neurophysiologie", "color": "#0984E3",
    },
    "cuantica": {
        "es": "Cuantica", "en": "Quantum", "de": "Quantenphysik",
        "color": "#FDCB6E",
    },
    "antropologia": {
        "es": "Antropologia", "en": "Anthropology", "de": "Anthropologie",
        "color": "#E84393",
    },
    "otros": {
        "es": "Otros", "en": "Others", "de": "Andere",
        "color": "#636E72",
    },
    "test": {
        "es": "Test", "en": "Test", "de": "Test",
        "color": "#A0A0A0",
    },
}

DEFAULT_COLOR = "#6C5CE7"


def domain_name(code, lang="es"):
    """Devuelve el nombre traducido del dominio. Fallback: code."""
    d = DOMAINS.get(code)
    if not d:
        return code
    return d.get(lang, d.get("es", code))


def domain_color(code):
    """Devuelve el color asignado al dominio. Fallback: DEFAULT_COLOR."""
    d = DOMAINS.get(code)
    return d["color"] if d else DEFAULT_COLOR


def domain_names(lang):
    """Dict {code: name} para el idioma dado."""
    return {k: v.get(lang, v.get("es", k)) for k, v in DOMAINS.items()}


def colors_map():
    """Dict {code: color}."""
    return {k: v["color"] for k, v in DOMAINS.items()}


def listar():
    """Lista de codigos de dominio en orden canonico."""
    return list(DOMAINS.keys())


if __name__ == "__main__":
    from tqdm import tqdm
    print("=== Test domains.py ===")
    for code in tqdm(listar(), desc="Dominios", ncols=80):
        nombre_es = domain_name(code, "es")
        nombre_en = domain_name(code, "en")
        color = domain_color(code)
        print(f"  {code:<18} {nombre_es:<18} {nombre_en:<20} {color}")
    # Verificaciones basicas
    assert domain_name("cosmologia", "en") == "Cosmology"
    assert domain_name("desconocido") == "desconocido"
    assert domain_color("desconocido") == DEFAULT_COLOR
    assert len(domain_names("de")) == len(DOMAINS)
    assert len(colors_map()) == len(DOMAINS)
    print("=== TEST OK ===")