import os
import re
import tempfile

def clean_and_merge_md_files(start_folder, exclude_keywords, output_file):
    def clean_file_content(file_path):
        """Clean the content of a single file and return the cleaned lines."""
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.readlines()
        
        cleaned_lines = []
        inside_hint = False
        for i,line in enumerate(content):
            # Skip lines containing excluded keywords
            if any(keyword in line for keyword in exclude_keywords):
                continue
            
            # Detect and skip {% hint %} ... {% endhint %} blocks
            if "{% hint style=\"success\" %}" in line and "Learn & practice" in content[i+1]:
                inside_hint = True
            if "{% endhint %}" in line:
                inside_hint = False
                continue
            if inside_hint:
                continue
            
            # Skip lines with <figure> ... </figure>
            if re.match(r"<figure>.*?</figure>", line):
                continue
            
            # Add the line if it passed all checks
            cleaned_lines.append(line.rstrip())
        
        # Remove excess consecutive empty lines
        cleaned_lines = remove_consecutive_empty_lines(cleaned_lines)
        return cleaned_lines

    def remove_consecutive_empty_lines(lines):
        """Allow no more than one consecutive empty line."""
        cleaned_lines = []
        previous_line_empty = False
        for line in lines:
            if line.strip() == "":
                if not previous_line_empty:
                    cleaned_lines.append("")
                previous_line_empty = True
            else:
                cleaned_lines.append(line)
                previous_line_empty = False
        return cleaned_lines

    def gather_files_in_order(start_folder):
        """Gather all .md files in a depth-first order."""
        files = []
        for root, _, filenames in os.walk(start_folder):
            md_files = sorted([os.path.join(root, f) for f in filenames if f.endswith(".md")])
            files.extend(md_files)
        return files

    # Gather files in depth-first order
    all_files = gather_files_in_order(start_folder)

    # Process files and merge into a single output
    with open(output_file, "w", encoding="utf-8") as output:
        for file_path in all_files:
            # Clean the content of the file
            cleaned_content = clean_file_content(file_path)

            # Skip saving if the cleaned file has fewer than 10 non-empty lines
            if len([line for line in cleaned_content if line.strip()]) < 10:
                continue

            # Get the name of the file for the header
            file_name = os.path.basename(file_path)

            # Write header, cleaned content, and 2 extra new lines
            output.write(f"# {file_name}\n\n")
            output.write("\n".join(cleaned_content))
            output.write("\n\n")

def main():
    # Specify the starting folder and output file
    start_folder = os.getcwd()
    output_file = os.path.join(tempfile.gettempdir(), "merged_output.md")
    
    # Keywords to exclude from lines
    exclude_keywords = [
        "STM Cyber",  # STM Cyber ads
        "offer several valuable cybersecurity services",  # STM Cyber ads
        "and hack the unhackable",  # STM Cyber ads
        "blog.stmcyber.com", # STM Cyber ads

        "RootedCON", # RootedCON ads
        "rootedcon.com", # RootedCON ads
        "the mission of promoting technical knowledge", # RootedCON ads

        "Intigriti", # Intigriti ads
        "intigriti.com", # Intigriti ads

        "Trickest", # Trickest ads
        "trickest.com", # Trickest ads,
        "Get Access Today:",

        "HACKENPROOF", # Hackenproof ads
        "hackenproof.com", # Hackenproof ads
        "HackenProof", # Hackenproof ads
        "discord.com/invite/N3FrSbmwdy", # Hackenproof ads
        "Hacking Insights:", # Hackenproof ads
        "Engage with content that delves", # Hackenproof ads
        "Real-Time Hack News:", # Hackenproof ads
        "Keep up-to-date with fast-paced", # Hackenproof ads
        "Latest Announcements:", # Hackenproof ads
        "Stay informed with the newest bug", # Hackenproof ads
        "start collaborating with top hackers today!", # Hackenproof ads
        "discord.com/invite/N3FrSbmwdy", # Hackenproof ads

        "Pentest-Tools", # Pentest-Tools.com ads
        "pentest-tools.com", # Pentest-Tools.com ads
        "perspective on your web apps, network, and", # Pentest-Tools.com ads
        "report critical, exploitable vulnerabilities with real business impact", # Pentest-Tools.com ads

        "SerpApi", # SerpApi ads
        "serpapi.com", # SerpApi ads
        "offers fast and easy real-time", # SerpApi ads
        "plans includes access to over 50 different APIs for scraping", # SerpApi ads
        
        "8kSec", # 8kSec ads
        "academy.8ksec.io", # 8kSec ads
        "Learn the technologies and skills required", # 8kSec ads

        "WebSec", # WebSec ads
        "websec.nl", # WebSec ads
        "which means they do it all; Pentesting", # WebSec ads
    ]
    
    # Clean and merge .md files
    clean_and_merge_md_files(start_folder, exclude_keywords, output_file)
    
    # Print the path to the output file
    print(f"Merged content has been saved to: {output_file}")

if __name__ == "__main__":
    # Execute this from the hacktricks folder to clean
    # It will clean all the .md files and compile them into 1 in a proper order
    main()
