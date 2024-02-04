#!/bin/bash
# Create lambda function zip files for each subdirectory under "lambdas/".
# Loops through the subdirectories under "lambdas/" and create a ZIP file for each, 
# including the Python packages from "requirements.txt" in each subdirectory. 
# Each lambda function directory in "lambdas/" should have a "requirements.txt" file and
# a python script that will be used for the lambda function.

# Output: "deploy" directory will be created in the root directory, and the ZIP files will be placed there.

# Example directory structure:
# root/
#   lambdas/
#     lambda1/
#       lambda1.py
#       requirements.txt
#     lambda2/
#       lambda2.py
#       requirements.txt
#     lambda3/
#       lambda3.py
#       requirements.txt

# # Base project directory
# BASE_DIR=${1:-"/Users/anguswatters/Desktop/github/recipe_api"}

# Check if the BASE_DIR is provided as a command-line argument, if so, use it, otherwise use the current directory
if [ -z "$1" ] || [ "$1" == "." ]; then
    BASE_DIR=$(pwd)  # Use the current directory if no argument is provided
    echo "BASE_DIR not provided, using current directory: $BASE_DIR"
    echo "pwd: $(pwd)"
else
    BASE_DIR=$1
fi

echo "BASE_DIR: $BASE_DIR"

# Set the deploy directory
DEPLOY_DIR="$BASE_DIR/deploy"

# Set the app directory name (where the lambda functions are located, each lambda function in its own subdirectory)
APP_DIR="lambdas"

echo "Creating deploy directory if it doesn't exist"
echo "DEPLOY_DIR:\n --> $DEPLOY_DIR"

# Creating the deploy directory
mkdir -p "$DEPLOY_DIR"

# Iterate through each subdirectory under "lambda/"
for SUBDIR in "$BASE_DIR/$APP_DIR"/*; do
    if [ -d "$SUBDIR" ]; then
        # Extract the directory name
        DIR_NAME=$(basename "$SUBDIR")

        # Set the target directory and ZIP file for the current subdirectory
        PKG_DIR="$BASE_DIR/$APP_DIR/package"
        TARGET_DIR="$SUBDIR/package"
        ZIP_FILE="$DEPLOY_DIR/$DIR_NAME.zip"

        echo "--------------------------------------------------------------"
        echo "---- Creating lambda package: '$DIR_NAME' ----"
        echo "--------------------------------------------------------------"

        echo "- SUBDIR: $SUBDIR"
        echo "- DIR_NAME: $DIR_NAME"
        echo "- PKG_DIR: $PKG_DIR"
        echo "- TARGET_DIR: $TARGET_DIR"
        echo "- ZIP_FILE: $ZIP_FILE"
        echo "------------------------------------------------"

        echo "Making temporary directory for Python packages"

        # # Ensure the "PKG_DIR" directory exists
        mkdir -p "$PKG_DIR"

        echo "Installing Python packages from 'requirements.txt to 'PKG_DIR'"

        pip install \
            --platform manylinux2014_x86_64 \
            --target "$PKG_DIR" \
            --implementation cp \
            --python-version 3.11 \
            --only-binary=:all: --upgrade \
            -q \
            -r "$SUBDIR/requirements.txt"

        # check if the current directory is the "app" directory, if not, then find and remove unwanted directories
        if [ "$DIR_NAME" != "app" ]; then

            echo "Removing 'tests', 'examples', and '__pycache__' files from package directory"

            # # # Remove unwanted directories (tests/, docs/, examples/, __pycache__/)
            find "$PKG_DIR" -type d -name "tests" -exec rm -rf {} +
            # find "$PKG_DIR" -type d -name "docs" -exec rm -rf {} +
            find "$PKG_DIR" -type d -name "examples" -exec rm -rf {} +
            find "$PKG_DIR" -type d -name "__pycache__" -exec rm -rf {} +
        else
            echo "'tests', 'examples', and '__pycache__' files are KEPT in 'app' package directory"
        fi

        # Go into the PKG_DIR directory
        cd "$PKG_DIR" 

        # Count the number of files in the directory
        file_count=$(find "$PKG_DIR" -type f | wc -l)

        echo "Number of files in the directory: $file_count"

        # Check if the directory is empty
        if [ "$file_count" -eq 0 ]; then
            echo "PKG_DIR directory is empty"
        else
            echo "PKG_DIR directory is NOT empty."
        fi

        echo "Adding simple JSON file to make sure directory is NOT empty."
            
        # Create an empty JSON file with the file count to make sure the directory is NOT empty
        echo "{\"$DIR_NAME\": $file_count}" > "$PKG_DIR/file_count.json"
        
        echo "------------------------------------------------"
        echo "Zipping 'PKG_DIR' contents into 'ZIP_FILE'..."

        # echo -e "PKG_DIR: $PKG_DIR\n---> ZIP_FILE:\n --> $ZIP_FILE"
        echo "Sending PKG_DIR contents to ZIP_FILE:"
        echo -e " PKG_DIR: '$PKG_DIR' \n   --------> \n ZIP_FILE: '$ZIP_FILE'"
        echo "------------------------------------------------"

        # Create the initial ZIP file with the Python packages
        zip -r9 -q "$ZIP_FILE" .

        # Go back to the original directory
        cd "$BASE_DIR/$APP_DIR/"

        echo "Updated ZIP_FILE with DIR_NAME contents"
        # echo "Updated '$ZIP_FILE' with '$DIR_NAME' contents"

        # For all directories except "app", add the contents of the given lambdas/ subdirectory (DIR_NAME) 
        # to the ZIP file EXCLUDING the "config.py" file,
        # otherwise in the 'app' directory, KEEP the "config.py" file
        if [ "$DIR_NAME" != "app" ]; then
            echo -e "Adding '$DIR_NAME' contents to:\n '$ZIP_FILE'\n(EXCLUDING 'config.py' file)"
            # Add the contents of the given lambdas/ subdirectory (DIR_NAME) to the ZIP file, (EXCLUDE the "config.py" file)
            zip -g "$ZIP_FILE" -r "$DIR_NAME" -x "$DIR_NAME/config.py"
            # zip -g "$ZIP_FILE" -r "$DIR_NAME" -x "$DIR_NAME/config.py" -x "*/__pycache__/*"
            # zip -g "$ZIP_FILE" -r "$DIR_NAME" -x "$DIR_NAME/config.py" -x "**/__pycache__/"
        else
            echo -e "Adding '$DIR_NAME' contents to:\n '$ZIP_FILE'\n(INCLUDING 'config.py' file)"
            # Add the contents of the given lambdas/ subdirectory (DIR_NAME) to the ZIP file (KEEP the "config.py" file)
            zip -g "$ZIP_FILE" -r "$DIR_NAME"
        fi

        echo "Removing $PKG_DIR"

        # remove the PKG_DIR directory
        rm -rf "$PKG_DIR"

        cd "$BASE_DIR"

        echo "====================================================="
        echo "====================================================="
    fi
done
