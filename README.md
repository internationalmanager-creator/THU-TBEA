# PIR — Programa de Investigacion Rigurosa

**Investigador:** Erick Duque
**ORCID:** 0009-0004-1245-5464
**Contacto:** international_manager@comllcusa.com

**Estado:** PRIVADO. No se publica hasta decision explicita del PI.

---

## Que es esto

Un repositorio de investigacion cientifica auditable. Cada dato tiene
provenance completa (cita ISO 690 + DOI + instrumento + condiciones +
hash SHA-256). Cada hipotesis se pre-registra antes de ver los datos.
Cada decision queda encadenada en un log cronografico criptografico.

El repositorio integra ademas el programa **THU-TBEA 5.3** (Teoria
Helicoidal Universal) como primer programa concreto de investigacion.

---

## Estructura de directorios

    .github/                CI/CD (audit, chain-guard, release)
    .githooks/              Hooks locales (pre-commit, pre-push, commit-msg)
    .streamlit/             Config del dashboard

    data/                   Base de datos SQLite + inputs + provenance
    docs/                   Documentacion adicional
    outputs/                Salidas regenerables (audit reports, logs)

    paper/thu/src/          Fuentes LaTeX multi-idioma (.tex)
    paper/thu/dist/         PDFs compilados (ES/EN/DE)
    paper/thu/build/        Intermedios de compilacion

    registry/               Registro PIR
    registry/preregistro/   Hipotesis pre-registradas (H-YYYY-NNN)
    registry/prisma/        Revisiones sistematicas (PRISMA 2020)
    registry/thu/           Contenido estructurado de THU-TBEA

    replication/            Paquetes de replicacion verificables
    seeds/                  Manifests SHA-256 encadenados

    src/                    Codigo fuente
    src/investigaciones/    Tests pre-declarados de hipotesis (INV-*)
    src/thu/                Modulos THU-TBEA
    src/viz/                Capa de visualizacion

    tests/                  Tests automatizados (pytest)

---

## Estandares aplicados

- PRISMA 2020 (revisiones sistematicas)
- Lakatos MSRP (estructura de programa)
- Popper (falsabilidad)
- ISO 8000 (calidad de datos)
- ISO 690 (citas)
- FAIR (Findable, Accessible, Interoperable, Reusable)
- COPE (etica)
- ISO-GUM (incertidumbres)

---

## Documentacion

- `docs/CI_CD.md` — Pipelines y proteccion automatica
- `docs/INVESTIGACIONES.md` — Ciclo completo de investigacion
- `registry/GLOSARIO.md` — Vocabulario y etiquetas
- `registry/DECISIONS.md` — Decisiones de diseno
- `registry/chronolog.md` — Registro cronografico exportado

---

## Ciclo de trabajo

    # Setup inicial (una vez)
    python -m venv venv
    source venv/bin/activate          # Linux/WSL
    # o: venv\Scripts\activate       # Windows
    pip install -r requirements.txt
    python src/freeze.py              # genera requirements.lock
    ./.githooks/install.sh            # instala hooks

    # Ejecucion completa
    ./run_all.sh --seed               # pipeline observable

    # Nueva investigacion
    python src/preregistro.py nuevo --titulo "..." --categoria X
    # ... completar y bloquear
    python src/preregistro.py bloquear H-2026-XXX

    # Dashboard general
    streamlit run app.py

    # Dashboard THU-TBEA dedicado
    streamlit run app_thu.py

---

## Verificacion antes de publicar

    python src/chronolog.py verificar
    python src/audit_report.py --verify outputs/audit_report_latest.txt
    python -m pytest tests/ -v
    python src/replication.py --verify replication/package_*.zip

Los cuatro en verde = repositorio auditable.

---

## Licencia

CC-BY-4.0 (aplicable solo tras publicacion explicita)

---

## Contacto

Erick Duque — international_manager@comllcusa.com
ORCID: 0009-0004-1245-5464