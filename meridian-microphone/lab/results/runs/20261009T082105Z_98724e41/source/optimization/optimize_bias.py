"""Use the same constrained optimizer for declared bias/current/servo parameters.

Example: .venv/bin/python optimization/optimize_bias.py fixture_0001
--parameters BIAS_R POLAR_R --iterations 3
"""
import runpy
from pathlib import Path

if __name__=='__main__':
    runpy.run_path(str(Path(__file__).with_name('optimize_values.py')),run_name='__main__')
