# pdfpublisher
PoC/beta version for combining and publishing PDF files for different localisations, as a basis for the Software Project course topic.

# Usage
### settings
under settings there should be the entries for:<br>
lecture_slides_dir: This tells the program from where to fetch the topic slides for the lectures.<br>
header, footer and divider files: Which file should be used. This file should be in the folder with the course specific files.<br>

### Titlefont
Fill these with what font, fontsize colour and maxlines you want to use

### publications
- These should be named as the name of the course and there can be as many as you want. They need to have the following:<br>
- Coursecode: The code for the course<br>
- publish_dir: The teams folder where the course slides should be published.<br>
- coursesize: ECTS amount for the course.<br>
- lectures: How many lectures the course contains<br>
- coursename: The name of the course<br>
- filename_prefix: prefix for the files.<br>
- lectureterm: what the lecture is called (i.e. oppitunti, luento)<br>
- course_slides_dir: where the course specific slides are.<br>
- After these you should have an equal amount of numbered entries as your lecture count followed by your coursename and the topics for the course. ex.<br>
1 = lecturename, topic1, topic2<br>
2 = lecturename2, topic3, topic5<br>

### Link health checking

The program allows you to health check the links present in published slides. This is used by using the `--linkcheck` or `-l` flag. This prints out any links which no longer hold the linked resource or is not a working website at all.

You can check links on a specific file by specifying it via `--checkfile` or `-f`. `-f <path to file>`

The flag `--silent` or `-s` is also available to minimize prints.

