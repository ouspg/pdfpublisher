class Course:
    def __init__(self, coursecode: str, coursesize: int, lectures: int, name: str, filename_prefix: str, lectureterm: str, publication_dir: str, course_slides_dir: str):
        self.name = name
        self.coursecode = coursecode
        self.coursesize = coursesize
        self.lectures = lectures
        self.filename_prefix = filename_prefix
        self.lectureterm = lectureterm
        self.publication_dir = publication_dir
        self.course_slides_dir = course_slides_dir
        self.lecture_list = list()

    def add_lecture(self, name, lectureNumber, list):
        self.lecture_list.append(
            Lecture(name, lectureNumber, list)
        )

class Lecture():
    def __init__(self, name: str, lectureNumber: int, topic_list: list):
        self.name = name
        self.lectureNumber = lectureNumber
        self.topic_list = topic_list

    def add_topic(self, topic):
        self.topics.append(topic)

if __name__ == "__main__":
    # test code
    course = Course("123456A", 100, 2,"My course", "MC_", "Fall2024", "/path/to/publication/dir")
    lecture1 = Lecture("Lecture 1", "1", ["Topic A", "Topic B"])
    lecture2 = Lecture("Lecture 2", "2", [])
    course.add_lecture("lecture 1", 1, ["Topic A", "Topic B"])
    course.add_lecture("lecture 2", 2, ["Topic c"])

    print(f"{course.name} has following lectures: {[x.name for x in course.lecture_list]}")
    for lecture in course.lecture_list:
        print(f"{course.name} has following topics in {lecture.name} {[x for x in lecture.topic_list]}")