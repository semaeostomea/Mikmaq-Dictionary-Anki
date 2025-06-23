import traceback
import sys

try:

    import random
    import genanki
    import os
    import json
    import re
    from tqdm import tqdm

    with open("files/all_words.json", "r", encoding="utf-8") as f:
        all_words = json.load(f)

    def compile_wordbank():
        wordbank = ",".join([f'"{all_words[random.randrange(len(all_words))]}"' for x in range(20)])
        return f"[{wordbank}]"

    class MyNote(genanki.Note):
        def __init__(self, model=None, fields=None, sort_field=None, tags=None, guid=None, due=0):
            self._model_name = model
            model = anki_model.get_type(model)
            super().__init__(model, fields, sort_field, tags, guid, due)

        @property
        def guid(self):
            if self._model_name == "misc":
                return genanki.guid_for(self.fields[0], self.fields[1], *self.fields[-3:-1])
            else:
                return genanki.guid_for(self.fields[0], self.fields[1])

    class NoteType():
        def __init__(self):
            path = "anki_ids/anki_model_ids.json"
            if os.path.isfile(path):
                with open(path, "r", encoding="utf-8") as f:
                    self.model_ids = json.load(f)
            else:
                self.model_ids = {
                    "all_info": random.randrange(1 << 30, 1 << 31),
                    "misc": random.randrange(1 << 30, 1 << 31)
                }
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(self.model_ids, f, ensure_ascii=False, indent=4)

            self.templates= {}
            
            self._load_templates()

        def _load_templates(self):
            for root, subdirs, files in os.walk("note_types"):
                for file in files:
                    path = f"{root.replace('\\', '/')}/{file}"
                    key = file.split(".")[0]

                    with open(path, "r", encoding="utf-8") as f:
                        self.templates[key] = f.read()

        def _type_misc(self):
            anki_model = genanki.Model(
                model_id = self.model_ids["misc"],
                name = "[misc] Mi'kmaq",
                fields = [
                    {"name": "Mikmaq"}, 
                    {"name": "English"}, 
                    {"name": "MikmaqAudio"},
                    {"name": "AltButtons"},
                    {"name": "POS"},
                    {"name": "PronunciationGuide"},
                    {"name": "WithFromMikmaq"},
                    {"name": "WithListening"},
                    {"name": "SourceLink"}],
                templates = [
                    {
                        "name": "[listening] Mi'kmaq",
                        "qfmt": self.templates["listening-mikmaq_front"],
                        "afmt": self.templates["listening-mikmaq_back"],
                    },
                    {
                        "name": "Mi'kmaq>English",
                        "qfmt": self.templates["mikmaq-english_front"],
                        "afmt": self.templates["mikmaq-english_back"],
                    },
                    {
                        "name": "English>Mi'kmaq",
                        "qfmt": self.templates["english-mikmaq_front"],
                        "afmt": self.templates["english-mikmaq_back"],
                    }
                ],
                css=self.templates["misc_style"],
            )
            return anki_model

        def _type_all_info(self):
            anki_model = genanki.Model(
                model_id = self.model_ids["all_info"],
                name = "[all info] Mi'kmaq>English",
                fields = [
                    {"name": "Mikmaq"},
                    {"name": "English"},
                    {"name": "MikmaqAudio"},
                    {"name": "PronunciationGuide"},
                    {"name": "Meanings"},
                    {"name": "POS"},
                    {"name": "ExampleSentence"},
                    {"name": "ExampleAudio"},
                    {"name": "GrammarForms"},
                    {"name": "English_2"},
                    {"name": "Meanings_2"},
                    {"name": "POS_2"},
                    {"name": "ExampleSentence_2"},
                    {"name": "ExampleAudio_2"},
                    {"name": "GrammarForms_2"},
                    {"name": "English_3"},
                    {"name": "Meanings_3"},
                    {"name": "POS_3"},
                    {"name": "ExampleSentence_3"},
                    {"name": "ExampleAudio_3"},
                    {"name": "GrammarForms_3"},
                    {"name": "SourceLink"}],
                templates = [
                    {
                        "name": "[all info] Mi'kmaq>English",
                        "qfmt": self.templates["all-info_front"],
                        "afmt": self.templates["all-info_back"],
                    }
                ],
                css = self.templates["all-info_style"],
            )
            return anki_model

        def get_type(self, name):
            if name == "misc":
                return self._type_misc()
            elif name == "all_info":
                return self._type_all_info()

    def createDeck(deck_name:str, note_list:list):
        path = f'anki_ids/{re.sub(r"[\W]", "_", deck_name)}_deck_id.txt'
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                deck_id = int(f.read())
        else:
            deck_id = random.randrange(1 << 30, 1 << 31)
            with open(path, "w", encoding="utf-8") as f:
                f.write(str(deck_id))

        anki_deck = genanki.Deck(deck_id, deck_name)
        anki_notes = []

        for note in note_list:
            anki_note = MyNote(
                model=note["note_type"],
                fields=note["fields"],
                tags=note["tags"]
            )
            anki_notes.append(anki_note)

        # random.shuffle(anki_notes)

        for anki_note in anki_notes:
            anki_deck.add_note(anki_note)

        return anki_deck

    def detailed_fields(word, entry):
        detailed = {
            "Mikmaq": word,
            "English": entry["translations"][0]["translation"],
            "MikmaqAudio": entry["recordings"][random.randrange(len(entry["recordings"]))],
            "PronunciationGuide": entry["pronunciation"],
            "Meanings": f'<ul>\n{"\n".join([f"  <li>{mean}</li>" for mean in entry["translations"][0]["meanings"]])}\n</ul>',
            "POS": entry["translations"][0]["pos"],
            "ExampleSentence": "",
            "ExampleAudio": "",
            "GrammarForms": "",
            "English_2": "",
            "Meanings_2": "",
            "POS_2": "",
            "ExampleSentence_2": "",
            "ExampleAudio_2": "",
            "GrammarForms_2": "",
            "English_3": "",
            "Meanings_3": "",
            "POS_3": "",
            "ExampleSentence_3": "",
            "ExampleAudio_3": "",
            "GrammarForms_3": "",
            "SourceLink": entry["source"]
        }
        len_examples = len(entry["translations"][0]["sentences"])
        if len_examples > 0:
            example = entry["translations"][0]["sentences"][random.randrange(len_examples)]
            detailed["ExampleAudio"] = example["recording"]
            detailed["ExampleSentence"] = f"""<dl>
    <dt>{example['text']}</dt>
    <dt>{example['translation']}</dt>
    </dl>"""
        
        grammar_forms = []
        for form in entry["translations"][0]["altforms"]:
            grammar_forms.append(f"""  <li>
        <dl>
        <dt>{form['text']}</dt>
        <dt>{form['translation']}</dt>
        <dd>{form['info']}</dd>
        </dl>
    </li>""")
        if len(grammar_forms) > 0:
            detailed["GrammarForms"] = f"<ul>\n{'\n'.join(grammar_forms)}\n</ul>"
        
        try:
            second = entry["translations"][1]
        except:
            pass
        else:
            detailed["English_2"] = second["translation"]
            detailed["Meanings_2"] = f'<ul>\n{"\n".join([f"  <li>{mean}</li>" for mean in second["meanings"]])}\n</ul>'
            detailed["POS_2"] = second["pos"]
            len_examples = len(second["sentences"])
            if len_examples > 0:
                example = second["sentences"][random.randrange(len_examples)]
                detailed["ExampleAudio_2"] = example["recording"]
                detailed["ExampleSentence_2"] = f"""<dl>
    <dt>{example['text']}</dt>
    <dt>{example['translation']}</dt>
    </dl>"""
            
            grammar_forms = []
            for form in second["altforms"]:
                grammar_forms.append(f"""  <li>
        <dl>
        <dt>{form['text']}</dt>
        <dt>{form['translation']}</dt>
        <dd>{form['info']}</dd>
        </dl>
    </li>""")
            if len(grammar_forms) > 0:
                detailed["GrammarForms_2"] = f"<ul>\n{'\n'.join(grammar_forms)}\n</ul>"
        
        try:
            third = entry["translations"][2]
        except:
            pass
        else:
            detailed["English_3"] = third["translation"]
            detailed["Meanings_3"] = f'<ul>\n{"\n".join([f"  <li>{mean}</li>" for mean in third["meanings"]])}\n</ul>'
            detailed["POS_3"] = third["pos"]
            len_examples = len(third["sentences"])
            if len_examples > 0:
                example = third["sentences"][random.randrange(len_examples)]
                detailed["ExampleAudio_3"] = example["recording"]
                detailed["ExampleSentence_3"] = f"""<dl>
    <dt>{example['text']}</dt>
    <dt>{example['translation']}</dt>
    </dl>"""
            
            grammar_forms = []
            for form in third["altforms"]:
                grammar_forms.append(f"""  <li>
        <dl>
        <dt>{form['text']}</dt>
        <dt>{form['translation']}</dt>
        <dd>{form['info']}</dd>
        </dl>
    </li>""")
            if len(grammar_forms) > 0:
                detailed["GrammarForms_3"] = f"<ul>\n{'\n'.join(grammar_forms)}\n</ul>"

        return list(detailed.values())

    def misc_fields(mikmaq, english, sourcelink, mikmaqaudio="", altbuttons="", pos="", pronunciationguide="", withfrommikmaq="true", withlistening=""):
        misc = {
            "Mikmaq": mikmaq, 
            "English": english, 
            "MikmaqAudio": mikmaqaudio, 
            "AltButtons": altbuttons, 
            "POS": pos, 
            "PronunciationGuide": pronunciationguide, 
            "WithFromMikmaq": withfrommikmaq,
            "WithListening": withlistening,
            "SourceLink": sourcelink
        }

        return list(misc.values())

    anki_model = NoteType()

    # deck_list = [createDeck("Mi'kmaq<>English", [])]
    # subdecks = {
    #     "Mi'kmaq<>English::Detailed Cards": [],
    #     "Mi'kmaq<>English::Miscellaneous": []
    # }

    note_list = []

    with open("files/js-mikmaq_dict.json", "r", encoding="utf-8") as f:
        dictionary = json.load(f)

    i = 0
    for word, entry in tqdm(dictionary.items()):
        # if i >= 100:
        #     break
        i += 1
        sourceLink = entry["source"]
        tags = [tag.replace(" ", "_") for tag in entry["categories"]]
        recording = entry["recordings"][random.randrange(len(entry["recordings"]))]
        # subdecks["Mi'kmaq<>English::Detailed Cards"].append({
        note_list.append({
            "note_type": "all_info",
            "fields": detailed_fields(word, entry),
            "tags": tags
        })


        if len(entry["translations"]) > 1:
            t = ",".join([f'["{t["translation"]}", "{t["pos"]}"]' for t in entry["translations"][1:]])
            withListening = f"[{t}]"
        else:
            withListening = "[]"

        for trans in entry["translations"]:
            # subdecks["Mi'kmaq<>English::Miscellaneous"].append({
            note_list.append({
                "note_type": "misc",
                "fields": misc_fields(word, trans["translation"], sourceLink, recording, compile_wordbank(), trans["pos"], entry["pronunciation"], "", withListening),
                "tags": tags
            })
            withListening = ""
        
            for sentence in trans["sentences"]:
                # subdecks["Mi'kmaq<>English::Miscellaneous"].append({
                note_list.append({
                    "note_type": "misc",
                    "fields": misc_fields(sentence["text"], sentence["translation"], sourceLink, sentence["recording"], compile_wordbank(), withlistening="[]"),
                    "tags": tags
                })

    # for k, v in subdecks.items():
    #     deck_list.append(createDeck(k, v))
    print("creating deck...")
    deck = createDeck("Mi'kmaq<>English", note_list)

    package = genanki.Package(deck, media_files=['files/_notoSans.ttf'])
    package.write_to_file(f'files/deck_output/Mikmaq.apkg')
    input("deck created successfully, press enter to open directory")
    os.startfile(".")
except Exception as error:
    traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
    input("press enter to close")