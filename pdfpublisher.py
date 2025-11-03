import configparser
import sys
import re
import io
import shutil
from pathlib import Path
from pypdf import PdfReader, PdfWriter
from pypdf._page import PageObject
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib import colors

from index import Course, Lecture

#############################################################################
# CONFIGURATION
#############################################################################
CONFIG_FILE = Path("settings.ini")
HEADER_FILE = "header"
FOOTER_FILE = "footer"

# Required mandatory configurations
REQUIRED_SETTINGS = {
    "settings": ["lecture_slides_dir","headerfile","footerfile","dividerfile","lecturecount"],
    "titlefont": ["font","font_max_size","font_min_size","colour","maxlines"],
}

# Mandatory options for all publications
PUBLICATION_OPTIONS = set(["coursename",
"coursesize",
"coursecode",
"lectures",
"lectureterm",
"filename_prefix",
"course_slides_dir",
"publish_dir"])

def load_config():
    config = configparser.ConfigParser()

    # Read existing file (if any)
    if CONFIG_FILE.exists():
        config.read(CONFIG_FILE)
    else:
        print(f"[ERROR] Config file not found. Creating new {CONFIG_FILE}.")
        CONFIG_FILE.touch()

    modified = False
    missing = []
    publications = []
  
    # Ensure all mandatory sections/keys exist
    for section, keys in REQUIRED_SETTINGS.items():
        if not config.has_section(section):
            config.add_section(section)
            modified = True

        for key in keys:
            if not config.has_option(section, key) or not config[section][key].strip():
                config.set(section, key, "")  # ensure entry exists but is empty
                modified = True
                missing.append(f"{section}.{key}")
              
    # Do we have publication targets?
    for section in config.sections():
      # Collect keys present in this section
      keys = set(config[section].keys())
      # Check if all required options are there
      if PUBLICATION_OPTIONS.issubset(keys):
        publications.append(section)    
    if len(publications) == 0:
      config.add_section("publication")
      for key in PUBLICATION_OPTIONS:
        config.set("publication",key, "") #add empty publication key
      modified = True
      
    # Save any modifications back to file
    if modified:
        with open(CONFIG_FILE, "w") as f:
            config.write(f)

    # If anything missing -> exit with error
    if missing:
        print("[ERROR] Missing mandatory settings:")
        for item in missing:
            print(f"  - {item}")
        print(f"\nPlease edit {CONFIG_FILE} and fill in the missing values.")
        sys.exit(1)
    if len(publications) == 0:
        print(f"[ERROR] At least one publication required! Added empty one to {CONFIG_FILE}!")
        sys.exit(1)
	
    return (config,publications)


#############################################################################
# Tekstin lisäys otsikkosivulle
#############################################################################

def split_to_lines(linecount, text):
    lines = [""]*linecount
    words = text.split()
    target = len(text)/linecount
    line = 0
    try:
        while(True):
            while len(lines[line])<target:
                lines[line] = f"{lines[line]} {words.pop(0)}"
            line += 1
    except IndexError:
        pass
    return lines

def add_title(page: PageObject, lectureterm: str, lecturenum: int, lecturetitle: str,font: str,font_max_size: int,font_min_size: int,font_colour: str,maxlines: int):

    #Page and text area width
    width = float(page.mediabox.width)
    height = float(page.mediabox.height)
    textwidth = width -100
    text = [f"{lectureterm} {lecturenum}",lecturetitle]

    #Font size settings
    font_size = font_max_size
    
    #Adjust font size
    while not all(stringWidth(line,font,font_size) <= textwidth for line in text):
        if font_size > font_min_size:
            font_size -= 1
        elif len(text) == maxlines:
            break
        else:
            #Lisätään rivejä
            newlinecount = len(text)
            text[1:] = split_to_lines(newlinecount,lecturetitle)
            font_size = font_max_size
    packet = io.BytesIO()
    c = canvas.Canvas(packet, (width, height))
    c.setFont(font,font_size)
    c.setFillColor(getattr(colors,font_colour, colors.white))
    lineheight = font_size * 1.2
    drawheight = height/2 + (len(text)*lineheight)/2
    for line in text:
        c.drawCentredString(width / 2.0, drawheight,line)
        drawheight -= lineheight
    c.save()
    packet.seek(0)
    page.merge_page(PdfReader(packet).pages[0])

