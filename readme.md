# Chorus — Languages Repository

This repository contains the language files for the bot `Chorus`. These are languages users can switch between or switch their server to all-together.

## Layout

- `language.json` — master manifest that maps language codes to metadata and locations.
- `<lang_code>/` — a directory for a language (e.g. `en_us/`, `arr_matey/`) containing one or more JSON files with message keys and translations.

Example tree:

```
languages/
  ├─ language.json
  ├─ en_us/
  │   └─ fun.json
  └─ arr_matey/
      └─ fun.json
```

## `language.json` overview

`language.json` is the control file the bot reads at startup. It maps language codes (like `en_us`) to an object with metadata. Typical keys:

- `is_default` (optional): boolean. When true, the bot uses this language as the fallback/default.
- `enabled`: boolean. Controls whether the bot attempts to load this language.
- `name`: human-friendly language name.
- `author`: the author or maintainer of the translation.
- `location`: path to the language directory or file (relative to the repo root).

Example snippet (actual `language.json` in this repo contains helpful notes):

```json
"en_us": {
  "is_default": true,
  "enabled": true,
  "name": "English (US)",
  "author": "ScarlxtPink",
  "location": "languages/en_us/"
}
```

## Adding a new language

1. Create a new directory under `languages/` named with the language code (e.g. `fr_fr/`) or add a single JSON file if you prefer.
2. Add the translation JSON files (for example `fun.json`, `errors.json`) with the same message keys used in existing languages.
3. Update `language.json` with a new entry for your language (set `enabled` to `true` when ready).
4. Optionally, set `is_default` to `true` for the new language if you want it to become the bot's default.

## Contributing

- Open a pull request adding your language folder and updating `language.json`.
- Follow existing naming conventions and keep files UTF-8 encoded.

## License & Credits

- See the `LICENSE` file in this folder for license details.
- Translations created/maintained by repository contributors; see `language.json` authorship fields.
- Author fields can be in multiple files, authorize yourself based on major changes.
