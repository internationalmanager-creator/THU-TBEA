"""Internacionalizacion EN/SP/DE.

Los nombres de dominio NO se duplican aqui: vienen de `domains.py`.
Este modulo solo aporta las claves de UI (labels, titulos, textos).
"""
try:
    from .domains import domain_names
except ImportError:
    # Ejecucion directa como script: anadir src/ al path
    import sys as _sys
    from pathlib import Path as _Path
    _sys.path.insert(0, str(_Path(__file__).parent.parent))
    from viz.domains import domain_names


_BASE = {
    "en": {
        "title": "Rigorous Research Program",
        "subtitle": "Auditable Scientific Investigation",
        "tagline": "Data integrity, pre-registration, and reproducibility",
        "lang_label": "Language",
        "nav_section": "Section",
        "nav_home": "Home", "nav_atlas": "Atlas",
        "nav_categories": "Categories", "nav_provenance": "Provenance",
        "nav_progress": "Progress", "nav_method": "Methodology",
        "nav_chronolog": "Chronolog",
        "kpi_total": "Total Entities", "kpi_categories": "Categories",
        "kpi_completed": "Documented", "kpi_orders": "Log Range",
        "kpi_events": "Log Events",
        "atlas_title": "Distribution Atlas",
        "atlas_theory": "Equation: log10(value) reveals structure at orders of magnitude.",
        "cat_title": "Distribution by Category",
        "cat_theory": "Count per category (bar) and proportional distribution (pie).",
        "prov_title": "Provenance Records",
        "prov_theory": ("Every entity carries full provenance: citation, DOI, "
                         "method, conditions, SHA-256 hash. Provenance is append-only: "
                         "corrections create new versions."),
        "prov_select": "Select entity",
        "prov_citation": "Citation", "prov_doi": "DOI",
        "prov_method": "Method", "prov_conditions": "Conditions",
        "prov_extract": "Extract", "prov_repro": "Reproducibility",
        "prov_version": "Version",
        "prog_title": "Documentation Progress",
        "prog_theory": "Progress bar shows fraction of documented entities.",
        "prog_goal": "Goal",
        "chrono_title": "Chronological Log",
        "chrono_theory": ("Hash-chained event log. Each event's hash depends on the "
                          "previous one: H_i = SHA256(ts | tipo | entidad | desc | "
                          "payload | H_{i-1}). Any tampering breaks the chain."),
        "chrono_verify": "Verify chain integrity",
        "chrono_chain_ok": "Chain OK — integrity verified",
        "chrono_chain_broken": "Chain BROKEN at event id {eid}",
        "chrono_export": "Export to Markdown",
        "chrono_show": "Show last",
        "method_title": "Methodology",
        "method_epistemic": "Epistemic Framework",
        "method_lakatos": "Lakatosian Structure (MSRP)",
        "method_fair": "FAIR Principles",
        "method_audit": "Cryptographic Auditability",
        "method_privacy": "Privacy",
        "method_decisions": "Design Decisions",
        "method_log": "Epistemic Log",
        "privacy_text": ("Private repository. Not for public distribution "
                          "until explicit decision."),
        "footer": "PIR - Rigorous Research Program",
        "reload": "Reload data",
    },
    "es": {
        "title": "Programa de Investigacion Rigurosa",
        "subtitle": "Investigacion Cientifica Auditable",
        "tagline": "Integridad de datos, pre-registro y reproducibilidad",
        "lang_label": "Idioma",
        "nav_section": "Seccion",
        "nav_home": "Inicio", "nav_atlas": "Atlas",
        "nav_categories": "Categorias", "nav_provenance": "Procedencia",
        "nav_progress": "Progreso", "nav_method": "Metodologia",
        "nav_chronolog": "Cronologia",
        "kpi_total": "Entidades Totales", "kpi_categories": "Categorias",
        "kpi_completed": "Documentadas", "kpi_orders": "Rango Log",
        "kpi_events": "Eventos",
        "atlas_title": "Atlas de Distribucion",
        "atlas_theory": "log10(valor) revela estructura en ordenes de magnitud.",
        "cat_title": "Distribucion por Categoria",
        "cat_theory": "Conteo por categoria (barras) y distribucion proporcional (pastel).",
        "prov_title": "Registros de Procedencia",
        "prov_theory": ("Cada entidad lleva procedencia completa: cita, DOI, metodo, "
                         "condiciones, hash SHA-256. La procedencia es append-only: "
                         "las correcciones crean nuevas versiones."),
        "prov_select": "Seleccionar entidad",
        "prov_citation": "Cita", "prov_doi": "DOI",
        "prov_method": "Metodo", "prov_conditions": "Condiciones",
        "prov_extract": "Extracto", "prov_repro": "Reproducibilidad",
        "prov_version": "Version",
        "prog_title": "Progreso de Documentacion",
        "prog_theory": "La barra muestra la fraccion documentada.",
        "prog_goal": "Meta",
        "chrono_title": "Registro Cronografico",
        "chrono_theory": ("Log de eventos encadenado por hash. El hash de cada evento "
                          "depende del anterior: H_i = SHA256(ts | tipo | entidad | "
                          "desc | payload | H_{i-1}). Cualquier alteracion rompe la cadena."),
        "chrono_verify": "Verificar integridad",
        "chrono_chain_ok": "Cadena OK - integridad verificada",
        "chrono_chain_broken": "Cadena ROTA en evento id {eid}",
        "chrono_export": "Exportar a Markdown",
        "chrono_show": "Mostrar ultimos",
        "method_title": "Metodologia",
        "method_epistemic": "Marco Epistemico",
        "method_lakatos": "Estructura Lakatosiana (MSRP)",
        "method_fair": "Principios FAIR",
        "method_audit": "Auditabilidad Criptografica",
        "method_privacy": "Privacidad",
        "method_decisions": "Decisiones de Diseno",
        "method_log": "Log Epistemico",
        "privacy_text": "Repositorio privado. No se distribuye hasta decision explicita.",
        "footer": "PIR - Programa de Investigacion Rigurosa",
        "reload": "Recargar datos",
    },
    "de": {
        "title": "Programm fur Rigorose Forschung",
        "subtitle": "Prufbare Wissenschaftliche Untersuchung",
        "tagline": "Datenintegritat, Vorregistrierung und Reproduzierbarkeit",
        "lang_label": "Sprache",
        "nav_section": "Abschnitt",
        "nav_home": "Startseite", "nav_atlas": "Atlas",
        "nav_categories": "Kategorien", "nav_provenance": "Herkunft",
        "nav_progress": "Fortschritt", "nav_method": "Methodik",
        "nav_chronolog": "Chronolog",
        "kpi_total": "Entitaten Gesamt", "kpi_categories": "Kategorien",
        "kpi_completed": "Dokumentiert", "kpi_orders": "Log-Bereich",
        "kpi_events": "Ereignisse",
        "atlas_title": "Verteilungsatlas",
        "atlas_theory": "log10(Wert) zeigt Struktur uber Grossenordnungen.",
        "cat_title": "Verteilung nach Kategorie",
        "cat_theory": "Anzahl pro Kategorie (Balken) und proportionale Verteilung (Kreis).",
        "prov_title": "Herkunftsnachweise",
        "prov_theory": ("Jede Entitat tragt vollstandige Herkunft: Zitat, DOI, "
                         "Methode, Bedingungen, SHA-256 Hash. Herkunft ist "
                         "append-only: Korrekturen erzeugen neue Versionen."),
        "prov_select": "Entitat auswahlen",
        "prov_citation": "Zitat", "prov_doi": "DOI",
        "prov_method": "Methode", "prov_conditions": "Bedingungen",
        "prov_extract": "Auszug", "prov_repro": "Reproduzierbarkeit",
        "prov_version": "Version",
        "prog_title": "Dokumentationsfortschritt",
        "prog_theory": "Der Balken zeigt den dokumentierten Anteil.",
        "prog_goal": "Ziel",
        "chrono_title": "Chronologisches Protokoll",
        "chrono_theory": ("Hash-verkettetes Ereignisprotokoll. Der Hash jedes "
                          "Ereignisses hangt vom vorherigen ab: H_i = SHA256("
                          "ts | typ | entitat | beschr | payload | H_{i-1}). "
                          "Jede Manipulation bricht die Kette."),
        "chrono_verify": "Kette verifizieren",
        "chrono_chain_ok": "Kette OK - Integritat verifiziert",
        "chrono_chain_broken": "Kette GEBROCHEN bei Ereignis id {eid}",
        "chrono_export": "Nach Markdown exportieren",
        "chrono_show": "Zeige letzte",
        "method_title": "Methodik",
        "method_epistemic": "Epistemischer Rahmen",
        "method_lakatos": "Lakatos-Struktur (MSRP)",
        "method_fair": "FAIR-Prinzipien",
        "method_audit": "Kryptografische Prufbarkeit",
        "method_privacy": "Datenschutz",
        "method_decisions": "Design-Entscheidungen",
        "method_log": "Epistemisches Protokoll",
        "privacy_text": ("Privates Repository. Keine Verteilung bis zur "
                          "ausdrucklichen Entscheidung."),
        "footer": "PIR - Programm fur Rigorose Forschung",
        "reload": "Daten neu laden",
    },
}


def get_translations(lang="es"):
    """Devuelve el dict de traducciones + domain_names para el idioma."""
    base = _BASE.get(lang, _BASE["es"]).copy()
    base["domain_names"] = domain_names(lang)
    return base


def available_languages():
    return list(_BASE.keys())


def language_label(code):
    return {"en": "English", "es": "Espanol", "de": "Deutsch"}.get(code, code)


if __name__ == "__main__":
    from tqdm import tqdm
    print("=== Test i18n.py ===")
    for lang in tqdm(available_languages(), desc="Idiomas", ncols=80):
        t = get_translations(lang)
        n_keys = len(t)
        n_domains = len(t["domain_names"])
        print(f"  {lang} ({language_label(lang)}): "
              f"{n_keys} claves, {n_domains} dominios")
    # Verificaciones
    t_es = get_translations("es")
    t_en = get_translations("en")
    assert t_es["title"] != t_en["title"]
    assert t_es["domain_names"]["cosmologia"] == "Cosmologia"
    assert t_en["domain_names"]["cosmologia"] == "Cosmology"
    assert "chronolog" in [k.replace("nav_", "") for k in t_es.keys()]
    print("=== TEST OK ===")