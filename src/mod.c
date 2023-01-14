#define PY_SSIZE_T_CLEAN
#include <Python.h>
#if PY_MAJOR_VERSION != 3
#error "Python 3 is needed to build"
#endif
#if PY_MINOR_VERSION == 11
#define GET_CODE(frame) PyFrame_GetCode(frame);
#else
#define GET_CODE(frame) frame->f_code;
#endif
#include <signal.h>
#include <setjmp.h>
#include <stdbool.h>
#include <stdio.h>
#include <frameobject.h> // needed to get members of PyFrameObject
#define GETOBJ() PyObject* obj; if (!PyArg_ParseTuple(args, "O", &obj)) return NULL

#ifdef _WIN32
#include <malloc.h>
#endif

#if defined(__GNUC__)
#define ALLOCA(size) alloca(size)
#elif defined(_WIN32)
#define ALLOCA(size) _alloca(size)
#else
#define ALLOCA(size) NULL; PyErr_SetString(PyExc_RuntimeError, "stack allocations are not supported on this system!"); return NULL;
#endif

static jmp_buf buf;

static PyObject* add_ref(PyObject* self, PyObject* args) {
    GETOBJ();
    Py_INCREF(obj);
    Py_RETURN_NONE;
}

static PyObject* remove_ref(PyObject* self, PyObject* args) {
    GETOBJ();
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
            code = GET_CODE(frame);
            Py_INCREF(code);
            name = code->co_name;
        } else {
            name = PyObject_GetAttrString(func, "__name__");
        }

        // this is basically a copy of PyFrame_GetCode, which is only available on 3.9+

        PyErr_Format(
            PyExc_RuntimeError,
            "segment violation occured during execution of %S",
            name
        );

        if (code) Py_DECREF(code);
        return NULL;
    }

    PyObject* result = PyObject_Call(func, params, kwargs);
    if (!result) return NULL;
    return result;
}

static PyObject* run_stack_callback(PyObject* self, PyObject* args) {
    int size;
    PyObject* tp;
    PyObject* func;

    if (!PyArg_ParseTuple(args, "iO!O", &size, &PyType_Type, &tp, &func)) return NULL;

    void* ptr = ALLOCA(size);
    PyObject* tp_args = PyTuple_New(2);
    PyTuple_SetItem(tp_args, 0, PyLong_FromVoidPtr(ptr));
    PyTuple_SetItem(tp_args, 1, PyLong_FromLong(size));
    PyObject* obj = PyObject_Call(tp, tp_args, NULL);
    if (!obj) return NULL;

    PyObject* tup = PyTuple_New(1);
    PyTuple_SetItem(tup, 0, obj);
    PyObject* result = PyObject_Call(func, tup, NULL);
    if (!result) return NULL;
    PyObject_SetAttrString(obj, "freed", Py_True);

    Py_INCREF(result);
    return result;
}

static PyObject* force_update_locals(PyObject* self, PyObject* args) {
    PyFrameObject* f;
    PyObject* key;
    PyObject* value;

    if (!PyArg_ParseTuple(args, "O!UO", &PyFrame_Type, &f, &key, &value))
        return NULL;

    Py_INCREF(f->f_locals);
    PyObject* target = PyDict_GetItem(f->f_locals, key);
    Py_INCREF(target);

    for (int i = 0; i < PyDict_GET_SIZE(f->f_locals); i++) {
        if (f->f_localsplus[i] == target) {
            Py_DECREF(f->f_localsplus[i]);
            f->f_localsplus[i] = value;
            Py_INCREF(value);
            break;
        }
    }

    Py_DECREF(f->f_locals);
    Py_DECREF(target);

    Py_RETURN_NONE;
}

static PyMethodDef methods[] = {
    {"add_ref", add_ref, METH_VARARGS, "Increment the reference count on the target object."},
    {"remove_ref", remove_ref, METH_VARARGS, "Decrement the reference count on the target object."},
    {"force_set_attr", force_set_attr, METH_VARARGS, "Force setting an attribute on the target type."},
    {"set_ref", set_ref, METH_VARARGS, "Set the reference count on the target object."},
    {"handle", handle, METH_VARARGS, "Enable the SIGSEGV handler."},
    {"run_stack_callback", run_stack_callback, METH_VARARGS, "Run a callback with a stack allocated pointer."},
    {"force_update_locals", force_update_locals, METH_VARARGS, "Force update the locals of the target frame."},
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
    if (signal(SIGSEGV, sigsegv_handler) == SIG_ERR) {
        PyErr_SetString(
            PyExc_ImportError,
            "cant load _pointers: failed to setup SIGSEGV handler"
        );
        return NULL;
    }

    return PyModule_Create(&module);
}
