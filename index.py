from hashlib import sha256


class Course:
    def __init__(self, name: str, lecture_count: int):
        self.name = name
        self.lectures = list()
        self.lecture_count = lecture_count

    def add_lecture(self, lecture):
        if isinstance(lecture, Lecture):
            self.lectures.append(lecture)
            self.lecture_count += 1
        else:
            raise TypeError("You can only add Lecture objects.")


class Lecture():
    def __init__(self, name: str):
        self.name = name
        self.topics = list()

    def add_topic(self, topic):
        if isinstance(topic, Topic):
            self.topics.append(topic)
        else:
            raise TypeError("You can only add Topic objects.")


class Topic():
    def __init__(self, name: str):
        self.name = name
        self.uid = self._set_uid()

    def _set_uid(self) -> str:
        return sha256(self.name.encode('utf-8')).hexdigest()[:10]

if __name__ == "__main__":
    # Example usage
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