#############################################################################
# Tiedostojen haku
#############################################################################
def load_directory(directory):
    files = {}
    folder = Path(directory)
    for f in folder.glob("*.pdf"):
        match = re.search(r'\d+', f.stem)
        num = int(match.group()) if match else None
        if isinstance(num, int):
            mtime = f.stat().st_mtime
            files[num] = {}
            files[num]["file"] = f
            files[num]["modtime"] = mtime
    for f in folder.glob("*"):
        mtime = f.stat().st_mtime
        files[f.name] = {}
        files[f.name]["file"] = f
        files[f.name]["modtime"] = mtime
    return files

def load_full_directory(directory):
    files = {}
    folder = Path(directory)
    for f in folder.glob("*"):
        mtime = f.stat().st_mtime
        files[f.name] = {}
        files[f.name]["file"] = f
        files[f.name]["modtime"] = mtime
    return files

def create_course_object(config, pub):
    course_code = config[pub]["coursecode"]
    course_size = config[pub]["coursesize"]
    name = config[pub]["coursename"]
    filename_prefix = config[pub]["filename_prefix"]
    lectures = config[pub]["lectures"]
    lecture_term = config[pub]["lectureterm"]
    publication_dir = config[pub]["publish_dir"]
    course_dir = config[pub]["course_slides_dir"]

    return Course(course_code,
                    int(course_size),
                    lectures,
                    name,
                    filename_prefix,
                    lecture_term,
                    publication_dir,
                    course_dir
            )

#############################################################################
# MAIN
#############################################################################
if __name__ == "__main__":
    (config, publications) = load_config()
    print("Config loaded successfully!")

