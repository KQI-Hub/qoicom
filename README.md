# qoicom
qoicom (QOI Compression Module) is a QOI encoder and decoder written in pure Python, intended for use by the KQI Reference Software.

qoicom supports lossy QOI encoding based on relative color error, without doing image preprocessing.

## usage
qoicom comes with cqoicom.py, an executable CLI wrapper for qoicom.

`python cqoicom.py input.[ppm/qoi] output.qoi <max_error [float], default: 0>`

cqoicom defaults to error 0, which should be lossless (please submit an issue if it's not!)

## algorithm
qoicom implements lossy runs and lossy indexing. the algorithm to calculate error is

`( re * 2 + ge * 4 + be ) / 5`

where re is red difference, ge is green difference, and be is blue difference.
