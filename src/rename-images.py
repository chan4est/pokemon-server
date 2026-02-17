import os
import re
import shutil

## Produced by ChatGPT 3.5

def copy_files(source_folder, destination_folder_group1, destination_folder_group2):
    # Define the regular expression pattern
    pattern = re.compile(r'^pm(\d*)\.([(s).]*)icon\.png$')

    # Iterate through each file in the source folder
    for filename in os.listdir(source_folder):
        source_path = os.path.join(source_folder, filename)

        # Check if the file is a PNG file and matches the pattern
        if os.path.isfile(source_path) and filename.lower().endswith('.png'):
            matches = pattern.match(filename)
            
            # If there is a match, extract capture groups
            if matches:
                group1 = matches.group(1)
                group2 = matches.group(2)

                # Define the new filename based on capture groups
                new_filename = f"{group1}.png"
                if group2:
                    new_filename = f"{group1}{group2}png"

                # Construct the destination file path
                if group2:
                    destination_path = os.path.join(destination_folder_group2, new_filename)
                else:
                    destination_path = os.path.join(destination_folder_group1, new_filename)

                # Copy the file to the destination folder
                shutil.copy2(source_path, destination_path)
                print(f"Copied: {filename} -> {destination_path}")

if __name__ == "__main__":
    source_folder = "/home/cforrest/go-copy/python/Source"  # Replace with the path to your source folder
    destination_folder_group1 = "/home/cforrest/go-copy/python/Regular"  # Replace with the path to your destination folder for group1
    destination_folder_group2 = "/home/cforrest/go-copy/python/Shiny"  # Replace with the path to your destination folder for group2
    
    # Ensure the destination folders exist; create if not.
    for folder in [destination_folder_group1, destination_folder_group2]:
        if not os.path.exists(folder):
            os.makedirs(folder)

    copy_files(source_folder, destination_folder_group1, destination_folder_group2)
