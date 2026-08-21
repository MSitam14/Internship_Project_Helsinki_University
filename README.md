# Molecular Structure Analysis Web Viewer

A web application developed during an internship at the University of Helsinki to provide an accessible interface for molecular structure analysis.

The project integrates several scientific tools and algorithms to analyse protein structures through a web interface.

## Features

The application currently provides three main analysis tools:

* **Fitness Score** — evaluates the local environment of atoms in a molecular structure.
* **Structure Comparison** — compares multiple molecular structures and calculates structural similarities.
* **Hotspot Detection** — identifies relevant positions and interaction hotspots within molecular structures.

The application also provides:

* Interactive 3D molecular visualization using 3Dmol.js.
* Visualization of structural comparison trees.
* Downloadable analysis results.
* Temporary storage of results using PostgreSQL.
* User keys for retrieving recent analysis results.

## Project Structure

The project is divided into three main components:

* `Fitness_score` — molecular fitness score calculation.
* `Grid_methods` — structure comparison and hotspot detection algorithms.
* `webViewer` — Flask web application and user interface.

```text
InternshipTestProject/
├── Fitness_score/
├── Grid_methods/
├── webViewer/
├── docs/
├── config.py
├── manage.py
├── README.md
└── requirements_webViewer.yml
```

## Quick Start

For installation instructions, see:

[Installation Guide](docs/installation.md)

For detailed technical documentation:

* [Fitness Score](docs/fitness-score.md)
* [Grid Methods](docs/grid-methods.md)
* [Web Viewer](docs/webviewer.md)
* [API Documentation](docs/api.md)

## Technologies

The project uses:

* Python 3.9
* Flask
* PostgreSQL
* SQLAlchemy
* Conda
* PyMOL
* 3Dmol.js
* Bootstrap

## Running the Project

After installation:

```bash
conda activate webViewer
python manage.py runserver
```

The application is then available at:

```text
http://127.0.0.1:5000
```

## Credits

The web interface was developed as part of an internship at the University of Helsinki.

The scientific algorithms used for structure comparison and hotspot analysis originate from the work of **Loïc Dréano**.

Additional scientific resources and credits are available on the application's Credits page.
