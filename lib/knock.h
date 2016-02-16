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


/**
 * Opaque knock handle
 */
struct KNOCK_Handle;


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
 * @param host the hostname of the target host to knock
 * @param port the port to open
 * @param protocol 1 for TCP; 0 for UDP
 * @return ??(should be a socket?)
 */
int
knock_knock(const char *host,
            unsigned short port,
            int protocol);


/* end of lib/knock.h */
