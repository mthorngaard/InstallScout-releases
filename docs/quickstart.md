# InstallScout – quick start

Version **1.8.49**. Fra en installer til en Win32-app i Intune. Programmet kører ikke installeren.

Den fulde vejledning er [vejledning.md](vejledning.md). Motorer, CLI og Graph står i [reference.md](reference.md). Word: [InstallScout-quickstart.docx](InstallScout-quickstart.docx).

## 1. Start

Dobbeltklik `InstallScoutPortable.exe`. Der skal ikke installeres noget. Sproget er English. Skift til Dansk øverst til højre. Træk en installer ind på vinduet, eller brug **Tilføj filer…**.

Downloadet er **ikke codesigned**. Windows eller virksomhedens sikkerhed kan advare eller blokere det. Vælg Behold / Kør alligevel, bed IT om at tillade filen, eller prøv den i en VM eller Windows Sandbox uden de politikker.

Vil du have den i Start-menuen, så kør `portable\Install.bat`. Den portable exe bliver liggende og kan stadig kopieres for sig selv.

## 2. Analysér

1. **Tilføj filer…** og vælg en EXE, MSI, COM eller MSIX.
2. Klik **Analysér**.

Den grønne linje er silent-kommandoen. Under den kan der ligge **Foreslåede switche**. Sæt flueben for at tage en switch med, og fjern det for at tage den ud. `/install` og `/norestart` sættes ikke på automatisk. Inno beholder `/NORESTART`.

Ret linjen, eller skriv et ekstra flag under **Ekstra switche** og klik **Tilføj**. Test kommandoen i en VM, før du ruller den ud.

## 3. Pak

Klik **Intune-pakke…** og vælg en mappe. Der gemmes en `.intunewin`, PSADT-kilden og `Detection.ps1`.

**Upload til Intune** er grå, indtil pakken findes. Ændrer du kommandoen bagefter, skal pakken laves igen.

## 4. Upload

Klik **Upload til Intune…**.

1. Ret **Navn i Intune**, hvis Company Portal skal hedde noget andet end produkt og version.
2. Lad **System** stå, medmindre appen er per bruger (typisk Squirrel).
3. Tjek logoet. En MSI har ofte intet ikon. Vælg en fil, indsæt et billede, eller fjern logoet.
4. Feltet viser én Edge-profil. Fold det ud for at vælge en anden, og klik **Log på Intune**. Vent til der står *Logget på som …*. Login er bundet til tenant og Client ID.
5. Vælg evt. ældre apps under supersedence. Ingenting er valgt på forhånd. **Update** installerer ovenpå. **Replace** afinstallerer først.
6. Klik **Upload**.

Krav: en konto der kan oprette Win32-apps (**Intune Administrator**, eller Intune-rollen **Application Manager**) og admin-consent for `DeviceManagementApps.ReadWrite.All`. InstallScout opretter ikke sin egen app.

## Samme løb fra kommandolinjen

```powershell
.\InstallScoutPortable.exe --cli .\setup.exe --intune C:\out\intune --publish-intune --icon .\logo.png
```

Uden `--icon` bruges ikonet fra EXE’en, hvis der er et.

## Detection, kort

Intune ser appen som installeret, når `Detection.ps1` skriver en linje og afslutter med kode 0.

- En MSI matches på product code.
- En EXE matches på navn, udgiver og version. Versionen skal være den samme eller nyere.
- `Logi Options+ Installer` matcher `Logi Options+`. `Logitech, Inc.` matcher `Logitech`.
