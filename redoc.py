# Imports
import argparse
import sys
import subprocess
import json
import re
import os
import jinja2

# Configure argparse
parser = argparse.ArgumentParser(
    description='Generates help documentation for a module from a reframe test'
)
parser.add_argument(
    '-m', '--module',
    type=str, required=True,
    help='The module for which to generate documentation'
)
parser.add_argument(
    '-o', '--output_dir',  # Change? (misleading)
    type=str, required=True,
    help=('The output directory for the reframe test '
          'from which to generate documentation')
)
parser.add_argument(
    '-s', '--src_dir',
    type=str,
    help=('The source directory for the reframe test '
          'from which to generate documentation')
)
args = parser.parse_args()

# Make sure directory arguments are formatted correctly
if args.src_dir is not None:
    src_dir = args.src_dir
    if len(src_dir) == 0:
        print('Argument error: src_dir should not be empty string')
        sys.exit(2)
    if src_dir[-1] == '/':
        src_dir = src_dir[:-1]
output_dir = args.output_dir
if len(output_dir) == 0:
    print('Argument error: please enter a non-empty string for output_dir')
    sys.exit(2)
if output_dir[-1] == '/':
    output_dir = output_dir[:-1]

# Determine template variable 'module'
module = args.module

# Determine template variable 'module_help'
module_help = ''
data_json = subprocess.check_output(
    ('LMOD_RC=/usr/local/pace-apps/lmod'
     '/site/lmodrc.lua'
     ' /usr/local/pace-apps/lmod/lmod'
     '/libexec/spider -o jsonSoftwarePage'
     ' "$MODULEPATH"'), shell=True
)
data = json.loads(data_json)
for package in data:
    if package['package'] == module:
        if 'help' in package['versions'][0]:
            module_help = package['versions'][0]['help']
            break
if re.match(r'^\s*module load.*', module_help):  # Prevents useless help text
    module_help = None

# Determine template variable 'makefile'

if args.src_dir is not None:
    makefile_path = '{}/Makefile'.format(src_dir)
    if os.path.exists(makefile_path):
        makefile = 'Makefile'
    else:
        makefile = ''
else:
    makefile = ''

# Determine template variables 'source_files',
# 'input_files', and 'input_directories'


# Determine whether files in src are relevant to this example
def find_relevant(src_files, text, relevant_src_files):
    for src_file in src_files:
        if '.' in src_file:
            name_noext = src_file[:src_file.find('.')]
        else:
            name_noext = src_file
        if name_noext in text and (src_file not in relevant_src_files):
            relevant_src_files.append(src_file)
            file_path = '{}/{}'.format(src_dir, src_file)
            if os.path.isfile(file_path):
                reader = open(file_path, 'r')
                new_text = reader.read()
                find_relevant(src_files, new_text, relevant_src_files)


# Determine whether a file in src is a source file or an input file
def has_source_extension(name):
    extensions = ['.c', '.cc', '.cpp', '.java', '.pl', '.vb', '.swift', '.f90',
                  '.f95', '.f03', '.for', '.f', '.py', '.sh']  # Add more
    for extension in extensions:
        pattern = '^[\\S ]+\\{}$'.format(extension)
        if re.match(pattern, name):
            return True
    return False


job_shell_file_path = '{}/rfm_{}_job.sh'.format(
    output_dir,
    output_dir.split('/')[-1]
)
job_shell_reader = open(job_shell_file_path, 'r')
job_shell = job_shell_reader.read()
build_shell_file_path = '{}/rfm_{}_build.sh'.format(
    output_dir,
    output_dir.split('/')[-1]
)
if os.path.exists(build_shell_file_path):
    build_shell_reader = open(build_shell_file_path, 'r')
    build_shell = build_shell_reader.read()
else:
    build_shell = ''
combined_shell = build_shell + job_shell
if args.src_dir is not None:
    src_files = os.listdir(src_dir)
    relevant_src_files = []
    find_relevant(src_files, combined_shell, relevant_src_files)
    source_files = []
    input_files = []
    input_directories = []
    for src_file in relevant_src_files:
        full_path = '{}/{}'.format(src_dir, src_file)
        if os.path.isdir(full_path):
            input_directories.append(src_file)
        elif has_source_extension(src_file):
            source_files.append(src_file)
        else:
            input_files.append(src_file)
else:
    source_files = []
    input_files = []

# Determine template variable 'repository'
repository = args.src_dir

# Determine template variables 'run_commands' and 'attribution'


