import os
import sys
import shutil
import hashlib
import time


def calculate_md5(file_path):
    """Calculate the MD5 checksum of a file."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def synchronize_folders(source_folder, replica_folder, log_file):
    """Synchronize the source folder to the replica folder."""
    with open(log_file, "a") as log:
        for root, _, files in os.walk(source_folder):
            for file_name in files:
                source_path = os.path.join(root, file_name)
                relative_path = os.path.relpath(source_path, source_folder)
                replica_path = os.path.join(replica_folder, relative_path)

                # Check if the file already exists in the replica folder
                if os.path.exists(replica_path):
                    source_md5 = calculate_md5(source_path)
                    replica_md5 = calculate_md5(replica_path)

                    # Compare MD5 checksums to determine if the file needs to be updated
                    if source_md5 != replica_md5:
                        shutil.copy2(source_path, replica_path)
                        log.write(f"Updated: {relative_path}\n")
                else:
                    # File doesn't exist in replica folder, copy it
                    shutil.copy2(source_path, replica_path)
                    log.write(f"Added: {relative_path}\n")

        # Clean up files in replica folder that are not present in source folder
        for root, _, files in os.walk(replica_folder):
            for file_name in files:
                replica_path = os.path.join(root, file_name)
                relative_path = os.path.relpath(replica_path, replica_folder)
                source_path = os.path.join(source_folder, relative_path)

                if not os.path.exists(source_path):
                    os.remove(replica_path)
                    log.write(f"Removed: {relative_path}\n")


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python sync_folders.py source_folder replica_folder interval_seconds log_file")
        sys.exit(1)

    source_folder = sys.argv[1]
    replica_folder = sys.argv[2]
    interval = int(sys.argv[3])
    log_file = sys.argv[4]

    while True:
        synchronize_folders(source_folder, replica_folder, log_file)
        print("Synchronization completed.")
        time.sleep(interval)
