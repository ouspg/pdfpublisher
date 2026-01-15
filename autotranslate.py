from config import load_config

def init_db():
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS original_slides (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            slide_id INTEGER,
            content_hash TEXT,
            last_updated REAL,
            UNIQUE(filename, slide_id)
        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS translated_slides (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            orig_slide_id INTEGER,
            lang_code TEXT,
            last_translated_hash TEXT,
            last_updated REAL,
            FOREIGN KEY(orig_slide_id) REFERENCES original_slides(id)
        )''')
        conn.commit()

#############################################################################
# TRANSLATION
#############################################################################

def process_pptx(file_path, language):
    print(f"Attempting to translate {file_path} to language: {language}")
    # Actual workhorse goes here
    
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
    init_db()
    
    #For every publication
    for pub in publications:
        if not silent:
            print(f"Tarkistetaan {config[pub]['coursename']} - käännökset: {config[pub]['translate_to']}") 
        # For every required language...
        courseObject = create_course_object(config, pub)
        for language in config[pub]['translate_to']:
            #Check headers etc.
            translate_pptx(Path(courseObject.course_slides_dir) / config["settings"]["headerfile"], language)
            translate_pptx(Path(courseObject.course_slides_dir) / config["settings"]["dividerfile"], language)
            translate_pptx(Path(courseObject.course_slides_dir) / config["settings"]["footerfile"], language)
            # Read the lecture names and topics from the configuration, error if not enough lecture definitions are found:
            try:
                for x in range(1, courseObject.lectures+1):
                    lecturelist = config[pub][str(x)].split(";")
                    lecture_name = lecturelist.pop(0).strip()
                    courseObject.add_lecture(lecture_name, x, [topic.strip() for topic in lecturelist])
            except KeyError:
                print(f"Lectures should be added as <lecturenumber = name, topic1, topic2 ... topicN> under publication {courseObject.name} in settings.ini")
                continue
            # Go through lectures
            for n in range(1, courseObject.lectures+1):
                for topic in courseObject.lecture_list[n-1].topic_list:
                    topic = f"{topic}.pptx"
                    translate_pptx(Path(config['settings']['lecture_slides_dir']) / topic, language)
                #publication-specific additional lecture slides
                translate_pptx(Path(config['settings']['lecture_slides_dir']) / topic, language)

