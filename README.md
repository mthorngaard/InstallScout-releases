# InstallScout

Public page: [mthorngaard.github.io/InstallScout-releases](https://mthorngaard.github.io/InstallScout-releases/)

InstallScout goes from silent switch finder to Intune upload. It reads an EXE, MSI, COM, or MSIX without running it, finds the silent install switches, builds a PSAppDeployToolkit (PSADT) `.intunewin` package, and uploads the Win32 app to Microsoft Intune with detection, a logo, and optional supersedence.

Use it for the full path: find the switches, package the command, then upload to Intune as a system or user install. It runs on Windows 10 and Windows 11. The interface is in English. Switch to Dansk in the top-right corner.

## Download

The current version is **1.8.47**: [releases](https://github.com/mthorngaard/InstallScout-releases/releases/latest)

| File | Use |
|---|---|
| [`InstallScout-1.8.47.zip`](https://github.com/mthorngaard/InstallScout-releases/releases/download/v1.8.47/InstallScout-1.8.47.zip) | Both files in one download. |
| `InstallScoutPortable.exe` | Copy it anywhere and run it. Nothing is installed. |
| `InstallScout.msi` | Installs to Program Files and adds a Start menu shortcut. |

The download is not code-signed. Windows or company security may warn or block it. Choose Keep / Run anyway, ask IT to allow the file, or try it in a VM or Windows Sandbox without those policies.

Drop an installer on the window, or use **Add files**. InstallScout does not run the installer. Review the silent command and test the package in a VM before you roll it out.

## Prerequisites

Windows 10 or Windows 11. Finding silent switches and building a local package does not need an Azure sign-in.

Upload to Intune also needs:

- Microsoft Edge. Sign-in opens in an Edge profile.
- An account that can create Win32 apps. In Microsoft Entra, that is the **Intune Administrator** role. In Intune role-based access control, **Application Manager** is enough. A custom role with the same app permissions works too.
- One-time admin consent in the tenant for the Graph permission `DeviceManagementApps.ReadWrite.All`. Sign-in uses the public Microsoft Graph PowerShell client unless you set another Client ID. InstallScout does not create an app registration.
- Conditional Access can still block that sign-in.

## Documentation

**Quick start:** [English](docs/quickstart-en.md) · [Dansk](docs/quickstart.md)  
**Guide:** [English](docs/guide.md) · [Dansk](docs/vejledning.md)  
**Technical reference:** [English](docs/reference-en.md) · [Dansk](docs/reference.md)

Word copies sit next to the Markdown files: [quick start](docs/InstallScout-quickstart-en.docx), [guide](docs/InstallScout-guide.docx), and [reference](docs/InstallScout-reference-en.docx). Danish Word files use the same names without `-en`.

## Credits

Intune packages are built with [PSAppDeployToolkit](https://github.com/PSAppDeployToolkit/PSAppDeployToolkit) 4.1.8 by the PSAppDeployToolkit Team. That toolkit is licensed under the [GNU Lesser General Public License v3.0](https://github.com/PSAppDeployToolkit/PSAppDeployToolkit/blob/main/COPYING.Lesser).
