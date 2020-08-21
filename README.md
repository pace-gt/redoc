# Redoc

### A tool for automatically generating user documentation for HPC software modules from Reframe sanity checks.

## Why Redoc?

Many high-performance computing (HPC) clusters use the
[Reframe regression testing framework](https://reframe-hpc.readthedocs.io/en/stable/)
to ensure that their user-facing software modules correctly provide access to
a program, library, or other piece of software. In order for Reframe to test a module,
it must be instructed to load the module and execute an example using its functionality,
which may involve compiling source code or running a program.
This is called a sanity check.

Many HPC clusters also wish to provice their users with documentation for each software module.
This documentation might instruct them to load the module and walk them through an example
using its functionality- quite possibly the same example that was used for the Reframe sanity check.

Redoc uses existing Reframe sanity checks for software modules to automatically generate user
documentation. Redoc creates a markdown file from each sanity check telling users
which files to access and which commands to run in order to replicate the example
used in the check, making use of the module's features.
This provides several advantages over creating user documentation for modules by hand:

- **It is easier and faster.** Redoc leverages existing Reframe sanity checks for modules.
    This makes it fast and easy to both create user documentation and keep it updated.
- **It is more robust.** Because the usage examples shown in the Redoc-generated documentation are also
    used in sanity checks, you can be sure that they will work when users try them
    as long as the sanity checks continue to pass.
    

## Using Redoc

This repository contains two scripts of interest:
- **redoc.py:** Generates a markdown file for one software module
    using one Reframe sanity check. It takes three arguments:
    the name of the module (-m),
    the path to the output directory of the Reframe sanity check (-o),
    and the path to the source directory of the Reframe sanity check (-s).
    It uses the provided information to populate a documentation template
    stored in the "templates" directory.
    redoc.py is designed to work on most HPC clusters that use Reframe regardless
    of how Reframe is configured.
    Note that this script should be run from the Redoc directory
    and that it requires the Jinja2 library.
- **redoc_wrapper.sh:** Iterates through Reframe tests and runs redoc.py on those marked with the "redoc" tag.
    This script takes no arguments and is fairly small, but is specifically designed to
    work for PACE's Reframe configuration and may not work on other clusters
    that use Reframe differently.

## Redoc Features

Each markdown file created by Redoc has the following sections, if relevant:
- **Module description:** The description displayed if a user runs `module help <module>`.
- **Files:** Enumerates the files necessary to run the example,
    as well as instructions for how to access them.
    It distinguishes between source code files, Makefiles, and other general input files.
- **Commands to run example:** Commands for loading the relevant module(s), compiling any necessary code,
    and running the example. Complete with comments.
- **Attribution:** A link to the source of the example, if provided to the Reframe sanity check
    by way of a comment in the post_run field like the following:
    self.post_run = ['# Attribution: <url>']