from config import load_config


#############################################################################
# MAIN
#############################################################################

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PDF Publisher AutoTranslate")
    parser.add_argument("--silent", "-s", action="store_true", help="Silent mode, minimal output")
    args = parser.parse_args()
    silent = args.silent

    (config, publications) = load_config()
    if not silent:
        print("Config loaded successfully!")
  # For every required language...

    # Check if translated file exists. Eg german translation: lecture.pptx --> lecture_de.pptx

    # If not, make an empty file for the translated version

    # Check if the original file is newer than the translation OR _if the file was just created_

    # If yes:

    # For every slide in the ORIGINAL VERSION:

    # Check for original_slide entry in sqlite3 database. If necessary INSERT filename, slide identifier, timestamp and hash

    # If hash doesn't match, UPDATE hash and timestamp

    # check translated slide from translated_slide table. If doesn't exist, create new slide, then INSERT filename, language, original slide identifier, translated slide identifier and timestamp

    # if timestamp of original slide is newer than translation, create a Gemini API call to translate all the texts of the slide. Then update the translated slide with the translated texts and UPDATE the SQLite table of the translated slide
# Check that the slide order is correct in the translated version in case of reorderings.
# Finally, detect any orphaned (deleted) slides that are no longer in the original but persist in the translation and delete those slides. 

