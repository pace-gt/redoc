#!/bin/bash

property="redoc"

if [ ! -z "$1" ]
then
    reframe -C ~/reframe/pace/config/settings.py --prefix ~/scratch/reframe -c ~/reframe/pace -R -t "$property" -r
fi

echo
echo Generating documentation for the following RTs:

lines="$(reframe -C ~/reframe/pace/config/settings.py --prefix ~/scratch/reframe -c ~/reframe/pace -R -t $property -l | grep '(found in')"
if [ -z "$lines" ]
then
    echo "No RT's with the '$property' property found!"
    echo Done.
    exit 0
fi

while IFS= read -r line
do
    module="$(echo "$line" | cut -d '/' -f 8)"
    rt="$(echo "$line" | cut -d ' ' -f 4)"
    pyfile="$(echo "$line" | cut -d ' ' -f 7 | cut -d ')' -f 1)"
    if grep -q 'self.sourcesdir =' "$pyfile"
    then
        if ! [ "$(grep -c 'self.sourcesdir = None' "$pyfile")" -eq "$(grep -c 'self.sourcesdir =' "$pyfile")" ]
        then
            echo "$module: $rt (Error: non-standard src directory.)"
            continue
        fi
    fi
    src_dir="$HOME/reframe/pace/$module/src"
    if [ -d "$src_dir" ]
    then
        src_dir_flag="-s $src_dir"
    else
        src_dir_flag=""
    fi
    serial_output_dir="$HOME/scratch/reframe/output/local/serial/PrgEnv-intel/$rt"
    parallel_output_dir="$HOME/scratch/reframe/output/local/parallel/PrgEnv-intel/$rt"
    [ -d "$serial_output_dir" ] && output_dir="$serial_output_dir"
    [ -d "$parallel_output_dir" ] && output_dir="$parallel_output_dir"
    if [ -z "$output_dir" ]
    then
        echo "$module: $rt (Error: can't find output directory.)"
        continue
    fi
    echo "$module: $rt"
    python generate_documentation.py -m "$module" $src_dir_flag -o "$output_dir"
done <<< "$lines"

echo Done.
echo
