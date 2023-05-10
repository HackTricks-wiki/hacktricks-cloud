import argparse
import os
import openai #pip3 install openai
import time
import shutil
import tempfile
import subprocess
import sys


MASTER_BRANCH="master"

def get_branch_files(branch):
    """Get a list of all files in a branch."""
    command = f"git ls-tree -r --name-only {branch}"
    result = subprocess.run(command.split(), stdout=subprocess.PIPE)
    files = result.stdout.decode().splitlines()
    return set(files)

def delete_unique_files(branch):
    """Delete files that are unique to branch2."""
    # Get the files in each branch
    files_branch1 = get_branch_files(MASTER_BRANCH)
    files_branch2 = get_branch_files(branch)

    # Find the files that are in branch2 but not in branch1
    unique_files = files_branch2 - files_branch1

    if unique_files:
        # Switch to the second branch
        subprocess.run(["git", "checkout", branch])

        # Delete the unique files from the second branch
        for file in unique_files:
            subprocess.run(["git", "rm", file])
        
        subprocess.run(["git", "checkout", MASTER_BRANCH])


def check_gh_branch(branch, temp_folder, file_path):
    branch_exists = subprocess.run(['git', 'show-ref', '--verify', '--quiet', 'refs/heads/' + branch])
    # If branch doesn't exist, create it
    if branch_exists.returncode != 0:
        subprocess.run(['git', 'checkout', '-b', branch])
    else:
        subprocess.run(['git', 'checkout', branch])
    
    # Walk through source directory
    for dirpath, dirnames, filenames in os.walk(temp_folder):
        # Compute destination path
        dest_path = os.path.join(os.getcwd(), os.path.relpath(dirpath, temp_folder))
        
        # Create directory structure in destination, if not already present
        if not os.path.exists(dest_path):
            os.makedirs(dest_path)
        
        # Copy each file from source to destination
        for file_name in filenames:
            src_file = os.path.join(dirpath, file_name)
            shutil.copy2(src_file, dest_path)

    print(f"Translated files copied to branch: {branch}")
    
    if file_path:
        subprocess.run(['git', 'add', "-A"])
        subprocess.run(['git', 'commit', '-m', f"Translated {file_path} to {branch}"[:72]])
        subprocess.run(['git', 'checkout', MASTER_BRANCH])
        print("Commit created and moved to master branch")
    else:
        print("No commiting anything, leaving in language branch")


def translate_text(language, text, file_path, model, cont=0):
    messages = [
        {"role": "system", "content": "You are a professional hacker, translator and writer. You write everything super clear and as concise as possible without loosing information."},
        {"role": "system", "content": f"The following is content from a hacking book about hacking techiques of cloud, SaaS platforms, CI/CD... The following content is from the file {file_path}. Translate the relevant English text to {language} and return the translation keeping the markdown syntax. Do not translate things like code, hacking technique names, cloud/SaaS platform names (like Workspace, aws, gcp...), the word 'leak', and markdown tags. Also don't add any extra stuff apart from the translation and markdown syntax."},
        {"role": "user", "content": text},
    ]
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=0
        )
    except Exception as e:
        print(e)
        if cont > 6:
            print(f"Page {file_path} could not be translated with text: {text}")
            exit(1)
        if "is currently overloaded" in str(e).lower():
            print("Overloaded, waiting 30 seconds")
            time.sleep(30)
        elif "timeout" in str(e).lower():
            print("Timeout, waiting 30 seconds")
            cont += 1
            time.sleep(30)
        return translate_text(language, text, file_path, model, cont)

    response_message = response["choices"][0]["message"]["content"]
    return response_message.strip()


def split_text(text):
    lines = text.split('\n')
    chunks = []
    chunk = ''

    for line in lines:
        if (line.startswith('#') and len(chunk.split() + line.split()) > 1100) or \
            len(chunk.split() + line.split()) > 1700:
            chunks.append(chunk.strip())
            chunk = ''
        
        chunk += line + '\n'

    chunks.append(chunk.strip())
    return chunks


def copy_gitbook_dir(source_path, dest_path):
    folder_name = ".gitbook/"
    source_folder = os.path.join(source_path, folder_name)
    destination_folder = os.path.join(dest_path, folder_name)
    if not os.path.exists(source_folder):
        print(f"Error: {source_folder} does not exist.")
    else:
        # Copy the .gitbook folder
        shutil.copytree(source_folder, destination_folder)
        print(f"Copied .gitbook folder from {source_folder} to {destination_folder}")

def copy_summary(source_path, dest_path):
    file_name = "SUMMARY.md"
    source_filepath = os.path.join(source_path, file_name)
    dest_filepath = os.path.join(dest_path, file_name)
    shutil.copy2(source_filepath, dest_filepath)

def translate_file(language, file_path, file_dest_path, model):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    content_chunks = split_text(content)

    start_time = time.time()
    translated_content = '\n'.join(translate_text(language, chunk, file_path, model) for chunk in content_chunks)
    elapsed_time = time.time() - start_time

    # make sure directory exists
    os.makedirs(os.path.dirname(file_dest_path), exist_ok=True)
    with open(file_dest_path, 'w', encoding='utf-8') as f:
        f.write(translated_content)
    
    print(f"Page {file_path} translated in {elapsed_time:.2f} seconds")


def translate_directory(language, source_path, dest_path, model):
    
    for subdir, dirs, files in os.walk(source_path):
        for file in files:
            if file == "SUMMARY.md":
                continue
            
            elif file.endswith('.md'):
                source_filepath = os.path.join(subdir, file)
                dest_filepath = os.path.join(dest_path, os.path.relpath(source_filepath, source_path))

                if os.path.exists(dest_filepath):
                    continue

                # Create the directory structure in the translated folder
                os.makedirs(os.path.dirname(dest_filepath), exist_ok=True)

                # Translate the file
                translate_file(language, source_filepath, dest_filepath, model)
                

if __name__ == "__main__":
    # Set up argparse
    parser = argparse.ArgumentParser(description='Translate gitbook and copy to a new branch.')
    parser.add_argument('-l', '--language', required=True, help='Target language for translation.')
    parser.add_argument('-b', '--branch', required=True, help='Branch name to copy translated files.')
    parser.add_argument('-k', '--api-key', required=True, help='API key to use.')
    parser.add_argument('-m', '--model', default="gpt-3.5-turbo", help='The openai model to use. By default: gpt-3.5-turbo')
    parser.add_argument('-o', '--org-id', help='The org ID to use (if not set the default one will be used).')
    parser.add_argument('-f', '--file-path', help='If this is set, only the indicated file will be translated.')
    parser.add_argument('-n', '--dont-cd', default=False, type=bool, help="If this is true, the script won't change the current directory.")
    args = parser.parse_args()

    source_folder = os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))
    dest_folder = tempfile.mkdtemp()
    language = args.language.capitalize()
    branch = args.branch
    model = args.model
    org_id = args.org_id

    openai.api_key = args.api_key
    if org_id:
        openai.organization = org_id

    if not args.dont_cd:
        # Change to the parent directory
        os.chdir(source_folder)
    
    if args.file_path:
        # Translate only the indicated file
        translate_file(language, args.file_path, os.path.join(dest_folder, args.file_path), model)
        # Delete possibly removed files from the master branch
        delete_unique_files(branch)
    else:
        # Translate everything
        translate_directory(language, source_folder, dest_folder, model)

    # Copy summary
    copy_summary(source_folder, dest_folder)

    # Copy .gitbook folder
    copy_gitbook_dir(source_folder, dest_folder) 

    # Create the branch and copy the translated files
    check_gh_branch(branch, dest_folder, args.file_path)
