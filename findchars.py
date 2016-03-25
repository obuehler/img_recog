__author__ = 'buehleo01'
from PIL import Image

class Character():
    """Class to hold a character image."""
    def __init__(self, pixels):
        self.pixels = pixels
        self.xmin = pixels[0][0]
        self.xmax = pixels[0][0]

        self.ymin = pixels[0][1]
        self.ymax = pixels[0][1]

        self.xsize = 0
        self.ysize = 0

        self.update()

    def update(self):
        """Look through the pixels and determine bounding rectangle"""
        for pixel in self.pixels:
            x = pixel[0]
            y = pixel[1]
            if x < self.xmin:
                self.xmin = x
            if x > self.xmax:
                self.xmax = x

            if y < self.ymin:
                self.ymin = y
            if y > self.ymax:
                self.ymax = y

        self.xsize = self.xmax-self.xmin
        self.ysize = self.ymax-self.ymin

    def adddata(self, data):
        for p in data:
            self.pixels.append(p)
        self.update()

    def boundingrect(self):
        """ Returns the bounding rectangle of the character in the form tuple(xmin, xmax, ymin, ymax) """
        return (self.xmin, self.xmax, self.ymin, self.ymax)

    def area(self):
        return self.xsize*self.ysize

    def draw(self):
        """Return an image representing the character"""
        canvas = Image.new("P", (self.xsize+1, self.ysize+1), 255)
        canvpmap = canvas.load()
        for pixel in self.pixels:
            canvpmap[pixel[0]-self.xmin, pixel[1]-self.ymin] = 0
        return canvas


def findcharacters(imgpath, dist_tol=10, darkness=80):
    """ Groups dark pixels together into characters.
    'Together' means that each pixel darker than darkness is within dist_tol of another dark pixel in that group.
    """
    img = Image.open(imgpath)
    img = img.convert("L").resize((500,500), Image.ANTIALIAS)
    imgpmap = img.load()

    # Look through image. If any pixel exceeds a certain 'blackness' make the corresponding output pixel black (0)
    characters = {}
    charnum = 0
    for x in range(img.size[0]):
        for y in range(img.size[1]):
            pixel = imgpmap[x, y]
            handled = False
            if pixel < darkness:
                # Check if this new dark pixel is near part of a known character
                for key in characters.keys():
                    for p in characters[key]:
                        if abs(x-p[0]) + abs(y-p[1]) <= dist_tol:  # Oh, it is, add it to that character
                            characters[key].append((x,y))
                            handled = True
                            break
                    if handled:
                        break

                if not handled:
                    # Make new character and add pixel
                    characters[charnum] = [(x,y)]
                    charnum += 1

    charobjs = []
    # Make a new charcter object for each character we found
    for key in characters.keys():
        if len(characters[key]) >= 10:  # Big enough, likely not just a rogue dark spot.
            charobjs.append(Character(characters[key]))

    # If bounding boxes overlap, combine chars into single char
    final = []
    for obj in charobjs:
        newchar = True
        for other in final:
            (xmin, xmax, ymin, ymax) = other.boundingrect()
            xin = (xmin <= obj.xmin <= xmax) or (xmin <= obj.xmax <= xmax)
            yin = (ymin <= obj.ymin <= ymax) or (ymin <= obj.ymax <= ymax)
            if xin and yin:  # Boxes overlap
                other.adddata(obj.pixels)  # Combine character pixels, dont add to final return list
                newchar = False
                break
        if newchar:  # Legit new character, add to final return list
            final.append(obj)

    return final

def charimages(charobjs):
    # Calculate average area of a character for this page
    totalarea = 0
    for char in charobjs:
        totalarea += char.area()

    avgarea = totalarea/len(charobjs)

    charimgs = []
    # Save all acceptable chars as their own images
    for i, char in enumerate(charobjs):
        if abs(char.area()-avgarea) < avgarea:
            image = char.draw()
            image.save(str(i) + '.png')
            charimgs.append(image)
    return charimgs


def boxcharacters(charobjs, impath):
    img = Image.open(impath)
    img = img.convert('RGB').resize((500,500), Image.ANTIALIAS)
    imgpmap = img.load()

    # Calculate average area of a character for this page
    totalarea = 0
    for char in charobjs:
        totalarea += char.area()

    avgarea = totalarea/len(charobjs)

    # Draw boxes around all the acceptable characters we found
    for char in charobjs:
        x = char.xmin
        y = char.ymin
        if abs(char.area()-avgarea) < avgarea:
            while y < char.ymax:
                imgpmap[char.xmin, y] = (255,0,100)
                imgpmap[char.xmax, y] = (255,0,100)
                y+=1
            while x < char.xmax:
                imgpmap[x, char.ymin] = (255,0,100)
                imgpmap[x, char.ymax] = (255,0,100)
                x+=1
    img.save("boxed.png")
    return img

if __name__ == "__main__":
    path = 'Photos\\digits.png'
    characters = findcharacters(path)
    boxcharacters(characters, path)