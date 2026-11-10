"""Reproduce the full analysis locally, without network access."""
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
SCRIPTS=['audit_data.py','baseline.py','robustness.py','staged_testing.py','error_analysis.py','incremental_value.py','nonlinear_comparison.py','final_checks.py','verify_results.py','build_report.py']
def main():
    env=os.environ.copy(); env['OMP_NUM_THREADS']='1'; env['MPLCONFIGDIR']=str(ROOT/'outputs/.matplotlib')
    for name in SCRIPTS:
        print(f'Running {name}',flush=True)
        subprocess.run([sys.executable,str(ROOT/'scripts'/name)],cwd=ROOT,env=env,check=True)
    print('Completed analysis and report. No external publication performed.')
if __name__=='__main__': main()
