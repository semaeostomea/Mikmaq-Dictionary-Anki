#!/bin/bash

if [ $1 ]; then
    arg=""
    if [ $2 ]; then
        arg="$2"
    fi
    if [ "$1" = "deck" ] || [ "$1" = "data" ] || [ "$1" = "all" ]; then
        cd ..
        source venv/scripts/activate &&
        cd mikmaq &&
        if [ "$1" = "data" ] || [ "$1" = "all" ]; then
            printf -v date '%(%Y-%m-%d)T' -1 &&
            printf -v time '%(%Y-%m-%d_%H-%M)T' -1 &&
            targetfolder="files/previous_versions/${date}" &&
            sourcefile="files/js-mikmaq_dict.json" &&
            targetfile="${targetfolder}/${time}_js-mikmaq_dict.json" &&

            if [ ! -d "files/html_files" ]; then
                mkdir "files/html_files" &&
                echo "created folder for HTML source files"
            fi &&
            if [ -f "${sourcefile}" ]; then
                if [ ! -d "${targetfolder}" ]; then
                    mkdir "${targetfolder}"
                fi &&
                cp "${sourcefile}" "${targetfile}"
            fi &&
            node compiledict.cjs "$arg"
        fi &&
        if [ "$1" = "deck" ] || [ "$1" = "all" ]; then
            python create_deck.py
        fi
    else 
        echo "Please provid the type of update (deck, data, all) as the first argument"
    fi
else
    echo "Please provid the type of update (deck, data, all) as the first argument"
fi

read -p "
Press [enter] to exit"