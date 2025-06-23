const fs = require('fs/promises');
const readline = require('readline');
const jsdom = require("jsdom");
const { JSDOM } = jsdom;

const htmlFilePath = "files/html_files";
const dictFilePath = "files/js-mikmaq_dict.json";
const filenamePath = "files/filename_map.json";
const urlSourcePath = "files/dictionary_entries_urls.json";
const cliArgs = process.argv.slice(2);
let filenameMap;
let scrape = false;

if (cliArgs.length > 0) {
    if (cliArgs[0] == "scrape") {
        scrape = true;
    };
};

const rl = readline.createInterface({ input: process.stdin, output: process.stdout });

rl.on('SIGINT', async () => {
    rl.close();
    throw new Error("KeyboardInterrupt");
});

function get_input(query) {
    // const rl = readline.createInterface({
    //     input: process.stdin,
    //     output: process.stdout,
    // });

    return new Promise(resolve => rl.question(query, answer => {
        // rl.close();
        resolve(answer);
    }))
}

function randint(max=1 << 30) {
  return Math.floor(Math.random() * max);
}

function sleep(pause) {
    return new Promise(resolve => {
        setTimeout(() => {resolve(true);}, pause);
    });
}

function sortDict(obj) {
    let keys = Object.keys(obj);
    keys.sort();
    let newObj = new Object();
    for (let key of keys) {
        newObj[key] = obj[key];
    };
    return newObj
};

async function loadFilenameMap() {
    let obj = {
        "map": new Object()
    };
    try {
        obj = await getDictObj(filenamePath)
    } catch {};
    filenameMap = obj;
    filenameMap.keys = Object.keys(obj.map);
    filenameMap.values = Object.values(obj.map);
};

async function saveFilenameMap() {
    if (filenameMap) {
        let json = JSON.stringify(filenameMap, null, 4);
        await fs.writeFile(filenamePath, json, 'utf8');
    };
};

/**
 * @param {HTMLElement} element
 */
async function pushEntryData(entryData, element, baseURI) {
    translationData = {
        "translation": null,
        "pos": null,
        "meanings": new Array(),
        "sentences": new Array(),
        "altforms": new Array()
    };
    translationData.translation = element.querySelector("div:first-child>b[data-title='Translation:']").nextSibling.textContent.replace(/[_\s]+/g, " ").trim();
    try {
        translationData.pos = element.querySelector("b[data-title='Part of Speech:']").nextSibling.textContent.replace(/[_\s]+/g, " ").trim();
    } catch {
        translationData.pos = ""
    };
    if (!entryData.pronunciation) {
        try {
            entryData.pronunciation = element.querySelector("b[data-title='Pronunciation Guide:']").nextSibling.textContent.replace(/[_\s]+/g, " ").trim();
        } catch {
            entryData.pronunciation = ""
        }
    };
    for (let meaningElem of element.querySelector("b[data-title='Meanings:']").nextSibling.querySelectorAll("li")) {
        translationData.meanings.push(meaningElem.textContent.replace(/[_\s]+/g, " ").trim());
    };
    exampleArray = element.querySelectorAll("b[data-title='Example of word used in a sentence:']+ul>li:has(div)");
    for (let exampleElem of exampleArray) {
        let exampleObj = {
            "text": exampleElem.querySelector("b[data-title='Text:']").nextSibling.textContent.replace(/[_\s]+/g, " ").trim(),
            "translation": exampleElem.querySelector("b[data-title='Translation:']").nextSibling.textContent.replace(/[_\s]+/g, " ").trim(),
            "recording": new URL(exampleElem.querySelector("b[data-title='Recording:']").nextSibling.getAttribute("href"), baseURI).href
        };
        translationData.sentences.push(exampleObj);
    };
    altformArray = element.querySelectorAll("b[data-title='Alternate Grammatical Forms:']+ul>li");
    
    for (let altElem of altformArray) {
        try {
            form = altElem.textContent.split("--");
            altforms = {
                "text": form[0].replace(/[_\s]+/g, " ").trim(),
                "translation": form[1].replace(/[_\s]+/g, " ").trim(),
                "info": form[2].replace(/[_\s]+/g, " ").trim()
            };
            translationData.altforms.push(altforms);
        } catch (error) {
            // console.error(error);
        };
    };

    entryData.translations.push(translationData);
};

