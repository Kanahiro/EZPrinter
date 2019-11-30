class PaperSettings:
    #length:mm
    #(width, height)
    papers = {
        "A0":(841,1189),
        "A1":(594,841),
        "A2":(420,594),
        "A3":(297,420),
        "A4":(210,297),
        "B0":(1030,1456),
        "B1":(728,1030),
        "B2":(515,728),
        "B3":(364,515),
        "B4":(257,364),
        "B5":(182,257),
        "Postcard":(100,148)
    }

    def getPapers(self):
        return self.papers

    def getPaperSize(self, key="A4", horizontal=False):
        papers = self.getPapers()
        selectedPaperSize = papers[key]
        if horizontal:
            return (selectedPaperSize[1], selectedPaperSize[0])
        return selectedPaperSize