#!/usr/bin/env python3
import os
import shutil
import subprocess
import sys

def run_command(command, description):
    print(f"\n🚀 {description}...")
    try:
        subprocess.check_call(command, shell=True)
        print(f"✅ {description} successful!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during {description}: {e}")
        sys.exit(1)

def main():
    # 1. Clean previous builds
    if os.path.exists("dist"):
        print("🧹 Cleaning old builds...")
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("layr0_imc.egg-info"):
        shutil.rmtree("layr0_imc.egg-info")

    # 2. Install build requirements
    run_command("pip install --upgrade build twine", "Installing build requirements")

    # 3. Build the package
    run_command("python -m build", "Building the package")

    # 4. Ask for upload destination
    print("\n📦 Package built successfully in dist/")
    print("Where would you like to upload?")
    print("1. TestPyPI (recommended first)")
    print("2. PyPI (Production)")
    print("3. Skip upload")
    
    choice = input("\nEnter your choice (1/2/3): ").strip()

    if choice == "1":
        run_command("python -m twine upload --repository testpypi dist/*", "Uploading to TestPyPI")
    elif choice == "2":
        run_command("python -m twine upload dist/*", "Uploading to PyPI")
    else:
        print("⏭️ Skipping upload.")

if __name__ == "__main__":
    main()
