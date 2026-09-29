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
