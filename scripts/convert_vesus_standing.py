"""
Convert a vesus.org-outputted txt standing to customized markdown table to be put on the website.
"""
import re
import sys
import os

def convert_vesus_file_to_markdown(input_filename):
    # Attempt to read the file
    try:
        with open(input_filename, 'r', encoding='utf-8') as file:
            lines = file.readlines()
    except FileNotFoundError:
        return f"Error: The file '{input_filename}' was not found. Please check the path."

    # Initialize the Markdown table with the requested headers
    md_table = [
        "| Pos | Name | Perf | Pts | DE | BH | BH/C1 | ARO |",
        "|---|---|---|---|---|---|---|---|"
    ]

    # Regex pattern to capture Vesus columns
    pattern = re.compile(
        r'^(\d+)\s+(\d+)\s+(.*?)\s+([mf]?)\s*([A-Z]{3})\s*\|\s*(\d+)\s+(\d+)\s*\|\s*([\d\.]+)\s+(\d+)\s+([\d\.]+)\s+([\d\.]+)\s+(\d+)\s*$'
    )

    for line in lines:
        # Check if the line matches our data row pattern
        match = pattern.match(line.strip())
        if match:
            # Extract the captured groups
            groups = list(match.groups())
            
            # Map the relevant groups to variables
            pos = groups[0]
            name = groups[2].strip() # Clean up trailing spaces in Name
            perf = groups[6]
            pts = groups[7]
            de = groups[8]
            bh = groups[9]
            bh_c1 = groups[10]
            aro = groups[11]

            # Highlight points and names in bold for the first three positions
            if pos in ['1', '2', '3']:
                pts = f"**{pts}**"
                name = f"**{name}**"
            
            # Build the row
            row_data = [pos, name, perf, pts, de, bh, bh_c1, aro]
            row = " | ".join(row_data)
            md_table.append(f"| {row} |")

    # Combine the table and wrap it in a centering HTML div
    # The newlines (\n\n) are crucial so Hugo parses the inner Markdown correctly
    final_table = '\n'.join(md_table)
    html_wrapped_table = f'<div align="center">\n\n{final_table}\n\n</div>'

    return html_wrapped_table

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python vesus_converter.py <input_file.txt>")
        sys.exit(1)
        
    input_file = sys.argv[1]
    
    markdown_output = convert_vesus_file_to_markdown(input_file)
    
    # Check if an error message was returned instead of markdown
    if markdown_output.startswith("Error:"):
        print(markdown_output)
        sys.exit(1)
        
    base_name = os.path.splitext(input_file)[0]
    output_file = f"{base_name}_output.md"
    
    print(markdown_output)
    
    with open(output_file, 'w', encoding='utf-8') as out_file:
        out_file.write(markdown_output)
    print(f"\nOutput saved to {output_file}")
