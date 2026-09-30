# InstallScout – teknisk reference

Version **1.8.49**. Kort forløb: [quickstart.md](quickstart.md). Brugerforløbet står i [vejledning.md](vejledning.md). Denne fil beskriver motorer, kommandolinje og Microsoft Graph. Word: [InstallScout-reference.docx](InstallScout-reference.docx).

InstallScout kører ikke installeren. Den læser filen, bygger en silent-kommando, pakker PSADT 4.1.8 til `.intunewin` og opretter en Win32-app.

---

## 1. Engines

En motor genkendes på byte-markører i filen, PE-sektioner og søskendefiler. Den motor med højest score vinder. `base_confidence` nedenfor er startværdien, før ekstra bevis lægges til.

Wrappers (7-Zip SFX, WinRAR SFX, IExpress, Self Extractor, ukendt EXE) pakkes ud lokalt, når den ydre fil ikke selv har en pålidelig silent-linje. Rene motorer som Inno, NSIS, Wacom og DDPM pakkes ikke ud.

`/install` sættes ikke på. Det er allerede standard for WiX Burn. `/norestart` sættes heller ikke på. Inno Setup beholder sin egen `/NORESTART`.

`{file}` er den citerede sti til installeren. `{product_code}` er MSI `ProductCode`. `{app}` er den installerede mappe, som PSADT kender ved afinstallation.

| Id | Navn | Silent install | Alternativ | Afinstallation | Start |
|---|---|---|---|---|---|
| `msi` | Windows Installer (MSI) | `msiexec /i "{file}" /qn` | `msiexec /i "{file}" /qb` | `msiexec /x "{product_code}" /qn` | 0.97 |
| `inno` | Inno Setup | `"{file}" /VERYSILENT /SUPPRESSMSGBOXES /NORESTART /SP-` | `"{file}" /SILENT /NORESTART` | `"{app}\unins000.exe" /VERYSILENT /NORESTART` | 0.95 |
| `wixburn` | WiX Burn | `"{file}" /quiet` | `"{file}" /passive` | `"{file}" /uninstall /quiet` | 0.93 |
| `ddpm` | Dell Display and Peripheral Manager | `"{file}" /Silent` | `"{file}" /Silent /CreateDebugLog="%TEMP%\DDPM-install.log"` | `"{file}" /uninst` | 0.93 |
| `advanced_installer` | Advanced Installer | `"{file}" /exenoui /qn` | `"{file}" /exenoui /passive /qn` | `"{file}" /exenoui /x // /qn` | 0.92 |
| `nsis` | NSIS | `"{file}" /S` | | `"{app}\uninstall.exe" /S` | 0.90 |
| `wacom` | Wacom Tablet Driver | `"{file}" /s` | `"{file}" /s /opt nowdc` | `"{file}" /s /u` | 0.90 |
| `msix` | MSIX / AppX | `Add-AppxPackage -Path "{file}"` | `Add-AppxProvisionedPackage -Online -PackagePath "{file}" -SkipLicense` | | 0.90 |
| `self_extractor` | Self Extractor | høstet, ellers indre setup | | `/uninst` eller `/uninstall` når det findes | 0.88 |
| `bitrock` | BitRock InstallBuilder | `"{file}" --mode unattended --unattendedmodeui none` | | | 0.88 |
| `install4j` | install4j | `"{file}" -q` | | | 0.85 |
| `installaware` | InstallAware | `"{file}" /s` | | | 0.80 |
| `sevenzip_sfx` | 7-Zip SFX | `"{file}" -y` | | | 0.80 |
| `qt_installer` | Qt Installer Framework | `"{file}" --silent --accept-licenses` | | | 0.80 |
| `installshield` | InstallShield | `"{file}" /s /v"/qn"` | `"{file}" /s /sms` | | 0.78 |
| `winrar_sfx` | WinRAR SFX | `"{file}" /S` | | | 0.75 |
| `squirrel` | Squirrel | `"{file}" --silent` | | | 0.72 |
| `clickonce` | ClickOnce | ingen pålidelig silent-linje | | | 0.70 |
| `iexpress` | IExpress | `"{file}" /Q` | | | 0.70 |
| `wise` | Wise Installer | `"{file}" /s` | | | 0.65 |

