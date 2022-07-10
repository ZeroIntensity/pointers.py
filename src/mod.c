#define PY_SSIZE_T_CLEAN
#include <Python.h>

static PyObject* method_add_ref(PyObject* self, PyObject* args) {
    Py_INCREF(args);
    Py_RETURN_NONE;
}

static PyObject* method_remove_ref(PyObject* self, PyObject* args) {
    Py_DECREF(args);
    Py_RETURN_NONE;
}

static PyMethodDef PointersMethods[] = {
    {"add_ref", method_add_ref, METH_VARARGS, "Increment the reference count on the target object."},
    {"remove_ref", method_remove_ref, METH_VARARGS, "Decrement the reference count on the target object."},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef pointersmod = {
    PyModuleDef_HEAD_INIT,
    "_pointers",
    NULL,
    -1,
    PointersMethods
};

PyMODINIT_FUNC PyInit__pointers(void) {
    return PyModule_Create(&pointersmod);
}