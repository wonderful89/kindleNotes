from operator import itemgetter, attrgetter


class AttrDisplay:
    def gatherAttrs(self):
        return ",".join(
            "{}={}".format(k, getattr(self, k)) for k in self.__dict__.keys()
        )
        # attrs = []
        # for k in self.__dict__.keys():
        #     item = "{}={}".format(k, getattr(self, k))
        #     attrs.append(item)
        # return attrs
        # for k in self.__dict__.keys():
        #     attrs.append(str(k) + "=" + str(self.__dict__[k]))
        # return ",".join(attrs) if len(attrs) else "no attr"

    def __str__(self):
        return "[{}:{}]".format(self.__class__.__name__, self.gatherAttrs())


class Sentence(AttrDisplay):
    content = ""
    pos = 0

    # def __str__(self):
    #     return '{content: "' + self.content + '", pos:' + str(self.pos) + "}"

    def __init__(self, content, pos):
        self.content = content
        self.pos = pos


class Chapter(AttrDisplay):
    sentences = []
    name = ""
    pos = 0

    # def __str__(self):
    #     return "{sentences: " + str(self.sentences) + ", name:" + self.name + "}"

    def __init__(self, name, sentences, pos):
        self.name = name
        self.sentences = sentences
        self.pos = pos

    def sortSen(self):
        self.sentences = sorted(self.sentences, key=attrgetter("pos"), reverse=False)


class BookInfo(AttrDisplay):
    name = ""
    chapters = []
    sentences = []
    hasChapter = True
    fileName = "test"

    beginTime = ""
    endTime = ""

    header = ""  # 输入到文件中
    content = ""
    end = ""

    def __init__(self, name, chapters, sentences):
        self.name = name
        self.chapters = chapters
        self.sentences = sentences
        if len(self.chapters) > 0:
            self.hasChapter = True
        else:
            self.hasChapter = False

    def appendChapter(self, chapter):
        self.chapters.append(chapter)

    def appendSen(self, sen):
        self.sentences.append(sen)

    def appendChapterSen(self, sen):
        chapterF = self.chapters[0]
        for chapter in self.chapters:
            if chapter.pos > sen.pos:
                break
            chapterF = chapter
        chapterF.sentences.append(sen)

    def sortChapter(self):
        for chapter in self.chapters:
            chapter.sortSen()

