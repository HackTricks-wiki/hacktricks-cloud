import argparse
import os
from openai import OpenAI #pip3 install openai
import time
import shutil
import tempfile
import subprocess
import sys
import tiktoken
import concurrent.futures
from tqdm import tqdm #pip3 install tqdm
import traceback



MASTER_BRANCH = "master"
VERBOSE = True
MAX_TOKENS = 10000 #gpt-4-1106-preview

def reportTokens(prompt, model):
    encoding = tiktoken.encoding_for_model(model)
    # print number of tokens in light gray, with first 50 characters of prompt in green. if truncated, show that it is truncated
    #print("\033[37m" + str(len(encoding.encode(prompt))) + " tokens\033[0m" + " in prompt: " + "\033[92m" + prompt[:50] + "\033[0m" + ("..." if len(prompt) > 50 else ""))
    return len(encoding.encode(prompt))


def check_git_dir(path):
    if os.path.isdir(os.path.join(path, '.git')):
        return True
    return False

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
    
    print(f"[+] Deleted {len(unique_files)} files from branch: {branch}")


def cp_translation_to_repo_dir_and_check_gh_branch(branch, temp_folder, translate_files):
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
    
    if translate_files:
        subprocess.run(['git', 'add', "-A"])
        subprocess.run(['git', 'commit', '-m', f"Translated {translate_files} to {branch}"[:72]])
        subprocess.run(['git', 'checkout', MASTER_BRANCH])
        print("Commit created and moved to master branch")
    else:
        print("No commiting anything, leaving in language branch")


