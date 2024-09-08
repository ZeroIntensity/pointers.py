#define Py_BUILD_CORE
#include <Python.h>
#include "internal/pycore_object.h"
#define METHOD(name, flags) {#name, name, flags, NULL}

static PyObject *
incref(PyObject *self, PyObject *ob)
{
    Py_INCREF(ob);
    Py_RETURN_NONE;
}


static PyObject *
decref(PyObject *self, PyObject *ob)
{
    Py_DECREF(ob);
    Py_RETURN_NONE;
}

static PyObject *
setref(PyObject *self, PyObject *args)
{
    PyObject *ob;
    Py_ssize_t refcount;

    if (!PyArg_ParseTuple(args, "On", &ob, &refcount))
        return NULL;

    Py_SET_REFCNT(ob, refcount);
    Py_RETURN_NONE;
}

static PyObject *
deref(PyObject *self, PyObject *addr)
{
    if (!PyLong_Check(addr))
    {
        PyErr_SetString(PyExc_TypeError, "expected integer as address");
        return NULL;
    }

    void *ptr = PyLong_AsVoidPtr(addr);
    PyObject *obj = (PyObject *) ptr;
    Py_INCREF(obj);
    return obj;
}

static PyObject *
getref(PyObject *self, PyObject *ob)
{
    return PyLong_FromSsize_t(Py_REFCNT(ob));
}

static PyObject *
setimmortal(PyObject *self, PyObject *ob)
{
    #if Py_MINOR_VERSION >= 12
    _Py_SetImmortal(ob);
    #endif
    Py_RETURN_NONE;
}

static PyMethodDef _pointers_methods[] = {
    METHOD(incref, METH_O),
    METHOD(decref, METH_O),
    METHOD(setref, METH_VARARGS),
    METHOD(deref, METH_O),
    METHOD(getref, METH_O),
    METHOD(setimmortal, METH_O),
    {NULL, NULL, 0, NULL}
};

static PyModuleDef _pointers_module = {
    .m_name = "_pointers",
    .m_methods = _pointers_methods
};

PyMODINIT_FUNC
PyInit__pointers()
{
    return PyModuleDef_Init(&_pointers_module);
}
