#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <signal.h>
#include <setjmp.h>
#include <stdbool.h>
#include <stdio.h>
#include <frameobject.h> // needed to get members of PyFrameObject
#define GETOBJ PyObject* obj; if (!PyArg_ParseTuple(args, "O", &obj)) return NULL
#define INIT_HANDLER(sig, handle, msg) if (signal(sig, handle) == SIG_ERR) { \
        PyErr_SetString(PyExc_ImportError, msg); \
        return NULL; \
    }
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

static void sigsegv_handler(int signum) {
    longjmp(buf, 1);
}

static void sigiot_handler(int signum) {
    longjmp(buf, 2);
}

static PyObject* handle(PyObject* self, PyObject* args) {
    PyObject* func;
    PyObject* params = NULL;
    PyObject* kwargs = NULL;

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

    if (val) {
        PyFrameObject* frame = PyEval_GetFrame();
        PyObject* name;
        PyCodeObject* code = NULL;

        if (frame) {
            code = frame->f_code;
            Py_INCREF(code);
            name = code->co_name;
        } else {
            name = PyObject_GetAttrString(func, "__name__");
        }

        // this is basically a copy of PyFrame_GetCode, which is only available on 3.9+

        PyErr_Format(
            PyExc_RuntimeError,
            "%s occured during execution of %S",
            val == 1 ? "segment violation" : "python aborted",
            name
        );

        if (code) Py_DECREF(code);
        return NULL;
    }

    PyObject* result = PyObject_Call(func, params, kwargs);
    if (!result) return NULL;
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
    INIT_HANDLER(
        SIGABRT,
        sigiot_handler,
        "cant load _pointers: failed to setup SIGIOT handler"
    );
    INIT_HANDLER(
        SIGSEGV,
        sigsegv_handler,
        "cant load _pointers: failed to setup SIGSEGV handler"
    );

    return PyModule_Create(&module);
}
