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
 * @file lib/knock.h
 * @brief Header file for the C library wrapper for knock client's interface
 * @author Sree Harsha Totakura <sreeharsha@totakura.in>
 */

/* Also support C++ to use our library  */
#ifdef __cplusplus
extern "C"
{
#if 0                           /* keep Emacsens' auto-indent happy */
}
#endif
#endif


 #define KNOCK_UDP 0
 #define KNOCK_TCP 1

/**
 * Opaque knock handle
 */
struct KNOCK_Handle;


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
knock_init();


/**
 * Function to create a new knock handle
 *
 * @param timeout number of seconds to wait before retrying the knock attempt
 * @param retries number of times to retry
 * @param verify flag to verify whether the port-knocking is successful or not
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
           const char *client_cert_passwd);


/**
 * Create knock handle with default parameters
 *
 * @param client_cert_passwd password for opening the client certificate.  If
 *          NULL the empty string will be used as a password
 * @return the knock handle; NULL upon error
 */
struct KNOCK_Handle *
knock_default_new (const char *client_cert_passwd);


/**
 * Knock the given port on the given host.
 *
 * @param handle the knock handle created either with knock_new() or
 *          knock_default_new()
 * @param host the hostname of the target host to knock
 * @param port the port to open
 * @param protocol 1 for TCP; 0 for UDP
 * @return 1 if the knocking is successful OR if verify flag was disable for the
 *          handle OR if protocol is UDP; 0 if the verify flag is enabled and
 *          port-knocking failed; -1 upon error
 */
int
knock_knock(struct KNOCK_Handle *handle,
            const char *host,
            unsigned short port,
            int protocol);

#if 0                           /* keep Emacsens' auto-indent happy */
{
#endif
#ifdef __cplusplus
}
#endif

/* end of lib/knock.h */
