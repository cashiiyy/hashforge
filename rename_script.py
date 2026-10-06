import os
import shutil

# Step 1: Rename files and directories
if os.path.exists("cupp.py"):
    os.remove("cupp.py")

if os.path.exists("cupp.cfg"):
    os.rename("cupp.cfg", "hashforge.cfg")

if os.path.exists("test_cupp.py"):
    os.rename("test_cupp.py", "test_hashforge.py")

if os.path.exists("cupp") and os.path.isdir("cupp"):
    os.rename("cupp", "hashforge")

# Step 2: Replace occurrences of 'cupp' with 'hashforge' in specific files
files_to_update = [
    "hashforge.py",
    "hashforge.cfg",
    "test_hashforge.py",
    "README.md",
    "CHANGELOG.md"
]

# also all python files in hashforge directory
for root, _, files in os.walk("hashforge"):
    for file in files:
        if file.endswith(".py"):
            files_to_update.append(os.path.join(root, file))

for file_path in files_to_update:
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        
        # We need to be careful with casing. Let's do a few simple replacements:
        content = content.replace("from cupp import", "from hashforge import")
        content = content.replace("from cupp.", "from hashforge.")
        content = content.replace("import cupp", "import hashforge")
        content = content.replace("cupp.cfg", "hashforge.cfg")
        
        # Also handle test references
        content = content.replace("cupp", "hashforge")
        content = content.replace("CUPP", "HashForge")

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

print("Renaming and replacements completed.")
