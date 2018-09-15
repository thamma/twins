import base64
import os


class ResourceManager:
    def __init__(self, root):
        self.root = root
        self.images = {}

    def get_image(self, path):
        if path not in self.images:
            filename = os.path.join(self.root, path)

            if not os.path.exists(filename):
                print(f"File '{filename}' not found!")
                filename = os.path.join(self.root, "404.png")

            with open(filename, "rb") as f:
                img_bytes = base64.b64encode(f.read())

            self.images[path] = "data:image;base64," + img_bytes.decode()

        return self.images[path]
