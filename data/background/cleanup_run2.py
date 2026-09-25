# -*- coding: utf-8 -*-
"""Limpiar run_id=2 (aborted) en SQLite."""
import sqlite3
from pathlib import Path

LAB = Path(r"C:\Users\kg4tr\Documents\Investigacion_lab_secreto")
DB = LAB / "data" / "raw" / "cosmic-birefringence-planck-act" / "data" / "computed" / "mcmc_runs.sqlite"

conn = sqlite3.connect(str(DB))
cur = conn.cursor()

# Marcar run_id=2 como aborted
cur.execute("""
    UPDATE mcmc_runs
    SET status='aborted', end_time=last_update
    WHERE run_id=2 AND status='running'
""")
conn.commit()
print(f"Filas afectadas: {cur.rowcount}")

# Mostrar estado actual
print()
print("Estado de las corridas:")
cur.execute("SELECT run_id, status, current_step, total_steps, last_update FROM mcmc_runs ORDER BY run_id DESC")
for r in cur.fetchall():
    print(f"  run_id={r[0]}  status={r[1]:10s}  {r[2]}/{r[3]}  last={r[4]}")

conn.close()
