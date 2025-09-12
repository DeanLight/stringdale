"""Script to sync settings between pyproject.toml and settings.ini for nbdev."""

import tomllib
import configparser
from pathlib import Path
from datetime import datetime

# Define the mapping between TOML keys and INI keys
# Format: {'toml_section': {'toml_key': ('ini_section', 'ini_key')}}
TOML_TO_INI_MAPPING = {
    'project': {
        'name': ('DEFAULT', 'repo'),  # This will also set lib_name since it uses %(repo)s
        'description': ('DEFAULT', 'description'),
        'requires-python': ('DEFAULT', 'min_python'),
        'version': ('DEFAULT', 'version')
    },
    'tool': {
        'nbdev': {
            'license': ('DEFAULT', 'license'),
            'doc_path': ('DEFAULT', 'doc_path'),
            'nbs_path': ('DEFAULT', 'nbs_path'),
            'lib_path': ('DEFAULT', 'lib_path'),
            'recursive': ('DEFAULT', 'recursive'),
            'tst_flags': ('DEFAULT', 'tst_flags'),
            'put_version_in_init': ('DEFAULT', 'put_version_in_init'),
            'branch': ('DEFAULT', 'branch'),
            'custom_sidebar': ('DEFAULT', 'custom_sidebar'),
            'doc_host': ('DEFAULT', 'doc_host'),
            'doc_baseurl': ('DEFAULT', 'doc_baseurl'),
            'git_url': ('DEFAULT', 'git_url'),
            'title': ('DEFAULT', 'title'),
            'audience': ('DEFAULT', 'audience'),
            'author': ('DEFAULT', 'author'),
            'author_email': ('DEFAULT', 'author_email'),
            'copyright': ('DEFAULT', 'copyright'),
            'keywords': ('DEFAULT', 'keywords'),
            'language': ('DEFAULT', 'language'),
            'status': ('DEFAULT', 'status'),
            'user': ('DEFAULT', 'user'),
        }
    }
}

def parse_toml(file_path: Path) -> dict:
    """Parse the TOML file and return its content as a dictionary."""
    with open(file_path, 'rb') as f:
        return tomllib.load(f)

def validate_toml_data(toml_data: dict) -> None:
    """Validate that all required keys exist in the TOML data."""
    missing_keys = []
    
    for toml_section, mappings in TOML_TO_INI_MAPPING.items():
        if toml_section not in toml_data:
            missing_keys.append(f"Section '{toml_section}' is missing")
            continue
            
        for toml_key, mapping_info in mappings.items():
            if isinstance(mapping_info, dict):
                # Check nested sections (like tool.nbdev)
                if toml_key not in toml_data[toml_section]:
                    missing_keys.append(f"Key '{toml_section}.{toml_key}' is missing")
                    continue
                    
                nested_section = toml_data[toml_section][toml_key]
                for nested_key in mapping_info.keys():
                    if nested_key not in nested_section:
                        missing_keys.append(f"Key '{toml_section}.{toml_key}.{nested_key}' is missing")
            else:
                # Check direct mappings
                if toml_key not in toml_data[toml_section]:
                    missing_keys.append(f"Key '{toml_section}.{toml_key}' is missing")
    
    if missing_keys:
        raise ValueError(
            "The following required keys are missing in pyproject.toml:\n" +
            "\n".join(f"- {key}" for key in missing_keys)
        )

def clean_python_version(version: str) -> str:
    """Clean python version string by removing any version specifiers."""
    # Remove any version specifiers (>=, >, <, <=, ==, ~=, !=)
    import re
    return re.sub(r'^[><=!~]+\s*', '', version)

def build_ini_dict(toml_data: dict) -> dict:
    """Build a dictionary suitable for creating an INI file based on the TOML data and mapping."""
    # First validate that all required keys exist
    validate_toml_data(toml_data)
    
    ini_data = {'DEFAULT': {}}
    
    # Process values from pyproject.toml
    for toml_section, mappings in TOML_TO_INI_MAPPING.items():
        for toml_key, mapping_info in mappings.items():
            if isinstance(mapping_info, dict):
                # Handle nested sections (like tool.nbdev)
                nested_section = toml_data[toml_section][toml_key]
                for nested_key, nested_mapping in mapping_info.items():
                    ini_section, ini_key = nested_mapping
                    ini_data.setdefault(ini_section, {})[ini_key] = str(nested_section[nested_key])
            else:
                # Handle direct mappings
                ini_section, ini_key = mapping_info
                value = str(toml_data[toml_section][toml_key])
                
                # Special case for min_python - clean version string
                if ini_key == 'min_python':
                    value = clean_python_version(value)
                
                ini_data.setdefault(ini_section, {})[ini_key] = value
                
                # Special case for repo/lib_name relationship
                if ini_key == 'repo':
                    ini_data[ini_section]['lib_name'] = '%(repo)s'
    
    return ini_data

def write_ini_file(ini_data: dict, file_path: Path) -> None:
    """Write the INI data to a file."""
    config = configparser.ConfigParser()
    
    # Add all sections and their values
    for section, values in ini_data.items():
        config[section] = values
    
    # Write to file with warning header
    with open(file_path, 'w') as configfile:
        # Write warning comment
        configfile.write("# This file is auto-generated from pyproject.toml\n")
        configfile.write("# DO NOT EDIT directly - make changes in pyproject.toml instead\n\n")
        # Write the config
        config.write(configfile)

def main():
    """Main function to sync settings between pyproject.toml and settings.ini."""
    # Get the project root directory (2 levels up from this script)
    project_root = Path(__file__).parent.parent
    
    toml_file = project_root / 'pyproject.toml'
    ini_file = project_root / 'settings.ini'
    proc_dir = project_root / '_proc'
    
    # Create _proc directory if it doesn't exist
    proc_dir.mkdir(parents=True, exist_ok=True)
    
    # Parse TOML and build INI data
    toml_data = parse_toml(toml_file)
    ini_data = build_ini_dict(toml_data)
    
    # Write the INI file
    write_ini_file(ini_data, ini_file)
    print(f"Successfully synced settings from {toml_file} to {ini_file}")

if __name__ == '__main__':
    main()
