# Find silent-switche til en Windows-app

For at finde silent-switchene til en app giver du InstallScout installeren. Programmet læser EXE-, MSI-, COM- eller MSIX-filen, navngiver motoren og skriver silent-kommandoen. Installeren bliver ikke kørt.

En silent-switch er et argument, der får setup til at køre færdigt uden dialoger. MSI-filer deler parametre til `msiexec`. EXE-filer gør ikke. Argumenterne afhænger af motoren, der har bygget filen: Inno Setup, NSIS, InstallShield, WiX Burn og de øvrige nedenfor.

Version **1.8.58**. Alle motorer, afinstallation og valgfri flag står i [reference.md](reference.md). Vejen fra kommandoen til en Win32-app i Intune står i [vejledning.md](vejledning.md).

## Sådan finder du switchene

1. Start `InstallScoutPortable.exe`. Der skal ikke installeres noget.
2. Træk appens installer ind på vinduet.
3. Klik **Analysér**. Silent-kommandoen ligger under Kommandoer. Sikkerheden står ved siden af motoren.

Samme opslag fra en prompt:

```powershell
.\InstallScoutPortable.exe --cli "C:\installers\setup.exe"
```

Filen bliver på maskinen. Efter det lokale resultat bliver WinGet og Chocolatey spurgt om produktnavn og leverandør. Installationsfilen bliver ikke uploadet. En sikker lokal kommando beholdes, når katalogerne er uenige.

`setup.exe /?` er det sædvanlige første forsøg, og mange installere skriver ingenting. InstallScout behøver ikke den hjælpetekst. Det matcher mærker i filen og bruger silent-formen for den motor.

## Silent-switche efter motor

`{file}` er installerens sti i anførselstegn.

| Motor | Silent install |
|---|---|
| Windows Installer (MSI) | `msiexec /i "{file}" /qn` |
| Inno Setup | `"{file}" /VERYSILENT /SUPPRESSMSGBOXES /NORESTART /SP-` |
| NSIS | `"{file}" /S` |
| InstallShield | `"{file}" /s /v"/qn"` |
| WiX Burn | `"{file}" /quiet` |
| Advanced Installer | `"{file}" /exenoui /qn` |

- **NSIS.** `/S` skal være stort. `/D=` skal stå sidst og uden anførselstegn.
- **Inno Setup.** `/S` er ikke silent-switchen. Brug `/VERYSILENT`. `/NORESTART` hører til Inno og bliver stående.
- **InstallShield.** `/qn` sendes videre med `/v"/qn"`. Et ældre InstallScript-setup kan kræve en optaget `setup.iss` (`/r`, derefter `/s /f1`).
- **WiX Burn.** `/quiet` er silent-switchen. `/install` er allerede standard og bliver ikke tilføjet.
- **Advanced Installer.** `/S` og `/VERYSILENT` giver typisk *Invalid command line*.

Foreslåede switche under kommandoen er valgfri flag fra filen eller motoren, for eksempel en Inno-log eller MSI `ALLUSERS=1`. Sæt flueben for at tage et flag med. `/install` og `/norestart` tilbydes ikke. Hele listen står i [referencen](reference.md).

## Når filen kun er en wrapper

En 7-Zip SFX, WinRAR SFX, IExpress-pakke eller nogle self-extractors har ingen pålidelig silent-linje i sig selv. InstallScout pakker det indre setup ud lokalt og bruger den kommando. Inno Setup, NSIS, Wacom og Dell Display and Peripheral Manager bliver ikke pakket ud.

En ydre `/sAll`, `--silent` eller `/silent` beholdes. En self-extractor i Adobe-stil bliver `"{file}" /sAll /rs /rps /msi /quiet`, når `/sAll` eller `/rps` findes i filen.

## Hvad kommandoen ikke beviser

Linjen er motorens silent-form plus flag læst i filen. Det er ikke en prøveinstallation. Gennemgå den, og prøv pakken i en VM, før du ruller den ud.

Leverandørindstillinger som licensserver eller sprog slås ikke op i et katalog over alle apps. ClickOnce har typisk ingen pålidelig silent-switch til en maskininstallation.

## Ofte stillede spørgsmål

### Hvordan finder jeg silent-switche til en app?

Træk installeren ind på InstallScout, og klik Analysér. Programmet læser filen, navngiver motoren og skriver silent-kommandoen. Du behøver ikke køre setup, og du behøver ikke søge på appens navn.

### Hvad er silent-switchen til MSI, Inno, NSIS og InstallShield?

MSI bruger `msiexec /i "{file}" /qn`. Inno Setup bruger `/VERYSILENT /SUPPRESSMSGBOXES /NORESTART /SP-`. NSIS bruger `/S` med stort S. InstallShield bruger `/s /v"/qn"`.

### Bliver installeren kørt, når switchene findes?

Nej. InstallScout læser filen. Installeren startes ikke.

### Hvad hvis setup.exe /? ikke viser noget?

Mange setup-programmer skriver ingen hjælp. Motoren har stadig en kendt silent-form. InstallScout matcher mærker i filen og bruger den form. Når den ydre fil kun er en wrapper, pakkes det indre setup ud, og de switche bruges.

### Kan den samme kommando bruges i Intune?

Ja. Efter Analysér bygger **Intune-pakke** en lokal `.intunewin`. **Upload til Intune** sender Win32-appen med install, uninstall, detection og et logo. Det kræver ikke et Azure-login at finde switchene.
