# Changelog

## [0.4.0](https://github.com/stone-tech-inc/rimhistory/tree/v0.4.0) (TBD)

### Improvements

* Implement a `Save` class with a namespace for accessing key data points and datasets

```text
Save.data
├───datasets
│   ├───mod
│   │   ├───dataframe
│   │   └───dictionary_list
│   ├───pawn
│   │   ├───dataframe
│   │   └───dictionary_list
│   ├───plant
│   │   ├───dataframe
│   │   └───dictionary_list
│   └───weather
│       ├───dataframe
│       └───dictionary_list
├───file_size
├───game_version
├───path
└───root
```

* The pandas DataFrame containing plant information for the save file can be accessed through `Save.data.datasets.plant.dataframe`. The namespace is created using `bunch`.
* Consolidate all functions related to loading or modifying save data in the `Save` class
* Bump `plotly` to 5.6.0

## [0.3.0](https://github.com/stone-tech-inc/rimhistory/tree/v0.3.0) (2022-02-09)

### New features

* Count of every living plant species
* Distribution chart that visualizes the current growth progress of living plants
* Pawn environment ambient temperature
* Current weather conditions

### Improvements

* Configure `dependabot` alerts
* Use the `tmp_path` pytest fixture for test data storage, allowing parallel processing of test cases with file I/O

## [0.2.0](https://github.com/stone-tech-inc/rimhistory/tree/v0.2.0) (2022-02-05)

### New features

* HTML report with summary information:
  * Game version
  * Save file size
  * List of installed mods
  * Pawn information
  * Flora presence and growth statistics

### Testing

* Use `coverage` to measure the code coverage during pytest execution and require 100% code coverage ([coverage documentation](https://coverage.readthedocs.io/en/6.3.1/))
* Add test cases to increase overall test coverage from 48% (v0.1.0) to 100% (v0.2.0)

## [0.1.0](https://github.com/stone-tech-inc/rimhistory/tree/v0.1.0) (2022-02-02)

### New features

* Python-based ELT solution that extracts meaningful information from XML data as structured data that can be easily turned into reports, visualizations, and metrics
