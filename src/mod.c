#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <signal.h>
#include <setjmp.h>
#include <frameobject.h>

static PyObject* SegvError = NULL;
static jmp_buf buf;

static PyObject* set_ref(PyObject* self, PyObject* args) {
    PyObject* obj;
    Py_ssize_t count;
    if (!PyArg_ParseTuple(
        args,
        "On",
        &obj,
        &count
        ))
        return NULL;

    Py_SET_REFCNT(
        obj,
        count
    );
    Py_RETURN_NONE;
}

static void jump(int signum) {
    assert(signum == 11);
    longjmp(
        buf,
        1
    );
}

static PyObject* segv_handler(PyObject* self, PyObject* args) {
    PyObject* callable;
    PyObject* params = NULL;
    PyObject* kwargs = NULL;

    if (!PyArg_ParseTuple(
        args,
        "O|O!O!",
        &callable,
        &PyTuple_Type,
        &params,
        &PyDict_Type,
        &kwargs
        ))
        return NULL;

    Py_XINCREF(params);
    if (!params) params = PyTuple_New(0);
    int value = setjmp(buf);

    if (value) {
        // SIGSEGV occurred
        signal(
            SIGSEGV,
            SIG_DFL
        );
        Py_XDECREF(params);

        PyObject* name;
        PyFrameObject* frame = PyEval_GetFrame();

        if (frame) {
            PyCodeObject* code = frame->f_code;
            name = code->co_name;
        } else {
            // frame could be NULL because of weird python
            name = PyObject_GetAttrString(
                callable,
                "__name__"
            );
        }

        if (!name)
            return NULL;

        Py_INCREF(name);

        PyErr_Format(
            SegvError,
            "segmentation fault occurred during execution of %S",
            name
        );

        Py_DECREF(name);
        return NULL;
    }

    if (signal(
        SIGSEGV,
        jump
        ) == SIG_ERR) {
        PyErr_SetString(
            PyExc_RuntimeError,
            "failed to set signal handler"
        );
        Py_XDECREF(params);
        return NULL;
    };
    PyObject* result = PyObject_Call(
        callable,
        params,
        kwargs
    );
    signal(
        SIGSEGV,
        SIG_DFL
    );

    Py_XDECREF(params);
    if (!result)
        return NULL;

    return result;
}

static PyMethodDef methods[] = {
    {"set_ref", set_ref, METH_VARARGS, NULL},
    {"handle", segv_handler, METH_VARARGS, NULL},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef mod_def = {
    PyModuleDef_HEAD_INIT,
    "_pointers",
    NULL,
    -1,
    methods
};

PyMODINIT_FUNC PyInit__pointers(void) {
    PyObject* module = PyModule_Create(&mod_def);
    if (!module) return NULL;

    SegvError = PyErr_NewException(
        "_pointers.SegvError",
        NULL,
        NULL
    );
    if (!SegvError) {
        Py_DECREF(module);
        return NULL;
    }

    if (PyModule_AddObject(
        module,
        "SegvError",
        SegvError
        ) < 0) {
        Py_DECREF(module);
        return NULL;
    }

    return module;
}
