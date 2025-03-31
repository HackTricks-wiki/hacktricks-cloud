import os
import requests
import zipfile
import tempfile
import time
import glob
import re

from openai import OpenAI

# Initialize OpenAI client
for name in os.environ:
    print(name)
client = OpenAI(api_key=os.getenv("MY_OPENAI_API_KEY"))

# Vector Store ID
VECTOR_STORE_ID = "vs_67e9f92e8cc88191911be54f81492fb8"

# --------------------------------------------------
# Step 1: Download and Extract Markdown Files
# --------------------------------------------------

def download_zip(url, save_path):
    print(f"Downloading zip from: {url}")
    response = requests.get(url)
    response.raise_for_status()  # Ensure the download succeeded
    with open(save_path, "wb") as f:
        f.write(response.content)
    print(f"Downloaded zip from: {url}")

def extract_markdown_files(zip_path, extract_dir):
    print(f"Extracting zip: {zip_path} to {extract_dir}")
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_dir)
    # Recursively find all .md files
    md_files = glob.glob(os.path.join(extract_dir, "**", "*.md"), recursive=True)

    return md_files

# Repository URLs
hacktricks_url = "https://github.com/HackTricks-wiki/hacktricks/archive/refs/heads/master.zip"
hacktricks_cloud_url = "https://github.com/HackTricks-wiki/hacktricks-cloud/archive/refs/heads/main.zip"

# Temporary directory for downloads and extraction
temp_dir = tempfile.mkdtemp()
try:
    # Download zip archives
    print("Downloading Hacktricks repositories...")
    hacktricks_zip = os.path.join(temp_dir, "hacktricks.zip")
    hacktricks_cloud_zip = os.path.join(temp_dir, "hacktricks_cloud.zip")
    download_zip(hacktricks_url, hacktricks_zip)
    download_zip(hacktricks_cloud_url, hacktricks_cloud_zip)
    
    # Extract the markdown files
    hacktricks_extract_dir = os.path.join(temp_dir, "hacktricks")
    hacktricks_cloud_extract_dir = os.path.join(temp_dir, "hacktricks_cloud")
    
    md_files_hacktricks = extract_markdown_files(hacktricks_zip, hacktricks_extract_dir)
    md_files_hacktricks_cloud = extract_markdown_files(hacktricks_cloud_zip, hacktricks_cloud_extract_dir)
    
    all_md_files = md_files_hacktricks + md_files_hacktricks_cloud
    print(f"Found {len(all_md_files)} markdown files.")
finally:
    # Optional cleanup of temporary files after processing
    # shutil.rmtree(temp_dir)
    pass

# --------------------------------------------------
# Step 2: Remove All Existing Files in the Vector Store
# --------------------------------------------------
# List current files in the vector store and delete each one.
existing_files = list(client.vector_stores.files.list(VECTOR_STORE_ID))
print(f"Found {len(existing_files)} files in the vector store. Removing them...")

for file_obj in existing_files:
    # Delete the underlying file object; this removes it from the vector store.
    try:
        client.files.delete(file_id=file_obj.id)
        print(f"Deleted file: {file_obj.id}")
        time.sleep(1) # Give it a moment to ensure the deletion is processed
    except Exception as e:
        # Handle potential errors during deletion
        print(f"Error deleting file {file_obj.id}: {e}")

# ----------------------------------------------------
# Step 3: Clean markdown Files 
# ----------------------------------------------------
# Clean markdown files and marge them so it's easier to 
# uplaod to the vector store.


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

            if line.startswith("#") and "reference" in line.lower(): #If references part reached, just stop reading the file
                break
            
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
            md_files = sorted([os.path.join(root, f) for f in filenames if f.endswith(".md") and f.lower() not in ["summary.md", "references.md"]])
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
            output.write(f"### Start file: {file_name} ###\n\n")
            output.write("\n".join(cleaned_content))
            output.write("\n\n")

# Specify the starting folder and output file
start_folder = os.getcwd()

# Keywords to exclude from lines
exclude_keywords = [
    "hacktricks-training.md",
    "![](<", # Skip lines with images
    "/images/" # Skip lines with images
    
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
ht_file = os.path.join(tempfile.gettempdir(), "hacktricks.md")
htc_file = os.path.join(tempfile.gettempdir(), "hacktricks-cloud.md")
clean_and_merge_md_files(hacktricks_extract_dir, exclude_keywords, ht_file)
print(f"Merged content has been saved to: {ht_file}")
clean_and_merge_md_files(hacktricks_cloud_extract_dir, exclude_keywords, htc_file)
print(f"Merged content has been saved to: {htc_file}")


# ----------------------------------------------------
# Step 4: Upload All Markdown Files to the Vector Store
# ----------------------------------------------------
# Upload two files to the vector store.
# Uploading .md hacktricks files individually can be slow,
# so thats why we merged it before into just 2 files.

file_streams = []

ht_stream = open(ht_file, "rb")
file_streams.append(ht_stream)
htc_stream = open(htc_file, "rb")
file_streams.append(htc_stream)

file_batch = client.vector_stores.file_batches.upload_and_poll(
        vector_store_id=VECTOR_STORE_ID,
        files=file_streams
    )

time.sleep(60)  # Sleep for a minute to ensure the upload is processed
ht_stream.close()
htc_stream.close()


""""This was to upload each .md independently, wich turned out to be a nightmare
# Ensure we don't exceed the maximum number of file streams

for file_path in all_md_files:
    # Check if we have reached the maximum number of streams
    if len(file_streams) >= 300:
        print("Reached maximum number of file streams (300). Uploading current batch...")
        # Upload the current batch before adding more files
        file_batch = client.vector_stores.file_batches.upload_and_poll(
            vector_store_id=VECTOR_STORE_ID,
            files=file_streams
        )
        print("Upload status:", file_batch.status)
        print("File counts:", file_batch.file_counts)
        # Clear the list for the next batch
        file_streams = []
        time.sleep(120)  # Sleep for 2 minutes to avoid hitting API limits
    try:
        stream = open(file_path, "rb")
        file_streams.append(stream)
    except Exception as e:
        print(f"Error opening {file_path}: {e}")

if file_streams:
    # Upload files and poll for completion
    file_batch = client.vector_stores.file_batches.upload_and_poll(
        vector_store_id=VECTOR_STORE_ID,
        files=file_streams
    )
    print("Upload status:", file_batch.status)
    print("File counts:", file_batch.file_counts)
else:
    print("No markdown files to upload.")"
    

# Close all file streams
for stream in file_streams:
    stream.close()
"""
