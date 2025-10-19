class Course:
    def __init__(self, coursecode: str, coursesize: int, lectures: int, name: str, filename_prefix: str, lectureterm: str, publication_dir: str):
        self.name = name
        self.coursecode = coursecode
        self.coursesize = coursesize
        self.lectures = lectures
        self.filename_prefix = filename_prefix
        self.lectureterm = lectureterm
        self.publication_dir = publication_dir
        self.lecture_list = list()

    def add_lecture(self, name, lectureNumber, topic_list):
        self.lecture_list.append(
            Lecture(name, lectureNumber, topic_list)
        )

"""
        if isinstance(lecture, Lecture):
            self.lecture_list.append(lecture)
        else:
            raise TypeError("You can only add Lecture objects.")
"""



class Lecture():
    def __init__(self, name: str, lectureNumber: int, topic_list: list):
        self.name = name
        self.lectureNumber = lectureNumber
        self.topic_list = topic_list

    def add_topic(self, topic):
        if isinstance(topic, Topic):
            self.topics.append(topic)
        else:
            raise TypeError("You can only add Topic objects.")


class Topic():
    def __init__(self, name: str):
        self.name = name

if __name__ == "__main__":
    # test code
    course = Course("My course", 0)
    lecture1 = Lecture("Lecture 1")
    lecture2 = Lecture("Lecture 2")
    topic1a = Topic("Topic A")
    topic2a = Topic("Topic B")

    print("UIDs for topics:")
    print(getattr(topic1a, "uid", None))
    print(getattr(topic2a, "uid", None))

    course.add_lecture(lecture1)
    course.add_lecture(lecture2)

    print(f"{course.name} has following lectures: {[x.name for x in course.lectures]}")

    lecture1.add_topic(topic1a)
    lecture1.add_topic(topic2a)
    print(f"{lecture1.name} has following topics: {[x.name for x in lecture1.topics]}")
    lecture2.add_topic(topic2a)
    print(f"{lecture2.name} has following topics: {[x.name for x in lecture2.topics]}")

    for lecture in course.lectures:
        print(f"Topics on {lecture.name}")
        for topic in lecture.topics:
            print(topic.name)
