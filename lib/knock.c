/*
 This file is part of Knock
 Copyright (C) 2015 Sree Harsha Totakura

 This program is free software; you can redistribute it and/or modify it under
 the terms of the GNU General Public License as published by the Free Software
 Foundation; either version 3, or (at your option) any later version.

 This program is distributed in the hope that it will be useful, but WITHOUT ANY
 WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
 PARTICULAR PURPOSE.  See the GNU General Public License for more details.

 You should have received a copy of the GNU General Public License along with
 this program.  If not, see <http://www.gnu.org/licenses/>.
*/

/**
 * @file lib/knock.c
 * @brief C library wrapper for knock's client interface
 * @author Sree Harsha Totakura <sreeharsha@totakura.in>
 */

#include <python2.7/Python.h>
#include <assert.h>

/* The path of the client interface module */
#define IMPORT_MODULE_PATH "knock_client.modules.ClientInterface"

/**
 * Pointers  to the API functions
 */
static PyObject *api_init;
static PyObject *api_init_defaults;
static PyObject *api_knock;

/**
 * Initializes the library.  This function should be called exactly once before
 * using any other functions of this library.
 *
 * Initializes the underlying python system and paths required for finding the
 * correct python modules for Knock's client interface.
 *
 * @return 0 upon success; -1 upon error
 */
int
knock_init() {
  PyObject *py_module_dict;

  Py_Initialize ();
  {
    PyObject *py_list_path;
    PyObject *py_list_syspath;
    char *kpath;
    PyObject *py_str_kpath;
    kpath = getenv ("KNOCKPATH");
    assert (NULL != kpath);
    py_str_kpath = PyString_FromString (kpath);
    py_list_path = PyList_New (1);
    PyList_SetItem (py_list_path, 0, py_str_kpath);
    py_list_syspath = PySys_GetObject ("path"); /* borrowed reference; do not decref! */
    py_list_syspath = PySequence_InPlaceConcat (py_list_syspath, py_list_path);
    Py_DECREF (py_list_path);
  }
  {
    /* module import */
    PyObject *py_module;
    py_module = PyImport_ImportModule (IMPORT_MODULE_PATH);
    if (NULL == py_module)
    {
      PyErr_Print ();
      return -1;
    }
    assert (PyModule_Check(py_module));
    py_module_dict = PyModule_GetDict (py_module);
    Py_DECREF (py_module);
    py_module = NULL;
    assert (NULL != py_module_dict);
  }
  /* initialise api functions */
  api_init = PyDict_GetItemString (py_module_dict, "init");
  api_init_defaults = PyDict_GetItemString (py_module_dict, "init_defaults");
  api_knock = PyDict_GetItemString (py_module_dict, "knock");
  Py_DECREF (py_module_dict);
  py_module_dict = NULL;
  return 0;
}

/**
 * Opaque knock handle
 */
struct KNOCK_Handle
{
  /**
   * DLL pointers
   */
  struct KNOCK_Handle *next;
  struct KNOCK_Handle *prev;

  /**
   * The interface object
   */
  PyObject *interface;
};

/**
 * Function to create a new knock handle
 *
 * @param timeout number of seconds to wait before retrying the knock attempt
 * @param retries number of times to retry
 * @param verify flag to verify the server certificate; 0 to disable, 1 to
 *          enable
 * @param server_cert_path path of the server certificate
 * @param client_cert_path path of the client certificate
 * @param client_cert_passwd password for opening the client certificate.  If
 *          NULL the empty string will be used as a password
 * @return the knock handle; NULL upon error
 */
struct KNOCK_Handle *
knock_new (unsigned int timeout,
           unsigned int retries,
           int verify,
           const char *server_cert_path,
           const char *client_cert_path,
           const char *client_cert_passwd)
{
  PyObject *py_args;
  PyObject *py_return;
  struct KNOCK_Handle *handle;

  assert (NULL != server_cert_path);
  assert (NULL != client_cert_path);
  if (NULL == client_cert_passwd)
    client_cert_passwd = "";
  py_args = Py_BuildValue ("(I I i s s s)",
                           timeout,
                           retries,
                           verify,
                           server_cert_path,
                           client_cert_path,
                           client_cert_passwd);
  assert (NULL != api_init);
  py_return = PyObject_CallObject (api_init,
                                   py_args);
  Py_DECREF (py_args);
  if (NULL == py_return)
  {
    PyErr_Print ();
    return NULL;
  }
  handle = malloc (sizeof (struct KNOCK_Handle));
  handle->interface = py_return;
  return handle;
}


/**
 * Create knock handle with default parameters
 *
 * @param client_cert_passwd password for opening the client certificate.  If
 *          NULL the empty string will be used as a password
 * @return the knock handle; NULL upon error
 */
struct KNOCK_Handle *
knock_default_new (const char *client_cert_passwd)
{
  PyObject *py_args;
  PyObject *py_return;
  struct KNOCK_Handle *handle;

  if (NULL == client_cert_passwd)
    client_cert_passwd = "";
  py_args = Py_BuildValue ("(s)", client_cert_passwd);
  assert (NULL != api_init_defaults);
  py_return = PyObject_CallObject (api_init_defaults,
                                   py_args);
  Py_DECREF (py_args);
  if (NULL == py_return)
  {
    PyErr_Print ();
    return NULL;
  }
  handle = malloc (sizeof (struct KNOCK_Handle));
  handle->interface = py_return;
  return handle;
}


/**
 * Knock the given port on the given host.
 *
 * @param host the hostname of the target host to knock
 * @param port the port to open
 * @param protocol 1 for TCP; 0 for UDP
 * @return ??(should be a socket?)
 */
int
knock_knock(const char *host,
            unsigned short port,
            int protocol)
{
  PyObject *py_args;
  PyObject *py_return;

  assert (NULL != host);
  py_args = Py_BuildValue ("(s H i)",
                           host,
                           port,
                           protocol);
  py_return = PyObject_CallObject (api_knock,
                                   py_args);
  Py_DECREF (py_args);
  if (NULL == py_return)
  {
    PyErr_Print ();
    return -1;
  }
  /* FIXME */
  assert (0);
  return 0;
}
