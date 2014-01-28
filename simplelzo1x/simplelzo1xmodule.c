/* simplelzo1xmodule.c -- Simple Python binding for the LZO compression library, specifically the lzo1x_1 decompression (version 1.00 of LZO, used in E-Safenet).

   Author: Jan Laan & Cedric Van Bockhaven, 2014
   Based on the LZO Python binding by Markus F.X.J. Oberhumer

   LZO is Copyright (C) 1996 - 2011 Markus F.X.J. Oberhumer

   The LZO library is free software; you can redistribute it and/or
   modify it under the terms of the GNU General Public License as
   published by the Free Software Foundation; either version 2 of
   the License, or (at your option) any later version.

   The LZO library is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with the LZO library; see the file COPYING.
   If not, write to the Free Software Foundation, Inc.,
   59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

   Markus F.X.J. Oberhumer
   <markus@oberhumer.com>
   http://www.oberhumer.com/opensource/lzo/
 */


#define MODULE_VERSION  "1.1"

#include <Python.h>
#include "lzo/lzo1x.h"

#if !defined(LZO_VERSION) || (LZO_VERSION != 0x1000)
	#error "Need exact LZO version 1.00"
#endif

#undef UNUSED
#define UNUSED(var)     ((void)&var)

static PyObject *LzoError;

static char compress__doc[] = "compress(str): Compresses a string with E-Safenet's lzo1x.\n";
static char decompress__doc[] = "decompress(str): Decompress a string with E-Safenet's lzo1x\n";

static PyObject *
compress(PyObject *dummy, PyObject *args)
{
    PyObject *result_str;
    lzo_voidp wrkmem = NULL;
    const lzo_bytep in;
    lzo_bytep out;
    lzo_uint in_len;
    lzo_uint out_len;
    lzo_uint new_len;
    int len;
    int err;

    /* init */
    UNUSED(dummy);
    if (!PyArg_ParseTuple(args, "s#", &in, &len))
        return NULL;
    if (len < 0)
        return NULL;
    in_len = len;
    out_len = in_len + in_len / 64 + 16 + 3;

    /* alloc buffers */
    result_str = PyString_FromStringAndSize(NULL, out_len);
    if (result_str == NULL)
        return PyErr_NoMemory();

    wrkmem = (lzo_voidp) PyMem_Malloc(LZO1X_MEM_COMPRESS * 2);

    if (wrkmem == NULL)
    {
        Py_DECREF(result_str);
        return PyErr_NoMemory();
    }

    /* compress */
    out = (lzo_bytep) PyString_AsString(result_str);
    new_len = out_len;

    out[0] = 0xf0;
    err = lzo1x_1_compress(in, in_len, out/*-+5*/, &new_len, wrkmem);

    PyMem_Free(wrkmem);
    if (err != LZO_E_OK || new_len > out_len)
    {
        /* this should NEVER happen */
        Py_DECREF(result_str);
        PyErr_Format(LzoError, "Error %i while compressing data", err);
        return NULL;
    }

    /* save uncompressed length /
    out[1] = (unsigned char) ((in_len >> 24) & 0xff);
    out[2] = (unsigned char) ((in_len >> 16) & 0xff);
    out[3] = (unsigned char) ((in_len >>  8) & 0xff);
    out[4] = (unsigned char) ((in_len >>  0) & 0xff);

    /* return */
    if (new_len != out_len)
        _PyString_Resize(&result_str, new_len);
    return result_str;
}

static PyObject *
decompress(PyObject *self, PyObject *args)
{
    PyObject *out_string;
    const lzo_bytep in;
    lzo_bytep out;
    lzo_uint in_len;
    lzo_uint out_len;
    lzo_uint new_len;
    int len;
    int err;


    if (!PyArg_ParseTuple(args, "s#", &in, &len))
        return NULL;

    in_len = len;
    out_len = 512;//always 512 bytes in our application

    out_string = PyString_FromStringAndSize(NULL, out_len);

    //decompress
    out = (lzo_bytep) PyString_AsString(out_string);
    new_len = out_len;

    err = lzo1x_decompress(in, in_len, out, &new_len, NULL);

    if (new_len != out_len)
        _PyString_Resize(&out_string, new_len);
    return out_string;
}

static PyMethodDef methods[] =
{
    {"compress", (PyCFunction)compress, METH_VARARGS, compress__doc},
    {"decompress", (PyCFunction)decompress, METH_VARARGS, decompress__doc},
    {NULL, NULL, 0, NULL}
};


static /* const */ char module_doc[]=
"This module can compress/decompress a string with the lzo1x algorithm of LZO 1.00 used in E-Safenet.\n"
"usage: decompress(string) / compress(string)"
;


#ifdef _MSC_VER
_declspec(dllexport)
#endif
void initsimplelzo1x(void)
{
    PyObject *m, *d, *v;

    if (lzo_init() != LZO_E_OK)
        return;

    m = Py_InitModule4("simplelzo1x", methods, module_doc,
                       NULL, PYTHON_API_VERSION);
    d = PyModule_GetDict(m);

    LzoError = PyErr_NewException("lzo.error", NULL, NULL);
    PyDict_SetItemString(d, "error", LzoError);

    v = PyString_FromString("Jan Laan <jan@noveria.nl>");
    PyDict_SetItemString(d, "__author__", v);
    Py_DECREF(v);
    v = PyString_FromString(MODULE_VERSION);
    PyDict_SetItemString(d, "__version__", v);
    Py_DECREF(v);
}
