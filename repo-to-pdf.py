import os
import argparse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import utils
import pathspec

def load_gitignore(repo_dir):
    gitignore_path = os.path.join(repo_dir, '.gitignore')
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r') as f:
            gitignore_patterns = f.read().splitlines()
        return pathspec.PathSpec.from_lines('gitwildmatch', gitignore_patterns)
    return None

def draw_text(c, text_lines, x, y, width, height, line_height):
    for line in text_lines:
        if y < line_height:
            c.showPage()
            y = height - 40
        c.drawString(x, y, line)
        y -= line_height
    return y

def repo_to_pdf(repo_dir, output_pdf):
    # Load .gitignore patterns
    spec = load_gitignore(repo_dir)

    # Create PDF
    c = canvas.Canvas(output_pdf, pagesize=A4)
    width, height = A4
    x = 40
    y = height - 40
    line_height = 12
    c.setFont("Helvetica", 12)

    # Iterate through the files
    for root, _, files in os.walk(repo_dir):
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, repo_dir)
            if relative_path.startswith('.'):
                continue

            # Check if the file is ignored
            if spec and spec.match_file(relative_path):
                continue

            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

                # Draw file path as title
                y = draw_text(c, [relative_path, "="*len(relative_path)], x, y, width, height, line_height)
                y -= line_height

                # Draw file content
                content_lines = content.splitlines()
                y = draw_text(c, content_lines, x, y, width, height, line_height)
                y -= line_height

    # Save the PDF
    c.save()

def main():
    parser = argparse.ArgumentParser(description='Convert a Git repository to a PDF.')
    parser.add_argument('repo_dir', type=str, help='Path to the local Git repository.')
    parser.add_argument('output_pdf', type=str, help='Output PDF file path.')

    args = parser.parse_args()

    repo_to_pdf(args.repo_dir, args.output_pdf)

if __name__ == '__main__':
    main()
