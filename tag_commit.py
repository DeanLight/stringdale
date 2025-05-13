#!/usr/bin/env python3
import subprocess
import configparser
import argparse
import sys
from pathlib import Path

def get_version_from_settings():
    """Get version from settings.ini file"""
    config = configparser.ConfigParser()
    settings_path = Path('settings.ini')
    
    if not settings_path.exists():
        raise FileNotFoundError("settings.ini not found")
    
    config.read(settings_path)
    
    if 'DEFAULT' not in config or 'version' not in config['DEFAULT']:
        raise ValueError("Could not find version in settings.ini DEFAULT section")
        
    return config['DEFAULT']['version']

def tag_exists(tag_name):
    """Check if a tag already exists"""
    try:
        result = subprocess.run(
            ['git', 'tag', '-l', tag_name],
            capture_output=True,
            text=True,
            check=True
        )
        return bool(result.stdout.strip())
    except subprocess.CalledProcessError as e:
        print(f"Error checking for existing tag: {e}")
        sys.exit(1)

def create_and_push_tag(version, commit=None, force=False):
    """Create and push a new tag"""
    tag_name = f"v{version}"
    
    # Create tag command
    tag_cmd = ['git', 'tag', '-a', tag_name, '-m', f"Release version {version}"]
    if commit:
        tag_cmd.append(commit)
    if force:
        tag_cmd.insert(2, '-f')  # Add force flag after 'tag' command
    
    try:
        # Create the tag
        subprocess.run(tag_cmd, check=True)
        
        # Push the tag
        push_cmd = ['git', 'push', 'origin', tag_name]
        if force:
            push_cmd.insert(2, '-f')  # Add force flag after 'push' command
        subprocess.run(push_cmd, check=True)
        
        print(f"Successfully created and pushed tag {tag_name}")
    except subprocess.CalledProcessError as e:
        print(f"Error during git operations: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Create a new version tag based on settings.ini version')
    parser.add_argument('--commit', help='Commit hash to tag (defaults to HEAD)')
    parser.add_argument('--force', action='store_true', help='Force create/update the tag even if it exists')
    
    args = parser.parse_args()
    
    try:
        # Get version from settings.ini
        version = get_version_from_settings()
        tag_name = f"v{version}"
        
        # Check if tag exists
        if tag_exists(tag_name) and not args.force:
            print(f"Warning: Tag {tag_name} already exists. Use --force to override.")
            sys.exit(1)
        
        # Create and push tag
        create_and_push_tag(version, args.commit, args.force)
        
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()