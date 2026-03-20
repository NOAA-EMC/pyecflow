#!/usr/bin/env python3
"""
pyecflow Demo Script
====================

This script demonstrates the full workflow of the pyecflow package:
1. Define a workflow configuration in Python (or load from YAML)
2. Create a WorkflowSuite with the configuration
3. Generate the ecFlow definition and scripts
4. Show the generated outputs

Run with: python demo.py
"""

import os
import tempfile

import yaml
import pyflow as pf
from pyecflow import WorkflowSuite


def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)


def print_file_contents(filepath, max_lines=50):
    """Print the contents of a file with line numbers."""
    with open(filepath, 'r') as f:
        lines = f.readlines()
    print(f"\n--- {os.path.basename(filepath)} ({len(lines)} lines) ---")
    for i, line in enumerate(lines[:max_lines], 1):
        print(f"{i:3d} | {line}", end='')
    if len(lines) > max_lines:
        print(f"\n... ({len(lines) - max_lines} more lines)")
    print()


def tree(directory, prefix=""):
    """Print a directory tree structure."""
    entries = sorted(os.listdir(directory))
    for i, entry in enumerate(entries):
        path = os.path.join(directory, entry)
        is_last = i == len(entries) - 1
        connector = "└── " if is_last else "├── "
        print(f"{prefix}{connector}{entry}")
        if os.path.isdir(path):
            extension = "    " if is_last else "│   "
            tree(path, prefix + extension)


def main():
    print_section("pyecflow Demo - Generating ecFlow Workflows from Config")

    # =========================================================================
    # STEP 1: Load the workflow configuration from YAML
    # =========================================================================
    print_section("Step 1: Load Workflow Configuration from YAML")

    # Load configuration from YAML file
    config_file = os.path.join(os.path.dirname(__file__), 'demo_config.yaml')
    print(f"Loading config from: {config_file}")

    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)

    # Show the YAML contents
    print_file_contents(config_file, max_lines=30)

    # Count families and tasks for display
    def count_items(cfg, family_count=0, task_count=0):
        for key, value in cfg.items():
            if key == 'includes':
                continue
            family_count += 1
            if value and 'tasks' in value:
                task_count += len(value['tasks'])
            if value and 'children' in value:
                fc, tc = count_items(value['children'])
                family_count += fc
                task_count += tc
        return family_count, task_count

    num_families, num_tasks = count_items(config)
    print(f"Configuration loaded with {num_families} families and {num_tasks} tasks")

    # =========================================================================
    # STEP 2: Create the WorkflowSuite
    # =========================================================================
    print_section("Step 2: Create WorkflowSuite")

    # Create suite with a local host (for demo purposes)
    suite = WorkflowSuite(
        'demo_workflow',
        host=pf.LocalHost('localhost'),
        defstatus=pf.state.suspended  # Start suspended for safety
    )

    print(f"Created suite: {suite.name}")
    print(f"Host: localhost (LocalHost)")
    print(f"Default status: suspended")

    # =========================================================================
    # STEP 3: Generate the family/task tree
    # =========================================================================
    print_section("Step 3: Generate Family/Task Tree")

    families = suite.generate_tree(config)

    print("Generated families:")
    for family_path in sorted(families.keys()):
        depth = family_path.count('/')
        print(f"  {'  ' * depth}• {family_path.split('/')[-1]} ({family_path})")

    # =========================================================================
    # STEP 4: Generate the suite files
    # =========================================================================
    print_section("Step 4: Generate Suite Files")

    # Create a temporary directory for the demo output
    demo_dir = tempfile.mkdtemp(prefix='pyecflow_demo_')
    suite_dir = os.path.join(demo_dir, 'demo_workflow')

    # Set ECF_FILES - required by pyflow's AnchorFamily to know where scripts go
    scripts_dir = os.path.join(suite_dir, 'scripts')
    os.makedirs(scripts_dir, exist_ok=True)
    suite.ECF_FILES = scripts_dir

    print(f"Output directory: {suite_dir}")
    print("\nGenerating suite files...")

    suite.generate_suite(suite_dir=suite_dir)

    print("Suite generation complete!")

    # =========================================================================
    # STEP 5: Show the generated output
    # =========================================================================
    print_section("Step 5: Generated Directory Structure")

    print(f"\n{suite_dir}/")
    tree(suite_dir)

    # Show the definition file
    print_section("Generated Definition File (.def)")
    def_file = os.path.join(suite_dir, 'def', 'demo_workflow.def')
    print_file_contents(def_file)

    # Show a sample script
    print_section("Sample Generated Script (.ecf)")

    # Find and show a script file
    scripts_dir = os.path.join(suite_dir, 'scripts')
    for root, dirs, files in os.walk(scripts_dir):
        for f in files:
            if f.endswith('.ecf'):
                script_path = os.path.join(root, f)
                print_file_contents(script_path, max_lines=30)
                break
        else:
            continue
        break

    # Show include files
    print_section("Include Files")
    include_dir = os.path.join(suite_dir, 'include')
    # head.h and tail.h are always deployed; envir-p1.h only if configured
    for include_file in ['head.h', 'tail.h', 'envir-p1.h']:
        include_path = os.path.join(include_dir, include_file)
        if os.path.exists(include_path):
            print_file_contents(include_path, max_lines=20)

    # =========================================================================
    # SUMMARY
    # =========================================================================
    print_section("Summary")

    # Count generated files
    file_counts = {'def': 0, 'ecf': 0, 'h': 0}
    for root, dirs, files in os.walk(suite_dir):
        for f in files:
            ext = f.split('.')[-1]
            if ext in file_counts:
                file_counts[ext] += 1

    print(f"""
pyecflow successfully generated:
  • {file_counts['def']} definition file(s) (.def)
  • {file_counts['ecf']} ecFlow script(s) (.ecf)
  • {file_counts['h']} include file(s) (.h)

Output location: {suite_dir}

To load this suite into ecFlow:
  ecflow_client --load={def_file}

To clean up the demo directory:
  rm -rf {demo_dir}
""")

    return suite_dir, demo_dir


if __name__ == '__main__':
    suite_dir, demo_dir = main()
