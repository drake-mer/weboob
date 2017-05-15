# -*- coding: utf-8 -*-

# Copyright(C) 2012 Romain Bignon
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


from .base import Capability, BaseObject, Field, IntField, DecimalField, \
                  StringField, BytesField, enum, UserError
from .date import DateField

__all__ = ['HousingPhoto', 'Housing', 'Query', 'City', 'CapHousing',
           'UTILITIES']


class TypeNotSupported(UserError):
    """
    Raised when query type is not supported
    """

    def __init__(self,
                 msg='This type of house is not supported by this module'):
        UserError.__init__(self, msg)


class HousingPhoto(BaseObject):
    """
    Photo of a housing.
    """
    data =      BytesField('Data of photo')

    def __init__(self, url):
        BaseObject.__init__(self, url.split('/')[-1], url)

    def __iscomplete__(self):
        return self.data

    def __str__(self):
        return self.url

    def __repr__(self):
        return '<HousingPhoto %r data=%do url=%r>' % (self.id, len(self.data) if self.data else 0, self.url)


UTILITIES = enum(INCLUDED=u'C.C.', EXCLUDED=u'H.C.', UNKNOWN=u'')


class Housing(BaseObject):
    """
    Content of a housing.
    """
    title =           StringField('Title of housing')
    area =            DecimalField('Area of housing, in m2')
    cost =            DecimalField('Cost of housing')
    price_per_meter = DecimalField('Price per meter ratio')
    currency =        StringField('Currency of cost')
    utilities =       Field('Utilities included or not', *UTILITIES.types)
    date =            DateField('Date when the housing has been published')
    location =        StringField('Location of housing')
    station =         StringField('What metro/bus station next to housing')
    text =            StringField('Text of the housing')
    phone =           StringField('Phone number to contact')
    photos =          Field('List of photos', list)
    rooms =           DecimalField('Number of rooms')
    bedrooms =        DecimalField('Number of bedrooms')
    details =         Field('Key/values of details', dict)


class Query(BaseObject):
    """
    Query to find housings.
    """
    TYPE_RENT = 0
    TYPE_SALE = 1
    TYPE_SHARING = 2

    HOUSE_TYPES = enum(APART=u'Apartment',
                       HOUSE=u'House',
                       PARKING=u'Parking',
                       LAND=u'Land',
                       OTHER=u'Other',
                       UNKNOWN=u'Unknown')

    type = IntField('Type of housing to find (TYPE_* constants)')
    cities = Field('List of cities to search in', list, tuple)
    area_min = IntField('Minimal area (in m2)')
    area_max = IntField('Maximal area (in m2)')
    cost_min = IntField('Minimal cost')
    cost_max = IntField('Maximal cost')
    nb_rooms = IntField('Number of rooms')
    house_types = Field('List of house types', list, tuple, default=HOUSE_TYPES.values)


class City(BaseObject):
    """
    City.
    """
    name =      StringField('Name of city')


class CapHousing(Capability):
    """
    Capability of websites to search housings.
    """

    def search_housings(self, query):
        """
        Search housings.

        :param query: search query
        :type query: :class:`Query`
        :rtype: iter[:class:`Housing`]
        """
        raise NotImplementedError()

    def get_housing(self, housing):
        """
        Get an housing from an ID.

        :param housing: ID of the housing
        :type housing: str
        :rtype: :class:`Housing` or None if not found.
        """
        raise NotImplementedError()

    def search_city(self, pattern):
        """
        Search a city from a pattern.

        :param pattern: pattern to search
        :type pattern: str
        :rtype: iter[:class:`City`]
        """
        raise NotImplementedError()
