#! /usr/bin/env python3

import sys
if sys.version_info[0] < 3:
    sys.exit("VPV must me run with Python3. Exiting")

from PyQt5 import QtGui
from vpv.vpv import Vpv

if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser("Volume Phenptype Viewer")
    parser.add_argument('-v', '-volumes',  dest='volumes', nargs='*', help='Volume paths seperated by spaces', default=False)
    parser.add_argument('-hm', '-heatmaps', dest='heatmaps', nargs='*', help='Heatmap paths seperated by spaces', default=False)
    parser.add_argument('-a',  '-annotations', dest='annotations', nargs='*', help='Annotations paths seperated by spaces', default=False)
    args = parser.parse_args()

    app = QtGui.QApplication(sys.argv)
    ex = Vpv()

    if args.volumes:
        ex.load_volumes(args.volumes, 'vol')
        # Can't have heatmaps loaded without any volumes loaded first
        if args.heatmaps:
            ex.load_volumes(args.heatmaps, 'heatmap')
        if args.annotations:
            ex.load_annotations(args.annotations)
    sys.exit(app.exec_())