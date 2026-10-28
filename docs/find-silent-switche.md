# Find silent-switche og upload til Intune

For at finde silent-switchene til en app giver du InstallScout installeren. Programmet læser EXE-, MSI-, COM- eller MSIX-filen, navngiver motoren og skriver silent-kommandoen. Installeren bliver ikke kørt. Ud fra den kommando bygger **Intune-pakke** en lokal `.intunewin`, og **Upload til Intune** sender Win32-appen.

En silent-switch er et argument, der får setup til at køre færdigt uden dialoger. MSI-filer deler parametre til `msiexec`. EXE-filer gør ikke. Argumenterne afhænger af motoren, der har bygget filen: Inno Setup, NSIS, InstallShield, WiX Burn og de øvrige nedenfor.

Version **1.8.71**. Alle motorer, afinstallation og valgfri flag står i [reference.md](reference.md). Vejen fra kommandoen til en Win32-app i Intune står i [vejledning.md](vejledning.md).

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

## Upload til Intune

1. **Analysér** — InstallScout skriver silent-kommandoen. Installeren bliver ikke kørt.
2. **Intune-pakke** — en lokal `.intunewin` med install, uninstall og detection.
3. **Upload til Intune** — Win32-appen, med System eller User, et logo og valgfri supersedence.

Det kræver ikke et Azure-login at finde switchene. Upload gør. Trinene i vinduet står i [vejledningen](vejledning.md).

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

Linjen er motorens silent-form plus flag læst i filen. Det er ikke en prøveinstallation. **Prøv i Sandbox** er valgfri. Når knappen vises, kører kommandoen i Windows Sandbox, ikke på denne pc. Du kan pakke og uploade, mens testen kører, og du kan stadig prøve pakken i en VM, før du ruller den ud.

Leverandørindstillinger som licensserver eller sprog slås ikke op i et katalog over alle apps. ClickOnce har typisk ingen pålidelig silent-switch til en maskininstallation.

## Ofte stillede spørgsmål

### Hvordan finder jeg silent install-kommandoen?

Træk installeren ind på InstallScout, og klik Analysér. Programmet læser filen, navngiver motoren og skriver silent-kommandoen. Du kører ikke setup, og du slår ikke appen op på navn.

### Hvordan installerer jeg en EXE silently?

Kommandoen afhænger af motoren. Inno Setup bruger `/VERYSILENT`. NSIS bruger `/S`. InstallShield bruger `/s /v"/qn"`. En MSI bruger `msiexec /i "{file}" /qn`. WiX Burn bruger `/quiet`. InstallScout skriver linjen til den fil, du giver den.

### Hvordan uploader jeg en EXE til Intune?

Klik Analysér, derefter Intune-pakke, og derefter Upload til Intune. Det gemmer en lokal `.intunewin` og sender Win32-appen med install, uninstall, detection og et logo. Du kører ikke selv Win32 Content Prep Tool.

### Hvad er silent-switchen til MSI, Inno, NSIS og InstallShield?

MSI bruger `msiexec /i "{file}" /qn`. Inno Setup bruger `/VERYSILENT /SUPPRESSMSGBOXES /NORESTART /SP-`. NSIS bruger `/S` med stort S. InstallShield bruger `/s /v"/qn"`.

### Bliver installeren kørt, når switchene findes?

Nej. InstallScout læser filen. Installeren startes ikke. **Prøv i Sandbox** er en særskilt knap. Den kører kommandoen kun inde i Windows Sandbox, og kun når du klikker.

### Hvordan tester jeg silent-kommandoen uden at installere på denne pc?

Klik **Prøv i Sandbox** efter Analysér, når Windows Sandbox er installeret. Testen er valgfri. Kommandoen og detection-scriptet kører i en sandbox, der kasseres bagefter, og du kan pakke og uploade, mens den kører. Denne pc ændres ikke. Knappen er skjult, når Sandbox ikke er installeret. Du kan stadig teste pakken i en VM.

### Hvad hvis setup.exe /? ikke viser noget?

Mange setup-programmer skriver ingen hjælp. Motoren har stadig en kendt silent-form. InstallScout matcher mærker i filen og bruger den form. Når den ydre fil kun er en wrapper, pakkes det indre setup ud, og de switche bruges.
