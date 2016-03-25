__author__ = 'buehleo01'
from findchars import findcharacters, charimages
from imgrecog import recognize

path = 'Photos\\nums2.png'
characters = findcharacters(path)
charpics = charimages(characters)
text = ''
for char in charpics:
    text += str(recognize(char)[0])

print len(text)
print text
