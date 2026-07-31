from pathlib import Path

LOG_DIR = Path("logs")

def clear_logs(log_dir: Path):
    if not log_dir.exists():
        print(f"{log_dir} does not exist.")
        return

    for item in log_dir.iterdir():
        try:
            if item.is_file() or item.is_symlink():
                item.unlink()
                print(f"Deleted file: {item}")
            elif item.is_dir():
                # Skip subdirectories, or use shutil.rmtree if you want to remove them too
                print(f"Skipping directory: {item}")
        except Exception as e:
            print(f"Failed to delete {item}: {e}")

if __name__ == "__main__":
    clear_logs(LOG_DIR)