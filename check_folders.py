import os

# --- This script checks the folder names inside your Dataset ---

DATASET_DIRECTORY = 'Dataset'

try:
    train_path = os.path.join(DATASET_DIRECTORY, 'train')
    val_path = os.path.join(DATASET_DIRECTORY, 'val')

    print("--- FOLDERS FOUND IN 'train' DIRECTORY: ---")
    train_folders = os.listdir(train_path)
    print(train_folders)
    print(f"Number of training classes: {len(train_folders)}")

    print("\n--- FOLDERS FOUND IN 'val' DIRECTORY: ---")
    val_folders = os.listdir(val_path)
    print(val_folders)
    print(f"Number of validation classes: {len(val_folders)}")

except FileNotFoundError:
    print(f"ERROR: Could not find the '{DATASET_DIRECTORY}' directory, or it is missing the 'train' or 'val' subdirectories.")