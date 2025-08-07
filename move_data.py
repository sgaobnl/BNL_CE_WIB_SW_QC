import shutil
import os

def copy_and_delete_folder(src_root, src_folder, dst_root):
    # Check if the source folder exists
    src_path = "/".join([src_root, src_folder])
    dst_path = "/".join([dst_root, src_folder])
    if not os.path.exists(src_path):
        print(f"Source folder does not exist: {src_path}")
        return
    if not os.path.exists(dst_root):
        print(f"Destination root path does not exist: {dst_root}")
        return

    try:
        # Create destination folder if it doesn't exist
        if not os.path.exists(dst_path):
            os.makedirs(dst_path)

        # Recursively copy each file and folder from source to destination
        for item in os.listdir(src_path):
            src_item = os.path.join(src_path, item)
            dest_item = os.path.join(dst_path, item)

            if os.path.isdir(src_item):
                # Copy folder contents, overwrite if needed
                if os.path.exists(dest_item):
                    shutil.rmtree(dest_item)
                shutil.copytree(src_item, dest_item)
            else:
                # Overwrite file
                print(f"Start copying Contents from '{src_item}' to '{dest_item}'")
                shutil.copy2(src_item, dest_item)

        print(f"Contents copied from '{src_path}' to '{dst_path}'")

        # Delete the original source folder
        shutil.rmtree(src_path)
        print(f"Original folder '{src_path}' deleted")

    except Exception as e:
        print(f"Error: {e}")

# Example usage:
if __name__ == "__main__":
    src_root = r"C:\SGAO\ColdTest\Tested\DAT_LArASIC_QC"
    src_folder = r"hello"
    dst_root = r"S:\RTS_DAT_LArASIC_QC"

    copy_and_delete_folder(src_root, src_folder, dst_root)

