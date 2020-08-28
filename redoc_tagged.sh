#!/bin/bash

tag="redoc"

if [ $# -ne 3 ]
then
    echo "Usage: redoc_all.sh <reframe config file> <reframe prefix> <reframe test directory>"
    exit 0
fi

echo
echo "Generating documentation from the following reframe tests:"

lines="$(reframe -C "$1" --prefix "$2" -c "$3" -R -t "$tag" -l | grep '(found in')"
if [ -z "$lines" ]
then
    echo "No RT's in $3 with the '$tag' tag found!"
    echo Done.
    exit 0
fi

while IFS= read -r line
do
    module="$(echo "$line" | cut -d '/' -f 8)"
    rt="$(echo "$line" | cut -d ' ' -f 4)"
    echo -n "    $module ($rt):"
    pyfile="$(echo "$line" | cut -d ' ' -f 7 | cut -d ')' -f 1)"
    if grep -q 'self.sourcesdir =' "$pyfile"
    then
        if ! [ "$(grep -c 'self.sourcesdir = None' "$pyfile")" -eq "$(grep -c 'self.sourcesdir =' "$pyfile")" ]
        then
            echo " Error: Non-standard src directory."
            continue
        fi
    fi
    src_dir="$3/$module/src"
    if [ -d "$src_dir" ]
    then
        src_dir_flag="-s $src_dir"
    else
        src_dir_flag=""
    fi

    rt_description="$(reframe -C "$1" --prefix "$2" -c "$3" -R -n "$rt" -L)"
    system="$(echo "$rt_description" | grep systems: | cut -d ' ' -f 9 | cut -d ',' -f 1 | tr ':' '/')"
    environment="$(echo "$rt_description" | grep environments: | cut -d ' ' -f 9 | cut -d ',' -f 1)"
    output_dir="$2/output/$system/$environment/$rt"

    if [ ! -d "$output_dir" ]
    then
        echo -n " Output directory not found. Running test to generate output directory..."
        reframe -C "$1" --prefix "$2" -c "$3" -R -n "$rt" -r 1>/dev/null 2>/dev/null
        echo -n " Done."
    fi

    if [ ! -d "$output_dir" ]
    then
        echo " Error: Output directory still not found."
        continue
    fi

    python redoc.py -m "$module" $src_dir_flag -o "$output_dir"

done <<< "$lines"

echo Done.
echo
rm reframe.log 1>/dev/null 2>/dev/null
rm reframe.out 1>/dev/null 2>/dev/null