def translate_text(language, text, file_path, model, cont=0, slpitted=False, client=None):
    if not text:
        return text
    
    messages = [
        {"role": "system", "content": "You are a professional hacker, translator and writer. You write everything super clear and as concise as possible without loosing information."},
        {"role": "system", "content": f"The following is content from a hacking book about hacking techiques. The following content is from the file {file_path}. Translate the relevant English text to {language} and return the translation keeping excatly the same markdown and html syntax. Do not translate things like code, hacking technique names, hacking word, cloud/SaaS platform names (like Workspace, aws, gcp...), the word 'leak', pentesting, and markdown tags. Also don't add any extra stuff apart from the translation and markdown syntax."},
        {"role": "user", "content": text},
    ]
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0
        )
    except Exception as e:
        print(e)
        if cont > 6:
            print(f"Page {file_path} could not be translated due to count with text: {text}\nReturning text as is.")
            return text
        if "is currently overloaded" in str(e).lower():
            print("Overloaded, waiting 30 seconds")
            time.sleep(30)
        elif "timeout" in str(e).lower():
            print("Timeout, waiting 30 seconds")
            cont += 1
            time.sleep(30)
        elif "rate limit" in str(e).lower():
            print("Rate limit, waiting 60 seconds")
            cont += 1
            time.sleep(60)
        elif "maximum context length" in str(e).lower():
            print("Maximum context length, splitting text in two and translating separately")
            if slpitted:
                #print(f"Page {file_path} could not be translated with text: {text}")
                print(f"Page {file_path} could not be translated.\nReturning text as is.")
                return text
            
            text1 = text.split('\n')[:len(text.split('\n'))//2]
            text2 = text.split('\n')[len(text.split('\n'))//2:]
            return translate_text(language, '\n'.join(text1), file_path, model, cont, False, client) + '\n' + translate_text(language, '\n'.join(text2), file_path, model, cont, True, client)
        
        print("Retrying translation")
        return translate_text(language, text, file_path, model, cont, False, client)

    response_message = response.choices[0].message.content.strip()

    # Sometimes chatgpt modified the number of "#" at the beginning of the text, so we need to fix that. This is specially important for the first line of the MD that mucst have only 1 "#"
    cont2 = 0
    while (text.startswith('# ') and not response_message[cont2:].startswith('# ')):
        cont2 += 1
        if cont2 > 3:
            cont2 = 0
            print(f"Error with initial '#', something went wrong, recheck: {response_message[:30]}")
            break
    
    response_message = response_message[cont2:]
        
    return response_message


def split_text(text, model):
    global MAX_TOKENS
    lines = text.split('\n')
    chunks = []
    chunk = ''
    in_code_block = False

    for line in lines:
        # If we are in a code block, just add the code to the chunk
        if line.startswith('```'):
            
            # If we are in a code block, finish it with the "```"
            if in_code_block:
                chunk += line + '\n'
            
            in_code_block = not in_code_block
            chunks.append(chunk.strip())
            chunk = ''

            # If a code block is started, add the "```" to the chunk
            if in_code_block:
                chunk += line + '\n'
            
            continue


        if (line.startswith('#') and reportTokens(chunk + "\n" + line.strip(), model) > MAX_TOKENS*0.8) or \
            reportTokens(chunk + "\n" + line.strip(), model) > MAX_TOKENS:
            
            chunks.append(chunk.strip())
            chunk = ''
        
        chunk += line.strip() + '\n'

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
    print("[+] Copied SUMMARY.md")

def translate_file(language, file_path, file_dest_path, model, client):
    global VERBOSE
    
    if file_path.endswith('SUMMARY.md'):
        return
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    content_chunks = split_text(content, model)

    translated_content = ''
    start_time = time.time()
    for chunk in content_chunks:
        # Don't trasnlate code blocks
        if chunk.startswith('```'):
            translated_content += chunk + '\n'
        else:
            translated_content += translate_text(language, chunk, file_path, model, cont=0, slpitted=False, client=client) + '\n'
    
    elapsed_time = time.time() - start_time

    # make sure directory exists
    os.makedirs(os.path.dirname(file_dest_path), exist_ok=True)
    with open(file_dest_path, 'w', encoding='utf-8') as f:
        f.write(translated_content)
    
    #if VERBOSE:
    print(f"Page {file_path} translated in {elapsed_time:.2f} seconds")


def translate_directory(language, source_path, dest_path, model, num_threads, client):
    all_markdown_files = []
    for subdir, dirs, files in os.walk(source_path):
        for file in files:
            if file.endswith('.md') and file != "SUMMARY.md":
                source_filepath = os.path.join(subdir, file)
                dest_filepath = os.path.join(dest_path, os.path.relpath(source_filepath, source_path))
                all_markdown_files.append((source_filepath, dest_filepath))
    
    print(f"Translating {len(all_markdown_files)} files")

    #with tqdm(total=len(all_markdown_files), desc="Translating Files") as pbar:
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = []
        for source_filepath, dest_filepath in all_markdown_files:
            if os.path.exists(dest_filepath):
                continue
            os.makedirs(os.path.dirname(dest_filepath), exist_ok=True)
            future = executor.submit(translate_file, language, source_filepath, dest_filepath, model, client)
            futures.append(future)

        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
                #pbar.update()
            except Exception as exc:
                tb = traceback.format_exc()
                print(f'Translation generated an exception: {exc}')
                print("Traceback:", tb)
                

if __name__ == "__main__":
    print("- Version 1.1.1")
    # Set up argparse
    parser = argparse.ArgumentParser(description='Translate gitbook and copy to a new branch.')
    parser.add_argument('-d', '--directory', action='store_true', help='Translate a full directory.')
    parser.add_argument('-l', '--language', required=True, help='Target language for translation.')
    parser.add_argument('-b', '--branch', required=True, help='Branch name to copy translated files.')
    parser.add_argument('-k', '--api-key', required=True, help='API key to use.')
    parser.add_argument('-m', '--model', default="gpt-3.5-turbo-0125", help='The openai model to use. By default: gpt-3.5-turbo-0125')
    parser.add_argument('-o', '--org-id', help='The org ID to use (if not set the default one will be used).')
    parser.add_argument('-f', '--file-paths', help='If this is set, only the indicated files will be translated (" , " separated).')
    parser.add_argument('-n', '--dont-cd', action='store_false', help="If this is true, the script won't change the current directory.")
    parser.add_argument('-t', '--threads', default=5, type=int, help="Number of threads to use to translate a directory.")
    #parser.add_argument('-v', '--verbose', action='store_false', help="Get the time it takes to translate each page.")
    args = parser.parse_args()

    source_folder = os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))
    dest_folder = tempfile.mkdtemp()
    language = args.language.capitalize()
    branch = args.branch
    model = args.model
    org_id = args.org_id 
    num_threads = args.threads
    #VERBOSE = args.verbose

    client = OpenAI(
        api_key=args.api_key,
        organization=org_id
    )
    
    # Start with the current directory.
    current_dir = os.getcwd()

    # Check if model is gpt-3.5
    if "gpt-3.5" in model:
        MAX_TOKENS = 2000

    # Check the current directory
    if check_git_dir(current_dir):
        print('Found .git directory in current directory: ' + current_dir)
    else:
        # Check the parent directory
        parent_dir = os.path.dirname(current_dir)
        if check_git_dir(parent_dir):
            print('Found .git directory in parent directory: ' + parent_dir)
            
            # Change the current working directory to the parent directory
            os.chdir(parent_dir)
            print('Current working directory has been changed to: ' + os.getcwd())
        else:
            print('No .git directory found in current or parent directory. Exiting.')
            exit(1)

    current_dir = os.getcwd()
    print(f"The translated files will be copied to {current_dir}, make sure this is the expected folder.")

    if not args.dont_cd:
        # Change to the parent directory
        os.chdir(source_folder)
    
    translate_files = None # Need to initialize it here to avoid error
    if args.file_paths:
        # Translate only the indicated file
        translate_files = [f for f in args.file_paths.split(' , ') if f]
        for file_path in translate_files:
            #with tqdm(total=len(all_markdown_files), desc="Translating Files") as pbar:
            with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
                futures = []                
                future = executor.submit(translate_file, language, file_path, os.path.join(dest_folder, file_path), model, client)
                futures.append(future)

                for future in concurrent.futures.as_completed(futures):
                    try:
                        future.result()
                        #pbar.update()
                    except Exception as exc:
                        print(f'Translation generated an exception: {exc}')
        
        # Delete possibly removed files from the master branch
        delete_unique_files(branch)
    
    elif args.directory:
        # Translate everything
        translate_directory(language, source_folder, dest_folder, model, num_threads, client)
    
    else:
        print("You need to indicate either a directory or a list of files to translate.")
        exit(1)

    # Copy summary
    copy_summary(source_folder, dest_folder)

    # Copy .gitbook folder
    copy_gitbook_dir(source_folder, dest_folder) 

    # Create the branch and copy the translated files
    cp_translation_to_repo_dir_and_check_gh_branch(branch, dest_folder, translate_files)
