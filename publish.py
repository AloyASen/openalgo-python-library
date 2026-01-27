#!/usr/bin/env python3
import os
import shutil
import subprocess
import sys
import time

def run_command(command, description, env=None):
    print(f"\n🚀 {description}...")
    try:
        subprocess.check_call(command, shell=True, env=env)
        print(f"✅ {description} successful!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during {description}: {e}")
        sys.exit(1)

def main():
    # 1. Clean previous builds
    folders_to_clean = ["dist", "build", "layr0_imc.egg-info"]
    for folder in folders_to_clean:
        if os.path.exists(folder):
            print(f"🧹 Cleaning {folder}...")
            try:
                shutil.rmtree(folder)
            except Exception as e:
                print(f"⚠️ Warning: Could not fully clean {folder}: {e}")

    # 2. Install build requirements
    run_command("pip install --upgrade build twine", "Installing build requirements")

    # 3. Build the package
    # Added --verbose to build
    run_command("python -m build --verbose", "Building the package")

    # 4. Handle Upload
    print("\n📦 Package built successfully in dist/")
    print("Where would you like to upload?")
    print("1. TestPyPI (recommended first)")
    print("2. PyPI (Production)")
    print("3. Skip upload")
    
    choice = input("\nEnter your choice (1/2/3): ").strip()

    if choice in ["1", "2"]:
        repo_arg = "--repository testpypi" if choice == "1" else ""
        repo_name = "TestPyPI" if choice == "1" else "PyPI"
        
        print(f"\n🔑 Preparing to upload to {repo_name}")
        
        token = os.environ.get("PYPI_TOKEN")
        if not token:
            print(f"Please enter your {repo_name} API token:")
            print("(Note: On Windows, you can also set it with: $env:PYPI_TOKEN = 'your-token')")
            token = input("> ").strip()
            
        if not token:
            print("❌ No token provided. Aborting.")
            sys.exit(1)
            
        # Use environment variables for twine
        env = os.environ.copy()
        env["TWINE_USERNAME"] = "__token__"
        env["TWINE_PASSWORD"] = token
        
        # Twine upload command with --verbose to diagnose 400 errors
        cmd = f"python -m twine upload {repo_arg} --verbose dist/*"
        
        run_command(cmd, f"Uploading to {repo_name}", env=env)
    else:
        print("⏭️ Skipping upload.")

if __name__ == "__main__":
    main()
