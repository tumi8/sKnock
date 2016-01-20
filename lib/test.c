#include <python2.7/Python.h>
#include <assert.h>

#define IMPORT_MODULE "testdir.hello"

#define LOG(...)\
  fprintf(stderr, __VA_ARGS__);

int main(int argc, char *argv[])
{
  PyObject *py_module;
  PyObject *py_str_cwd;
  PyObject *py_list_path;
  char *cwd;
  PyObject *py_list_syspath;

  Py_SetProgramName(argv[0]);  /* optional but recommended */
  Py_Initialize();
  py_list_path = PyList_New(1);
  cwd = getcwd(NULL, 0);
  assert (NULL != cwd);
  py_str_cwd = PyString_FromString(cwd);
  PyList_SetItem(py_list_path, 0, py_str_cwd);
  free(cwd); cwd = NULL;

  py_list_syspath = PySys_GetObject("path");
  py_list_syspath = PySequence_InPlaceConcat(py_list_syspath, py_list_path);
  py_list_path = NULL;
  py_list_syspath = NULL;       /* py_list_syspath is a borrowed reference */

  py_module = PyImport_ImportModule(IMPORT_MODULE);
  if (NULL == py_module)
    PyErr_Print();
  assert (PyModule_Check(py_module));
  PyObject *py_dict_module;
  py_dict_module = PyModule_GetDict(py_module);
  assert (NULL != py_dict_module);
  PyObject *py_func_hello = NULL;
  /* Dictionary get gives a borrowed reference */
  py_func_hello = PyDict_GetItemString(py_dict_module, "hello");
  assert (NULL != py_func_hello);
  assert (PyFunction_Check (py_func_hello));

  PyObject *py_func_hello_args = NULL;
  py_func_hello_args = Py_BuildValue("(s)", "Python from C");
  PyObject *py_return;
  if (NULL == (py_return = PyObject_CallObject(py_func_hello,
                                               py_func_hello_args)))
    PyErr_Print();
  else
    Py_DECREF(py_return);

  py_return = PyObject_CallFunction(py_func_hello,
                                    "(s)", "World from C");
  Py_XDECREF (py_return);
  /* PyRun_SimpleString("from time import time,ctime\n" */
  /*                    "print 'Today is',ctime(time())\n" */
  /*                    "import sys\n" */
  /*                    "print repr(sys.path)"); */
  Py_Finalize();
  return 0;
}
