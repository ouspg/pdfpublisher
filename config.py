from configparser import ConfigParser
from pathlib import Path

class ConfigManager:
    """
    A simple configuration manager that:
    - loads settings.ini
    - ensures required sections/keys exist
    - writes missing placeholders
    - provides helper getters
    """

    def __init__(self, path: Path | str = "settings.ini"):

	   self.REQUIRED_SETTINGS = {
    "settings": ["lecture_slides_dir","headerfile","footerfile","dividerfile"],
	"gen_ai": ["AI","API_KEY","Model","Request_timeout_ms","Max_requests_per_minute"],
    "titlefont": ["font","font_max_size","font_min_size","colour","maxlines"],
        }
       self.PUBLICATION_OPTIONS = set(["coursecode",
"translate_to",
"publish_dir",
"coursesize",
"lectures",
"coursename",
"filename_prefix",
"lectureterm",
"course_slides_dir"])
	
        self.path = Path(path)
        self.config = ConfigParser()

        self._load()
        self._ensure_required()
        self._save_if_modified()

    # ---------------------------------------------------------
    # Internal helpers
    # ---------------------------------------------------------

    def _load(self):
        # Load config here based on previous code.

    def _ensure_required(self):
        """Ensure all required sections and keys exist."""
        self.modified = False
        for section, keys in self.required.items():
            if not self.config.has_section(section):
                self.config.add_section(section)
                self.modified = True

            for key in keys:
                if not self.config.has_option(section, key):
                    self.config.set(section, key, "")
                    self.modified = True

    def _save_if_modified(self):
        if self.modified:
            with self.path.open("w") as f:
                self.config.write(f)

    # ---------------------------------------------------------
    # Public utility getters
    # ---------------------------------------------------------

    def get(self, section: str, key: str, fallback=None) -> str:
        return self.config.get(section, key, fallback=fallback)

    def get_int(self, section: str, key: str, fallback=None) -> int:
        return self.config.getint(section, key, fallback=fallback)

    def get_bool(self, section: str, key: str, fallback=None) -> bool:
        return self.config.getboolean(section, key, fallback=fallback)

    def set(self, section: str, key: str, value: str):
        self.config.set(section, key, value)
        with self.path.open("w") as f:
            self.config.write(f)




#############################################################################
# CONFIGURATION
#############################################################################
CONFIG_FILE = Path("settings.ini")
HEADER_FILE = "header"
FOOTER_FILE = "footer"

# Required mandatory configurations
REQUIRED_SETTINGS = {
    "settings": ["lecture_slides_dir","headerfile","footerfile","dividerfile"],
	"gen_ai": ["AI","API_KEY","Model","Request_timeout_ms","Max_requests_per_minute"],
    "titlefont": ["font","font_max_size","font_min_size","colour","maxlines"],
}

# Mandatory options for all publications
PUBLICATION_OPTIONS = set(["coursecode",
"publish_dir",
"coursesize",
"lectures",
"coursename",
"filename_prefix",
"lectureterm",
"course_slides_dir"])

#############################################################################
# Load and validate
#############################################################################




def load_config():
    config = configparser.ConfigParser()

    # Read existing file (if any)
    try:
        if CONFIG_FILE.exists():
            config.read(CONFIG_FILE)
        else:
            print(f"[ERROR] Config file not found. Creating new {CONFIG_FILE}.")
            CONFIG_FILE.touch()

    except configparser.DuplicateSectionError as e:
        print("[ERROR] duplicate section found in settings.ini:", e.section)
        sys.exit(1)
    except configparser.ParsingError as e:
        print("[ERROR] parsing error in settings.ini:", e)
        sys.exit(1)
    except configparser.DuplicateOptionError as e:
        print("[ERROR] duplicate option found in settings.ini under section:", e.section, "option:", e.option)
        sys.exit(1)
    modified = False
    missing = []
    publications = []
  
    # Ensure all mandatory sections/keys exist
    for section, keys in REQUIRED_SETTINGS.items():
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
    if len(publications) == 0:
      config.add_section("publication")
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
    if len(publications) == 0:
        print(f"[ERROR] At least one publication required! Added empty one to {CONFIG_FILE}!")
        sys.exit(1)
	
    return (config,publications)
