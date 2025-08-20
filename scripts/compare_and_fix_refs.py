#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path

SRC_DIR = Path("./src")
REFS_JSON = Path("/tmp/refs.json")

# Matches content between {{#ref}} and {{#endref}}, including newlines, lazily
REF_RE = re.compile(r"{{#ref}}\s*([\s\S]*?)\s*{{#endref}}", re.MULTILINE)

def extract_refs(text: str):
    """Return a list of refs (trimmed) in appearance order."""
    return [m.strip() for m in REF_RE.findall(text)]

def replace_refs_in_text(text: str, new_refs: list):
    """Replace all refs in text with new_refs, maintaining order."""
    matches = list(REF_RE.finditer(text))
    if len(matches) != len(new_refs):
        return text  # Can't replace if counts don't match
    
    # Replace from end to beginning to avoid offset issues
    result = text
    for match, new_ref in zip(reversed(matches), reversed(new_refs)):
        # Get the full match span to replace the entire {{#ref}}...{{#endref}} block
        start, end = match.span()
        # Format the replacement with proper newlines
        formatted_replacement = f"{{{{#ref}}}}\n{new_ref}\n{{{{#endref}}}}"
        result = result[:start] + formatted_replacement + result[end:]
    
    return result

def main():
    parser = argparse.ArgumentParser(description="Compare and fix refs between current branch and master branch")
    parser.add_argument("--files-unmatched-paths", type=str, 
                       help="Path to file where unmatched file paths will be saved (comma-separated on first line)")
    args = parser.parse_args()
    
    if not SRC_DIR.is_dir():
        raise SystemExit(f"Not a directory: {SRC_DIR}")
    
    if not REFS_JSON.exists():
        raise SystemExit(f"Reference file not found: {REFS_JSON}")
    
    # Load the reference refs from master branch
    try:
        with open(REFS_JSON, 'r', encoding='utf-8') as f:
            master_refs = json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise SystemExit(f"Error reading {REFS_JSON}: {e}")
    
    print(f"Loaded reference data for {len(master_refs)} files from {REFS_JSON}")
    
    files_processed = 0
    files_modified = 0
    files_with_differences = 0
    unmatched_files = []  # Track files with unmatched refs
    
    for md_path in sorted(SRC_DIR.rglob("*.md")):
        rel = md_path.relative_to(SRC_DIR).as_posix()
        rel_with_src = f"{SRC_DIR.name}/{rel}"  # Include src/ prefix for output
        files_processed += 1
        
        try:
            content = md_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            # Fallback if encoding is odd
            content = md_path.read_text(errors="replace")
        
        current_refs = extract_refs(content)
        
        # Check if file exists in master refs
        if rel not in master_refs:
            if current_refs:
                print(f"⚠️  NEW FILE with refs: {rel_with_src} (has {len(current_refs)} refs)")
                files_with_differences += 1
                unmatched_files.append(rel_with_src)
            continue
        
        master_file_refs = master_refs[rel]
        
        # Compare ref counts
        if len(current_refs) != len(master_file_refs):
            print(f"📊 REF COUNT MISMATCH: {rel_with_src} -- Master: {len(master_file_refs)} refs, Current: {len(current_refs)} refs")
            files_with_differences += 1
            unmatched_files.append(rel_with_src)
            continue
        
        # If no refs in either, skip
        if not current_refs and not master_file_refs:
            continue
        
        # Compare individual refs
        differences_found = False
        for i, (current_ref, master_ref) in enumerate(zip(current_refs, master_file_refs)):
            if current_ref != master_ref:
                if not differences_found:
                    print(f"🔍 REF DIFFERENCES in {rel_with_src}:")
                    differences_found = True
                print(f"   Ref {i+1}:")
                print(f"     Master:  {repr(master_ref)}")
                print(f"     Current: {repr(current_ref)}")
        
        if differences_found:
            files_with_differences += 1
            unmatched_files.append(rel_with_src)
            
            # Replace current refs with master refs
            try:
                new_content = replace_refs_in_text(content, master_file_refs)
                if new_content != content:
                    md_path.write_text(new_content, encoding="utf-8")
                    files_modified += 1
                    print(f"   ✅ Fixed refs in {rel_with_src}")
                else:
                    print(f"   ❌ Failed to replace refs in {rel_with_src}")
            except Exception as e:
                print(f"   ❌ Error fixing refs in {rel_with_src}: {e}")
    
    # Save unmatched files to specified path if requested
    if args.files_unmatched_paths and unmatched_files:
        try:
            unmatched_paths_file = Path(args.files_unmatched_paths)
            unmatched_paths_file.parent.mkdir(parents=True, exist_ok=True)
            with open(unmatched_paths_file, 'w', encoding='utf-8') as f:
                f.write(','.join(unmatched_files))
            print(f"📝 Saved {len(unmatched_files)} unmatched file paths to: {unmatched_paths_file}")
        except Exception as e:
            print(f"❌ Error saving unmatched paths to {args.files_unmatched_paths}: {e}")
    elif args.files_unmatched_paths and not unmatched_files:
        # Create empty file if no unmatched files found
        try:
            unmatched_paths_file = Path(args.files_unmatched_paths)
            unmatched_paths_file.parent.mkdir(parents=True, exist_ok=True)
            unmatched_paths_file.write_text('\n', encoding='utf-8')
            print(f"� No unmatched files found. Created empty file: {unmatched_paths_file}")
        except Exception as e:
            print(f"❌ Error creating empty unmatched paths file {args.files_unmatched_paths}: {e}")
    
    print(f"\n�📈 SUMMARY:")
    print(f"   Files processed: {files_processed}")
    print(f"   Files with differences: {files_with_differences}")
    print(f"   Files modified: {files_modified}")
    if unmatched_files:
        print(f"   Unmatched files: {len(unmatched_files)}")

if __name__ == "__main__":
    main()
