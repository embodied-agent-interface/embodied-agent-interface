import os
import subprocess
import sys
import shutil

def check_install_conda():
    try:
        subprocess.run(['conda', '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Conda is installed.")
        return True
    except FileNotFoundError:
        print("Conda is not installed. Please install Conda first.")
        return False

def check_install_cmake():
    try:
        subprocess.run(['cmake', '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Cmake is installed.")
    except FileNotFoundError:
        print("Cmake is not installed. Installing Cmake using Conda...")
        subprocess.run(['conda', 'install', '-y', 'cmake'], check=True)
        print("Cmake installation completed.")

def git_clone_repo():
    repo_url = 'https://github.com/embodied-agent-interface/iGibson.git'
    if not os.path.exists('iGibson'):
        subprocess.run(['git', 'clone', '--recursive', repo_url], check=True)
        print("iGibson repository cloned successfully.")
    else:
        print("iGibson repository already exists. Skipping cloning.")

def install_igibson():
    os.chdir('iGibson')
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-e','.'], check=True)
    print("iGibson installed successfully.")

def main():
    if check_install_conda():
        check_install_cmake()
        git_clone_repo()
        install_igibson()

if __name__ == "__main__":
    main()
