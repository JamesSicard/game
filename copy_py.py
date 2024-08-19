import os
import pyperclip

def copy_python_files_to_clipboard(source_dir):
    combined_content = ""
    # Iterate through each file in the source directory
    for filename in os.listdir(source_dir):
        # Check if the file has a .py extension
        if filename.endswith('.py'):
            # Construct the full file path
            filepath = os.path.join(source_dir, filename)
            # Read the content of the file
            with open(filepath, 'r') as file:
                content = file.read()
                # Format the content as specified
                formatted_content = f'"{filename}" ```{content}```\n'
                combined_content += formatted_content
    
    # Copy the combined content to the clipboard
    pyperclip.copy(combined_content)
    print("The contents have been copied to the clipboard.")

# Example usage:
source_directory = 'castle'  # Change this to your source directory
copy_python_files_to_clipboard(source_directory)