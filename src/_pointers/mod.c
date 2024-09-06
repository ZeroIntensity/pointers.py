#include <Python.h>

static PyModuleDef _pointers_module = {
    .m_name = "_pointers"
};

PyMODINIT_FUNC
PyInit__pointers()
{
    return PyModuleDef_Init(&_pointers_module);
}
