# Find silent install switches and upload to Intune

To find the silent switches for an app, give InstallScout the installer. It reads the EXE, MSI, COM, or MSIX, names the engine, and writes the silent command. The installer is not run. From that command, **Intune package** builds a local `.intunewin`, and **Upload to Intune** sends the Win32 app.

A silent switch is an argument that finishes setup with no dialogs. MSI installers share `msiexec` parameters. EXE installers do not. The arguments depend on the engine that built the file: Inno Setup, NSIS, InstallShield, WiX Burn, and the others below.

Version **1.8.61**. Every engine, uninstall command, and optional flag is in [reference-en.md](reference-en.md). The path from that command to an Intune Win32 app is in [guide.md](guide.md).

## How to find the switches

1. Start `InstallScoutPortable.exe`. Nothing has to be installed.
2. Drop the app's installer on the window.
3. Click **Analyze**. The silent command is on the Commands tab. Confidence is shown next to the engine.

The same lookup from a prompt:

```powershell
.\InstallScoutPortable.exe --cli "C:\installers\setup.exe"
```

The file stays on the machine. After the local result, WinGet and Chocolatey are asked for the product name and vendor only. The installer is not uploaded. A confident local command is kept when those catalogs disagree.

`setup.exe /?` is the usual first try, and many installers print nothing. InstallScout does not need that help text. It matches markers in the file and applies the silent form for that engine.

## Silent switches by engine

`{file}` is the quoted path of the installer.

| Engine | Silent install |
|---|---|
| Windows Installer (MSI) | `msiexec /i "{file}" /qn` |
| Inno Setup | `"{file}" /VERYSILENT /SUPPRESSMSGBOXES /NORESTART /SP-` |
| NSIS | `"{file}" /S` |
| InstallShield | `"{file}" /s /v"/qn"` |
| WiX Burn | `"{file}" /quiet` |
| Advanced Installer | `"{file}" /exenoui /qn` |

## Upload to Intune

1. **Analyze** — InstallScout writes the silent command. The installer is not run.
2. **Intune package** — a local `.intunewin` with install, uninstall, and detection.
3. **Upload to Intune** — the Win32 app, with System or User, a logo, and optional supersedence.

Finding the switches does not need an Azure sign-in. Upload does. The steps in the window are in the [guide](guide.md).

- **NSIS.** `/S` must be capital. `/D=` must be last and unquoted.
- **Inno Setup.** `/S` is not the silent switch. Use `/VERYSILENT`. `/NORESTART` belongs to Inno and stays.
- **InstallShield.** `/qn` is passed through `/v"/qn"`. An older InstallScript setup may need a recorded `setup.iss` (`/r`, then `/s /f1`).
- **WiX Burn.** `/quiet` is the silent switch. `/install` is already the default, so it is not added.
- **Advanced Installer.** `/S` and `/VERYSILENT` typically produce *Invalid command line*.

Suggested switches under the command are optional flags from the file or the engine, such as an Inno log or MSI `ALLUSERS=1`. Tick one to add it. `/install` and `/norestart` are not offered. The full list is in the [reference](reference-en.md).

## When the file is only a wrapper

A 7-Zip SFX, WinRAR SFX, IExpress package, or some self-extractors have no reliable silent line of their own. InstallScout unpacks the inner setup locally and uses that command. Inno Setup, NSIS, Wacom, and Dell Display and Peripheral Manager are not unpacked.

An outer `/sAll`, `--silent`, or `/silent` is kept. An Adobe-style self-extractor becomes `"{file}" /sAll /rs /rps /msi /quiet` when `/sAll` or `/rps` is in the file.

## What the command does not prove

The line is the engine's silent form, plus flags read from the file. It is not a test install. **Try in Sandbox** is optional. When the button is shown, it runs the command in Windows Sandbox, not on this PC. You can package and upload while that test runs, and you can still try the package in a VM before you roll it out.

Vendor settings such as a license server or a language are not looked up from a catalog of every app. ClickOnce usually has no reliable silent switch for a machine install.

## Frequently asked questions

### How do I find the silent install command?

Drop the installer on InstallScout and click Analyze. The program reads the file, names the engine, and writes the silent command. You do not run the setup, and you do not look the app up by name.

### How do I install an EXE silently?

The command depends on the engine. Inno Setup uses `/VERYSILENT`. NSIS uses `/S`. InstallShield uses `/s /v"/qn"`. An MSI uses `msiexec /i "{file}" /qn`. WiX Burn uses `/quiet`. InstallScout writes the line for the file you give it.

### How do I upload an EXE to Intune?

Click Analyze, then Intune package, then Upload to Intune. That saves a local `.intunewin` and sends the Win32 app with install, uninstall, detection, and a logo. You do not run the Win32 Content Prep Tool yourself.

### What are the silent switches for MSI, Inno, NSIS, and InstallShield?

MSI uses `msiexec /i "{file}" /qn`. Inno Setup uses `/VERYSILENT /SUPPRESSMSGBOXES /NORESTART /SP-`. NSIS uses `/S`, capital S. InstallShield uses `/s /v"/qn"`.

### Does finding the switches run the installer?

No. InstallScout reads the file. The installer is not started. **Try in Sandbox** is a separate button. It runs the command only inside Windows Sandbox, and only when you click it.

### How do I test the silent command without installing on this PC?

Click **Try in Sandbox** after Analyze, when Windows Sandbox is installed. The test is optional. The command and the detection script run in a disposable sandbox, and you can package and upload while it runs. This PC is not changed. The button is hidden when Sandbox is not installed. You can still test the package in a VM.

### What if setup.exe /? shows nothing?

Many setup programs print no help. The engine still has a known silent form. InstallScout matches markers in the file and applies that form. When the outer file is only a wrapper, the inner setup is unpacked and those switches are used.
