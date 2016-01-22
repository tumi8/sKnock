#include <python2.7/Python.h>
#include <assert.h>

#define IMPORT_MODULE "knock_client.modules.ClientInterface"

#define LOG(...)\
  fprintf(stderr, __VA_ARGS__);

int main(int argc, char *argv[])
{
  PyObject *py_module;
  PyObject *py_str_kpath;
  PyObject *py_list_path;
  char *kpath;
  PyObject *py_list_syspath;

  Py_SetProgramName(argv[0]);  /* optional but recommended */
  Py_Initialize();
  py_list_path = PyList_New(1);
  kpath = getenv("KNOCKPATH");
  assert (NULL != kpath);
  py_str_kpath = PyString_FromString(kpath);
  PyList_SetItem(py_list_path, 0, py_str_kpath);
  kpath = NULL;

  py_list_syspath = PySys_GetObject("path");
  py_list_syspath = PySequence_InPlaceConcat(py_list_syspath, py_list_path);
  Py_DECREF(py_list_path);
  py_list_path = NULL;
  py_list_syspath = NULL;       /* py_list_syspath is a borrowed reference */

  py_module = PyImport_ImportModule(IMPORT_MODULE);
  if (NULL == py_module)
    PyErr_Print();
  assert (PyModule_Check(py_module));
  PyObject *py_dict_module;
  py_dict_module = PyModule_GetDict(py_module);
  Py_DECREF (py_module); py_module = NULL;
  assert (NULL != py_dict_module);
  PyObject *py_func_knock_init = NULL;
  /* Dictionary get gives a borrowed reference */
  py_func_knock_init = PyDict_GetItemString(py_dict_module, "init_defaults");
  py_dict_module = NULL;         /* borrowed reference! */
  assert (NULL != py_func_knock_init);
  assert (PyFunction_Check (py_func_knock_init));

  PyObject *py_args_knock_init = NULL;
  py_args_knock_init = Py_BuildValue("(s)", "knockpassword");
  PyObject *py_return;
  if (NULL == (py_return = PyObject_CallObject(py_func_knock_init,
                                               py_args_knock_init)))
  {
    fprintf(stderr, "Failed to create interface object\n");
    PyErr_Print();
    goto cleanup;
  }
  PyObject_Print(py_return, stdout, Py_PRINT_RAW);
  Py_DECREF(py_return);

 cleanup:
  Py_DECREF (py_args_knock_init);
  Py_Finalize();
  return 0;
}
