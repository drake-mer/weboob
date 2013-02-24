# -*- coding: utf-8 -*-

# Copyright(C) 2010-2012 Julien Veyssier
#
# This file is part of weboob.
#
# weboob is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# weboob is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with weboob. If not, see <http://www.gnu.org/licenses/>.


try:
    from urlparse import parse_qs
except ImportError:
    from cgi import parse_qs  # NOQA

from urlparse import urlsplit

from weboob.capabilities.subtitle import Subtitle
from weboob.capabilities.base import NotAvailable
from weboob.tools.browser import BasePage
from weboob.tools.misc import get_bytes_size


__all__ = ['SubtitlesPage','SearchPage']


class SearchPage(BasePage):
    """ Page which contains results as a list of movies
    """
    def iter_subtitles(self):
        tabresults = self.parser.select(self.document.getroot(),'table#search_results')
        if len(tabresults) > 0:
            table = tabresults[0]
            # for each result line, explore the subtitle list page to iter subtitles
            for line in table.getiterator('tr'):
                links = self.parser.select(line,'a')
                if len(links) > 0:
                    a = links[0]
                    url = a.attrib.get('href','')
                    if "ads.opensubtitles" in url:
                        continue
                    self.browser.location("http://www.opensubtitles.org%s"%url)
                    # TODO verifier si on ne chope pas toutes les lignes. plusieurs tableaux ?
                    assert self.browser.is_on_page(SubtitlesPage) or self.browser.is_on_page(SubtitlePage)
                    # subtitles page does the job
                    for subtitle in self.browser.page.iter_subtitles():
                        yield subtitle


class SubtitlesPage(BasePage):
    """ Page which contains several subtitles for a single movie
    """
    def get_subtitle(self,id_file):
        tabresults = self.parser.select(self.document.getroot(),'table#search_results')
        if len(tabresults) > 0:
            table = tabresults[0]
            # for each result line, get informations
            for line in table.getiterator('tr'):
                idline = line.attrib.get('id','').replace('name','')
                if idline == id_file:
                    return self.get_subtitle_from_line(line)

    def iter_subtitles(self):
        # TODO verifier les ads
        tabresults = self.parser.select(self.document.getroot(),'table#search_results')
        if len(tabresults) > 0:
            table = tabresults[0]
            # for each result line, get informations
            for line in table.getiterator('tr'):
                yield self.get_subtitle_from_line(line)

    def get_subtitle_from_line(self,line):
        id_movie = line.attrib.get('id','').replace('name','')
        cells = self.parser.select(line,'td')
        if len(cells) > 0:
            first_cell = cells[0]
            links = self.parser.select(line,'a')
            a = links[0]
            urldetail = a.attrib.get('href','')
            name = a.text
            long_name = self.parser.select(first_cell,'span').attrib.get('title','')
            name = "%s (%s)"%(name,long_name)
            second_cell = cells[1]
            link = self.parser.select(second_cell,'a',1)
            lang = link.attrib.get('onclick','').split('/')[-1].split('-')[-1]
            nb_cd = cells[2].text.strip().lower().replace('CD','')
            fps = 0
            desc = ''
            cell_dl = cells[4]
            href = self.parser.select(cell_dl,'a',1).attrib.get('href','')
            url = "http://www.opensubtitles.org%s"%href
            id_file = href.split('/')[-1]

            id = "%s|%s"%(id_movie,id_file)
            subtitle = Subtitle(id,name)
            subtitle.url = url
            subtitle.fps = fps
            subtitle.language = lang
            subtitle.nb_cd = nb_cd
            subtitle.description = "no desc"
            return subtitle


class SubtitlePage(BasePage):
    """ Page which contains a single subtitle for a movie
    """
    def get_subtitle(self,id):
        return []

    def iter_subtitles(self):
        return
        yield "plop"
