# Attribution / Data Sources

This repository contains exercise catalog data used by IronVexel.

## wger Project

Some exercise entries in `iv_exercise_catalog_ro_en.jsonl` are derived from the public wger exercise database.

- Source project: wger Project
- Website: https://wger.de
- Source repository: https://github.com/wger-project/wger
- API endpoint used for import: https://wger.de/api/v2/exerciseinfo/
- Imported data was normalized, filtered, converted, and adapted to the IronVexel exercise catalog schema.

## License note

The wger application source code is licensed separately from the exercise data. Exercise data and related content from wger may be distributed under Creative Commons licenses depending on the specific entry/source.

IronVexel does not claim ownership over source data imported from wger. Attribution is preserved here for transparency and compliance.

If this project is distributed commercially or publicly, keep this attribution file and also show attribution inside the application under a Legal / Data Sources / Credits screen.

## IronVexel transformations

The imported exercise data was adapted for IronVexel by:

- converting wger exercise records into JSONL format;
- mapping muscle groups to IronVexel categories;
- mapping equipment values to IronVexel equipment types;
- mapping movement patterns to IronVexel movement categories;
- adding default sets, reps, rest seconds, goals, and app-specific tags;
- deduplicating entries by ID.

These transformations are part of the IronVexel catalog format, while original exercise source data remains attributed to wger where applicable.
