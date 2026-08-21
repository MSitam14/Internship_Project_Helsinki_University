# API Documentation

## Overview

The project provides several Flask APIs.

They are divided into:

* Fitness Score API.
* Grid Methods API.
* User Key API.
* Temporary Database APIs.

---

# Fitness Score API

## Base Route

```text
/api-score
```

---

## `POST /api-score/score`

Calculates the Fitness Score of a molecular structure.

### Request

The request must contain:

* `params`
* `pdb`

Example:

```json
{
    "params": {
        "densities_fold": "Fitness_score/data/densities/sybyl/",
        "frequencies_fold": "Fitness_score/data/frequencies/sybyl/",
        "run_frequencies": true,
        "water_env": true,
        "atom_type": "sybyl",
        "environment_size": 3,
        "pocket_num": null,
        "model_num": 1,
        "l_ori": null
    },
    "pdb": {
        "name": "protein.pdb",
        "content": "ATOM ...\nEND\n"
    }
}
```

### Processing

The API:

1. Validates the request.
2. Creates a temporary input file.
3. Calls the Fitness Score calculation.
4. Converts the result into JSON-compatible data.
5. Removes temporary files.
6. Returns the generated files.

### Success Response

```json
{
    "status": "success",
    "content": {
        "cif_file": {},
        "csv_file": {},
        "log_file": {}
    }
}
```

### Error Response

```json
{
    "status": "error",
    "message": "..."
}
```

### Status Codes

* `200` — Successful calculation.
* `400` — Invalid request or calculation error.

---

# Grid Methods API

## Base Route

```text
/api-hot-comp
```

---

## `GET /api-hot-comp/status`

Checks whether the API is available.

### Response

```json
{
    "status": "success",
    "message": "API is running"
}
```

### Status Code

```text
200
```

---

## `POST /api-hot-comp/comparison`

Performs a structural comparison between two molecular structures.

### Request

The request must contain:

* `params`
* `pdb1`
* `pdb2`

Example:

```json
{
    "params": {
        "global_parameters": {
            "run_comparison": "True",
            "run_hotspot": "False"
        },
        "comparison_parameters": {
            "tree": "structures"
        },
        "hotspot_parameters": {}
    },
    "pdb1": {
        "name": "structure_1.pdb",
        "content": "ATOM ...\n"
    },
    "pdb2": {
        "name": "structure_2.pdb",
        "content": "ATOM ...\n"
    }
}
```

### Processing

The API:

1. Creates a temporary directory.
2. Writes both molecular structures.
3. Adds the temporary path to the comparison parameters.
4. Calls `main_api(params)`.
5. Collects the generated results.
6. Removes temporary files.

### Success Response

```json
{
    "status": "success",
    "content": {}
}
```

### Error Response

```json
{
    "status": "error",
    "message": "..."
}
```

### Status Codes

* `200` — Successful comparison.
* `400` — Invalid request or comparison error.

---

## `POST /api-hot-comp/hotSpots`

Performs hotspot detection on a molecular structure.

### Request

The request must contain:

* `params`
* `pdb`

Example:

```json
{
    "params": {
        "global_parameters": {
            "run_comparison": "False",
            "run_hotspot": "True"
        },
        "comparison_parameters": {},
        "hotspot_parameters": {
            "hotspot_type": "C.ar",
            "number_of_rounds": "1"
        }
    },
    "pdb": {
        "name": "structure.pdb",
        "content": "ATOM ...\n"
    }
}
```

### Processing

The API:

1. Creates a temporary directory.
2. Writes the molecular structure.
3. Adds the temporary path to the hotspot parameters.
4. Calls `main_api(params)`.
5. Collects the generated results.
6. Removes temporary files.

### Status Codes

* `200` — Successful analysis.
* `400` — Invalid request or analysis error.

---

# User Key API

## Base Route

```text
/api-key
```

---

## `GET /api-key/generateUserKey`

Generates a unique temporary user key.

The key contains 16 alphanumeric characters.

Before being returned, the key is checked against the existing temporary storage tables.

### Response

```json
{
    "status": "success",
    "user_key": "..."
}
```

---

# Fitness Score Database API

## Base Route

```text
/api-database-score
```

---

## `POST /api-database-score/saveDataWithUserKey/<userKey>`

Stores a Fitness Score result.

### Required Data

The JSON request contains:

```text
parameter
cif_file_name
cif_file_content
csv_file_name
csv_file_content
```

Log fields are optional.

### Success Response

```text
201
```

---

## `GET /api-database-score/getDataWhithUserKey/<userKey>`

Retrieves a stored Fitness Score result.

The returned data contains:

* Parameters.
* mmCIF file.
* CSV file.
* Log file.

---

# Comparison Database API

## Base Route

```text
/api-database-comparison
```

---

## `POST /api-database-comparison/saveDataWithUserKey/<userKey>`

Stores a comparison result.

The request must contain:

```json
{
    "data": {},
    "parameter": {}
}
```

### Success Response

```text
201
```

---

## `GET /api-database-comparison/getDataWhithUserKey/<userKey>`

Retrieves a stored comparison result.

---

# Hotspot Database API

## Base Route

```text
/api-database-hotSpots
```

---

## `POST /api-database-hotSpots/saveDataWithUserKey/<userKey>`

Stores a hotspot analysis result.

The request must contain:

```json
{
    "data": {},
    "parameter": {}
}
```

### Success Response

```text
201
```

---

## `GET /api-database-hotSpots/getDataWhithUserKey/<userKey>`

Retrieves a stored hotspot result.

---

# Temporary Storage

All stored results are temporary.

Each result is associated with a:

```text
user_key
```

The following information is used to manage expiration:

```text
date_last_used
```

Entries inactive for more than 30 minutes are automatically removed.

Whenever a result is successfully accessed, its `date_last_used` value is updated.

---

# Error Responses

The APIs generally return errors using the following format:

```json
{
    "status": "error",
    "message": "..."
}
```

Common status codes are:

| Status Code | Description                       |
| ----------- | --------------------------------- |
| `200`       | Successful request                |
| `201`       | Resource successfully created     |
| `400`       | Invalid request or missing data   |
| `404`       | Resource not found                |
| `500`       | Internal server or database error |

---

## Related Documentation

* [Installation Guide](installation.md)
* [Fitness Score](fitness-score.md)
* [Grid Methods](grid-methods.md)
* [Web Viewer](webviewer.md)
