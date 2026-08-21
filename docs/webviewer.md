# Web Viewer

## Overview

`webViewer` is the main Flask application of the project.

It provides the web interface used to:

* Upload molecular structures.
* Configure analysis parameters.
* Launch scientific calculations.
* Display molecular structures.
* Display scores and analysis results.
* Visualize comparison trees.
* Download generated files.
* Temporarily store analysis results.

The application acts as the interface between the user and the scientific modules:

* `Fitness_score`
* `Grid_methods`

---

# Application Entry Point

The application factory is located in:

```text
webViewer/app/__init__.py
```

The application is created using:

```python
create_app(config_name)
```

The application factory:

1. Creates the Flask application.
2. Loads the configuration.
3. Initializes Bootstrap.
4. Initializes SQLAlchemy.
5. Registers the HTML page blueprints.
6. Registers the API blueprints.
7. Registers the scientific APIs.

The application is started through:

```text
manage.py
```

---

# Application Architecture

The main application structure is:

```text
webViewer/
├── requirements.txt
└── app/
    ├── __init__.py
    ├── models.py
    │
    ├── viewer/
    │   ├── __init__.py
    │   ├── routes.py
    │   └── api.py
    │
    ├── templates/
    │
    └── static/
```

The main files have the following roles:

| File               | Role                                                 |
| ------------------ | ---------------------------------------------------- |
| `app/__init__.py`  | Flask application factory and blueprint registration |
| `app/models.py`    | SQLAlchemy database models                           |
| `viewer/routes.py` | HTML pages and form processing                       |
| `viewer/api.py`    | Temporary result storage APIs                        |
| `templates/`       | Jinja2 HTML templates                                |
| `static/`          | JavaScript, CSS, images, and visualization tools     |

---

# Configuration

The application configuration is loaded from:

```text
config.py
```

Environment variables are loaded from:

```text
.env
```

The main variables are:

* `SECRET_KEY`
* `DB_USER`
* `DB_PASSWORD`
* `DB_HOST`
* `DB_PORT`
* `DB_NAME`
* `DATABASE_URL`
* `FLASK_CONFIG`

`DATABASE_URL` takes priority when it is defined.

The default configuration uses:

```text
DevelopmentConfig
```

The production configuration disables debug mode.

---

# Database

The application uses:

* PostgreSQL
* SQLAlchemy

The database can be initialized with:

```bash
python manage.py init_db
```

> **Warning:** This command deletes all existing tables before recreating them.

The database is mainly used to temporarily store analysis results.

---

# Starting the Server

The application can be started from the project root using:

```bash
python manage.py runserver
```

By default, the application runs on:

```text
127.0.0.1:5000
```

Additional options can be used:

```bash
python manage.py runserver --host 0.0.0.0 --port 5000 --debug
```

The Flask application is created using:

```python
create_app(
    os.environ.get("FLASK_CONFIG", "default")
)
```

---

# Web Navigation

The HTML routes are defined in:

```text
webViewer/app/viewer/routes.py
```

The main pages are:

| Route                    | Method | Description                           |
| ------------------------ | ------ | ------------------------------------- |
| `/`                      | GET    | Redirects to `/home`                  |
| `/home`                  | GET    | Home page                             |
| `/fitnessForm`           | GET    | Fitness Score form                    |
| `/pdbInfoRequest`        | POST   | Reads a PDB file and scoring options  |
| `/requestFormComparison` | GET    | Structure comparison form             |
| `/infoComparisonRequest` | POST   | Reads two PDB files for comparison    |
| `/requestFormHotSpots`   | GET    | Hotspot detection form                |
| `/infoHotSpotsRequest`   | POST   | Reads a PDB file for hotspot analysis |
| `/credits`               | GET    | Credits page                          |

The application also provides dedicated result pages for:

* Fitness Score.
* Structure Comparison.
* Hotspot Detection.

---

# Fitness Score Workflow

The Fitness Score workflow is:

