# -*- coding: utf-8 -*-
"""
$Id$

Copyright 2008-2010 Lode Leroy
Copyright 2010 Lars Kruse <devel@sumpfralle.de>

This file is part of PyCAM.

PyCAM is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

PyCAM is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with PyCAM.  If not, see <http://www.gnu.org/licenses/>.
"""

from pycam.Geometry import TransformableContainer
from pycam.Geometry.Model import ContourModel
from pycam.Geometry.Line import Line
from pycam.Geometry.Point import Point


class Letter(TransformableContainer):
    
    def __init__(self, lines):
        self.lines = lines

    def minx(self):
        return min([line.minx for line in self.lines])

    def maxx(self):
        return max([line.maxx for line in self.lines])

    def miny(self):
        return min([line.miny for line in self.lines])

    def maxy(self):
        return max([line.maxy for line in self.lines])

    def get_positioned_lines(self, base_point, skew=None):
        result = []
        # TODO: calculate skew
        for line in self.lines:
            new_line = Line(line.p1.add(base_point), line.p2.add(base_point))
            result.append(new_line)
        return result


class Charset(object):

    def __init__(self, name=None, author=None, letterspacing=3.0,
            wordspacing=6.75, linespacingfactor=1.0, encoding=None):
        self.letters = {}
        self.letterspacing = letterspacing
        self.wordspacing = wordspacing
        self.linespacingfactor = linespacingfactor
        self.default_linespacing = 1.6
        self.default_height = 10.0
        if name is None:
            self.names = []
        else:
            if isinstance(name, (list, set, tuple)):
                self.names = name
            else:
                self.names = [name]
        if author is None:
            self.authors = []
        else:
            if isinstance(author, (list, set, tuple)):
                self.authors = author
            else:
                self.authors = [author]
        if encoding is None:
            self.encoding = "iso-8859-1"
        else:
            self.encoding = encoding

    def add_character(self, character, lines):
        if len(lines) > 0:
            self.letters[character] = Letter(lines)

    def get_names(self):
        return self.names

    def render(self, text, origin=None, skew=0):
        result = ContourModel()
        if origin is None:
            origin = Point(0, 0, 0)
        base = origin
        for line in text.splitlines():
            line_height = self.default_height
            for character in line:
                if character == " ":
                    base = base.add(Point(self.wordspacing, 0, 0))
                elif character in self.letters:
                    charset_letter = self.letters[character]
                    for line in charset_letter.get_positioned_lines(base):
                        result.append(line)
                    # update line height
                    line_height = max(line_height, charset_letter.maxy())
                    # shift the base position
                    base = base.add(Point(
                            charset_letter.maxx() + self.letterspacing, 0, 0))
                else:
                    # unknown character - add a small whitespace
                    base = base.add(Point(self.letterspacing, 0, 0))
            # go to the next line
            line_spacing = line_height * self.default_linespacing * self.linespacingfactor
            base = Point(origin.x, base.y - line_spacing, origin.z)
        return result
