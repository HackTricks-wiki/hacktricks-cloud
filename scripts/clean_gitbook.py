import os
import re

def parse_summary(summary_file):
    """Parse the SUMMARY.md file to extract listed Markdown pages."""
    listed_pages = set()
    with open(summary_file, "r", encoding="utf-8") as f:
        for line in f:
            match = re.search(r'\(([^)]+\.md)\)', line)
            if match:
                listed_pages.add(os.path.normpath(match.group(1)))
    return listed_pages

def find_all_markdown_files(base_dir):
    """Find all Markdown (.md) files in the repository."""
    all_files = set()
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".md"):
                relative_path = os.path.relpath(os.path.join(root, file), base_dir)
                if not any(p in relative_path for p in [".github/", "LICENSE.md", "SUMMARY.md"]):
                    all_files.add(os.path.normpath(relative_path))
    return all_files

def delete_unused_files(base_dir, unused_files):
    """Delete files that are not used."""
    for file in unused_files:
        full_path = os.path.join(base_dir, file)
        if os.path.exists(full_path):
            os.remove(full_path)
            print(f"Deleted: {file}")
        else:
            print(f"File not found (already removed?): {file}")

def main():
    repo_dir = os.path.abspath(os.path.join(os.getcwd(), ".."))  # Parent directory as repository root
    summary_file = os.path.join(repo_dir, "SUMMARY.md")

    if not os.path.exists(summary_file):
        print("ERROR: SUMMARY.md file not found in the repository root.")
        return

    print("Parsing SUMMARY.md...")
    listed_pages = parse_summary(summary_file)

    print("Finding all Markdown files...")
    all_markdown_files = find_all_markdown_files(repo_dir)

    unused_files = all_markdown_files - listed_pages

    if not unused_files:
        print("All Markdown files are used. No files to delete.")
    else:
        print("Unused Markdown files found:")
        for file in unused_files:
            print(file)

        confirm = input("Do you want to delete these files? (yes/no): ").strip().lower()
        if confirm == "yes":
            delete_unused_files(repo_dir, unused_files)
            print("Unused files deleted.")
        else:
            print("No files were deleted.")

if __name__ == "__main__":
    main()
