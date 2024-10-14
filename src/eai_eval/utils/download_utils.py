import logging
import os
import zipfile
import fire
import eai_eval
import gdown  # Import gdown for downloading Google Drive files

log = logging.getLogger(__name__)

def unzip_file(zip_file_path, extract_to_path):
    """Extracts the content of a zip file to the specified folder."""
    try:
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to_path)
        print(f"Extracted {zip_file_path} to {extract_to_path}")
    except zipfile.BadZipFile as e:
        log.error(f"Error extracting the ZIP file: {e}")
        raise

def download_helm_output():
    """
    Download and unzip helm_output.zip from Google Drive to helm_output_path
    """
    # Google Drive file ID (from your link)
    file_id = "15RG2tVWDiDQpXioyT4TTB64sOIQqUl5d"
    
    # The direct Google Drive download URL format
    url = f"https://drive.google.com/uc?id={file_id}"

    # Local paths
    helm_output_path = eai_eval.helm_output_path  # Folder where the content will be unzipped
    zip_file_path = os.path.join(helm_output_path, "helm_output.zip")  # Temporary zip file path

    # Ensure the parent directory exists
    if not os.path.exists(helm_output_path):
        os.makedirs(helm_output_path)

    # Download the .zip file using gdown
    print(f"Downloading helm zip file from Google Drive to {zip_file_path}")
    gdown.download(url, zip_file_path, quiet=False)

    # Unzip the contents to helm_output_path
    print(f"Unzipping {zip_file_path} to {helm_output_path}")
    unzip_file(zip_file_path, helm_output_path)

    # Optionally, delete the zip file after extraction
    os.remove(zip_file_path)
    print(f"Deleted the zip file: {zip_file_path}")

def main():
    download_helm_output()

if __name__ == "__main__":
    fire.Fire(main)