# Determine whether a line in 'run_commands' compiles source code
def starts_with_compiler(line):
    compilers = ['mpiicpc', 'cc', 'gcc', 'icc', 'icpc', 'javac', 'gfortran',
                 'ifort']  # Add more
    for compiler in compilers:
        pattern = '^{} [\\S\\s]+$'.format(compiler)
        if re.match(pattern, line):
            return True
    return False


onerror_block = (
    '_onerror()\n'
    '{\n'
    '    exitcode=$?\n'
    '    echo "-reframe: command \\`$BASH_COMMAND\''
    ' failed (exit code: $exitcode)"\n'
    '    exit $exitcode\n'
    '}\n'
    '\n'
    'trap _onerror ERR'
)

run_commands = combined_shell.replace('#!/bin/bash', '').replace(
    onerror_block, '')
run_command_lines = run_commands.splitlines()
module_load_lines = []
compile_comment = False
remove_comment = False
run_comment = False
cat_comment = False
attribution = ''
new_run_command_lines = []
for line in run_command_lines:
    if line.strip():
        if re.match('^ ', line) and not re.match('^  ', line):
            line = line[1:]
        if re.match('^module load \\S+$', line):
            if line not in module_load_lines:
                if not module_load_lines:
                    new_run_command_lines.append(
                        '# Load {} and other necessary modules'.format(module)
                    )
                module_load_lines.append(line)
                new_run_command_lines.append(line)
        elif starts_with_compiler(line):
            if not compile_comment:
                new_run_command_lines.append('\n# Compile source code')
                compile_comment = True
            new_run_command_lines.append(line)
        elif re.match('^rm', line):
            if not remove_comment:
                new_run_command_lines.append('\n# Remove files created')
                remove_comment = True
            new_run_command_lines.append(line)
        elif re.match('^cat', line):
            if not cat_comment:
                new_run_command_lines.append('\n# Display results')
                cat_comment = True
            new_run_command_lines.append(line)
        elif re.match(r'^\s*#+\s*[Aa]ttribution: ', line):
            patt = re.compile(r'^\s*#+\s*[Aa]ttribution: ([\S\s]*)$')
            attribution = patt.match(line).group(1)
        else:
            if not run_comment:
                new_run_command_lines.append('\n# Run example')
                run_comment = True
            new_run_command_lines.append(line)
while new_run_command_lines.count('\n# Run example') > 1:
    new_run_command_lines.remove('\n# Run example')
run_commands = os.linesep.join(new_run_command_lines)

# Configure jinja
loader = jinja2.PackageLoader(__name__, 'templates')
env = jinja2.Environment(
    loader=loader,
)


# Define function for use in template. Returns file contents.
def include_src_file(src_file):
    line_limit = 50
    max_line_length = 120
    file_path = '{}/{}'.format(src_dir, src_file)
    reader = open(file_path, 'r')
    ret_lines = []
    line_num = 0
    limit_reached = False
    for line in reader:
        if line_num < line_limit:
            if len(line) <= max_line_length:
                ret_lines.append(line)
            else:
                ret_lines.append(line[:max_line_length - 3] + '...')
        else:
            limit_reached = True
        line_num += 1
    if limit_reached:
        ret_lines.append('.\n.\n.\n')
    return ''.join(ret_lines)


# Define function for use in template. Returns directory contents.
def include_input_dir(input_dir):
    item_limit = 25
    dir_path = '{}/{}'.format(src_dir, input_dir)
    contents = os.listdir(dir_path)
    ret_str = ''
    item_num = 0
    limit_reached = False
    for item in contents:
        if item_num < item_limit:
            ret_str += '- {}\n'.format(item)
        else:
            limit_reached = True
        item_num += 1
    if limit_reached:
        ret_str += '.\n.\n.'
    return ret_str


# Ensure that above template functions are accessib/e
env.globals['include_src_file'] = include_src_file
env.globals['include_input_dir'] = include_input_dir

# Load template, substitute in variables, and save resulting markdown file
template = env.get_template('template.md')
populated = template.render(
    module=module,
    module_help=module_help,
    source_files=source_files,
    makefile=makefile,
    input_files=input_files,
    input_directories=input_directories,
    repository=repository,
    run_commands=run_commands,
    attribution=attribution
)
docs_dir = 'docs'
if not os.path.exists(docs_dir):
    os.makedirs(docs_dir)
doc_name = '{}/{}.md'.format(docs_dir, module)
if os.path.exists(doc_name):
    os.remove(doc_name)
writer = open(doc_name, 'w')
writer.write(populated)
print(' Doc generated!')