/**
 * @param {Window} window
 */
async function parseHTMLEntry(window) {
    let noRecordings = {
        entries: new Array()
    };
    let title = window.document.querySelector(".page-content>h1.entry-scope").textContent.replace(/[_\s]+/g, " ").trim();
    let baseURI = window.document.getElementById("sourceUrlElement").href
    if (!window.document.querySelector(".page-content>div:nth-child(2)>:first-child").textContent.trim().toLowerCase().startsWith("recordings")) {
        // noRecordings.entries.push({word: baseURI});
        console.log({word: baseURI});
        return
    };
    let entryData = {
        "source": baseURI,
        "recordings": new Array(),
        "pronunciation": null,
        "translations": new Array(),
        "categories": new Array()
    };
    for (let x of window.document.querySelectorAll('b')) {
        x.setAttribute('data-title', x.textContent.trim())
    };

    for (let recordingElem of window.document.querySelectorAll(".page-content>div:nth-child(2)>ul>li>a")) {
        let absolute_href = new URL(recordingElem, baseURI).href
        entryData.recordings.push(absolute_href)
    };

    let translationList = window.document.querySelectorAll(".page-content>ul>li");
    if (translationList.length > 0) {
        for (let element of translationList) {
            await pushEntryData(entryData, element, baseURI);
        };
    } else {
        await pushEntryData(entryData, window.document.querySelector(".page-content"), baseURI)
    };

    for (let catElem of window.document.querySelectorAll(".page-content>h3")) {
        let match = catElem.textContent.match(/"[\w ]+"/);
        if (match.length > 0) {
            let category = match[0].replace(/[_\s]+/g, " ").replace(/"/g, "").trim();
            entryData.categories.push(category);
        };
    };
    return {
        "title": title,
        "data": entryData
    }
};

async function getHTMLEntry(fileName) {
    let file = await fs.readFile(`${htmlFilePath}/${fileName}`, 'utf8');
    let window = new JSDOM(file).window;
    let entryObj = await parseHTMLEntry(window);
    return entryObj
};

async function saveHTMLEntry(baseURI) {
    let response = await fetch(baseURI)
    // await fs.writeFile('/html_files2/test.html', response.body);
    let content = await response.text();
    let window = new JSDOM(content).window;
    let title = window.document.querySelector(".page-content>h1.entry-scope").textContent.replace(/[_\s]+/g, " ").trim();
    
    let sourceElem = window.document.createElement("a");
    sourceElem.id = "sourceUrlElement";
    sourceElem.setAttribute("href", baseURI);
    window.document.body.appendChild(sourceElem);

    if (!filenameMap) {
        await loadFilenameMap();
    };

    let fileName;

    if (filenameMap.keys.includes(title)) {
        fileName = filenameMap.map[title];
    } else {
        fileName = randint();
        while (filenameMap.values.includes(fileName)) {
            fileName = randint();
        }; 
        filenameMap.map[title] = fileName;
        filenameMap.keys.push(title);
        filenameMap.values.push(fileName);
    };

    await fs.writeFile(`${htmlFilePath}/${fileName}.html`, window.document.documentElement.outerHTML, 'utf8');
    let entryObj = await parseHTMLEntry(window);
    return entryObj
};

async function saveUrls(baseURI="https://mikmaqonline.org/all-words.html") {
    let response = await fetch(baseURI);
    // await fs.writeFile('./test.html', response.body);
    let content = await response.text();
    let window = new JSDOM(content).window;
    let obj = {
        urls: new Array()
    };
    for (let entry of window.document.querySelectorAll(".page-content ul>li>a:first-child")) {
        obj.urls.push(new URL(entry.href, baseURI).href);
    };
    let json = JSON.stringify(obj, null, 4);
    await fs.writeFile(urlSourcePath, json, 'utf8');
    console.log("update URL source file");
};

async function getUrls() {
    let file = await fs.readFile(urlSourcePath, 'utf8')
    let obj = JSON.parse(file);
    return obj.urls
};

async function getHtmlFiles(path=htmlFilePath) {
    let files = await fs.readdir(path);
    return files
};

async function getDictObj(path) {
    let file = await fs.readFile(path, 'utf8')
    let obj = JSON.parse(file);
    return obj
};

async function saveDictObj(obj, path) {
    let json = JSON.stringify(sortDict(obj), null, 4);
    await fs.writeFile(path, json, 'utf8');
};

async function compileDict(resume=false, useFiles=false) {
    let dictObj;
    if (resume && !useFiles) {
        dictObj = await getDictObj(dictFilePath);
    } else {
        dictObj = new Object();
    };
    
    let sourceType;
    let entrySourceList;
    if (useFiles) {
        entrySourceList = await getHtmlFiles();
        sourceType = "HTML files";
    } else {
        entrySourceList = await getUrls();
        sourceType = "URLs";
    };
    let start = Object.keys(dictObj).length
    console.log(`${entrySourceList.length} headwords\nskipping ${start}\nsource: ${sourceType}`)
    i = 0
    try {
        for (let entrySource of entrySourceList.slice(start)) {
            if (i % 500 == 0) {
                console.log(`${i} headwords processed`);
            }
            i ++
            let entryObj
            if (useFiles) {
                entryObj = await getHTMLEntry(entrySource);
            } else {
                entryObj = await saveHTMLEntry(entrySource);
                await sleep(0.1);
            };
            if (entryObj) {
                dictObj[entryObj.title] = entryObj.data;
            } else {
                console.log(entrySource);
            };
        };
    } catch (error) {
        console.error(error);
        console.log("Exiting loop prematurely");
    };
    console.log(`${i} headwords processed\n${Object.keys(dictObj).length} keys in dictionary`);
    await saveDictObj(dictObj, dictFilePath);
    await saveFilenameMap();
};

async function saveWordlist() {
    let obj = await getDictObj(dictFilePath);
    let words = new Set(Object.keys(obj));
    for (let entry of Object.values(obj)) {
        for (let t of entry["translations"]) {
            for (let s of t["sentences"]) {
                for (let word of s["text"].replace(/[^\w']+/g, " ").trim().split(" ")) {
                    words.add(word.trim().toLowerCase());
                };
            };
        };
    };
    let json = JSON.stringify(Array.from(words).sort(), null, 4)
    await fs.writeFile("files/all_words.json", json, 'utf8');
};

async function main(scrape) {
    let resume = false;
    let useFiles = false;
    let input = "none";

    if (!scrape) {
        while (!["web", "files"].includes(input)) {
            input = await get_input('\
    To compile the dictionary from the web, input [web], this will also save/update all HTML source files.\n\
    To compile the dictionary from previously saved source files, input [files].\n\n\
    Please respond with [web] or [files]\n');
        };
        if (input == "web") {
            while (!["y", "n"].includes(input.toLowerCase())) {
                input = await get_input('Do you want to resume a previously aborted compilation?\n\nPlease respond with [Y] or [N]\n');
            };
            if (input == "y") {
                resume = true;
            };
        } else if (input == "files") {
            useFiles = true;
        };
    };

    let start = Date.now();
    if (!resume && !useFiles) {
        await saveUrls();
    };
    await compileDict(resume, useFiles);
    await saveWordlist();
    let elapsedTime = Date.now() - start;
    let elapsedSeconds = Math.floor(elapsedTime / 1000);
    console.log(`Elapsed time in seconds: ${elapsedSeconds}\nin minutes: ${Math.ceil(elapsedSeconds / 60)}`);
    rl.close();
    process.exit();
};

main(scrape);