```text
User
 ↓
Fitness Score Form
 ↓
PDB Upload
 ↓
Parameter Conversion
 ↓
JSON Request
 ↓
Fitness Score API
 ↓
Result Files
 ↓
3D Visualization and Download
```

The detailed process is:

1. The user opens `/fitnessForm`.
2. A molecular structure is uploaded.
3. The form is processed by `/pdbInfoRequest`.
4. The file content is decoded using UTF-8.
5. Form values are converted into Python data types.
6. `RequestParamFitness.toJson()` creates the JSON payload.
7. The result page is displayed.
8. JavaScript calls `/api-score/score`.
9. The results are displayed in the browser.

The generated payload contains parameters such as:

* `densities_fold`
* `frequencies_fold`
* `run_frequencies`
* `water_env`
* `atom_type`
* `environment_size`
* `pocket_num`
* `model_num`
* `l_ori`

---

# Structure Comparison Workflow

The comparison workflow is:

1. The user opens `/requestFormComparison`.
2. Two PDB files are selected.
3. `/infoComparisonRequest` processes the files.
4. `RequestGridComparisonParameters` creates the parameter object.
5. The data is converted into JSON.
6. The comparison result page is displayed.
7. JavaScript calls `/api-hot-comp/comparison`.
8. The results are displayed in the browser.

The results can include:

* Cleaned molecular structures.
* Structural comparison data.
* Heatmaps.
* Newick trees.
* SVG visualizations.

Molecular structures are displayed using 3Dmol.js.

---

# Hotspot Workflow

The hotspot workflow is similar to the comparison workflow.

1. The user opens `/requestFormHotSpots`.
2. A PDB file is selected.
3. `/infoHotSpotsRequest` processes the uploaded structure.
4. `RequestGridHotspotParameters` prepares the parameters.
5. The data is converted into JSON.
6. The hotspot result page is displayed.
7. JavaScript calls `/api-hot-comp/hotSpots`.
8. The generated results are displayed.

The main parameter groups are:

```text
global_parameters
hotspot_parameters
```

---

# Temporary Result Storage

Analysis results can be temporarily stored in PostgreSQL.

The application provides separate storage systems for:

* Fitness Score results.
* Structure Comparison results.
* Hotspot results.

Each result is associated with a unique user key.

The stored data is automatically removed after 30 minutes of inactivity.

Whenever stored data is accessed successfully, its `date_last_used` value is updated.

This extends the temporary lifetime of the stored result.

---

# Database Models

The SQLAlchemy models are defined in:

```text
webViewer/app/models.py
```

The main tables are:

| Table                      | Content                                |
| -------------------------- | -------------------------------------- |
| `temp_save_score_one_file` | Parameters, mmCIF, CSV, and log files  |
| `temp_save_comparison`     | Comparison parameters and JSON results |
| `temp_save_hot_spots`      | Hotspot parameters and JSON results    |

Each table uses:

* `user_key` as the primary identifier.
* `date_last_used` to manage temporary storage.

Inactive entries older than 30 minutes are automatically removed.

---

# Result Visualization

The application uses JavaScript to display scientific results directly in the browser.

The visualizations include:

* 3D molecular structures.
* Fitness Score coloring.
* Structural comparison trees.
* Newick tree visualization.
* Hotspot information.
* Downloadable result files.

The main visualization library used for molecular structures is:

```text
3Dmol.js
```

The result page JavaScript communicates with both:

* The scientific APIs.
* The temporary storage APIs.

---

# Error Handling

Unknown pages are handled by a custom 404 error handler.

The following template is displayed:

```text
viewer/pageNotFound.html
```

API responses generally use the following structure:

```json
{
    "status": "error",
    "message": "..."
}
```

Common HTTP status codes include:

* `200` — Successful request.
* `201` — Data successfully created.
* `400` — Invalid request or missing data.
* `404` — Page or resource not found.
* `500` — Internal server or database error.

---

## Related Documentation

* [Installation Guide](installation.md)
* [Fitness Score](fitness-score.md)
* [Grid Methods](grid-methods.md)
* [API Documentation](api.md)
