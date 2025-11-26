#!/usr/bin/env python3
"""
Test script to verify the PyPI-based outdated check works correctly.
"""

import tempfile
import os
import json
import subprocess
import requests


def check_pip_outdated_direct(repo_path: str) -> str:
    """
    Direct implementation of check_pip_outdated for testing.
    """
    try:
        requirements_file = os.path.join(repo_path, "requirements.txt")

        if not os.path.exists(requirements_file):
            return json.dumps({"status": "error", "message": "No requirements.txt found"})

        # Read requirements
        with open(requirements_file, 'r') as f:
            requirements = f.readlines()

        # Parse package names (basic parsing)
        packages = []
        for line in requirements:
            line = line.strip()
            if line and not line.startswith('#'):
                # Simple parsing - handle package==version
                if '==' in line:
                    parts = line.split('==')
                    packages.append({
                        "name": parts[0].strip(),
                        "current": parts[1].strip() if len(parts) > 1 else "unknown"
                    })
                elif '>=' in line:
                    parts = line.split('>=')
                    packages.append({
                        "name": parts[0].strip(),
                        "current": parts[1].strip() if len(parts) > 1 else "unknown"
                    })
                else:
                    packages.append({
                        "name": line,
                        "current": "unspecified"
                    })

        # Check each package against PyPI directly
        outdated_list = []

        for pkg in packages:
            try:
                pkg_name = pkg["name"]
                current_version = pkg.get("current", "unspecified")

                # Skip if no version specified
                if current_version == "unspecified":
                    continue

                # Query PyPI API for latest version
                response = requests.get(
                    f"https://pypi.org/pypi/{pkg_name}/json",
                    timeout=5
                )

                if response.status_code == 200:
                    pypi_data = response.json()
                    latest_version = pypi_data["info"]["version"]

                    # Compare versions (simple string comparison for now)
                    if current_version != latest_version:
                        outdated_list.append({
                            "name": pkg_name,
                            "current": current_version,
                            "latest": latest_version
                        })
            except Exception as e:
                # Skip packages that can't be checked
                print(f"Warning: Could not check {pkg.get('name', 'unknown')}: {e}")
                continue

        return json.dumps({
            "status": "success",
            "package_manager": "pip",
            "outdated_count": len(outdated_list),
            "outdated_packages": outdated_list
        }, indent=2)

    except Exception as e:
        return json.dumps({"status": "error", "message": f"Error checking pip packages: {str(e)}"})


def test_outdated_detection():
    """Test that old versions are correctly detected as outdated."""
    print("🧪 Testing PyPI-based outdated detection...")
    print()

    # Create a temporary directory with a test requirements.txt
    with tempfile.TemporaryDirectory() as temp_dir:
        requirements_file = os.path.join(temp_dir, "requirements.txt")

        # Write old versions that should be detected as outdated
        with open(requirements_file, 'w') as f:
            f.write("pydantic==1.8.2\n")
            f.write("requests==2.25.0\n")

        print(f"📝 Created test requirements.txt with old versions:")
        print("   - pydantic==1.8.2 (from 2021)")
        print("   - requests==2.25.0 (from 2021)")
        print()

        # Run the check (call the underlying function directly)
        print("🔍 Checking for outdated packages via PyPI API...")
        result = check_pip_outdated_direct(temp_dir)

        print()
        print("📊 Result:")
        print(result)
        print()

        # Parse and verify
        import json
        data = json.loads(result)

        if data["status"] == "success":
            outdated_count = data["outdated_count"]
            outdated_packages = data["outdated_packages"]

            if outdated_count > 0:
                print(f"✅ SUCCESS: Detected {outdated_count} outdated package(s)")
                for pkg in outdated_packages:
                    print(f"   - {pkg['name']}: {pkg['current']} → {pkg['latest']}")
                return True
            else:
                print("❌ FAIL: No outdated packages detected (should have found pydantic and requests)")
                return False
        else:
            print(f"❌ ERROR: {data.get('message', 'Unknown error')}")
            return False


if __name__ == "__main__":
    print("=" * 70)
    print("PyPI Outdated Detection Test")
    print("=" * 70)
    print()

    success = test_outdated_detection()

    print()
    print("=" * 70)
    if success:
        print("✅ Test passed!")
    else:
        print("❌ Test failed!")
    print("=" * 70)