### Særlige regler

- **NSIS.** `/S` skal være stort. `/D=` skal stå sidst og uden citationstegn.
- **Inno.** `/S` er ikke silent her. `/NORESTART` er Innos egen switch og bliver stående.
- **InstallShield.** Nyere wrappers sender `/qn` videre med `/v"/qn"`. Ældre InstallScript kan kræve en optaget `setup.iss` (`/r`, derefter `/s /f1`).
- **WiX Burn.** `/quiet` er silent. `/install` udelades, fordi install er default.
- **Advanced Installer.** `/S` og `/VERYSILENT` giver typisk *Invalid command line*.
- **DDPM.** `/Silent` er ikke InstallShield `/s /v"/qn"`.
- **Wacom.** Den downloadede fil er en 7-Zip SFX, men silent er `/s` på EXE’en, ikke `-y`.
- **Self Extractor.** Ydre `/sAll`, `--silent` eller `/silent` beholdes. Adobe-kæden bliver `"fil" /sAll /rs /rps /msi /quiet`, når `/sAll` eller `/rps` står i filen. Uden ydre silent-flag udpakkes den indre MSI/EXE.
- **Squirrel.** Installerer som regel per bruger. Context bliver User.
- **ClickOnce.** Ingen silent-skabelon. Intune-pakning er ikke et pålideligt mål.
- **MSIX.** Detection bruger pakkenavn, ikke product code.

### Foreslåede switche

Op til 10 forslag. Først flag fundet i filen (`/analytics no`, `/sso no` og andre `navn yes|no`), derefter motorens valgfrie flag. `/install` og `/norestart` foreslås ikke. Et flueben sætter switchen på silent-linjen og gør den lokale `.intunewin` ugyldig, så pakken skal bygges igen.

| Motor | Forslag ud over det, filen selv nævner |
|---|---|
| MSI | `ALLUSERS=1`, `REBOOT=ReallySuppress`, `/l*v "%TEMP%\install.log"` |
| Inno | `/NORESTARTAPPLICATIONS`, `/LOG="%TEMP%\install.log"`, `/MERGETASKS=!desktopicon` |
| NSIS | `/NCRC` |
| InstallShield | `/f2"%TEMP%\install.log"` |
| WiX Burn | `/log "%TEMP%\install.log"` |
| Advanced Installer | `/exenoupdates` |
| Wise | `/l="%TEMP%\install.log"` |
| DDPM | `/TelemetryConsent=false`, `/HeadlessMode=true`, `/CreateDebugLog=%TEMP%\DDPM.log`, `/TurnOffCA` |
| Wacom | `/opt nowdc` |

### Detection i forhold til motor

`Detection.ps1` skriver til STDOUT og afslutter med kode 0, når appen er installeret. Tom STDOUT betyder ikke installeret. Scriptet kaster ikke.

| Kilde | Match |
|---|---|
| MSI `ProductCode`, eller en GUID i afinstallationskommandoen | Den nøgle i Uninstall, og version `>=` |
| EXE uden product code | DisplayName, Publisher og version `>=` |
| MSIX | Pakkenavn, og version når den kendes |

Et efterstillet Installer, Setup eller Bootstrapper må mangle i DisplayName. `Logi Options+ Installer` matcher `Logi Options+`. Et generisk restord som Advanced bruges ikke. Selskabsendelser ignoreres, så `Logitech, Inc.` matcher `Logitech`. Version sammenlignes numerisk. Samme version og nyere tæller. Ældre gør ikke.

Nøgler der læses: `HKLM` og `HKCU`, begge med `WOW6432Node`, under `SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall`.

---

## 2. CLI

`InstallScoutPortable.exe` uden argumenter åbner GUI. En frossen EXE åbner også GUI, medmindre et CLI-flag er sat. Fra kilde er `python -m installscout` det samme.

Et af disse flag tvinger CLI, også uden `--cli`: `--json`, `--out`, `--psadt`, `--intune`, `--online`, `--sihq`, `--publish-intune`, `--switches`, `--icon`, `--supersede`, `--supersede-id`.

