# Grid Methods

## Overview

The `Grid_methods` module provides two main scientific analysis pipelines:

* **Structure Comparison**
* **Hotspot Detection**

The module can be executed locally or through the Flask API.

## Entry Points

The main file is:

```text
Grid_methods/src/main.py
```

It provides two main functions:

* `main()` for local execution.
* `main_api(json_parameters)` for API requests.

The Flask API is defined in:

```text
Grid_methods/src/api.py
```

---

## Local Execution with `main()`

The `main()` function initializes the global parameters using:

```python
gp.init()
```

It then loads the default parameters and configuration files before executing the requested analysis pipeline.

The two available pipelines are controlled by:

* `run_comparison`
* `run_hotspot`

Both pipelines can be enabled independently.

---

# Structure Comparison

When `run_comparison` is enabled, the comparison workflow performs the following steps:

1. Clean and prepare the molecular structures.
2. Check that valid structures remain in the dataset.
3. Perform structural alignment when required.
4. Calculate structural similarities.
5. Optionally calculate sequence similarities.
6. Generate trees and visualizations.

The comparison process can generate trees based on:

* `structures`
* `sequences`
* `both`

The selected tree type is controlled by the `tree` parameter.

Newick files are removed automatically when:

```text
save_newick_files = False
```

---

## Structure Comparison Workflow

The general comparison workflow is:

```text
Input structures
        ↓
Structure cleaning
        ↓
Dataset validation
        ↓
Structural alignment
        ↓
Similarity calculation
        ↓
Tree generation
        ↓
Visualization generation
```

The generated results can include:

* Structural comparison data.
* Distance matrices.
* Coverage matrices.
* Heatmaps.
* Newick trees.
* SVG tree visualizations.

---

# Hotspot Detection

When `run_hotspot` is enabled, the program performs the following steps:

1. Read the hotspot parameters.
2. Prepare the molecular structure dataset.
3. Validate the dataset.
4. Generate the required grids.
5. Calculate hotspot scores.
6. Identify relevant hotspot positions.

The main hotspot calculation is launched through:

```python
launch_structure_hotspot()
```

The result contains the calculated scores and identified hotspot positions.

---

## `main_api(json_parameters)`

The `main_api()` function is the main entry point used by the Flask API.

```python
main_api(json_parameters)
```

At the beginning of each request, the function:

1. Reinitializes the PyMOL environment.
2. Initializes the global parameters.
3. Validates the received parameter dictionaries.
4. Executes the requested analysis pipeline.
5. Collects the generated files.
6. Converts them into JSON-compatible objects.
7. Removes temporary output directories.

The main parameter groups are:

```text
global_parameters
comparison_parameters
hotspot_parameters
```

---

## Comparison API Workflow

For a comparison request, `main_api()`:

1. Prepares the dataset.
2. Cleans the molecular structures.
3. Performs structural alignment.
4. Calculates structural similarities.
5. Generates the selected tree.
6. Generates visualizations.
7. Recursively reads the output directory.
8. Stores the results in a Python dictionary.
9. Removes the temporary output directory.

The returned dictionary contains the generated files and their contents.

---

## Hotspot API Workflow

For a hotspot request, `main_api()`:

1. Prepares the dataset.
2. Cleans the input structure.
3. Creates the required analysis grids.
4. Executes the hotspot calculation.
5. Collects the generated files.
6. Converts the files into JSON-compatible objects.
7. Removes temporary output files.

---

## File Serialization

The API must convert generated files into JSON-compatible data.

Text files are stored as UTF-8 strings.

Binary files are encoded using Base64.

For example:

```json
{
    "encoding": "base64",
    "data": "..."
}
```

This allows generated files to be transmitted through JSON responses.

---

## Common Parameters

The following example shows the main parameter structure used by the API:

```json
{
    "global_parameters": {
        "run_comparison": "True",
        "run_hotspot": "False",
        "atom_type": "SYBYL",
        "grid_spacing": "0.35",
        "grid_padding": "1.0",
        "discard_hydrogen": "True",
        "discard_water": "True"
    },
    "comparison_parameters": {
        "tree": "structures",
        "consider_elements": "True",
        "comparison_normalisation": "Min",
        "grid_geometry": "Sphere"
    },
    "hotspot_parameters": {
        "grid_geometry": "Sphere",
        "max_neighbor_number": "3",
        "hotspot_type": "C.ar",
        "tag_threshold": "1",
        "bad_score_threshold": "0.8",
        "good_score_threshold": "0.2",
        "number_of_rounds": "1"
    }
}
```

Parameter values can be received as strings.

The validation functions convert them to the appropriate data types before the scientific calculations are executed.

Input paths are replaced by temporary directories created specifically for each API request.

---

## Direct Execution

`Grid_methods` can also be executed directly.

The program loads:

```text
Grid_methods/config/parameters.json
```

and can be started with:

```bash
python Grid_methods/src/main.py
```

---

## Related Documentation

For the Flask endpoints, see:

[API Documentation](api.md)

For the web application that uses this module, see:

[Web Viewer Documentation](webviewer.md)
