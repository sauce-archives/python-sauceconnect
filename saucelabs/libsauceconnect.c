#include <Python.h>
#include <sauceconnect.h>
#include <string.h>


/**
 * Utility methods for marshalling `sc_ctx` struct.
 **/
static void del_sc_ctx(PyObject *obj)
{
    free(PyCapsule_GetPointer(obj, "sc_ctx"));
}

static struct sc_ctx *PyObject_AsCtx(PyObject *obj)
{
    struct sc_ctx *ctx = (struct sc_ctx *) PyCapsule_GetPointer(obj, "sc_ctx");

    return ctx;
}

static PyObject *PyObject_FromCtx(struct sc_ctx *ctx, int must_free)
{
    return PyCapsule_New(ctx, "sc_ctx", must_free ? del_sc_ctx : NULL);
}

/*
 * Only works when there is a single argument, which is the context
 */
static struct sc_ctx *get_context(PyObject *args)
{
    PyObject *py_ctx = NULL;
    struct sc_ctx *ctx = NULL;

    if(!PyArg_ParseTuple(args, "O", &py_ctx)) {
        return NULL;
    }
    if(!(ctx =  PyObject_AsCtx(py_ctx))) {
        return NULL;
    }

    return ctx;
}




static PyObject *
connect_sc_new(PyObject *self, PyObject *args)
{
    struct sc_ctx *ctx = sc_new();

    PyObject *py_ctx = PyObject_FromCtx(ctx, 0);
    Py_INCREF(py_ctx);
    return Py_BuildValue("O", py_ctx);
}

static PyObject *
connect_sc_free(PyObject *self, PyObject *args)
{
    struct sc_ctx *ctx = get_context(args);
    sc_free(ctx);

    return Py_BuildValue("s", NULL);
}

static PyObject *
connect_sc_get_int(PyObject *self, PyObject *args)
{
    PyObject *py_ctx;
    struct sc_ctx *ctx;
    int param;
    int value;

    if(!PyArg_ParseTuple(args, "Oi", &py_ctx, &param)) {
        return Py_BuildValue("i", 0);
    }
    if(!(ctx =  PyObject_AsCtx(py_ctx))) {
        return NULL;
    }

    sc_get(ctx, param, &value, sizeof(value));
    return Py_BuildValue("i", value);
}

static PyObject *
connect_sc_get_string(PyObject *self, PyObject *args)
{
    PyObject *py_ctx;
    struct sc_ctx *ctx;
    int param;
    char *value = NULL;

    if(!PyArg_ParseTuple(args, "Oi", &py_ctx, &param)) {
        return Py_BuildValue("i", 0);
    }
    if(!(ctx =  PyObject_AsCtx(py_ctx))) {
        return NULL;
    }

    sc_get(ctx, param, &value, sizeof(value));
    return Py_BuildValue("s", value);
}

static PyObject *
connect_sc_set_int(PyObject *self, PyObject *args)
{
    PyObject *py_ctx;
    struct sc_ctx *ctx;
    int param;
    int value;

    if(!PyArg_ParseTuple(args, "Oii", &py_ctx, &param, &value)) {
        return Py_BuildValue("i", 0);
    }
    if(!(ctx =  PyObject_AsCtx(py_ctx))) {
        return NULL;
    }

    int status = sc_set(ctx, param, &value);
    return Py_BuildValue("i", status);
}

static PyObject *
connect_sc_set_string(PyObject *self, PyObject *args)
{
    PyObject *py_ctx;
    struct sc_ctx *ctx;
    int param;
    char *value;

    if(!PyArg_ParseTuple(args, "Ois", &py_ctx, &param, &value)) {
        return NULL;
    }
    if(!(ctx =  PyObject_AsCtx(py_ctx))) {
        return NULL;
    }

    int status = sc_set(ctx, param, value);
    return Py_BuildValue("i", status);
}

static PyObject *
connect_sc_init(PyObject *self, PyObject *args)
{
    struct sc_ctx *ctx = get_context(args);

    int status = sc_init(ctx);
    return Py_BuildValue("i", status);
}

static PyObject *
connect_sc_run(PyObject *self, PyObject *args)
{
    struct sc_ctx *ctx = get_context(args);

    int status = sc_run(ctx);
    return Py_BuildValue("i", status);
}

static PyObject *
connect_sc_stop(PyObject *self, PyObject *args)
{
    struct sc_ctx *ctx = get_context(args);

    if (sc_status(ctx) == SC_STATUS_RUNNING)
        sc_stop(ctx);

    return Py_BuildValue("i", 0);
}

static PyObject *
connect_sc_status(PyObject *self, PyObject *args)
{
    struct sc_ctx *ctx = get_context(args);

    int status = sc_status(ctx);
    return Py_BuildValue("i", status);
}

