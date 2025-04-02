# Asynchronous File Sorter

## Description
This script sorts files from a source directory into various subdirectories of a target directory based on their extensions. The program uses asynchronous programming for efficient processing of large numbers of files simultaneously.

## Features
- **Asynchronous processing**: uses `asyncio` for parallel reading and copying of files
- **Recursive traversal**: ability to process nested folders
- **Extension-based sorting**: automatically creates subdirectories for each file type
- **Duplicate handling**: automatically renames files with identical names
- **Detailed logging**: records all operations and errors to console and log file

## Installation

### Requirements
- Python 3.7 or higher
- Standard Python library (no additional dependencies required)

### Installation
1. Clone the repository or download the script file:
```bash
git clone https://github.com/username/async-file-sorter.git
```

2. Make the script file executable (for Linux/Mac):
```bash
chmod +x file_sorter.py
```

## Usage

### Basic Usage
```bash
python file_sorter.py -s /path/to/source/folder -d /path/to/destination/folder
```

### Command Line Options
- `-s, --source`: Source folder containing files to sort (required parameter)
- `-d, --destination`: Target folder where sorted files will be placed (required parameter)
- `-r, --recursive`: Process subfolders recursively (optional parameter)

### Examples

#### Sorting Files from a Single Folder
```bash
python file_sorter.py -s ~/Downloads -d ~/Sorted
```

#### Recursively Sorting Files
```bash
python file_sorter.py -s ~/Desktop/Unsorted -d ~/Desktop/Sorted -r
```

## Project Structure
```
.
├── file_sorter.py     # Main program script
├── file_sorter.log    # Log file (created when script runs)
└── README.md          # This file
```

## How It Works
1. The script analyzes the specified command-line parameters
2. Checks for the existence of the source directory and creates the target directory if it doesn't exist
3. Recursively or non-recursively traverses all files in the source directory
4. For each file:
   - Determines its extension
   - Creates the corresponding subfolder in the target directory (if it doesn't already exist)
   - Copies the file to the appropriate folder
   - Renames the file if a file with the same name already exists
5. Logs all operations and errors

## Special Case Handling
- Files without extensions are placed in a `no_extension` subfolder
- If a file with the same name already exists in the target subfolder, a unique identifier is added to the filename

## Logging
The script maintains a detailed operation log. Logs are written to:
- The console (INFO level and above)
- The `file_sorter.log` file (INFO level and above)

## Limitations
- The script copies files rather than moving them, so original files remain in place
- Large files may consume significant memory during copying
- The script checks only file extensions, not their contents