"""
Orchestration du pipeline ETL multi-sources avec Prefect.
  extract (Postgres + calendrier + API météo)  ->  dbt run  ->  dbt test

Pipeline rejouable de bout en bout en une commande :  python etl/flow.py
"""
import subprocess
import sys
from pathlib import Path

from prefect import flow, task, get_run_logger

ROOT = Path(__file__).resolve().parent.parent
WH = ROOT / "warehouse"
DBT_ENV = {"DBT_PROFILES_DIR": str(WH)}


def _run(cmd, cwd=None, env=None):
    import os
    log = get_run_logger()
    full_env = {**os.environ, **(env or {})}
    r = subprocess.run(cmd, cwd=cwd, env=full_env, capture_output=True, text=True)
    if r.stdout:
        log.info(r.stdout.strip()[-3000:])
    if r.returncode != 0:
        log.error((r.stderr or r.stdout).strip()[-3000:])
        raise RuntimeError(f"Échec : {' '.join(cmd)}")


@task(retries=2, retry_delay_seconds=10)
def extract():
    _run([sys.executable, str(ROOT / "etl" / "extract.py")])


@task(retries=1)
def dbt_run():
    _run([sys.executable, "-m", "dbt.cli.main", "run"], cwd=str(WH), env=DBT_ENV)


@task(retries=1)
def dbt_test():
    _run([sys.executable, "-m", "dbt.cli.main", "test"], cwd=str(WH), env=DBT_ENV)


@flow(name="entrepot-etl")
def pipeline():
    extract()
    dbt_run()
    dbt_test()


if __name__ == "__main__":
    pipeline()
