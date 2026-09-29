# InstallScout

InstallScout reads a Windows installer without running it, builds the silent command and a PSADT Win32 package, and uploads the app to Intune with detection, logo, and optional supersedence.

The program is for Windows 10 and 11. The interface is in English. Switch to Dansk in the top-right corner.

## Download

The current version is **1.8.45**: [releases](https://github.com/mthorngaard-hue/InstallScout-releases/releases/latest)

| File | Use |
|---|---|
| `InstallScoutPortable.exe` | Copy it anywhere and run it. Nothing is installed. |
| `InstallScout.msi` | Installs to Program Files and adds a Start menu shortcut. |

Drop an installer on the window, or use **Add files**. InstallScout does not run the installer. Review the silent command and test the package in a VM before you roll it out.

## Documentation

**Quick start:** [English](docs/quickstart-en.md) · [Dansk](docs/quickstart.md)  
**Guide:** [English](docs/guide.md) · [Dansk](docs/vejledning.md)  
**Technical reference:** [English](docs/reference-en.md) · [Dansk](docs/reference.md)

Word copies sit next to the Markdown files: [quick start](docs/InstallScout-quickstart-en.docx), [guide](docs/InstallScout-guide.docx), and [reference](docs/InstallScout-reference-en.docx). Danish Word files use the same names without `-en`.
