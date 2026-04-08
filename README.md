# UEFN Asset Importer

A simple GUI tool to import `.uasset` and `.umap` files into your [UEFN](https://www.epicgames.com/fortnite/unreal-editor) projects. Designed for quick asset management, drag-and-drop support, and easy ZIP/folder imports.

---

## Features

* Import individual `.uasset` or `.umap` files, entire folders, or ZIP archives.
* Drag-and-drop support (if `tkinterdnd2` is installed).
* Save your UEFN project directory and app settings.
* Light, dark, or system-themed UI.
* Progress bar and status updates during import.
* Simple configuration via `config.json`.

---

## Installation

1. Clone this repository:

```bash
git clone https://github.com/ItsMarwanUEFN/uefn_importer.git
cd uefn_importer
```

2. Install required packages (Python 3.12+ recommended):

```bash
pip install tkinterdnd2
```

> Note: `tkinter` is usually included with Python on Windows.

3. Run the app:

```bash
python main.py
```

---

## Usage

1. On first launch, set your UEFN project directory.
2. Drag-and-drop a folder, ZIP, or select files using the buttons.
3. Enter a project name for import.
4. Click **Import to UEFN Project** to copy assets into your project.

You can also configure:

* Warnings for unsupported file types.
* UI theme (light, dark, system).
* Default `config.json` location.

---

## Supported File Types

* `.uasset`
* `.umap`

Unsupported file types will trigger a warning (if enabled in settings).

---

## Screenshots

<img width="796" height="826" alt="startup screen" src="https://github.com/user-attachments/assets/e959bc87-d24d-4e2c-941d-26522b6d2410" />
<img width="796" height="825" alt="main interface" src="https://github.com/user-attachments/assets/89a95140-090d-4047-9856-e6ebf050aecd" />
<img width="797" height="825" alt="settings tab" src="https://github.com/user-attachments/assets/08e7d360-4d65-4115-b7fc-d196beb7477b" />


---

## Contributing

Feel free to open issues or ask questions. Contributions are welcome but please **do not sell this tool**.

* Follow me on Twitter: [@itsmarwanuefn](https://twitter.com/itsmarwanuefn)
* Support the project: [Buy me a coffee](https://www.buymeacoffee.com/itsmarwan)

---

## License

This project is free to use for personal or educational purposes. Redistribution for profit is not allowed.
