#include <Python.h>

static PyMethodDef methods[] = {
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    "_pointers",
    NULL,
    -1,
    methods
};

PyMODINIT_FUNC PyInit__pointers(void) {
    return PyModule_Create(&module);
}
