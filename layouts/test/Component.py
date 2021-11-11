from src.Component import Component

class StaticImage(Component):

    info_format = {
        "image": str, # image file name
        "position": list # [x, y]
    }

    def init_component(self, info: dict):
        self.image = info["image"]
        self.position = tuple(info["position"])
        self.canvas.load_image(self.image)

    def process_input_and_draw(self, current_input):
        self.canvas.draw_image(self.image, self.position)