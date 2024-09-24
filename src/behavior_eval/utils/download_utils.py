from igibson.utils.assets_utils import show_progress,download_assets,download_ig_dataset
import logging
import os
import subprocess
from urllib.request import urlretrieve
import fire
import igibson


log = logging.getLogger(__name__)

pbar = None


def git_lfs_pull(repo_path):
    """
    Perform git lfs pull in the specified repository path
    """
    if os.path.exists(repo_path):
        log.info(f"Running 'git lfs pull' in {repo_path}")
        subprocess.run(["git", "lfs", "pull"], cwd=repo_path)
    else:
        log.warning(f"Repository path {repo_path} does not exist")

def download_igibson_key():
    """
    Download iGibson key
    """
    key_path = igibson.key_path  # Path to the iGibson key
    url = "https://storage.googleapis.com/gibson_scenes/igibson.key"

    # Ensure the parent directory of key_path exists
    if not os.path.exists(os.path.dirname(key_path)):
        os.makedirs(os.path.dirname(key_path))

    # Download the file
    print("Downloading iGibson key from {}".format(url))
    urlretrieve(url, key_path,show_progress)
    print("iGibson key downloaded to {}".format(key_path))

def main():
    
    download_ig_dataset()
    download_assets()
    git_lfs_pull(igibson.ig_dataset_path)
    git_lfs_pull(igibson.assets_path)
    download_igibson_key()
        
if __name__ == "__main__":
    fire.Fire(main)