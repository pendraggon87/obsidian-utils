# obsidian-utils
Utility scripts for Obsidian Notes

## Todolist aggregator

Aggregate all open tasks into one page by assigning a custom block id (UUID4) to each open task and embedding them within a master page.

```python
> python obtodolist.py --vault "c:\Vault\Location" --name "Open items"
```

### Todo

- Better documentation. Duh.
- Add error handling to check vault exists as part of a lambda in argparse
- Add actual documentation to this script
- Move to using / instead of \\ for file paths (yes yes, I created this on Windows. Deal with it for now kthx)