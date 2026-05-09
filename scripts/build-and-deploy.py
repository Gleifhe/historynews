#!/usr/bin/env python3
"""
build-and-deploy.py — Build the Hugo site, validate, and optionally deploy.

Usage:
    python scripts/build-and-deploy.py                # Build + validate only
    python scripts/build-and-deploy.py --deploy        # Build + validate + git push
"""

import os
import subprocess
import sys
import argparse


def run(cmd, cwd=None):
    """Run a command and return (success, output)."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    return result.returncode == 0, result.stdout + result.stderr


def main():
    parser = argparse.ArgumentParser(description='Build and deploy History News')
    parser.add_argument('--deploy', action='store_true', help='Git commit and push after build')
    args = parser.parse_args()

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Step 1: Validate articles
    print('=' * 50)
    print('Step 1: Validating articles...')
    print('=' * 50)
    ok, out = run(f'python "{os.path.join(root, "scripts", "validate-articles.py")}"', cwd=root)
    print(out)
    if not ok:
        print('Validation failed. Fix issues before building.')
        sys.exit(1)

    # Step 2: Build Hugo site
    print('=' * 50)
    print('Step 2: Building Hugo site...')
    print('=' * 50)
    ok, out = run('hugo', cwd=root)
    print(out)
    if not ok:
        print('Hugo build failed.')
        sys.exit(1)

    # Step 3: Check page count
    import re
    m = re.search(r'Pages\s*\│\s*(\d+)', out)
    if m:
        print(f'Pages built: {m.group(1)}')

    # Step 4: Deploy if requested
    if args.deploy:
        print('=' * 50)
        print('Step 3: Deploying to GitHub...')
        print('=' * 50)

        ok, out = run('git add -A', cwd=root)
        ok, out = run('git status --short', cwd=root)
        if not out.strip():
            print('Nothing to commit.')
            return

        print(f'Changes:\n{out}')
        ok, out = run('git commit -m "Content update: new articles and site updates"', cwd=root)
        print(out)

        ok, out = run('git push', cwd=root)
        print(out)
        if ok:
            print('Deployed successfully.')
        else:
            print('Push failed.')
            sys.exit(1)
    else:
        print('\nBuild successful. Run with --deploy to push to GitHub.')


if __name__ == '__main__':
    main()
