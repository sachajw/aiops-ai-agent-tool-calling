#!/usr/bin/env python3
"""
Docker Path Finder - Helps locate docker on your system

Run this to find where docker is installed and update the code if needed.
"""

import os
import shutil
import subprocess


def find_docker():
    """Find docker executable on the system."""
    print("🔍 Searching for docker executable...\n")

    # Method 1: shutil.which (respects PATH)
    print("Method 1: Using shutil.which() (checks PATH)")
    docker_path = shutil.which('docker')
    if docker_path:
        print(f"  ✅ Found: {docker_path}")
    else:
        print(f"  ❌ Not found in PATH")
    print()

    # Method 2: Common locations
    print("Method 2: Checking common locations")
    common_paths = [
        '/usr/local/bin/docker',
        '/opt/homebrew/bin/docker',
        '/usr/bin/docker',
        '/bin/docker',
        '/opt/local/bin/docker',
        '/snap/bin/docker',
        '~/.orbstack/bin/docker',
        '/Applications/OrbStack.app/Contents/MacOS/docker',
    ]

    found_locations = []
    for path in common_paths:
        expanded = os.path.expanduser(path)
        if os.path.isfile(expanded) and os.access(expanded, os.X_OK):
            print(f"  ✅ Found: {expanded}")
            found_locations.append(expanded)
        else:
            print(f"  ❌ Not found: {path}")

    print()

    # Method 3: Try running docker --version
    print("Method 3: Testing if docker command works")
    try:
        result = subprocess.run(
            ['docker', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"  ✅ Docker command works!")
            print(f"     {result.stdout.strip()}")
        else:
            print(f"  ❌ Docker command failed")
            print(f"     {result.stderr.strip()}")
    except FileNotFoundError:
        print(f"  ❌ Docker command not found (FileNotFoundError)")
    except Exception as e:
        print(f"  ❌ Error: {e}")

    print()

    # Method 4: Check $PATH
    print("Method 4: Your current PATH")
    path_var = os.environ.get('PATH', '')
    print(f"  PATH contains {len(path_var.split(':'))} directories:")
    for i, path_dir in enumerate(path_var.split(':'), 1):
        has_docker = os.path.isfile(os.path.join(path_dir, 'docker'))
        marker = "🐳" if has_docker else "  "
        print(f"  {marker} {i}. {path_dir}")

    print()

    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    if docker_path:
        print(f"✅ Docker found via shutil.which(): {docker_path}")
        print("\n✅ Python should be able to find docker automatically.")
        print("   If you still get errors, there might be an environment issue.")
    elif found_locations:
        print(f"✅ Docker found at: {found_locations[0]}")
        print("\n⚠️  Docker is NOT in your Python PATH.")
        print("   The code should still find it using hardcoded paths.")
        print(f"   If not, you can explicitly use: {found_locations[0]}")
    else:
        print("❌ Docker not found anywhere!")
        print("\nPossible solutions:")
        print("1. Install Docker/OrbStack:")
        print("   brew install orbstack")
        print("   OR download Docker Desktop from docker.com")
        print()
        print("2. Ensure it's running (open the app)")
        print()
        print("3. Add to PATH (for zsh):")
        print('   echo \'export PATH="/usr/local/bin:/opt/homebrew/bin:$PATH"\' >> ~/.zshrc')
        print('   source ~/.zshrc')

    print("=" * 70)


if __name__ == "__main__":
    find_docker()