| Flag | Betydning |
|---|---|
| `paths` | Filer eller mapper. Endelser: `.exe`, `.msi`, `.com`, `.msix`, `.appx`, `.msixbundle`, `.appxbundle` |
| `--gui` | Åbn GUI, også når der er stier |
| `--cli` | Tving tekstoutput |
| `--json` | Skriv analysen som JSON på stdout |
| `--out PATH` | Skriv samme JSON til en fil |
| `--psadt DIR` | Skriv PSADT-kilde, uden `.intunewin` |
| `--intune DIR` | Skriv `.intunewin`, PSADT-kilde, `Intune.txt` og `Detection.ps1` |
| `--no-copy-installer` | Lad installeren ligge, hvor den er. Pakken peger på den oprindelige sti |
| `--publish-intune` | Opret Win32-appen. Kræver `--intune` |
| `--icon PATH` | PNG, JPEG, GIF, ICO eller BMP til `largeIcon`. Uden flag bruges ikon fra EXE eller en søskendefil |
| `--supersede update\|replace` | Supersedence mod ældre Win32-apps med beslægtet navn. Højst 10 |
| `--supersede-id GUID` | Gentages. Brug kendte app-id’er i stedet for navnesøgning |
| `--tenant ID` | Tom betyder `organizations` |
| `--client-id ID` | Tom betyder Microsoft Graph PowerShell |
| `--online` | WinGet og Chocolatey. Kun produktnavn og vendor sendes |
| `--sihq` | Åbn navnesøgning på silentinstallhq.com. Kommandoen overskrives ikke |
| `--switches TEXT` | Tilføj argumenter til silent-linjen på alle filer i kørslen |
| `--lang en\|da` | Sprog for CLI-tekst. GUI husker sit eget valg |
| `-r` / `--recursive` | Søg mapper rekursivt. Det er standard |
| `--no-recursive` | Kun den angivne mappe |
| `--version` | Skriv version og afslut |

Exitkode `0` er succes. Exitkode `2` bruges, når der ikke er nogen understøttet fil, `--publish-intune` mangler `--intune`, eller `--icon` ikke kan læses.

```powershell
.\InstallScoutPortable.exe --cli .\setup.exe
.\InstallScoutPortable.exe --cli .\setup.exe --online
.\InstallScoutPortable.exe --cli .\setup.exe --switches "/LOG=C:\logs\app.log" --json --out .\analysis.json
.\InstallScoutPortable.exe --cli .\setup.exe --intune C:\out\intune
.\InstallScoutPortable.exe --cli .\setup.exe --intune C:\out\intune --publish-intune --icon .\logo.png --supersede update
.\InstallScoutPortable.exe --cli .\setup.exe --intune C:\out\intune --publish-intune --supersede replace --supersede-id <app-guid>
```

`--json` er en liste af analyseobjekter: sti, motor, confidence, kommandoer, høstede switche, `option_flags`, VersionInfo, MSI-egenskaber og noter. Den første kommando med formål `silent_install` er den anbefalede linje.

Intune-installationslinjen i portalen er altid PSADT, ikke den rå silent-kommando:

```text
.\Invoke-AppDeployToolkit.exe -DeploymentType Install -DeployMode Silent
.\Invoke-AppDeployToolkit.exe -DeploymentType Uninstall -DeployMode Silent
```

`setupFilePath` er `Invoke-AppDeployToolkit.exe`.

---

## 3. Graph

Win32-felterne `detectionRules`, `displayVersion` og `maxRunTimeInMinutes` findes på Graph **beta**, ikke på v1.0. App-kald går derfor til `https://graph.microsoft.com/beta`. `GET /me` til whoami går til `https://graph.microsoft.com/v1.0`.

### Login

OAuth 2.0 authorization code med PKCE. Device code bruges ikke. En lokal HTTP-lytter på `http://localhost:<port>/` tager koden. Browseren åbnes i Edge-arbejdsprofilen, når den kan genkendes.

| | |
|---|---|
| Authority | `https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize` og `/token` |
| Standard-tenant | `organizations` |
| Standard-klient | `14d82eec-204b-4c2f-b7e8-296a70dab67e` (Microsoft Graph PowerShell, offentlig klient) |
| Scopes | `DeviceManagementApps.ReadWrite.All`, `User.Read`, `offline_access`, `openid`, `profile` |
| Tokenfil | `%LOCALAPPDATA%\InstallScout\graph.json`, Windows DPAPI for den aktuelle bruger (`ISC1`). Bundet til tenant og Client ID. Klartekst slettes. |
| Fornyelse | Refresh-token. Et 401 prøves én gang efter refresh. Udløbet session sletter tokenfilen. En anden tenant eller et andet Client ID genbruger ikke sessionen |

