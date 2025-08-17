import configparser
import sys
from pathlib import Path

#############################################################################
# CONFIGURATION
#############################################################################
CONFIG_FILE = Path("settings.ini")
HEADER_FILE = "header"
FOOTER_FILE = "footer"

# Required mandatory configurations
REQUIRED_SETTINGS = {
    "slides": ["directory_pptx","directory_pdf"],
}

# Mandatory options for all publications
PUBLICATION_OPTIONS = ["pptx_directory","publish_directory","filename_prefix"]

def load_config():
    config = configparser.ConfigParser()

    # Read existing file (if any)
    if CONFIG_FILE.exists():
        config.read(CONFIG_FILE)
    else:
        print(f"[ERROR] Config file not found. Creating new {CONFIG_FILE}.")
        CONFIG_FILE.touch()

    modified = False
    missing = []
    publications = []
  
    # Ensure all mandatory sections/keys exist
    for section, keys in MANDATORY_SETTINGS.items():
        if not config.has_section(section):
            config.add_section(section)
            modified = True

        for key in keys:
            if not config.has_option(section, key) or not config[section][key].strip():
                config.set(section, key, "")  # ensure entry exists but is empty
                modified = True
                missing.append(f"{section}.{key}")
              
    # Do we have publication targets?
    for section in config.sections():
      # Collect keys present in this section
      keys = set(config[section].keys())
      # Check if all required options are there
      if PUBLICATION_OPTIONS.issubset(keys):
        publications.append(section)        
    if count(publications) == 0:
      config.set("publication")
      for key in PUBLICATION_OPTIONS:
        config.set("publication",key, "") #add empty publication key
      modified = True
      
    # Save any modifications back to file
    if modified:
        with open(CONFIG_FILE, "w") as f:
            config.write(f)

    # If anything missing -> exit with error
    if missing:
        print("[ERROR] Missing mandatory settings:")
        for item in missing:
            print(f"  - {item}")
        print(f"\nPlease edit {CONFIG_FILE} and fill in the missing values.")
        sys.exit(1)
    if count(publications) == 0:
        print(f"[ERROR] At least one publication required! Added empty one to {CONFIG_FILE}!")
        sys.exit(1)
    return config

#############################################################################
# MAIN
#############################################################################
if __name__ == "__main__":
    config = load_config()
    print("Config loaded successfully!")
    print("Database host:", config["database"]["host"])