static PyObject *
connect_sc_get_info(PyObject *self, PyObject *args)
{
    PyObject *py_ctx;
    struct sc_ctx *ctx;
    int what;
    int info;

    if(!PyArg_ParseTuple(args, "Oi", &py_ctx, &what)) {
        return NULL;
    }
    if(!(ctx =  PyObject_AsCtx(py_ctx))) {
        return NULL;
    }

    sc_get_info(ctx, what, &info);
    return Py_BuildValue("i", info);
}







static PyMethodDef ConnectMethods[] = {
    { "sc_new",        connect_sc_new,        METH_NOARGS,
        "Create a new Sauce Connect context" },
    { "sc_free",       connect_sc_free,       METH_VARARGS,
        "Free a new Sauce Connect context" },
    { "sc_get_int",    connect_sc_get_int,    METH_VARARGS,
        "Getter for configuration parameters" },
    { "sc_get_string", connect_sc_get_string, METH_VARARGS,
        "Getter for configuration parameters" },
    { "sc_set_int",    connect_sc_set_int,    METH_VARARGS,
        "Setter for configuration parameters" },
    { "sc_set_string", connect_sc_set_string, METH_VARARGS,
        "Setter for configuration parameters" },
    { "sc_init",       connect_sc_init,       METH_VARARGS,
        "Initialize tunnel" },
    { "sc_run",        connect_sc_run,        METH_VARARGS,
        "Run the main event loop" },
    { "sc_stop",       connect_sc_stop,       METH_VARARGS,
        "Stop the Sauce Connect main event loop" },
    { "sc_status",     connect_sc_status,     METH_VARARGS,
        "Get the current status of Sauce Connect" },
    { "sc_get_info",   connect_sc_get_info,   METH_VARARGS,
        "Get information on Sauce Connect internals" },
    {NULL, NULL, 0, NULL}        /* Sentinel */

};

PyMODINIT_FUNC
initlibsauceconnect(void)
{
    PyObject *module = Py_InitModule("libsauceconnect", ConnectMethods);

    // mirror constants from sauceconnect.h into Python
    PyModule_AddIntConstant(module, "SC_PARAM_IS_SERVER", SC_PARAM_IS_SERVER);
    PyModule_AddIntConstant(module, "SC_PARAM_KGP_HOST", SC_PARAM_KGP_HOST);
    PyModule_AddIntConstant(module, "SC_PARAM_KGP_PORT", SC_PARAM_KGP_PORT);
    PyModule_AddIntConstant(module, "SC_PARAM_EXT_HOST", SC_PARAM_EXT_HOST);
    PyModule_AddIntConstant(module, "SC_PARAM_EXT_PORT", SC_PARAM_EXT_PORT);
    PyModule_AddIntConstant(module, "SC_PARAM_LOGFILE", SC_PARAM_LOGFILE);
    PyModule_AddIntConstant(module, "SC_PARAM_LOGLEVEL", SC_PARAM_LOGLEVEL);
    PyModule_AddIntConstant(module, "SC_PARAM_MAX_LOGSIZE", SC_PARAM_MAX_LOGSIZE);
    PyModule_AddIntConstant(module, "SC_PARAM_CERTFILE", SC_PARAM_CERTFILE);
    PyModule_AddIntConstant(module, "SC_PARAM_KEYFILE", SC_PARAM_KEYFILE);
    PyModule_AddIntConstant(module, "SC_PARAM_LOCAL_PORT", SC_PARAM_LOCAL_PORT);
    PyModule_AddIntConstant(module, "SC_PARAM_USER", SC_PARAM_USER);
    PyModule_AddIntConstant(module, "SC_PARAM_API_KEY", SC_PARAM_API_KEY);
    PyModule_AddIntConstant(module, "SC_PARAM_PROXY", SC_PARAM_PROXY);
    PyModule_AddIntConstant(module, "SC_PARAM_PROXY_USERPWD", SC_PARAM_PROXY_USERPWD);
    PyModule_AddIntConstant(module, "SC_PARAM_RECONNECT", SC_PARAM_RECONNECT);

    PyModule_AddIntConstant(module, "SC_STATUS_RUNNING", SC_STATUS_RUNNING);
    PyModule_AddIntConstant(module, "SC_STATUS_EXITING", SC_STATUS_EXITING);

    PyModule_AddIntConstant(module, "SC_INFO_KGP_IS_CONNECTED", SC_INFO_KGP_IS_CONNECTED);
    PyModule_AddIntConstant(module, "SC_INFO_KGP_LAST_STATUS_CHANGE", SC_INFO_KGP_LAST_STATUS_CHANGE);
}
