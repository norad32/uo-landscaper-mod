---
title: Installation
layout: home
nav_order: 1
---

# Installation

Follow these steps to set up UO Landscaper Mod:

1. Install UO Landscaper
   If you haven't already, download and install UO Landscaper from one of the provided sources.
2. Remove System, Transition and Statics folder
   Open Command Prompt and execute the following commands to remove the `System`, `Transition`, and `Statics` folders:

```bash
cd "C:\Path\To\UO_Landscaper"
rd rmdir /s /q "Data\System" && rd /s /q "Data\Transition" && rd /s /q "Data\Statics"
```

3. Clone repo
   Clone the UO Landscaper Mod repository to your local machine:

```bash
git clone https://github.com/norad32/uo-landscaper-mod.git
```

This will create a uo-landscaper-mod folder with all the necessary data files.

4. Integrate the Mod
   Copy the data files from the cloned repository into the UO Landscaper's data directory:

```bash
xcopy /E /I "uo-landscaper-mod\Data" "C:\Path\To\UO_Landscaper\Data"
```

_Ensure you replace C:\Path\To\UO_Landscaper with your actual installation path._