Eget Client ID skal være en public client med redirect `http://localhost` og samme tilladelse. InstallScout opretter ikke en app-registration. Den bruger, der logger på, skal kunne oprette Win32-apps. Entra-rollen Intune Administrator, eller Intune-rollen Application Manager, dækker det. Tenant skal stadig have admin-consent for `DeviceManagementApps.ReadWrite.All`.

### Opret og upload

1. `POST /deviceAppManagement/mobileApps` med `#microsoft.graph.win32LobApp`.
2. `POST .../microsoft.graph.win32LobApp/contentVersions`.
3. `POST .../contentVersions/{version}/files` med krypteret størrelse og ukrypteret størrelse.
4. Poll filen, til `azureStorageUri` findes.
5. `PUT` den krypterede blob i bidder på 6 MiB.
6. `POST .../files/{id}/commit` med `fileEncryptionInfo`.
7. `PATCH` appen med `committedContentVersion`.

Hvis upload eller commit fejler, slettes den nye app. Supersedence kører bagefter og sletter ikke appen, hvis den fejler.

Kryptering er den samme form som Microsoft Win32 Content Prep: AES-CBC, 256-bit nøgle, HMAC-SHA256, `ProfileVersion1`, digest `SHA256`. Nøgle, IV, MAC og digest sendes i commit. Selve installeren sendes ikke under online-opslag, kun i den krypterede `.intunewin`.

### App-payload

| Felt | Værdi |
|---|---|
| `displayName` | Navn i dialogen, ellers `{produkt} {version}`. Højst 500 tegn |
| `publisher` | Vendor, eller produktnavnet når vendor er Unknown. Højst 500 |
| `displayVersion` | Analyseret version. Højst 50 tegn |
| `description` | Motor, context og detection-opsummering. Højst 4000 |
| `installCommandLine` / `uninstallCommandLine` | PSADT Silent, som ovenfor |
| `setupFilePath` | `Invoke-AppDeployToolkit.exe` |
| `applicableArchitectures` | `x64`, `x86` eller `arm64` |
| `minimumSupportedWindowsRelease` | `Windows10_22H2` |
| `installExperience.runAsAccount` | `system` eller `user` |
| `installExperience.deviceRestartBehavior` | `suppress` (No specific action) |
| `installExperience.maxRunTimeInMinutes` | `60` |
| `allowAvailableUninstall` | `true` |
| `detectionRules` | Ét PowerShell-script, `enforceSignatureCheck` false, `runAs32Bit` false, indhold base64 UTF-8 |
| `largeIcon` | Udelades, når der ikke er et logo. Ellers `mimeContent` med PNG, JPEG eller GIF |
| `returnCodes` | `0` success, `1707` success, `3010` softReboot, `1641` hardReboot, `1618` retry |

Et MSI-ikon inde i pakken læses ikke. Logo kommer fra EXE/DLL/COM-ressourcen, fra `logo.png` / `icon.ico` ved siden af filen, eller fra den fil brugeren vælger.

### Supersedence

Søgning er `GET /deviceAppManagement/mobileApps` med `$filter=startswith(displayName,'…')` og `$top=50`, højst 5 sider. Hele kataloget hentes ikke. Søgeordet er produktnavnet, ikke det redigerede Intune-navn.

`POST /deviceAppManagement/mobileApps/{id}/updateRelationships` med `#microsoft.graph.mobileAppSupersedence`:

| `supersedenceType` | Betydning |
|---|---|
| `update` | Installér den nye uden at afinstallere den gamle først |
| `replace` | Afinstallér den gamle, og installér derefter den nye |

Højst 10 mål. Ingenting vælges automatisk i GUI. CLI med `--supersede` vælger de apps, hvis navn ligner produktet.

Portal-link efter succes:

```text
https://intune.microsoft.com/#view/Microsoft_Intune_Apps/SettingsMenu/~/0/appId/{appId}
```
