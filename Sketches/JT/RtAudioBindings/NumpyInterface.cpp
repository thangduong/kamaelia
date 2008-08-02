#define PY_ARRAY_UNIQUE_SYMBOL RtAudio_Numeric_PyArray_API
#include "Python.h"
#include <numpy/arrayobject.h>
#include "RtAudio.h"

void importNumpy() {
    import_array();
}

int formatToType(RtAudioFormat format) {
    switch (format) {
        case RTAUDIO_SINT8:
            return NPY_INT8;
        case RTAUDIO_SINT16:
            return NPY_INT16;
        case RTAUDIO_SINT24:
            // Numpy has no Int24 type, so use Int32 instead
            return NPY_INT32;
        case RTAUDIO_SINT32:
            return NPY_INT32;
        case RTAUDIO_FLOAT32:
            return NPY_FLOAT32;
        case RTAUDIO_FLOAT64:
            return NPY_FLOAT64;
    }
    return -1;
}

PyObject *bufferToArray(char *buffer, unsigned int bufferSize,
                       RtAudioFormat format) {
    int dims[1];
    dims[0] = bufferSize;
    PyArrayObject *array = (PyArrayObject *) PyArray_SimpleNewFromData(1, dims,
                                                formatToType(format), buffer);
    return PyArray_Return(array);
}

char *arrayToBuffer(PyObject *array) {
    return PyArray_BYTES(array);
}

unsigned int arraySize(PyObject *array) {
    return PyArray_ITEMSIZE(array);
}
