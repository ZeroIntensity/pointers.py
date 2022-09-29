#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <signal.h>
#include <setjmp.h>
#include <stdbool.h>
#define GETOBJ PyObject* obj; if (!PyArg_ParseTuple(args, "O", &obj)) return NULL
#define CALL_ATTR(ob, attr) PyObject_Call(PyObject_GetAttrString(ob, attr), PyTuple_New(0), NULL)
static jmp_buf buf;

static PyObject* add_ref(PyObject* self, PyObject* args) {
    GETOBJ;
    Py_INCREF(obj);
    Py_RETURN_NONE;
}

static PyObject* remove_ref(PyObject* self, PyObject* args) {
    GETOBJ;
    Py_DECREF(obj);
    Py_RETURN_NONE;
}

static PyObject* set_ref(PyObject* self, PyObject* args) {
    PyObject* obj;
    Py_ssize_t count;
    if (!PyArg_ParseTuple(args, "On", &obj, &count)) return NULL;
    obj->ob_refcnt = count; // i dont care
    Py_RETURN_NONE;
}

static PyObject* force_set_attr(PyObject* self, PyObject* args) {
    PyTypeObject* type;
    PyObject* value;
    char* key;

    if (!PyArg_ParseTuple(args, "OsO", &type, &key, &value)) return NULL;

    PyDict_SetItemString(type->tp_dict, key, value);
    PyType_Modified(type);

    Py_RETURN_NONE;
}

void handler(int signum) {
    longjmp(buf, 1);
}

static PyObject* handle(PyObject* self, PyObject* args) {
    PyObject* func;
    PyObject* params = NULL;
    PyObject* kwargs = NULL;
    PyObject* faulthandler = PyImport_ImportModule("faulthandler");

    if (!PyArg_ParseTuple(
            args,
            "O|O!O!",
            &func,
            &PyTuple_Type,
            &params,
            &PyDict_Type,
            &kwargs
        )
    ) return NULL;

    if (!params) params = PyTuple_New(0);
    if (!kwargs) kwargs = PyDict_New();

    int val = setjmp(buf);

    CALL_ATTR(faulthandler, "disable");
    // faulthandler needs to be shut off in case of a segfault or its message will still print

    if (setjmp(buf)) {
        CALL_ATTR(faulthandler, "enable");
        PyCodeObject* code = PyFrame_GetCode(PyEval_GetFrame());

        PyErr_Format(
            PyExc_RuntimeError,
            "segment violation occured during execution of %S",
            code->co_name
        );
        return NULL;
    }

    PyObject* result = PyObject_Call(func, params, kwargs);

    if (!result) return NULL;

    CALL_ATTR(faulthandler, "enable");
    return result;
}

static PyMethodDef methods[] = {
    {"add_ref", add_ref, METH_VARARGS, "Increment the reference count on the target object."},
    {"remove_ref", remove_ref, METH_VARARGS, "Decrement the reference count on the target object."},
    {"force_set_attr", force_set_attr, METH_VARARGS, "Force setting an attribute on the target type."},
    {"set_ref", set_ref, METH_VARARGS, "Set the reference count on the target object."},
    {"handle", handle, METH_VARARGS, "Enable the SIGSEGV handler."},
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
    if (signal(SIGSEGV, handler) == SIG_ERR) {
        PyErr_SetString(PyExc_RuntimeError, "failed to setup SIGSEGV handler");
        return NULL;
    }

    return PyModule_Create(&module);
}
