import os
import csv

def write_to_csv_line(file_path, line_number, data):
    """
    Writes the given data to a specified line in a CSV file.

    - If the file does not exist, it creates it and writes the data at the specified line.
    - If the file exists, it modifies only the specified line but overwrites the raw data instead of keeping it.
    - Ensures that the provided data is written in separate columns.

    Parameters:
        file_path (str): The path to the CSV file.
        line_number (int): The line number to write the data (1-based index).
        data (list): The data to be written in the specified line (each item in a separate column).
    """
    target_row = line_number - 1  # Convert 1-based index to 0-based index

    # Check if the file exists
    if not os.path.exists(file_path):
        # print(f"File {file_path} does not exist. Creating a new file...")

        # Create the file and write empty rows up to the specified line
        with open(file_path, "w", newline="") as file:
            writer = csv.writer(file)

            # Write empty rows up to the target line
            for _ in range(target_row):
                writer.writerow([])  # Write an empty row

            # Write the target data
            writer.writerow(data)

        # print(f"Successfully created {file_path} and written {data} to line {line_number}.")

    else:
        # print(f"File {file_path} exists. Overwriting line {line_number}...")

        # Read existing content
        with open(file_path, "r", newline="") as file:
            rows = list(csv.reader(file))  # Read existing content

        # Ensure the file has enough rows
        while len(rows) <= target_row:
            rows.append([])  # Add empty rows if necessary

        # **Overwrite only the target line with new data**
        rows[target_row] = data  # Replace raw data instead of keeping it

        # Write back the modified content
        with open(file_path, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerows(rows)

        # print(f"Successfully overwritten line {line_number} with {data} in {file_path}.")
