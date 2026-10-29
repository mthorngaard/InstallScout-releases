# InstallScout

Public page: [mthorngaard.github.io/InstallScout-releases](https://mthorngaard.github.io/InstallScout-releases/)

Find silent install switches for a Windows app without running the installer. InstallScout reads an EXE, MSI, COM, or MSIX, names the engine, and writes the silent command. It can then build a PSAppDeployToolkit (PSADT) `.intunewin` package and upload the Win32 app to Microsoft Intune.

**What's new in 1.8.72.** About names the anonymous startup call to Aptabase in the EU (eu.aptabase.com). It sends the version and language, not file names or paths. INSTALLSCOUT_USAGE=0 turns the call off.

![Twenty-second InstallScout walkthrough: drop an installer, try the silent command in Windows Sandbox, check WinGet, build the intunewin package, and upload the Win32 app](assets/installscout.gif?v=1.8.72)

## What it does

- **Silent command** — names the engine (Inno, NSIS, MSI, InstallShield, WiX Burn, Squirrel, and others) and writes the install line. The installer is not run.
- **Try in Sandbox** — optional. Runs that command and the detection script in Windows Sandbox, so this PC is not changed. You can package and upload while it runs. Shown when Windows Sandbox is installed.
- **Your edit** — change the line, add a switch, or tick a suggested one before anything is packaged.
- **Online check** — looks up the product name in WinGet and Chocolatey. The file is not uploaded.
- **System or User** — chosen from the engine and the command.
- **Intune package** — a local `.intunewin` with PSADT, install, uninstall, and detection.
- **Upload** — the Win32 app in Intune, with a logo and optional supersedence.

Windows 10 and 11. The interface is in English. Switch to Dansk in the top-right corner.

## Expected quality

These figures are estimates for a typical Intune queue: MSI, Inno, NSIS, InstallShield, WiX Burn, and known vendor EXE files. They describe the first result, before the command is edited. InstallScout does not measure whether the package or the detection succeeded.

- The package installs silently in about **80%** of cases.
- Detection then matches about **75%** of the installs that succeeded.
- Both succeed on the first attempt in about **60–65%** of cases.

| Class | Silent install | Detection after a successful install |
|---|---|---|
| MSI and WiX MSI | about 95% | about 95% |
| Inno, Advanced Installer, WiX Burn | about 85% | about 75% |
| NSIS and Self Extractor with known flags | about 75% | about 70% |
| InstallShield | about 60% | about 70% |
| Squirrel, ClickOnce, Qt, unknown EXE | about 35% | about 40% in Sandbox, lower in Intune |

MSI carries the package rate. `msiexec /qn` is stable, and detection uses the product code. InstallScript without a recorded `setup.iss`, custom dialogs, and an EXE whose Apps & features name differs from the file pull the rate down.

Detection is the narrower step for an EXE. It requires the name, the publisher, and the version together. The file version is often more precise than `DisplayVersion`, so the script can report the app as missing after a successful install. A per-user install can pass in Windows Sandbox and still fail in Intune, because detection runs as SYSTEM and reads that account’s HKCU.

Below about 40% confidence, treat the package as a draft. The hit rate there is closer to one in three.

The same note is in the [guide](https://mthorngaard.github.io/InstallScout-releases/docs/guide.html) and the [Danish vejledning](https://mthorngaard.github.io/InstallScout-releases/docs/vejledning.html).

## Download

The current version is **1.8.72**: [releases](https://github.com/mthorngaard/InstallScout-releases/releases/latest)

| File | Use |
|---|---|
| [`InstallScout-1.8.72.zip`](https://github.com/mthorngaard/InstallScout-releases/releases/download/v1.8.72/InstallScout-1.8.72.zip) | Both files in one download. |
| `InstallScoutPortable.exe` | Copy it anywhere and run it. Nothing is installed. |
| `InstallScout.msi` | Installs to Program Files and adds a Start menu shortcut. |

The download is not code-signed. Windows or company security may warn or block it. Choose Keep / Run anyway, ask IT to allow the file, or try it in a VM or Windows Sandbox without those policies.

On startup, one anonymous call to Aptabase in the EU (`eu.aptabase.com`) sends the version and language. File names and paths are not sent. `INSTALLSCOUT_USAGE=0` turns the call off.

Drop an installer on the window, or use **Add files**. **Try in Sandbox** is optional and runs the command without installing on this PC. You can package and upload while it runs, and you can still test the package in a VM before you roll it out.

## Prerequisites

Windows 10 or Windows 11. Finding silent switches and building a local package does not need an Azure sign-in.

**Try in Sandbox** needs Windows Sandbox installed. The button is not shown without it.

Upload to Intune also needs:

- Microsoft Edge. Sign-in opens in an Edge profile.
- An account that can create Win32 apps. In Microsoft Entra, that is the **Intune Administrator** role. In Intune role-based access control, **Application Manager** is enough. A custom role with the same app permissions works too.
- One-time admin consent in the tenant for the Graph permission `DeviceManagementApps.ReadWrite.All`. Sign-in uses the public Microsoft Graph PowerShell client unless you set another Client ID. InstallScout does not create an app registration.
- Conditional Access can still block that sign-in.

## Documentation

**Find silent switches:** [English](https://mthorngaard.github.io/InstallScout-releases/docs/find-silent-switches.html) · [Dansk](https://mthorngaard.github.io/InstallScout-releases/docs/find-silent-switche.html)  
**Quick start:** [English](https://mthorngaard.github.io/InstallScout-releases/docs/quickstart-en.html) · [Dansk](https://mthorngaard.github.io/InstallScout-releases/docs/quickstart.html)  
**Guide:** [English](https://mthorngaard.github.io/InstallScout-releases/docs/guide.html) · [Dansk](https://mthorngaard.github.io/InstallScout-releases/docs/vejledning.html)  
**Technical reference:** [English](https://mthorngaard.github.io/InstallScout-releases/docs/reference-en.html) · [Dansk](https://mthorngaard.github.io/InstallScout-releases/docs/reference.html)

PDF copies sit next to the Markdown files: [quick start](docs/InstallScout-quickstart-en.pdf?v=1.8.72), [guide](docs/InstallScout-guide.pdf?v=1.8.72), and [reference](docs/InstallScout-reference-en.pdf?v=1.8.72). Danish PDF files use the same names without `-en`.

## Credits

Intune packages are built with [PSAppDeployToolkit](https://github.com/PSAppDeployToolkit/PSAppDeployToolkit) 4.1.8 by the PSAppDeployToolkit Team. That toolkit is licensed under the [GNU Lesser General Public License v3.0](https://github.com/PSAppDeployToolkit/PSAppDeployToolkit/blob/main/COPYING.Lesser).

Inner setup unpacking uses [7-Zip](https://www.7-zip.org/) Extra (`7za`) by Igor Pavlov, licensed under the GNU LGPL.
