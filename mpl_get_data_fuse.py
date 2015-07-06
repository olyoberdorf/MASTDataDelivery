"""
.. module:: mpl_get_data_fuse

   :synopsis: Returns FUSE spectral data as a JSON string through Randy's
   mast_plot.pl service.

.. moduleauthor:: Scott W. Fleming <fleming@stsci.edu>
"""

import collections
from data_series import DataSeries
from operator import itemgetter
import requests

#--------------------
def mpl_get_data_fuse(obsid):
    """
    Given an FUSE observation ID, returns the spectral data.

    :param obsid: The FUSE observation ID to retrieve the data from.

    :type obsid: str

    :returns: JSON -- The spectral data for this observation ID.

    Error codes:
    0 = No error.
    1 = No data returned by mast_plot.pl service.
    """

    # This defines a data point for a DataSeries object as a namedtuple.
    data_point = collections.namedtuple('DataPoint', ['x', 'y'])

    # For FUSE, this defines the x-axis and y-axis units as a string.
    fuse_xunit = "Angstroms"
    fuse_yunit = "ergs/cm^2/s/Angstrom"

    # Initiate a reqest from Randy's perl script service.  Note the return is
    # a 3-element list, each element itself if a list containing another list.
    return_request = requests.get("https://archive.stsci.edu/cgi-bin/mast_plot"
                                  ".pl?FUSE=" + obsid.upper()).json()

    if len(return_request[0][0]) != 1:
        # Wavelengths are the first list in the returned 3-element list.
        wls = [float(x) for x in return_request[0][0]]

        # Fluxes are the second list in the returned 3-element list.
        fls = [float(x) for x in return_request[1][0]]

        # This error code will be used unless there's a problem reading any
        # of the FITS files in the list.
        errcode = 0

        # Make sure wavelengths and fluxes are sorted
        # from smallest wavelength to largest.
        sort_indexes = [x[0] for x in sorted(enumerate(wls), key=itemgetter(1))]
        wls = [wls[x] for x in sort_indexes]
        fls = [fls[x] for x in sort_indexes]

        # Zip the wavelengths and fluxes into tuples to create the plot series.
        plot_series = [data_point(x=x, y=y) for x, y in zip(wls, fls)]

        # Create the return DataSeries object.
        return_dataseries = DataSeries('fuse', obsid, plot_series,
                                       ['FUSE_' + obsid],
                                       [fuse_xunit], [fuse_yunit], errcode)
    else:
        errcode = 1
        # Otherwise there was likely a problem: file missing on disk, etc.
        return_dataseries = DataSeries('fuse', obsid, [], [], [], [], errcode)

    # Return the DataSeries object back to the calling module.
    return return_dataseries
#--------------------