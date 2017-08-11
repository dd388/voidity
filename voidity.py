#!/bin/env python3

import os
import docx
import sys
import magic
import csv
from PIL import Image
from glob import glob
from argparse import ArgumentParser

# Size of file
def size(obj):
    res = os.stat(obj)
    if res.st_size > 1000000:
        return False
    else:
        return True


# Image tests
def image_dimensions(obj):
    if (obj.size[0] < 100) or (obj.size[1] < 100):
        return True
    else:
        return False


def image_color(obj):
    if len(obj.getcolors()) < 3:
        return True
    else:
        return False


# Word doc tests
def word_length(obj):
    if len(obj.paragraphs) < 2:
        return True
    else:
        w = 0
        for o in obj.paragraphs:
            w = w + len(o.text)
        if w < 100:
            return True
        else:
            return False


# Plain(ish) text tests
def text_length(obj):
    if len(obj) < 100:
        return True
    else:
        return False

#http://git.imagemagick.org/repos/ImageMagick/commit/501b648ee40f804228c76fddc02ca479c75666f3
def png_min_size(obj):
    if os.path.getsize(obj) < 61:
        return True
    else:
        return False

#http://git.imagemagick.org/repos/ImageMagick/commit/f9574dc71cc1ab8219b3bdfba11bf67dc2d98c71
def jpeg_min_size(obj):
    if os.path.getsize(obj) < 107:
        return True
    else:
        return False

#http://git.imagemagick.org/repos/ImageMagick/commit/3cc9d45352ebb92947d27c46e2604104b7ebfe90
def jng_min_size(obj):
    if os.path.getsize(obj) < 147:
        return True
    else:
        return False

def main():
    parser = ArgumentParser()
    parser.add_argument('input_dir', metavar='[input directory]',
                        help='Path of files to scan')
    parser.add_argument('output', metavar='[output file]',
                        help='File to output report (will not overwrite)')
    args = parser.parse_args()

    if os.path.isfile(args.output):
        sys.exit('error: output file already exists')
    else:
            fieldnames = ['filename', 'less than 1mb', 'less than minimum size', 'less than 100x100', 'less than three colors', 'less than 100 chars']
            outfile = open(args.output, 'w')
            outfilecsv = csv.DictWriter(outfile, fieldnames = fieldnames)
            outfilecsv.writeheader()

    if os.path.exists(args.input_dir) and os.path.isdir(args.input_dir):
        tc = [_tc for _tc in glob(os.path.join(args.input_dir, '*')) if not os.path.isdir(_tc)]
    else:
        sys.exit('error: input directory doesn\'t exist or the input directory isn\'t a directory')

    for tf in tc:
        tfp = {}

        tfp['filename'] = tf
        tfp['less than 1mb'] = size(tf)

        try:
            ftype = magic.from_file(tf)
            fmime = magic.from_file(tf, mime=True)
        except:
            sys.exit('error: unable to run "file" on input: {0}'.format(tf))

        if fmime == 'image/png':
            tfp['less than minimum size'] = png_min_size(tf)

        elif fmime == 'image/jpeg':
            tfp['less than minimum size'] = str(jpeg_min_size(tf))

        elif fmime == 'image/x-jng' or tf.endswith('jng'):
            tfp['less than minimum size'] = str(jng_min_size(tf))
 
        if ftype.find('image data') != -1:
            try:
                f = Image.open(tf)
                tfp['less than 100x100'] = image_dimensions(f)
                tfp['less than three colors'] = image_color(f)
            except:
                pass

        elif ftype.find('Microsoft Word') != -1: 
            f = docx.Document(tf)
            tfp['less than 100 chars'] = word_length(f)

        elif ftype == 'ASCII text':
            f = open(tf).read()
            tfp['less than 100 chars'] = text_length(f)

        outfilecsv.writerow(tfp)

if __name__ == '__main__':
    main()
