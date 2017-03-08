
import numpy as np
import os
import tempfile
from PyQt4 import QtCore, Qt
from scipy import ndimage
from scipy.misc import imresize
from common import Orientation, read_image
from read_minc import minc_to_numpy


class Volume(Qt.QObject):
    axial_slice_signal = QtCore.pyqtSignal(str, name='axial_signal')

    def __init__(self, vol, model, datatype,  memory_map=False):
        super(Volume, self).__init__()
        self.data_type = datatype
        self.name = None
        self.model = model
        self._arr_data = self._load_data(vol, memory_map)
        self.voxel_size = 28  # Temp hard coding
        self.interpolate = False
        # Set to False if Volume to be destroyed. We can't just delete this object as there are reference to
        # it in Slices.Layers and possibly others
        self.active = True
        self.int_order = 3
        self.min = float(self._arr_data.min())
        self.max = float(self._arr_data.max())

    def get_shape(self):
        return self._arr_data.shape

    def get_axial_slot(self):
        print('get_axial_slot')

    def pixel_axial(self, z, y, x):
        """
        get pixel intensity. due to way pyqtgraph orders the axes, we have to flip the z axis
        """
        y = self._arr_data.shape[1] - y
        return self._arr_data[z, y, x], (z, y, x)

    def pixel_sagittal(self, z, y, x):
        """
        get pixel intensity. due to way pyqtgraph orders the axes, we have to flip the y axis
        """
        return self._arr_data[z, y, x], (z, y, x)

    def pixel_coronal(self, z, y, x):
        """
        get pixel intensity. due to way pyqtgraph orders the axes, we have to flip the y axis
        """
        return self._arr_data[z, y, x], (z, y, x)

    def intensity_range(self):
        return self.min, self.max

    def _load_data(self, path, memmap=False):
        """
        Open data and convert
        todo: error handling
        :param path:
        :return:
        """
        ext = os.path.splitext(path)[1].lower()
        if ext == '.mnc':
            return minc_to_numpy(path)

        vol = read_image(path)
        if memmap:
            temp = tempfile.TemporaryFile()
            m = np.memmap(temp, dtype=vol.dtype, mode='w+', shape=vol.shape)
            m[:] = vol[:]
            return m
        else:
            return vol

    def get_data(self, orientation, index=0):
        """
        Return a 2d slice of image data of the specified axis. If index=None, midpoint is returned
        :param orientation:
        :param index:
        :return:
        """
        if orientation == Orientation.sagittal:
            return self._get_sagittal(index)
        if orientation == Orientation.coronal:
            return self._get_coronal(index)
        if orientation == Orientation.axial:
            return self._get_axial(index)

    def dimension_length(self, orientation):
        """
        Temp bodge. return the number of slices in this dimension
        :param orientation:
        :return:
        """
        if orientation == Orientation.sagittal:
            return self._arr_data[0, 0, :].size
        if orientation == Orientation.coronal:
            return self._arr_data[0, :, 0].size
        if orientation == Orientation.axial:
            return self._arr_data[:, 0, 0].size

    def set_voxel_size(self, size):
        """
        Set the voxel size in real world dimensions
        :param size:
        :return:
        """
        self.voxel_size = size

    def _get_coronal(self, index):
        slice_ = np.flipud(np.rot90(self._arr_data[:, index, :], 1))
        if self.interpolate:
            return self._interpolate(slice_)
        return slice_

    def _get_sagittal(self, index):

        slice_ = np.rot90(self._arr_data[:, :, index], 1)
        if self.interpolate:
            return np.flipud(self._interpolate(slice_))
        return np.flipud(slice_)

    def _get_axial(self, index):
        slice_ = np.rot90(self._arr_data[index, :, :], 3)
        if self.interpolate:
            return self._interpolate(slice_)
        return slice_

    def set_lower_level(self, level):
        #print 'l', level
        self.levels[0] = level

    def set_upper_level(self, level):
        #print 'u', level
        self.levels[1] = level

    def destroy(self):
        self._arr_data = None
        self.active = False

    def set_interpolation(self, state):
        self.interpolate = state

    def _interpolate(self, slice_):
        return imresize(ndimage.zoom(slice_, 2, order=4), 0.5, interp='bicubic')
        #return ndimage.gaussian_filter(slice_, sigma=0.7, order=0)