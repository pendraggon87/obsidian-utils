import argparse
import glob
import logging
import os
import re
import shutil
import uuid
from datetime import datetime
from pathlib import Path

'''
    TODO: Add error handling to check vault exists as part of a lambda in argparse
    TODO: Add actual documentation to this script
    TODO: Move to using / instead of \\ for file paths (yes yes, I created this on Windows. Deal with it for now)
'''

#region Configure argparse
parser = argparse.ArgumentParser(
    prog = "obsidiantodo",
    description = "Todolist aggregator for Obsidian Notes"
)
parser.add_argument("--vault",
    type = str,
    help = "Location of your Obsidian Vault"
)
parser.add_argument("-t"
    "--tags",
    default = ["todo"],
    action = "store",
    nargs = "+",
    required = False,
    help = "Tags to apply to the todolist page"
)
parser.add_argument("-n"
    "--name",
    default = "Open items",
    action = "store",
    required = False,
    help = "Name and heading of the todolist page"
)
parser.add_argument("--no-backup",
    action = "store_true",
    required = False,
    help = "Skip backup of vault. Not recommended."
)
parser.add_argument("-p",
    "--backup-path",
    action = "store",
    type = str,
    required = False,
    help = "Vault backup location. Defaults to directory above the vault."
)
parser.add_argument("-v",
    "--verbose",
    action = "store_true",
    help = "Enable verbose logging"
)
args = parser.parse_args()
#endregion

#region Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG if args.verbose else logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG if args.verbose else logging.INFO)
ch.setFormatter(formatter)
logger.addHandler(ch)
#endregion

vault = args.vault
backup_path = Path(args.vault).parent.absolute() if args.backup_path == None else args.backup_path
generator = "Obsidian Todo Aggregator"
version = "21.05.1a"
tags = args.t__tags
todolist_heading = args.n__name
todolist_filename = f"{args.n__name}.md"
todolist_filepath = vault # TODO: Make this customizable
incomplete_pattern = re.compile(r"^\s*-\s\[\s\].*$", re.MULTILINE)
uuid_pattern = re.compile(r'.*\^([0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12})$', re.I)

def backup_vault(backup_path: str, vault_path: str):
    logger.info(f"Backing up vault {vault} to {backup_path}.zip")
    shutil.make_archive(backup_path, "zip", vault_path)



def get_todo_list() -> str:
    todo = f"""---
tags: [{','.join(tags)}]
generator: {generator} v{version}
created: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
---

# {todolist_heading}

"""
    logger.info(f"Searching {vault} for incomplete todos")
    for filename in glob.iglob(vault + "/**/*.md", recursive=True):
        logger.debug(f"Filename:\t{filename}")
        if(filename == f"{todolist_filepath}\\{todolist_filename}"):
            continue
        with open(filename, "r", encoding="utf8") as f:
            text = f.read()
        matches = re.findall(incomplete_pattern, text)
        if matches:
            logger.info(f"{filename} has {len(matches)} incomplete todos")
            
            link_path = os.path.dirname(filename).replace(vault, '').replace('\\', '/').strip("/")
            
            if link_path == '':
                link = os.path.basename(filename)
            else:
                link = f"{link_path}/{os.path.basename(filename)}"
            todo += f"\n## [[{link}]]\n"
            
            for match in matches:
                if not uuid_pattern.match(match):
                    u = uuid.uuid4()
                    newtext = f"{match} ^{u}"
                    todo += f"![[{link}#^{u}]]\n"
                    text = text.replace(match, newtext)
                else:
                    todo += f"![[{link}#^{uuid_pattern.match(match).group(1)}]]\n"
        with open(filename, "w", encoding="utf8") as f:
            f.write(text)
    
    return todo

def write_todolist(todo_text: str, file_name: str):
    logger.info(f"Writing todo list to {file_name}")
    with open(file_name, "w", encoding="utf8") as f:
        f.write(todo_text)

def main():
    vault_name = os.path.basename(os.path.normpath(vault))
    backup_vault(f"{backup_path}\\{vault_name}", vault)
    
    todos = get_todo_list()

    write_todolist(todos, f"{todolist_filepath}/{todolist_filename}")

if __name__ == "__main__":
    main()
