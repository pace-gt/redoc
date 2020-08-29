#!/bin/bash

# Define constants
config_file="config.json"
tag="redoc"
docs="docs"

# Ensure proper usage
if [ $# -ne 0 ]
then
    echo "Error: redoc_tagged does not take arguments."
    exit 2
fi

# Read info from redoc config file
if [ -f "$config_file" ]
then
    reframe_config_file="$(jq -r ".reframe_config_file" config.json)"
    reframe_prefix="$(jq -r ".reframe_prefix" config.json)"
    reframe_test_directory="$(jq -r ".reframe_test_directory" config.json)"
else
    echo "Error: Please set up $config_file."
    exit 1
fi

# Ensure that specified reframe config file exists
if [ ! -f "$reframe_config_file" ]
then
    echo "Error: File '$reframe_config_file' does not exist."
    exit 1
fi

# Ensure that specified reframe test directory exists
if [ ! -d "$reframe_test_directory" ]
then
    echo "Error: Directory '$reframe_test_directory' does not exist."
    exit 1
fi

# Announce start of loop
echo
echo "Generating documentation from the following reframe tests:"

# Find reframe tests with redoc tag
lines="$(reframe -C "$reframe_config_file" --prefix "$reframe_prefix" -c "$reframe_test_directory" -R -t "$tag" -l | grep '(found in')"

# Exit if no tests found
if [ -z "$lines" ]
then
    echo "No RT's in $reframe_test_directory with the '$tag' tag found!"
    echo Done.
    exit 0
fi

# Main loop
while IFS= read -r line
do

    # Determine basic information about reframe test
    module="$(echo "$line" | cut -d '/' -f 8)"
    rt="$(echo "$line" | cut -d ' ' -f 4)"
    echo -n "    $module ($rt):"
    pyfile="$(echo "$line" | cut -d ' ' -f 7 | cut -d ')' -f 1)"

    # Check if documentation already exists
    if [ -f "$docs/${module}.md" ]
    then
        echo " Error: '$docs/${module}.md' already exists! To generate a new version, delete it and rerun redoc_tagged."
        continue
    fi

    # Make sure source directory is named src and located where expected
    if grep -q 'self.sourcesdir =' "$pyfile"
    then
        if ! [ "$(grep -c 'self.sourcesdir = None' "$pyfile")" -eq "$(grep -c 'self.sourcesdir =' "$pyfile")" ]
        then
            echo " Error: Non-standard src directory."
            continue
        fi
    fi
    src_dir="$reframe_test_directory/$module/src"
    if [ -d "$src_dir" ]
    then
        src_dir_flag="-s $src_dir"
    else
        src_dir_flag=""
    fi

    # Determine output directory location of reframe test
    rt_description="$(reframe -C "$reframe_config_file" --prefix "$reframe_prefix" -c "$reframe_test_directory" -R -n "$rt" -L)"
    system="$(echo "$rt_description" | grep systems: | cut -d ' ' -f 9 | cut -d ',' -f 1 | tr ':' '/')"
    environment="$(echo "$rt_description" | grep environments: | cut -d ' ' -f 9 | cut -d ',' -f 1)"
    output_dir="$reframe_prefix/output/$system/$environment/$rt"

    # If output directory does not exist, generate it by running reframe test
    if [ ! -d "$output_dir" ]
    then
        echo -n " Output directory not found. Running test to generate output directory..."
        reframe -C "$reframe_config_file" --prefix "$reframe_prefix" -c "$reframe_test_directory" -R -n "$rt" -r 1>/dev/null 2>/dev/null
        echo -n " Done."
    fi

    # Ensure that output directory exists
    if [ ! -d "$output_dir" ]
    then
        echo " Error: Output directory still not found."
        continue
    fi

    # Call redoc script on reframe test
    python redoc.py -m "$module" $src_dir_flag -o "$output_dir"

done <<< "$lines"

# Announce end of loop
echo Done.
echo

# Remove any files created by reframe
rm reframe.log 1>/dev/null 2>/dev/null
rm reframe.out 1>/dev/null 2>/dev/null