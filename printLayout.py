class PrintLayout:
    def init(self, mapImage, title="title", subtitle="", attribution="", scale=True, direction=False):
        self.mapImage = mapImage
        self.title = title
        self.subtitle = subtitle
        self.attribution = attribution
        self.scale = scale
        self.direction = direction

    def makePage(self):
        print(self)