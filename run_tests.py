#!/usr/bin/env python
"""
Test runner script for Climate Dashboard project.

Usage:
    python run_tests.py              # Run all tests
    python run_tests.py --unit       # Run only unit tests
    python run_tests.py --integration # Run only integration tests
    python run_tests.py --api        # Run only API tests
    python run_tests.py --coverage   # Run tests with coverage report
"""

import sys
import subprocess
from pathlib import Path

def main():
    """Run pytest with appropriate arguments."""
    args = sys.argv[1:]
    
    pytest_args = []
    
    if '--unit' in args:
        pytest_args.extend(['-m', 'unit'])
    elif '--integration' in args:
        pytest_args.extend(['-m', 'integration'])
    elif '--api' in args:
        pytest_args.extend(['-m', 'api'])
    elif '--model' in args:
        pytest_args.extend(['-m', 'model'])
    elif '--database' in args:
        pytest_args.extend(['-m', 'database'])
    
    if '--coverage' in args:
        pytest_args.extend([
            '--cov=backend',
            '--cov-report=html',
            '--cov-report=term-missing'
        ])
    
    if '--verbose' in args or '-v' in args:
        pytest_args.append('-v')
    
    # Run pytest
    result = subprocess.run(['pytest'] + pytest_args, cwd=Path(__file__).parent)
    sys.exit(result.returncode)

if __name__ == '__main__':
    main()

