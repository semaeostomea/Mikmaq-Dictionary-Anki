# Mi'kmaq dictionary files and Anki deck generator
#### Generated files can be found <ins>[here](./files/)</ins>
This repository contains scripts to generate a Mi'kmaq Anki deck from a JSON file that is based on the [Mi'kmaq Online Talking Dictionary](https://mikmaqonline.org/).

## How to Use
The generated files are updated regularly, this includes the Anki deck [`Mikmaq.apkg`](./deck_output/Mikmaq.apkg) as well as the dictionary file [`js-mikmaq_dict.json`](./files/js-mikmaq_dict.json) and all files needed to generate them if necessary.<br>
You'll need [node.js](https://nodejs.org/) to generate dictionary data, and [python](https://www.python.org/) to generate the Anki deck. Module/package requirements are found in [`package.json`](./package.json) and [`requirements.txt`](./requirements.txt) respectively.

### Anki deck
#### You can also find the deck on [AnkiWeb](https://ankiweb.net/shared/info/1341925420)
The deck does not include any local audio files — instead, it loads the audio files directly from the online dictionary. This keeps the file size small and sync/loading times short, but limits offline-usage.<br>
There are also known issues with alternative grammar forms not being formatted correctly — due to inconsistent formatting on the website. These grammar forms are only included as additional info in one card type.
#### Generating
If you want to change the makeup of the deck, edit [`create_deck.py`](./create_deck.py) and/or the files in [`note_types`](./files/note_types/), to change the content (i.e. words and sentences) manually (or programmatically), edit [`js-mikmaq_dict.json`](./files/js-mikmaq_dict.json). To update the deck file afterwards, run [`update.sh deck`](./update.sh)
#### Note Types
You can get the source code for the note types [here](./files/note_types/) without installing the deck.<br>
There are currently 2 note types with 1 and 3 card types respectively:
* \[all info\] Mi'kmaq>English
* \[misc\] Mi'kmaq
    1. \[listening\] Mi'kmaq
    2. Mi'kmaq>English
    3. English>Mi'kmaq

### Updating files
All required scripts are called by [`update.sh`](./update.sh), which takes one argument: `deck`, `data` or `all`.<br>You can edit [`compiledict.cjs`](./compiledict.cjs) to change how [`js-mikmaq_dict.json`](./files/js-mikmaq_dict.json) is generated.
#### `update.sh deck`
updates [`Mikmaq.apkg`](./files/deck_output/Mikmaq.apkg)
#### `update.sh data`
will ask for the type of source to use, please only use `files` — more info [down here](#html-source-files).<br>
If `web` is chosen, the online dictionary is re-scraped and all source files updated. This operation can be resumed if an error occured.<br>
Will update [`js-mikmaq_dict.json`](./files/js-mikmaq_dict.json) regardless of which option is chosen.
#### `update.sh all`
will first update [`js-mikmaq_dict.json`](./files/js-mikmaq_dict.json) (as [above](#updatesh-data)) and proceed to update [`Mikmaq.apkg`](./files/deck_output/Mikmaq.apkg) unless an error occured.
### HTML source files
Out of respect for the owners of the [Mi'kmaq Online Talking Dictionary](https://mikmaqonline.org/), the source files should not be updated by you unless necessary — as long as the files [here](./files/html_files/) are up-to-date, please use them as your source. Updating these requires fetching a few thousand pages.

## License
The [Mi'kmaq Online Talking Dictionary](https://mikmaqonline.org/) that serves as a source for the dictionary data is licensed under the [Creative Commons Attribution-NonCommercial 4.0 International license](https://creativecommons.org/licenses/by-nc/4.0/deed.en), which extends to the modified data in the dictionary and anki deck files.

The font used in the Anki notes is [Noto Sans](https://fonts.google.com/noto/specimen/Noto+Sans), which is licensed under the [SIL Open Font License, Version 1.1](https://openfontlicense.org/open-font-license-official-text/)

The rest of the project (i.e. the source code to generate the modified data) is licensed under the [EUPL](https://eupl.eu/1.2/en/)