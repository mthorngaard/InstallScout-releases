# InstallScout – quick start

Version **1.8.48**. From an installer to a Win32 app in Intune. The program does not run the installer.

The full guide is [guide.md](guide.md). Engines, the CLI, and Graph are in [reference-en.md](reference-en.md). Word: [InstallScout-quickstart-en.docx](InstallScout-quickstart-en.docx).

## 1. Start

Double-click `InstallScoutPortable.exe`. Nothing has to be installed. The language is English. Switch to Dansk in the top-right corner. Drop an installer on the window, or use **Add files…**.

The download is **not code-signed**. Windows or company security may warn or block it. Choose Keep / Run anyway, ask IT to allow the file, or try it in a VM or Windows Sandbox without those policies.

To put it on the Start menu, run `portable\Install.bat`. The portable exe stays where it is and can still be copied on its own.

## 2. Analyze

1. **Add files…** and choose an EXE, MSI, COM, or MSIX.
2. Click **Analyze**.

The green line is the silent command. **Suggested switches** may appear under it. Tick a switch to add it, and untick to remove it. `/install` and `/norestart` are not added automatically. Inno keeps `/NORESTART`.

Edit the line, or type an extra flag under **Extra switches** and click **Add**. Test the command in a VM before you roll it out.

## 3. Package

Click **Intune package…** and choose a folder. That saves an `.intunewin`, the PSADT source, and `Detection.ps1`.

**Upload to Intune** stays grey until the package exists. If you change the command afterwards, build the package again.

## 4. Upload

Click **Upload to Intune…**.

1. Edit **Name in Intune** if Company Portal should not show the product name and version.
2. Leave **System** unless the app is per user (typically Squirrel).
3. Check the logo. An MSI often has no icon. Choose a file, paste an image, or remove the logo.
4. The field shows one Edge profile. Open it to pick another, then click **Sign in to Intune**. Wait until it says *Signed in as …*. Sign-in is bound to the tenant and Client ID.
5. Optionally pick older apps under supersedence. Nothing is selected beforehand. **Update** installs over the old app. **Replace** uninstalls it first.
6. Click **Upload**.

Requirement: an account that can create Win32 apps (**Intune Administrator**, or the Intune role **Application Manager**) and admin consent for `DeviceManagementApps.ReadWrite.All`. InstallScout does not create its own app.

## The same run from the command line

```powershell
.\InstallScoutPortable.exe --cli .\setup.exe --intune C:\out\intune --publish-intune --icon .\logo.png
```

Without `--icon`, the icon is taken from the EXE when one is present.

## Detection, in short

Intune treats the app as installed when `Detection.ps1` writes a line and exits 0.

- An MSI is matched on its product code.
- An EXE is matched on name, publisher, and version. The version must be the same or newer.
- `Logi Options+ Installer` matches `Logi Options+`. `Logitech, Inc.` matches `Logitech`.
