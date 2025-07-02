# PSEUDOCODE:
"""
Function: validate_destination_path(path) -> bool
* Try to create and delete tmp file in the directory
* If successful, return True
* Catch permission or IO errors -> return False

Function: perform_backup(src, dst, compress=False)
* Verify paths exist
* If compress:
- * Zip contents and move to dst
* Else:
- * recursively copy files using shutil
* return status/logs
"""