from operator import itemgetter, attrgetter
import json


class AttrDisplay:
    def asdict(self):
        return ""

    def toJSONStr(self):
        return json.dumps(self.asdict(), sort_keys=True, indent=4)

    def __str__(self):
        jsonStr = json.dumps(self.asdict(), sort_keys=True, indent=4)
        return jsonStr


class Sentence(AttrDisplay):
    content = ""
    pos = 0

    def __iter__(self):
        yield "content", self.content
        yield "pos", self.pos

    def asdict(self):
        return {"content": self.content, "pos": self.pos}

    def __init__(self, content, pos):
        self.content = content
        self.pos = pos


class Chapter(AttrDisplay):
    sentences = []
    name = ""
    pos = 0

    def __iter__(self):
        yield "name", self.name
        yield "pos", self.pos
        # yield "sentences", dict(self.sentences)

    def asdict(self):
        newSens = []
        for cusSen in self.sentences:
            newSens.append(cusSen.asdict())
        return {"name": self.name, "pos": self.pos, "sentences": newSens}

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

    def asdict(self):
        chaptersT = []
        sensT = []
        for sen in self.sentences:
            sensT.append(sen.asdict())
        for chapter in self.chapters:
            chaptersT.append(chapter.asdict())
        return {
            "name": self.name,
            "beginTime": self.beginTime,
            "endTime": self.endTime,
            "fileName": self.fileName,
            "hasChapter": self.hasChapter,
            "sentences": sensT,
            "chapters": chaptersT,
        }

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

    def sentenceLen(self):
        if self.hasChapter == False:
            return len(self.sentences)
        total = 0
        for chapter in self.chapters:
            total += len(chapter.sentences)
        return total
