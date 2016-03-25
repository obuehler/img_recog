__author__ = 'Buehleo01'
import os
from PIL import Image
import sys


class PDFReader:
    """Extracts jpgs embedded in the supplied PDF"""
    def extractjpg(self, pdfs):
        # Hex codes for beginning and end of embedded jpg
        startcode = "\xff\xd8"
        endcode = "\xff\xd9"

        for f in pdfs:
            # Make a folder for jpgs of each pdf
            segments = f.split('/')
            filent = segments[segments.__len__()-1]
            name = filent.split('.')[0]
            try:
                os.mkdir(name)
            except WindowsError:  # Dir already exists, just keep going
                pass

            i = 0  # index within pdf binary
            njpg = 0  # jpg number
            pdf = open(f, 'rb').read()
            # Embedded jpg locator loop
            while True:
                istream = pdf.find("stream", i)  # Stream contains data
                if istream < 0:
                    break
                istart = pdf.find(startcode, istream, istream+20) # Locate start of embedded jpg
                if istart < 0:
                    i = istream+20
                    continue
                iend = pdf.find("endstream", istart)  # End of stream
                if iend < 0:
                    raise Exception("Didn't find end of stream!")
                iend = pdf.find(endcode, iend-20) + 2  # Locate end of embedded jpg
                if iend < 0:
                    raise Exception("Didn't find end of JPG!")
                print "JPG %d found in %s binary from %d to %d" % (njpg, name, istart, iend)

                # Make a jpg file with the binary segment
                jpg = pdf[istart:iend]
                jpgfile = open(name + "/jpg%d.jpg" % njpg, "wb")
                jpgfile.write(jpg)
                jpgfile.close()
                njpg += 1
                i = iend

if __name__ == "__main__":
    files = ['C:/Users/buehleo01/Pictures/FPH-14-070.pdf',
             'C:/Users/buehleo01/Pictures/FPH-14-071.pdf',
             'C:/Users/buehleo01/Pictures/FPH-14-072.pdf'
            ]
    reader = PDFReader()
    reader.extractjpg(files)