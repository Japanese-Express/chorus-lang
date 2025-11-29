
import json
import os
from typing import Any, Optional

class Language:
    """Handles language loading and management."""

    def __init__(self, json_metadata: dict, locale_code: str):
        """Initializes a Language instance.
        
        Args:
            json_metadata (dict): The json data loaded from the language file.
            locale_code (str): The locale code (e.g., "en-us").
        """
        self.name = json_metadata.get("name", "Unknown") # name of the language
        self.author = json_metadata.get("author", "Unknown") # author of the language file
        self.enabled = json_metadata.get("enabled", False) # whether this language is enabled
        self.notes = json_metadata.get("notes", "") # optional notes about the language
        self.location = json_metadata.get("location", "") # location of the language files
        self.locale_code = locale_code
        self.__read_data(self.location)

    def __read_data(self, location: str) -> None:
        """A private method to read language data from the given location.
        Data of the language is stored in self.data, a dictionary.
        
        Args:
            key (str): The key to look up in the language data.
        """
        if os.path.isdir(location):
            # aggregate all json files in the directory into one language
            aggregated_data: dict = {}
            found_any = False
            for fname in sorted(os.listdir(location)):
                if not fname.endswith('.json'):
                    # There should be no non-json files, but skip them if present
                    print("Warning: Skipping non-json file", fname, "in language directory", location)
                    continue
                fp = os.path.join(location, fname)
                try:
                    ld = json.load(open(fp, 'r'))
                except Exception:
                    print(f"Warning: Failed to load language file `{fp}`")
                    continue
                data_piece = ld.get('data', {})
                if isinstance(data_piece, dict):
                    # data found, update concurrent dictionary
                    aggregated_data.update(data_piece)
                found_any = True

            if not found_any:
                print(f"Warning: No language json files found in directory `{location}` for code `{self.locale_code}`")
                return
            self.data = aggregated_data
            print("- Loaded language", self.locale_code, "from directory", location)
        else:
            # direct file
            file_path = location
            if os.path.exists(file_path):
                # load single file language
                lang_data = json.load(open(file_path, "r"))
                self.data = lang_data.get("data", {})
                print("- Loaded language", self.locale_code, "from file", file_path)
            else:
                print(f"Warning: Language file `{file_path}` for code `{self.locale_code}` does not exist.")
    
    def get(
            self, 
            key: str, *, 
            default: Optional[str] = None,
            replacements: Optional[dict[str, Any]] = None
    ) -> Optional[str]:
        """Get a translated string for `key`, or `default` if not found.

        Args:
            key: The internal key to look up (e.g. `fun.joke.error`).
            default: The default string to return if the key is not found. If None,
              will attempt to get from the default language as a fallback.
            replacements: See Notes.
        
        Notes:
            - `replacements` is an optional dictionary of `{placeholder: value}` pairs
              to replace in the resulting string. Placeholders in the string are forced
              into the format of `{placeholder}`.
        """
        got = self.data.get(key, default)
        # If the value is missing, not a string, or falsy, try fallback.
        if not got or not isinstance(got, str):
            if default is None:
                # try to get from default language fallback
                default_lang = LanguageHolder.get_language(None)
                # Avoid infinite recursion when this language IS the default
                if default_lang is self:
                    return None
                got = default_lang.get(key, default=None, replacements=replacements)
                if not got:
                    # no fallback found
                    return None
                # found; add it to our cache so we can just use it for next time
                self.data[key] = got
            else:
                # just use provided default
                got = default
        if replacements:
            # {placeholder} replacements
            # example: replacements={"count": 5} will replace {count} with 5
            for k, v in replacements.items():
                got = got.replace(f"{{{k}}}", str(v))
        return got

class LanguageHolder:
    """Holds all loaded languages and manages user/guild language preferences."""
    languages: dict[str, Language] = {}
    db_location: Optional[str] = None
    default_code: str = "en_us"

    @staticmethod
    def load_languages(json_path: str):
        """Load all languages from the json db into memory.

        `json_path` should point to `language.json` which maps language codes
        to a folder or file path. Existing in-memory languages are cleared
        and reloaded.
        """
        # Clear existing languages before loading new ones, easy refresh
        LanguageHolder.languages.clear()
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"JSON path `{json_path}` does not exist.")
        
        print("Loading languages from", json_path)
        locations: dict = json.load(open(json_path, "r"))
        # loop through all entries, key=`code`, value=`{location: str, name: str, ...}`
        for code, loc_dict in locations.items():

            # skip notes or non-language entries
            if isinstance(code, str) and code.startswith("notes"):
                continue

            # allow either directory or direct file
            assert isinstance(loc_dict, dict), f"Language entry for code `{code}` is not a dictionary."
            assert "location" in loc_dict, f"Language entry for code `{code}` is missing a location."
            assert "name" in loc_dict, f"Language entry for code `{code}` is missing a name."

            # if `is_default` is set, mark this as the default language
            is_default = loc_dict.get("is_default", False)
            if is_default:
                print("- Setting default language to", code)
                LanguageHolder.default_code = code
            
            # create Language instance and store it
            lang = Language(loc_dict, code)
            LanguageHolder.languages[code] = lang
        print("Loaded languages:", list(LanguageHolder.languages.keys()))

    @staticmethod
    def get_language(code: Optional[str]) -> Language:
        """Return a Language object for `code`, falling back to default."""
        if not code:
            code = LanguageHolder.default_code
        if code in LanguageHolder.languages:
            return LanguageHolder.languages[code]
        # fallback to default if requested code missing
        return LanguageHolder.languages.get(LanguageHolder.default_code, next(iter(LanguageHolder.languages.values())))