# TODO: check for errors in class implementation

    slide_updates = load_directory(config['settings']['lecture_slides_dir'])

    for pub in publications:
        print(f"Tarkistetaan {config[pub]['coursename']}")
        courseObject = Course(config[pub]['coursecode'],
                            int(config[pub]['coursesize']),
                            int(config[pub]['lectures']),
                            config[pub]['coursename'],
                            config[pub]['filename_prefix'],
                            config[pub]['lectureterm'],
                            config[pub]['publish_dir'],
                            config[pub]['course_slides_dir'])

        #Load publication-specific update dates
        pubslides = load_directory(courseObject.course_slides_dir)

	# Support for not all courses containing all lectures:
    #TODO: Make lecture object here? Or atleast rework the next line to work with the lecture objects.
        try:
            for x in range(1, courseObject.lectures+1):
                lecturelist = config[pub][str(x)].split(",")
                lecture_name = lecturelist.pop(0).strip()
                courseObject.add_lecture(lecture_name, x, [topic.strip() for topic in lecturelist])
        except KeyError:
            print(f"Courses should be added as <lecturenumber = name, topic1, topic2 ... topicN> under publication {courseObject.name} in settings.ini")
            continue
        #old code:
        """
        lectures = {int(x.strip()) for x in config[pub]["lectures"].split(",")}
        lecturenumber = 1
        """
        

        # Load header/footer slides
        Startingslides = PdfReader(Path(courseObject.course_slides_dir) / config["settings"]["headerfile"])
        Dividerslides = PdfReader(Path(courseObject.course_slides_dir) / config["settings"]["dividerfile"])
        Endingslides = PdfReader(Path(courseObject.course_slides_dir) / config["settings"]["footerfile"])

        # Go through all or a subset of lectures
        #TODO: rework this to account for oob and Settings.ini changes?
        for n in range(1, courseObject.lectures+1):
            #If not included in this publication, continue
            if n not in [lecture.lectureNumber for lecture in courseObject.lecture_list]:
                print(f"Luentomateriaali {n}: tämä luento ei sisälly tähän kurssiin.")
                continue

            # Check if the publication folder exists, create if necessary, check published file
            matpubdir = f"{courseObject.publication_dir}/{courseObject.lectureterm} {lecturenumber:02}"
            matpubpath = Path(matpubdir)
            if not matpubpath.exists():
                matpubpath.mkdir(parents=True, exist_ok=True)
            filename = re.sub(r'[\\/]', '', f"{lecturenumber:02} - {courseObject.filename_prefix} {courseObject.lectureterm.lower()} {lecturenumber} – {config['settings'][str(n)]}.pdf")[:200]
            published_slides = matpubpath / filename

            # First check the slides, later additional materials
            if not n in slide_updates:
                print(f"Luentomateriaali {n} -> Luento {lecturenumber}: luentokalvot eivät vielä saatavilla")
            elif not n in pubslides:
                print(f"Luentomateriaali {n} -> Luento {lecturenumber}: kurssikohtaiset täydentävät kalvot eivät vielä saatavilla!")	    
            elif published_slides.exists() and slide_updates[n]["modtime"] <= published_slides.stat().st_mtime and pubslides[n]["modtime"] <= published_slides.stat().st_mtime:
                print(f"Luentomateriaali {n} -> Luento {lecturenumber}: ajan tasalla")
            else:
                if not published_slides.exists():
                    print(f"Luentomateriaali {n} -> Luento {lecturenumber}: ei vielä julkaistu -> julkaistaan")
                else:
                    print(f"Luentomateriaali {n} -> Luento {lecturenumber} on päivitetty -> julkaistaan")
                newslides = PdfWriter()

                # Take starting slide, update course and lecture name
                firstslide = Startingslides.pages[0]
                add_title(firstslide,courseObject.lectureterm,n,config["settings"][str(n)],config["titlefont"]["font"],int(config["titlefont"]["font_max_size"]),int(config["titlefont"]["font_max_size"]),config["titlefont"]["colour"],int(config["titlefont"]["maxlines"]));

                newslides.add_page(firstslide)
                for page in Startingslides.pages[1:]:
                    newslides.add_page(page)

                # Insert lecture slides
                #TODO: make the lecture slides from the topics here?
                for topic in [lecture.topic_list for lecture in courseObject.lecture_list]:
                    Lectureslides = PdfReader(slide_updates[n]["file"])
                    for page in Lectureslides.pages:
                        newslides.add_page(page)

		# Insert divider slides
                for page in Dividerslides.pages:
                    newslides.add_page(page)

                # Insert course-specific slides into the placeholder
                Courseslides = PdfReader(pubslides[n]["file"])
                for page in Courseslides.pages:
                    newslides.add_page(page)

		# Insert footer slides
                for page in Endingslides.pages:
                    newslides.add_page(page)

		# Write to file
                print("Luodaan pdf...")
                #filename = re.sub(r'[\\/]', '', f"{lecturenumber:02} - {config[pub]['filename_prefix']} {config[pub]['lectureterm']} {lecturenumber}: {config['settings'][str(n)]}.pdf")[:200]
                with open(published_slides,"wb") as f:
                    newslides.write(f)

            # Check materials
            materials_for_all = load_full_directory(f"{config['settings']['slides_dir']}/{n:02}")
            materials_forcourse = load_full_directory(f"{courseObject.course_slides_dir}/{n:02}")
            materials_published = load_full_directory(matpubdir)
            if len(materials_for_all) + len(materials_forcourse) > 0:
                for filename, file in materials_for_all.items():
                    if filename not in materials_published:
                        print(f"...Tiedostoa {filename} ei ole vielä julkaistu, julkaistaan.")
                        shutil.copy2(file['file'], matpubpath / filename)
                    elif file["modtime"] > materials_published[filename]["modtime"]:
                        print(f"...Tiedostosta {filename} on uudempi versio, julkaistaan.")
                        shutil.copy2(file['file'], materials_published[filename]["file"])
                    else:
                        print(f"...Tiedosto {filename} on ajan tasalla")
                for filename, file in materials_forcourse.items():
                    if filename not in materials_published:
                        print(f"...Tiedostoa {filename} ei ole vielä julkaistu, julkaistaan.")
                        shutil.copy2(file['file'], matpubpath / filename)
                    elif file["modtime"] > materials_published[filename]["modtime"]:
                        print(f"...Tiedostosta {filename} on uudempi versio, julkaistaan.")
                        shutil.copy2(file['file'], materials_published[filename]["file"])
                    else:
                        print(f"...Tiedosto {filename} on ajan tasalla")
            lecturenumber += 1

