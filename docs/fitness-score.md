# Fitness Score

## Overview

The `Fitness_score` module calculates a fitness score for atoms in molecular structures.

The calculation evaluates the local atomic environment and compares observed distances with reference density distributions.

## Entry Points

`Fitness_score` does not contain a `main.py` file.

The local entry point is:

```text
Fitness_score/src/Scoring_website_mmcif.py
```

The main execution function is:

```python
main()
```

The Flask API is defined in:

```text
Fitness_score/src/api.py
```

The API uses:

```python
apiMain()
```

to communicate with the scoring algorithm.

## Local Execution

The `main()` function reads the configuration from:

```text
Fitness_score/data/input/Scoring_parameters.txt
```

It processes `.pdb` and `.cif` files located in the configured input directory.

For each atom, the algorithm:

1. Determines the atomic type.
2. Identifies neighbouring atoms.
3. Evaluates the local atomic environment.
4. Compares distances with reference density distributions.
5. Calculates a fitness score.
6. Optionally calculates `Fobs/Fexp`.

## API Function

The main API function is:

```python
apiMain(parameter_json, pdb_path, file_path)
```

It receives the parameters and molecular structure from the web application.

The function returns:

```json
{
    "cif_file": {
        "file_name": "...",
        "file_content": "..."
    },
    "csv_file": {
        "file_name": "...",
        "file_content": "..."
    },
    "log_file": {
        "file_name": "...",
        "file_content": "..."
    }
}
```

## Output Files

### mmCIF File

Contains the molecular structure with calculated fitness scores added to the atomic data.

### CSV File

Contains detailed scoring information, including:

* `Score_i`
* `Score_total`
* `Fobs_Fexp_i`

when frequency calculations are enabled.

### Log File

Contains warnings and information generated during the calculation.

Temporary output files are removed after their contents have been read.

## Related Documentation

See the complete API documentation in:

[API Documentation](api.md)
