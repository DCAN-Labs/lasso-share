import re
import os
import argparse # Added argparse for command-line argument handling

def convert_html_to_text(html_filepath: str, text_filepath: str):
    """
    Reads content from an HTML file, strips all HTML tags using a regular
    expression, and saves the resulting plain text to a new file.

    NOTE: For highly complex HTML (e.g., heavily nested structures, broken
    tags), a dedicated HTML parsing library like BeautifulSoup is recommended.
    This method uses standard library 're' for simplicity and dependency-free
    operation. It also attempts to clean up multiple newlines.

    Args:
        html_filepath: The path to the input HTML file.
        text_filepath: The path to the output text file.
    """
    try:
        # 1. Read the HTML file content
        with open(html_filepath, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # 2. Strip all HTML tags using regex: removes everything between < and >
        # This is simple and effective for many cases.
        plain_text = re.sub(r'<[^>]+>', ' ', html_content)

        # 3. Clean up the resulting text
        # Replace multiple spaces/tabs with a single space
        plain_text = re.sub(r'\s{2,}', ' ', plain_text)
        # Remove leading/trailing whitespace
        plain_text = plain_text.strip()
        # Ensure paragraphs are separated by at least one newline (optional cleanup)
        plain_text = re.sub(r' \s* ', '\n\n', plain_text)
        plain_text = re.sub(r'\n\s*\n', '\n\n', plain_text)


        # 4. Write the cleaned plain text to the output file
        with open(text_filepath, 'w', encoding='utf-8') as f:
            f.write(plain_text)

        print(f"Successfully converted '{html_filepath}' to plain text.")
        print(f"Output saved to '{text_filepath}'")

    except FileNotFoundError:
        print(f"Error: The file '{html_filepath}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# --- Command Line Usage ---
if __name__ == "__main__":
    # 1. Set up the argument parser
    parser = argparse.ArgumentParser(
        description="Convert an HTML file to a plain text file by stripping tags."
    )
    
    # 2. Add required positional argument for the input file
    parser.add_argument(
        "input_file",
        type=str,
        help="The path to the input HTML file."
    )
    
    # 3. Add optional argument for the output file
    parser.add_argument(
        "--output",
        dest="output_file",
        type=str,
        default="output.txt",
        help="The path to the output text file (default: output.txt)."
    )
    
    # 4. Parse the arguments
    args = parser.parse_args()

    # 5. Run the conversion with the provided arguments
    convert_html_to_text(args.input_file, args.output_file)
