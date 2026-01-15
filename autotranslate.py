from config import load_config
import os
import sqlite3
import hashlib
import json
import time
from pathlib import Path
from pptx import Presentation
import google.generativeai as genai

def init_db():
    with sqlite3.connect("translations.db") as conn:
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

def get_slide_content(slide):
    """Extracts text and returns a hash for tracking changes."""
    texts = [shape.text.strip() for shape in slide.shapes if hasattr(shape, "text") and shape.text.strip()]
    content_str = "||".join(texts)
    content_hash = hashlib.md5(content_str.encode('utf-8')).hexdigest()
    return texts, content_hash

def sync_slide_order(orig_prs, trans_prs):
    """Reorders the translated slides to match the original slide sequence."""
    orig_order = [s.slide_id for s in orig_prs.slides]
    
    # Get the XML element for the slide ID list
    sldIdLst = trans_prs.slides._sldIdLst
    
    # Create a mapping of slide_id to its XML element
    id_to_element = {s.slide_id: s._element for s in trans_prs.slides}
    
    # Clear and re-append in the correct order
    for sid in orig_order:
        if sid in id_to_element:
            element = id_to_element[sid]
            sldIdLst.remove(element)
            sldIdLst.append(element)

def call_gemini_translate(model, texts, target_lang):
    if not texts: return []
    prompt = f"Translate the following Finnish strings to {target_lang}. Return ONLY a JSON list of strings in the exact same order:\n{json.dumps(texts)}"
    try:
        response = model.generate_content(prompt)
        raw = response.text.strip().strip('`').replace('json', '')
        return json.loads(raw)
    except Exception as e:
        print(f"Translation Error: {e}")
        return []

#############################################################################
# TRANSLATION
#############################################################################

def process_pptx(file_path, languages, model)
    path = Path(file_path)
    for lang in languages:
        print(f"Attempting to translate {file_path} to language: {language}")
        trans_path = path.parent / f"{path.stem}_{lang}{path.suffix}"
        # Check if translated file exists. Eg german translation: lecture.pptx --> lecture_de.pptx
        newfile = False
        if not trans_path.exists():
            newfile = True
            # If not, make a copy for the translated version
            Presentation(file_path).save(trans_path)

        # Check if the original file is newer than the translation OR _if the file was just created_    
        if path.stat().st_mtime < trans_path.stat().st_mtime or not newfile:
            continue

        # Process
        orig_prs = Presentation(file_path)
        trans_prs = Presentation(trans_path)

        # 1. Map slides by ID
        orig_slides = {s.slide_id: s for s in orig_prs.slides}
        trans_slides = {s.slide_id: s for s in trans_prs.slides}

        with sqlite3.connect("translations.db") as conn:
                cursor = conn.cursor()
                
                # 2. Update/Translate individual slides
                for sid, slide in orig_slides.items():
                    texts, current_hash = get_slide_content(slide)
                    
                    cursor.execute("SELECT id, content_hash FROM original_slides WHERE filename=? AND slide_id=?", (str(path), sid))
                    row = cursor.fetchone()
                    
                    if not row:
                        cursor.execute("INSERT INTO original_slides (filename, slide_id, content_hash, last_updated) VALUES (?, ?, ?, ?)",
                                       (str(path), sid, current_hash, time.time()))
                        db_orig_id = cursor.lastrowid
                    else:
                        db_orig_id, old_hash = row
                        if old_hash != current_hash:
                            cursor.execute("UPDATE original_slides SET content_hash=?, last_updated=? WHERE id=?", 
                                           (current_hash, time.time(), db_orig_id))

                    # 3. Check translation status
                    cursor.execute("SELECT last_translated_hash FROM translated_slides WHERE orig_slide_id=? AND lang_code=?", (db_orig_id, lang))
                    t_row = cursor.fetchone()
                    
                    if not t_row or t_row[0] != current_hash:
                        print(f"[{lang}] Translating slide {sid}...")
                        translated_texts = call_gemini_translate(model, texts, lang)
                        
                        if sid in trans_slides and translated_texts:
                            target_slide = trans_slides[sid]
                            text_idx = 0
                            for shape in target_slide.shapes:
                                if hasattr(shape, "text") and shape.text.strip():
                                    if text_idx < len(translated_texts):
                                        shape.text = translated_texts[text_idx]
                                        text_idx += 1
                        
                        if not t_row:
                            cursor.execute("INSERT INTO translated_slides (orig_slide_id, lang_code, last_translated_hash, last_updated) VALUES (?, ?, ?, ?)",
                                           (db_orig_id, lang, current_hash, time.time()))
                        else:
                            cursor.execute("UPDATE translated_slides SET last_translated_hash=?, last_updated=? WHERE orig_slide_id=? AND lang_code=?",
                                           (current_hash, time.time(), db_orig_id, lang))

                #4.  Detect any orphaned (deleted) slides that are no longer in the original but persist in the translation and delete those slides. 
                trans_ids = list(trans_slides.keys())
                for sid in trans_ids:
                    if sid not in orig_slides:
                        print(f"[{lang}] Deleting orphaned slide {sid}...")
                        # Remove from XML
                        sldIdLst = trans_prs.slides._sldIdLst
                        sldId = [s for s in sldIdLst if s.id == sid][0]
                        sldIdLst.remove(sldId)

                conn.commit()

            # 5. Check that the slide order is correct in the translated version in case of reorderings.
            sync_slide_order(orig_prs, trans_prs)
            trans_prs.save(trans_path)
            print(f"Success: {trans_path} updated.")





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

    genai.configure(api_key=config["gen_ai"]["API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')

    #For every publication
    for pub in publications:
        if not silent:
            print(f"Tarkistetaan {config[pub]['coursename']} - käännökset: {config[pub]['translate_to']}") 
        courseObject = create_course_object(config, pub)
        #Check headers etc.
        translate_pptx(Path(courseObject.course_slides_dir) / config["settings"]["headerfile"], config[pub]['translate_to'])
        translate_pptx(Path(courseObject.course_slides_dir) / config["settings"]["dividerfile"], config[pub]['translate_to'])
        translate_pptx(Path(courseObject.course_slides_dir) / config["settings"]["footerfile"], config[pub]['translate_to'])
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
                translate_pptx(Path(config['settings']['lecture_slides_dir']) / topic, config[pub]['translate_to'])
            #publication-specific additional lecture slides
            translate_pptx(Path(config['settings']['lecture_slides_dir']) / topic, config[pub]['translate_to'])

