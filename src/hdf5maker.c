#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <numpy/arrayobject.h>
#include "eiger_defs.h"
#include "raw_file.h"

#include <stdio.h>
#include <unistd.h>

/* Docstrings */
static char module_docstring[] =
    "sls_cmodule provies access to compiled c++ and ROOT functions supporting "
    "detector calibration. The library uses numpy arrays as input and return "
    "values.";

/* Available functions */
static PyObject *read_raw(PyObject *self, PyObject *args);

static PyArray_Descr *get_frame_header_dt();

/* Module specification */
static PyMethodDef module_methods[] = {
    {"read_frame", (PyCFunction)read_raw, METH_VARARGS, "hej"},
    // {"find_trimbits", find_trimbits, METH_VARARGS, find_trimbits_doc},
    // {"vrf_fit", vrf_fit, METH_VARARGS, find_trimbits_doc},
    // {"hist", hist, METH_VARARGS, find_trimbits_doc},
    // {"gaus_float", gaus_float, METH_VARARGS, find_trimbits_doc},
    {NULL, NULL, 0, NULL}};

static struct PyModuleDef hdf5maker_def = {
    PyModuleDef_HEAD_INIT, "_hdf5maker", module_docstring, -1, module_methods};

/* Initialize the module */
PyMODINIT_FUNC PyInit__hdf5maker(void) {
    PyObject *m = PyModule_Create(&hdf5maker_def);
    if (m == NULL) {
        return NULL;
    }

    /* Load `numpy` functionality. */
    import_array();

    PyArray_Descr *obj = get_frame_header_dt();
    PyObject_SetAttrString(m, "frame_header_dt", (PyObject*)obj);
    Py_DECREF(obj);
    return m;
}

static PyObject *read_raw(PyObject *self, PyObject *args) {
    PyObject *fobj;
    int n_frames, dr;
    if (!PyArg_ParseTuple(args, "OII", &fobj, &dr, &n_frames))
        return NULL;

    int fd = PyObject_AsFileDescriptor(fobj);
    if (fd < 0)
        return NULL;

    // Allocate data for header and frames
    PyArray_Descr *dtype = get_frame_header_dt();
    const npy_intp header_dims[] = {n_frames};
    PyObject *header = PyArray_SimpleNewFromDescr(1, header_dims, dtype);
    npy_intp dims[] = {n_frames, PORT_NROWS_WGAP, PORT_NCOLS_WGAP};
    PyObject *data = PyArray_SimpleNew(3, dims, dr_to_dtype(dr));

    const size_t bytes_to_copy = dr * PORT_NROWS * PORT_NCOLS / 8;
    sls_detector_header* h_ptr = PyArray_BYTES((PyArrayObject*)header);
    char *frame_ptr = PyArray_BYTES((PyArrayObject*)data);
    PyArray_FILLWBYTE((PyArrayObject*)data, 0);
    const int stride = PyArray_STRIDE((PyArrayObject*)data, 0);
    char *buffer = malloc(bytes_to_copy+sizeof(sls_detector_header));

    char * expanded_buffer = NULL;
    if (dr == 4){
        expanded_buffer = malloc(bytes_to_copy * 2);
    }

    for (int i = 0; i < n_frames; ++i) {
        size_t sz = read(fd, buffer, bytes_to_copy+sizeof(sls_detector_header));
        memcpy(h_ptr, buffer, sizeof(sls_detector_header));
        if(dr == 4){
            //expand 4->8 bits
        }else{
            copy_to_place(frame_ptr, buffer+sizeof(sls_detector_header), dr, h_ptr->row, h_ptr->column);
        }
        frame_ptr += stride;
        h_ptr++;
    }

    free(buffer);
    free(expanded_buffer);

    PyObject *ret = PyTuple_Pack(2, header, data);
    Py_DECREF(header);
    Py_DECREF(data);
    return ret;
}

static PyArray_Descr *get_frame_header_dt() {
    // Move this to a function that gets run on init
    PyObject *dtype_dict;
    PyArray_Descr *dtype;
    dtype_dict = Py_BuildValue(
        "[(s, s), (s, s), (s, s), (s, s), (s, s), (s, s), (s, s), (s, s), (s, "
        "s), (s, s), (s, s), (s, s), (s, s), (s, s)]",
        "Frame Number", "u8", "SubFrame Number/ExpLength", "u4",
        "Packet Number", "u4", "Bunch ID", "u8", "Timestamp", "u8", "Module Id",
        "u2", "Row", "u2", "Column", "u2", "Reserved", "u2", "Debug", "u4",
        "Round Robin Number", "u2", "Detector Type", "u1", "Header Version",
        "u1", "Packets Caught Mask", "V64");

    PyArray_DescrConverter(dtype_dict, &dtype);
    Py_DECREF(dtype_dict);
    return dtype;
}