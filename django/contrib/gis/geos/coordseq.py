"""
This module houses the GEOSCoordSeq object, which is used internally
by GEOSGeometry to house the actual coordinates of the Point,
LineString, and LinearRing geometries.
"""

from ctypes import byref, c_byte, c_double, c_uint

from django.contrib.gis.geos import prototypes as capi
from django.contrib.gis.geos.base import GEOSBase
from django.contrib.gis.geos.error import GEOSException
from django.contrib.gis.geos.libgeos import CS_PTR, geos_version_tuple
from django.contrib.gis.shortcuts import numpy


class GEOSCoordSeq(GEOSBase):
    "The internal representation of a list of coordinates inside a Geometry."

    ptr_type = CS_PTR

    def __init__(self, ptr, z=False):
        "Initialize from a GEOS pointer."
        # TODO when dropping support for GEOS 3.13 the z argument can be
        # deprecated in favor of using the GEOS function GEOSCoordSeq_hasZ.
        if not isinstance(ptr, CS_PTR):
            raise TypeError("Coordinate sequence should initialize with a CS_PTR.")
        self._ptr = ptr
        self._z = z

    def __iter__(self):
        "Iterate over each point in the coordinate sequence."
        for i in range(self.size):
            yield self[i]

    def __len__(self):
        "Return the number of points in the coordinate sequence."
        return self.size

    def __str__(self):
        "Return the string representation of the coordinate sequence."
        return str(self.tuple)

    def __getitem__(self, index):
        "Return the coordinate sequence value at the given index."
        self._checkindex(index)
        return self._get_point(index)

    def __setitem__(self, index, value):
        "Set the coordinate sequence value at the given index."
        # Checking the input value
        if isinstance(value, (list, tuple)):
            pass
        elif numpy and isinstance(value, numpy.ndarray):
            pass
        else:
            raise TypeError(
                "Must set coordinate with a sequence (list, tuple, or numpy array)."
            )
        # Checking the dims of the input
        n_args = self._num_ordinates
        if len(value) != n_args:
            raise TypeError("Dimension of value does not match.")
        self._checkindex(index)
        self._set_point(index, value)

    # #### Internal Routines ####
    def _checkindex(self, index):
        "Check the given index."
        if not (0 <= index < self.size):
            raise IndexError(f"Invalid GEOS Geometry index: {index}")

    def _checkdim(self, dim):
        "Check the given dimension."
        if dim < 0 or dim > 3:
            raise GEOSException(f'Invalid ordinate dimension: "{dim:d}"')

    def _get_x(self, index):
        return capi.cs_getx(self.ptr, index, byref(c_double()))

    def _get_y(self, index):
        return capi.cs_gety(self.ptr, index, byref(c_double()))

    def _get_z(self, index):
        return capi.cs_getz(self.ptr, index, byref(c_double()))

    def _get_m(self, index):
        return capi.cs_getm(self.ptr, index, byref(c_double()))

    def _set_x(self, index, value):
        capi.cs_setx(self.ptr, index, value)

    def _set_y(self, index, value):
        capi.cs_sety(self.ptr, index, value)

    def _set_z(self, index, value):
        capi.cs_setz(self.ptr, index, value)

    def _set_m(self, index, value):
        capi.cs_setm(self.ptr, index, value)

    @property
    def _num_ordinates(self):
        "Return the number of ordinates per point."
        n = 2
        if self._z:
            n += 1
        if self.dims > n:
            n += 1
        return n

    def _get_point(self, index):
        "Return coordinates as a tuple for the given index."
        coords = (self._get_x(index), self._get_y(index))
        if self._z:
            coords += (self._get_z(index),)
        if self.dims > len(coords):
            coords += (self._get_m(index),)
        return coords

    def _set_point(self, index, value):
        "Set coordinates from a sequence for the given index."
        it = iter(value)
        self._set_x(index, next(it))
        self._set_y(index, next(it))
        if self._z:
            self._set_z(index, next(it))
        if len(value) > 2 + int(self._z):
            self._set_m(index, next(it))

    # #### Ordinate getting and setting routines ####
    def getOrdinate(self, dimension, index):
        "Return the value for the given dimension and index."
        self._checkindex(index)
        self._checkdim(dimension)
        return capi.cs_getordinate(self.ptr, index, dimension, byref(c_double()))

    def setOrdinate(self, dimension, index, value):
        "Set the value for the given dimension and index."
        self._checkindex(index)
        self._checkdim(dimension)
        capi.cs_setordinate(self.ptr, index, dimension, value)

    def getX(self, index):
        "Get the X value at the index."
        return self.getOrdinate(0, index)

    def setX(self, index, value):
        "Set X with the value at the given index."
        self.setOrdinate(0, index, value)

    def getY(self, index):
        "Get the Y value at the given index."
        return self.getOrdinate(1, index)

    def setY(self, index, value):
        "Set Y with the value at the given index."
        self.setOrdinate(1, index, value)

    def getZ(self, index):
        "Get Z with the value at the given index."
        return self.getOrdinate(2, index)

    def setZ(self, index, value):
        "Set Z with the value at the given index."
        self.setOrdinate(2, index, value)

    def getM(self, index):
        "Get M with the value at the given index."
        return self.getOrdinate(3, index)

    def setM(self, index, value):
        "Set M with the value at the given index."
        self.setOrdinate(3, index, value)

    # ### Dimensions ###
    @property
    def size(self):
        "Return the size of this coordinate sequence."
        return capi.cs_getsize(self.ptr, byref(c_uint()))

    @property
    def dims(self):
        "Return the dimensions of this coordinate sequence."
        return capi.cs_getdims(self.ptr, byref(c_uint()))

    @property
    def hasz(self):
        """
        Return whether this coordinate sequence is 3D. This property value is
        inherited from the parent Geometry.
        """
        return self._z

    @property
    def hasm(self):
        """
        Return whether this coordinate sequence has M dimension.
        """
        if geos_version_tuple() >= (3, 14):
            return capi.cs_hasm(self._ptr)
        else:
            raise NotImplementedError(
                "GEOSCoordSeq with an M dimension requires GEOS 3.14+."
            )

    # ### Other Methods ###
    def clone(self):
        "Clone this coordinate sequence."
        return GEOSCoordSeq(capi.cs_clone(self.ptr), self.hasz)

    @property
    def kml(self):
        "Return the KML representation for the coordinates."
        if self.hasz:
            coords = [f"{coord[0]},{coord[1]},{coord[2]}" for coord in self]
        else:
            coords = [f"{coord[0]},{coord[1]},0" for coord in self]

        coordinate_string = " ".join(coords)
        return f"<coordinates>{coordinate_string}</coordinates>"

    @property
    def tuple(self):
        "Return a tuple version of this coordinate sequence."
        n = self.size
        if n == 1:
            return self._get_point(0)
        return tuple(self._get_point(i) for i in range(n))

    @property
    def is_counterclockwise(self):
        """Return whether this coordinate sequence is counterclockwise."""
        ret = c_byte()
        if not capi.cs_is_ccw(self.ptr, byref(ret)):
            raise GEOSException(
                'Error encountered in GEOS C function "%s".' % capi.cs_is_ccw.func_name
            )
        return ret.value == 1
