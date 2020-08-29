# Redoc

### A tool for automatically generating user documentation for HPC software modules from Reframe sanity checks.

## What is Redoc?

Many high-performance computing (HPC) clusters use the
[Reframe regression testing framework](https://reframe-hpc.readthedocs.io/en/stable/)
to ensure that their user-facing software modules correctly provide access to
a program, library, or other piece of software. In order for Reframe to test a module,
it must be instructed to load the module and execute an example exercise using its functionality,
which may involve source code or input files.
This is called a regression test or sanity check.

Many HPC clusters also wish to provice their users with documentation for each software module.
The creation of this documentation might be quite similar to the implementation of a Reframe
sanity check; the user, like Reframe, is instructed to load a module, access certain files,
and run certain commands.

Redoc uses existing Reframe sanity checks for software modules to automatically generate documentation,
walking users through the same exercises performed by Reframe.
This provides several advantages over creating module user documentation by hand:

- **It is easier and faster.** Redoc leverages existing Reframe sanity checks to generate guides,
    making it fast and easy to create new user documentation and update existing documentation.
- **The example exercises are more robust.** Because the example exercises described in the
    Redoc-generated documentation are also
    exactly carried out in Reframe sanity checks, you can be sure that they will work when users try them
    as long as the checks continue to pass.
- **The documentation is more cohesive.** By editing the markdown template,
    it is easy to introduce changes uniformly to all pages comprising the documentation.

## What does documentation generated by Redoc look like?

Redoc generates a markdown file, or doc, for each software module.
Each doc begins with a description of the module, if Lmod supplies one.
Next, the doc lists the files necessary for the exercise, including any
source code files, Makefiles, and general input files.
It explains how each file can be accessed directly from the reframe sanity check's source directory.
The third section of each doc shows the commands necessary to run the exercise,
with automatically inserted comments explaining common actions.
Finally, the doc provides attribution for the exercise, if provided in the implementation
of the reframe sanity test.

## Setting up Redoc

Note: some of the items below are labeled as "required to run redoc_tagged.sh."
This script is required to make optimal use of Redoc; without it, little
functionality is available.

### Download

To download Redoc, run
`git clone git@gitlab.pace.gatech.edu:pace-apps/redoc.git`
No install is necessary.

### Dependencies

**Required:**
- [Reframe regression testing framework](https://reframe-hpc.readthedocs.io/en/stable/)
- [Jinja2 templating package for Python](https://jinja.palletsprojects.com/en/2.11.x/)

**Recommended:**
- [jq command line JSON processor](https://stedolan.github.io/jq/) (Required
  to run redoc_tagged.sh)
- [LMOD environment module system](https://lmod.readthedocs.io/en/latest/) (Required
  to automatically include module descriptions in documentation)

### Additional setup steps

1. **Set up your Reframe regression tests.** In order for redoc to do anything,
   you must have Reframe regression tests. In order to run redoc_tagged.sh,
   these tests must be structured in a particular way, described here.
   The tests for each module must be defined in a script named <module>.py,
   where <module> is the name of the module tested. This script must be placed in
   a directory called <module>. If any of the tests for this module require
   any files, these must be placed in a directory called 'src', which
   must also be placed in the <module> directory. Tests that do not require
   any files should include the line `self.sourcesdir = None`.
   Finally, all of the directories named <module> for various modules must be
   in the same parent directory, which will be referred to as the reframe test directory.
2. **Set up the Redoc config file.** In order to run redoc_tagged.sh,
   you must set up the Redoc config file, named config.json.
   In particular, it needs to be given five pieces of information:
    1. reframe_config_file: The path to your Reframe config file.
    2. reframe_prefix: The path to your Reframe stage and output directories.
    3. reframe_test_directory: The path to your reframe tests, structured
       as perscribed above.
    4. lmod_path: The path to lmod.
   5. lmodrc_path: The path to lmodrc.lua.
3. **Tag Reframe tests with 'redoc'.** Each test with the 'redoc' tag will be used
   to generate documentation whenever redoc_tagged.sh is run. Ideal candidates are regression
   tests that use some of the basic features of a module without needing a long time to run.
4. **Supply attribution where desired.** To attribute an exercise used in a test to a
   particular website, insert the url in the test's post_run field: 
   `self.post_run = ['Attribution: <url>']` 
   (If the test already has a post_run field, simply add the above string to the array.)

## Using Redoc

Using Redoc will consist mainly of running redoc_tagged.sh, though occasionally you
may want to make an individual doc by running redoc.py. This may be necessary,
for example, to create a doc for a reframe test that cannot be structured
as perscribed in setup step 1 above.

### Repository Contents
- templates: Contains the markdown template that is populated during
  the generation of documentation.
- .gitignore: Instructs git not to store the individual docs generated.
- README.md: This file.
- config.json: Redoc config file. In order to run redoc_tagged.sh,
  it must be populated with some basic information about reframe and lmod on your system.
- redoc.py: Generates a doc for a software module from a reframe regression test.
  Typically, this script is not run directly; rather, it is called by redoc_tagged.sh.
  However, it is possible (and in some cases necessary) to directly run redoc.py
  to generate a particular piece of documentation. It takes 5 keyword arguments:
  1. -m (required): The name of the module for which to generate documentation.
  2. -o (required): The path to the output directory of the reframe test to be used.
  3. -s (optional): The path to the source directory of the reframe test to be used. Should only be omitted if exercise does not require any files.
  4. -l (optional): The path to lmod.
  5. -u (optional): The path to lmodrc.lua.
  The documentation is saved to a directory called 'docs', which is created if it does
  not already exist.
- redoc_tagged.sh: Calls redoc.py on every Reframe test with the 'redoc' tag, automatically
  supplying the arguments. This is the most efficient way to generate large amounts
  of documentation.

