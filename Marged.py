import os


def merge_files(file_list, output_file):
    with open(output_file, 'wb') as outfile:
        for file_name in file_list:
            with open(file_name, 'rb') as infile:
                outfile.write(infile.read())
                outfile.write(b"\n")  # Optional: Add a newline between files

# Example usage
file_list = ['suricata.py', 'App.js']
output_file = 'merged_output.txt'  # This will be a binary file with mixed content
merge_files(file_list, output_file)