# Copyright (c) 2012-2013 LiuYC https://github.com/liuyichen/
# Copyright 2012-2014 ksyun.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.
import base64
import datetime
from hashlib import sha256
from hashlib import sha1
import hmac
import logging
from email.utils import formatdate
from operator import itemgetter
import functools
import time
import calendar

from kscore.exceptions import NoCredentialsError
from kscore.utils import normalize_url_path, percent_encode_sequence
from kscore.compat import HTTPHeaders
from kscore.compat import quote, unquote, urlsplit, parse_qs
from kscore.compat import urlunsplit
from kscore.compat import json
from collections import namedtuple


import sys
import logging
import select
import functools
import socket
import inspect

from kscore.compat import six
from kscore.compat import HTTPHeaders, HTTPResponse, urlunsplit, urlsplit
from kscore.exceptions import UnseekableStreamError
from kscore.utils import percent_encode_sequence
from kscore.vendored.requests import models
from kscore.vendored.requests.sessions import REDIRECT_STATI
from kscore.vendored.requests.packages.urllib3.connection import \
    VerifiedHTTPSConnection
from kscore.vendored.requests.packages.urllib3.connection import \
    HTTPConnection
from kscore.vendored.requests.packages.urllib3.connectionpool import \
    HTTPConnectionPool
from kscore.vendored.requests.packages.urllib3.connectionpool import \
    HTTPSConnectionPool


logger = logging.getLogger(__name__)


class KSHTTPResponse(HTTPResponse):
    # The *args, **kwargs is used because the args are slightly
    # different in py2.6 than in py2.7/py3.
    def __init__(self, *args, **kwargs):
        self._status_tuple = kwargs.pop('status_tuple')
        HTTPResponse.__init__(self, *args, **kwargs)

    def _read_status(self):
        if self._status_tuple is not None:
            status_tuple = self._status_tuple
            self._status_tuple = None
            return status_tuple
        else:
            return HTTPResponse._read_status(self)


class KSHTTPConnection(HTTPConnection):
    """HTTPConnection that supports Expect 100-continue.

    This is conceptually a subclass of httplib.HTTPConnection (though
    technically we subclass from urllib3, which subclasses
    httplib.HTTPConnection) and we only override this class to support Expect
    100-continue, which we need for S3.  As far as I can tell, this is
    general purpose enough to not be specific to S3, but I'm being
    tentative and keeping it in kscore because I've only tested
    this against KSYUN services.

    """
    def __init__(self, *args, **kwargs):
        HTTPConnection.__init__(self, *args, **kwargs)
        self._original_response_cls = self.response_class
        # We'd ideally hook into httplib's states, but they're all
        # __mangled_vars so we use our own state var.  This variable is set
        # when we receive an early response from the server.  If this value is
        # set to True, any calls to send() are noops.  This value is reset to
        # false every time _send_request is called.  This is to workaround the
        # fact that py2.6 (and only py2.6) has a separate send() call for the
        # body in _send_request, as opposed to endheaders(), which is where the
        # body is sent in all versions > 2.6.
        self._response_received = False
        self._expect_header_set = False

    def close(self):
        HTTPConnection.close(self)
        # Reset all of our instance state we were tracking.
        self._response_received = False
        self._expect_header_set = False
        self.response_class = self._original_response_cls

    def _tunnel(self):
        # Works around a bug in py26 which is fixed in later versions of
        # python. Bug involves hitting an infinite loop if readline() returns
        # nothing as opposed to just ``\r\n``.
        # As much as I don't like having if py2: <foo> code blocks, this seems
        # the cleanest way to handle this workaround.  Fortunately, the
        # difference from py26 to py3 is very minimal.  We're essentially
        # just overriding the while loop.
        if sys.version_info[:2] != (2, 6):
            return HTTPConnection._tunnel(self)

        # Otherwise we workaround the issue.
        self._set_hostport(self._tunnel_host, self._tunnel_port)
        self.send("CONNECT %s:%d HTTP/1.0\r\n" % (self.host, self.port))
        for header, value in self._tunnel_headers.iteritems():
            self.send("%s: %s\r\n" % (header, value))
        self.send("\r\n")
        response = self.response_class(self.sock, strict=self.strict,
                                       method=self._method)
        (version, code, message) = response._read_status()

        if code != 200:
            self.close()
            raise socket.error("Tunnel connection failed: %d %s" %
                               (code, message.strip()))
        while True:
            line = response.fp.readline()
            if not line:
                break
            if line in (b'\r\n', b'\n', b''):
                break

    def _send_request(self, method, url, body, headers, *py36_up_extra):
        self._response_received = False
        if headers.get('Expect', b'') == b'100-continue':
            self._expect_header_set = True
        else:
            self._expect_header_set = False
            self.response_class = self._original_response_cls
        rval = HTTPConnection._send_request(
            self, method, url, body, headers, *py36_up_extra)
        self._expect_header_set = False
        return rval

    def _convert_to_bytes(self, mixed_buffer):
        # Take a list of mixed str/bytes and convert it
        # all into a single bytestring.
        # Any six.text_types will be encoded as utf-8.
        bytes_buffer = []
        for chunk in mixed_buffer:
            if isinstance(chunk, six.text_type):
                bytes_buffer.append(chunk.encode('utf-8'))
            else:
                bytes_buffer.append(chunk)
        msg = b"\r\n".join(bytes_buffer)
        return msg

    def _send_output(self, message_body=None, **py36_up_extra):
        self._buffer.extend((b"", b""))
        msg = self._convert_to_bytes(self._buffer)
        del self._buffer[:]
        # If msg and message_body are sent in a single send() call,
        # it will avoid performance problems caused by the interaction
        # between delayed ack and the Nagle algorithm.
        if isinstance(message_body, bytes):
            msg += message_body
            message_body = None
        self.send(msg)
        if self._expect_header_set:
            # This is our custom behavior.  If the Expect header was
            # set, it will trigger this custom behavior.
            logger.debug("Waiting for 100 Continue response.")
            # Wait for 1 second for the server to send a response.
            read, write, exc = select.select([self.sock], [], [self.sock], 1)
            if read:
                self._handle_expect_response(message_body)
                return
            else:
                # From the RFC:
                # Because of the presence of older implementations, the
                # protocol allows ambiguous situations in which a client may
                # send "Expect: 100-continue" without receiving either a 417
                # (Expectation Failed) status or a 100 (Continue) status.
                # Therefore, when a client sends this header field to an origin
                # server (possibly via a proxy) from which it has never seen a
                # 100 (Continue) status, the client SHOULD NOT wait for an
                # indefinite period before sending the request body.
                logger.debug("No response seen from server, continuing to "
                             "send the response body.")
        if message_body is not None:
            # message_body was not a string (i.e. it is a file), and
            # we must run the risk of Nagle.
            self.send(message_body)

    def _consume_headers(self, fp):
        # Most servers (including S3) will just return
        # the CLRF after the 100 continue response.  However,
        # some servers (I've specifically seen this for squid when
        # used as a straight HTTP proxy) will also inject a
        # Connection: keep-alive header.  To account for this
        # we'll read until we read '\r\n', and ignore any headers
        # that come immediately after the 100 continue response.
        current = None
        while current != b'\r\n':
            current = fp.readline()

    def _handle_expect_response(self, message_body):
        # This is called when we sent the request headers containing
        # an Expect: 100-continue header and received a response.
        # We now need to figure out what to do.
        fp = self.sock.makefile('rb', 0)
        try:
            maybe_status_line = fp.readline()
            parts = maybe_status_line.split(None, 2)
            if self._is_100_continue_status(maybe_status_line):
                self._consume_headers(fp)
                logger.debug("100 Continue response seen, "
                             "now sending request body.")
                self._send_message_body(message_body)
            elif len(parts) == 3 and parts[0].startswith(b'HTTP/'):
                # From the RFC:
                # Requirements for HTTP/1.1 origin servers:
                #
                # - Upon receiving a request which includes an Expect
                #   request-header field with the "100-continue"
                #   expectation, an origin server MUST either respond with
                #   100 (Continue) status and continue to read from the
                #   input stream, or respond with a final status code.
                #
                # So if we don't get a 100 Continue response, then
                # whatever the server has sent back is the final response
                # and don't send the message_body.
                logger.debug("Received a non 100 Continue response "
                             "from the server, NOT sending request body.")
                status_tuple = (parts[0].decode('ascii'),
                                int(parts[1]), parts[2].decode('ascii'))
                response_class = functools.partial(
                    KSHTTPResponse, status_tuple=status_tuple)
                self.response_class = response_class
                self._response_received = True
        finally:
            fp.close()

    def _send_message_body(self, message_body):
        if message_body is not None:
            self.send(message_body)

    def send(self, str):
        if self._response_received:
            logger.debug("send() called, but reseponse already received. "
                         "Not sending data.")
            return
        return HTTPConnection.send(self, str)

    def _is_100_continue_status(self, maybe_status_line):
        parts = maybe_status_line.split(None, 2)
        # Check for HTTP/<version> 100 Continue\r\n
        return (
            len(parts) >= 3 and parts[0].startswith(b'HTTP/') and
            parts[1] == b'100')


class KSHTTPSConnection(VerifiedHTTPSConnection):
    pass


# Now we need to set the methods we overrode from KSHTTPConnection
# onto KSHTTPSConnection.  This is just a shortcut to avoid
# copy/pasting the same code into KSHTTPSConnection.
for name, function in KSHTTPConnection.__dict__.items():
    if inspect.isfunction(function):
        setattr(KSHTTPSConnection, name, function)


def prepare_request_dict(request_dict, endpoint_url, user_agent=None):
    """
    This method prepares a request dict to be created into an
    KSRequestObject. This prepares the request dict by adding the
    url and the user agent to the request dict.

    :type request_dict: dict
    :param request_dict:  The request dict (created from the
        ``serialize`` module).

    :type user_agent: string
    :param user_agent: The user agent to use for this request.

    :type endpoint_url: string
    :param endpoint_url: The full endpoint url, which contains at least
        the scheme, the hostname, and optionally any path components.
    """
    r = request_dict
    if user_agent is not None:
        headers = r['headers']
        headers['User-Agent'] = user_agent
    url = _urljoin(endpoint_url, r['url_path'])
    if r['query_string']:
        encoded_query_string = percent_encode_sequence(r['query_string'])
        if '?' not in url:
            url += '?%s' % encoded_query_string
        else:
            url += '&%s' % encoded_query_string
    r['url'] = url


def create_request_object(request_dict):
    """
    This method takes a request dict and creates an KSRequest object
    from it.

    :type request_dict: dict
    :param request_dict:  The request dict (created from the
        ``prepare_request_dict`` method).

    :rtype: ``kscore.ksrequest.KSRequest``
    :return: An KSRequest object based on the request_dict.

    """
    r = request_dict
    return KSRequest(method=r['method'], url=r['url'],
                      data=r['body'],
                      headers=r['headers'])


def _urljoin(endpoint_url, url_path):
    p = urlsplit(endpoint_url)
    # <part>   - <index>
    # scheme   - p[0]
    # netloc   - p[1]
    # path     - p[2]
    # query    - p[3]
    # fragment - p[4]
    if not url_path or url_path == '/':
        # If there's no path component, ensure the URL ends with
        # a '/' for backwards compatibility.
        if not p[2]:
            return endpoint_url + '/'
        return endpoint_url
    if p[2].endswith('/') and url_path.startswith('/'):
        new_path = p[2][:-1] + url_path
    else:
        new_path = p[2] + url_path
    reconstructed = urlunsplit((p[0], p[1], new_path, p[3], p[4]))
    return reconstructed


class KSRequest(models.RequestEncodingMixin, models.Request):
    def __init__(self, *args, **kwargs):
        self.auth_path = None
        if 'auth_path' in kwargs:
            self.auth_path = kwargs['auth_path']
            del kwargs['auth_path']
        models.Request.__init__(self, *args, **kwargs)
        headers = HTTPHeaders()
        if self.headers is not None:
            for key, value in self.headers.items():
                headers[key] = value
        self.headers = headers
        # This is a dictionary to hold information that is used when
        # processing the request. What is inside of ``context`` is open-ended.
        # For example, it may have a timestamp key that is used for holding
        # what the timestamp is when signing the request. Note that none
        # of the information that is inside of ``context`` is directly
        # sent over the wire; the information is only used to assist in
        # creating what is sent over the wire.
        self.context = {}

    def prepare(self):
        """Constructs a :class:`KSPreparedRequest <KSPreparedRequest>`."""
        # Eventually I think it would be nice to add hooks into this process.
        p = KSPreparedRequest(self)
        p.prepare_method(self.method)
        p.prepare_url(self.url, self.params)
        p.prepare_headers(self.headers)
        p.prepare_cookies(self.cookies)
        p.prepare_body(self.data, self.files)
        p.prepare_auth(self.auth)
        return p

    @property
    def body(self):
        p = models.PreparedRequest()
        p.prepare_headers({})
        p.prepare_body(self.data, self.files)
        if isinstance(p.body, six.text_type):
            p.body = p.body.encode('utf-8')
        return p.body


class KSPreparedRequest(models.PreparedRequest):
    """Represents a prepared request.

    :ivar method: HTTP Method
    :ivar url: The full url
    :ivar headers: The HTTP headers to send.
    :ivar body: The HTTP body.
    :ivar hooks: The set of callback hooks.

    In addition to the above attributes, the following attributes are
    available:

    :ivar query_params: The original query parameters.
    :ivar post_param: The original POST params (dict).

    """
    def __init__(self, original_request):
        self.original = original_request
        super(KSPreparedRequest, self).__init__()
        self.hooks.setdefault('response', []).append(
            self.reset_stream_on_redirect)

    def reset_stream_on_redirect(self, response, **kwargs):
        if response.status_code in REDIRECT_STATI and \
                self._looks_like_file(self.body):
            logger.debug("Redirect received, rewinding stream: %s", self.body)
            self.reset_stream()

    def _looks_like_file(self, body):
        return hasattr(body, 'read') and hasattr(body, 'seek')

    def reset_stream(self):
        # Trying to reset a stream when there is a no stream will
        # just immediately return.  It's not an error, it will produce
        # the same result as if we had actually reset the stream (we'll send
        # the entire body contents again if we need to).
        # Same case if the body is a string/bytes type.
        if self.body is None or isinstance(self.body, six.text_type) or \
                isinstance(self.body, six.binary_type):
            return
        try:
            logger.debug("Rewinding stream: %s", self.body)
            self.body.seek(0)
        except Exception as e:
            logger.debug("Unable to rewind stream: %s", e)
            raise UnseekableStreamError(stream_object=self.body)

    def prepare_body(self, data, files, json=None):
        """Prepares the given HTTP body data."""
        super(KSPreparedRequest, self).prepare_body(data, files, json)

        # Calculate the Content-Length by trying to seek the file as
        # requests cannot determine content length for some seekable file-like
        # objects.
        if 'Content-Length' not in self.headers:
            if hasattr(data, 'seek') and hasattr(data, 'tell'):
                orig_pos = data.tell()
                data.seek(0, 2)
                end_file_pos = data.tell()
                self.headers['Content-Length'] = str(end_file_pos - orig_pos)
                data.seek(orig_pos)
                # If the Content-Length was added this way, a
                # Transfer-Encoding was added by requests because it did
                # not add a Content-Length header. However, the
                # Transfer-Encoding header is not supported for
                # KSYUN Services so remove it if it is added.
                if 'Transfer-Encoding' in self.headers:
                    self.headers.pop('Transfer-Encoding')

HTTPSConnectionPool.ConnectionCls = KSHTTPSConnection
HTTPConnectionPool.ConnectionCls = KSHTTPConnection


logger = logging.getLogger(__name__)


EMPTY_SHA256_HASH = (
    'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855')
# This is the buffer size used when calculating sha256 checksums.
# Experimenting with various buffer sizes showed that this value generally
# gave the best result (in terms of performance).
PAYLOAD_BUFFER = 1024 * 1024
ISO8601 = '%Y-%m-%dT%H:%M:%SZ'
SIGV4_TIMESTAMP = '%Y%m%dT%H%M%SZ'
SIGNED_HEADERS_BLACKLIST = [
    'expect',
    'user-agent'
]


class BaseSigner(object):
    REQUIRES_REGION = False

    def add_auth(self, request):
        raise NotImplementedError("add_auth")


ReadOnlyCredentials = namedtuple('ReadOnlyCredentials',
                                 ['access_key', 'secret_key', 'token'])


class Credentials(object):
    """
    Holds the credentials needed to authenticate requests.

    :ivar access_key: The access key part of the credentials.
    :ivar secret_key: The secret key part of the credentials.
    :ivar token: The security token, valid only for session credentials.
    :ivar method: A string which identifies where the credentials
        were found.
    """

    def __init__(self, access_key, secret_key, token=None,
                 method=None):
        self.access_key = access_key
        self.secret_key = secret_key
        self.token = token

        if method is None:
            method = 'explicit'
        self.method = method

        self._normalize()

    def _normalize(self):
        # Keys would sometimes (accidentally) contain non-ascii characters.
        # It would cause a confusing UnicodeDecodeError in Python 2.
        # We explicitly convert them into unicode to avoid such error.
        #
        # Eventually the service will decide whether to accept the credential.
        # This also complies with the behavior in Python 3.

        self.access_key = self.access_key
        self.secret_key = self.secret_key

    def get_frozen_credentials(self):
        return ReadOnlyCredentials(self.access_key,
                                   self.secret_key,
                                   self.token)


class SigV4Auth(BaseSigner):
    """
    Sign a request with Signature V4.
    """
    REQUIRES_REGION = True

    def __init__(self, credentials, service_name, region_name):
        self.credentials = credentials
        # We initialize these value here so the unit tests can have
        # valid values.  But these will get overriden in ``add_auth``
        # later for real requests.
        self._region_name = region_name
        self._service_name = service_name

    def _sign(self, key, msg, hex=False):
        if hex:
            sig = hmac.new(key, msg.encode('utf-8'), sha256).hexdigest()
        else:
            sig = hmac.new(key, msg.encode('utf-8'), sha256).digest()
        return sig

    def headers_to_sign(self, request):
        """
        Select the headers from the request that need to be included
        in the StringToSign.
        """
        header_map = HTTPHeaders()
        split = urlsplit(request.url)
        for name, value in request.headers.items():
            lname = name.lower()
            if lname not in SIGNED_HEADERS_BLACKLIST:
                header_map[lname] = value
        if 'host' not in header_map:
            header_map['host'] = split.netloc
        return header_map

    def canonical_query_string(self, request):
        # The query string can come from two parts.  One is the
        # params attribute of the request.  The other is from the request
        # url (in which case we have to re-split the url into its components
        # and parse out the query string component).
        if request.params:
            return self._canonical_query_string_params(request.params)
        else:
            return self._canonical_query_string_url(urlsplit(request.url))

    def _canonical_query_string_params(self, params):
        l = []
        for param in sorted(params):
            value = str(params[param])
            l.append('%s=%s' % (quote(param, safe='-_.~'),
                                quote(value, safe='-_.~')))
        cqs = '&'.join(l)
        return cqs

    def _canonical_query_string_url(self, parts):
        canonical_query_string = ''
        if parts.query:
            # [(key, value), (key2, value2)]
            key_val_pairs = []
            for pair in parts.query.split('&'):
                key, _, value = pair.partition('=')
                key_val_pairs.append((key, value))
            sorted_key_vals = []
            # Sort by the key names, and in the case of
            # repeated keys, then sort by the value.
            for key, value in sorted(key_val_pairs):
                sorted_key_vals.append('%s=%s' % (key, value))
            canonical_query_string = '&'.join(sorted_key_vals)
        return canonical_query_string

    def canonical_headers(self, headers_to_sign):
        """
        Return the headers that need to be included in the StringToSign
        in their canonical form by converting all header keys to lower
        case, sorting them in alphabetical order and then joining
        them into a string, separated by newlines.
        """
        headers = []
        sorted_header_names = sorted(set(headers_to_sign))
        for key in sorted_header_names:
            value = ','.join(v.strip() for v in
                             sorted(headers_to_sign.get_all(key)))
            headers.append('%s:%s' % (key, value))
        return '\n'.join(headers)

    def signed_headers(self, headers_to_sign):
        l = ['%s' % n.lower().strip() for n in set(headers_to_sign)]
        l = sorted(l)
        return ';'.join(l)

    def payload(self, request):
        if request.body and hasattr(request.body, 'seek'):
            position = request.body.tell()
            read_chunksize = functools.partial(request.body.read,
                                               PAYLOAD_BUFFER)
            checksum = sha256()
            for chunk in iter(read_chunksize, b''):
                checksum.update(chunk)
            hex_checksum = checksum.hexdigest()
            request.body.seek(position)
            return hex_checksum
        elif request.body:
            # The request serialization has ensured that
            # request.body is a bytes() type.
            return sha256(request.body).hexdigest()
        else:
            return EMPTY_SHA256_HASH

    def canonical_request(self, request):
        cr = [request.method.upper()]
        path = self._normalize_url_path(urlsplit(request.url).path)
        cr.append(path)
        cr.append(self.canonical_query_string(request))
        headers_to_sign = self.headers_to_sign(request)
        cr.append(self.canonical_headers(headers_to_sign) + '\n')
        cr.append(self.signed_headers(headers_to_sign))
        if 'X-Amz-Content-SHA256' in request.headers:
            body_checksum = request.headers['X-Amz-Content-SHA256']
        else:
            body_checksum = self.payload(request)
        cr.append(body_checksum)
        return '\n'.join(cr)

    def _normalize_url_path(self, path):
        normalized_path = quote(normalize_url_path(path), safe='/~')
        return normalized_path

    def scope(self, request):
        scope = [self.credentials.access_key]
        scope.append(request.context['timestamp'][0:8])
        scope.append(self._region_name)
        scope.append(self._service_name)
        scope.append('aws4_request')
        return '/'.join(scope)

    def credential_scope(self, request):
        scope = []
        scope.append(request.context['timestamp'][0:8])
        scope.append(self._region_name)
        scope.append(self._service_name)
        scope.append('aws4_request')
        return '/'.join(scope)

    def string_to_sign(self, request, canonical_request):
        """
        Return the canonical StringToSign as well as a dict
        containing the original version of all headers that
        were included in the StringToSign.
        """
        sts = ['AWS4-HMAC-SHA256']
        sts.append(request.context['timestamp'])
        sts.append(self.credential_scope(request))
        sts.append(sha256(canonical_request.encode('utf-8')).hexdigest())
        return '\n'.join(sts)

    def signature(self, string_to_sign, request):
        key = self.credentials.secret_key
        k_date = self._sign(('AWS4' + key).encode('utf-8'),
                            request.context['timestamp'][0:8])
        k_region = self._sign(k_date, self._region_name)
        k_service = self._sign(k_region, self._service_name)
        k_signing = self._sign(k_service, 'aws4_request')
        return self._sign(k_signing, string_to_sign, hex=True)

    def add_auth(self, request):
        if self.credentials is None:
            raise NoCredentialsError
        datetime_now = datetime.datetime.utcnow()
        request.context['timestamp'] = datetime_now.strftime(SIGV4_TIMESTAMP)
        # This could be a retry.  Make sure the previous
        # authorization header is removed first.
        self._modify_request_before_signing(request)
        canonical_request = self.canonical_request(request)
        logger.debug("Calculating signature using v4 auth.")
        logger.debug('CanonicalRequest:\n%s', canonical_request)
        string_to_sign = self.string_to_sign(request, canonical_request)
        logger.debug('StringToSign:\n%s', string_to_sign)
        signature = self.signature(string_to_sign, request)
        logger.debug('Signature:\n%s', signature)

        self._inject_signature_to_request(request, signature)

    def _inject_signature_to_request(self, request, signature):
        l = ['AWS4-HMAC-SHA256 Credential=%s' % self.scope(request)]
        headers_to_sign = self.headers_to_sign(request)
        l.append('SignedHeaders=%s' % self.signed_headers(headers_to_sign))
        l.append('Signature=%s' % signature)
        request.headers['Authorization'] = ', '.join(l)
        return request

    def _modify_request_before_signing(self, request):
        if 'Authorization' in request.headers:
            del request.headers['Authorization']
        self._set_necessary_date_headers(request)
        if self.credentials.token:
            if 'X-Amz-Security-Token' in request.headers:
                del request.headers['X-Amz-Security-Token']
            request.headers['X-Amz-Security-Token'] = self.credentials.token

    def _set_necessary_date_headers(self, request):
        # The spec allows for either the Date _or_ the X-Amz-Date value to be
        # used so we check both.  If there's a Date header, we use the date
        # header.  Otherwise we use the X-Amz-Date header.
        if 'Date' in request.headers:
            del request.headers['Date']
            datetime_timestamp = datetime.datetime.strptime(
                request.context['timestamp'], SIGV4_TIMESTAMP)
            request.headers['Date'] = formatdate(
                int(calendar.timegm(datetime_timestamp.timetuple())))
            if 'X-Amz-Date' in request.headers:
                del request.headers['X-Amz-Date']
        else:
            if 'X-Amz-Date' in request.headers:
                del request.headers['X-Amz-Date']
            request.headers['X-Amz-Date'] = request.context['timestamp']


class S3SigV4Auth(SigV4Auth):

    def _modify_request_before_signing(self, request):
        super(S3SigV4Auth, self)._modify_request_before_signing(request)
        if 'X-Amz-Content-SHA256' in request.headers:
            del request.headers['X-Amz-Content-SHA256']
        request.headers['X-Amz-Content-SHA256'] = self.payload(request)

    def _normalize_url_path(self, path):
        # For S3, we do not normalize the path.
        return path


class SigV4QueryAuth(SigV4Auth):
    DEFAULT_EXPIRES = 3600

    def __init__(self, credentials, service_name, region_name,
                 expires=DEFAULT_EXPIRES):
        super(SigV4QueryAuth, self).__init__(credentials, service_name,
                                             region_name)
        self._expires = expires

    def _modify_request_before_signing(self, request):
        # Note that we're not including X-Amz-Signature.
        # From the docs: "The Canonical Query String must include all the query
        # parameters from the preceding table except for X-Amz-Signature.
        signed_headers = self.signed_headers(self.headers_to_sign(request))
        auth_params = {
            'X-Amz-Algorithm': 'AWS4-HMAC-SHA256',
            'X-Amz-Credential': self.scope(request),
            'X-Amz-Date': request.context['timestamp'],
            'X-Amz-Expires': self._expires,
            'X-Amz-SignedHeaders': signed_headers,
        }
        if self.credentials.token is not None:
            auth_params['X-Amz-Security-Token'] = self.credentials.token
        # Now parse the original query string to a dict, inject our new query
        # params, and serialize back to a query string.
        url_parts = urlsplit(request.url)
        # parse_qs makes each value a list, but in our case we know we won't
        # have repeated keys so we know we have single element lists which we
        # can convert back to scalar values.
        query_dict = dict(
            [(k, v[0]) for k, v in parse_qs(url_parts.query).items()])
        # The spec is particular about this.  It *has* to be:
        # https://<endpoint>?<operation params>&<auth params>
        # You can't mix the two types of params together, i.e just keep doing
        # new_query_params.update(op_params)
        # new_query_params.update(auth_params)
        # percent_encode_sequence(new_query_params)
        operation_params = ''
        if request.data:
            # We also need to move the body params into the query string.
            # request.data will be populated, for example, with query services
            # which normally form encode the params into the body.
            # This means that request.data is a dict() of the operation params.
            query_dict.update(request.data)
            request.data = ''
        if query_dict:
            operation_params = percent_encode_sequence(query_dict) + '&'
        new_query_string = (operation_params +
                            percent_encode_sequence(auth_params))
        # url_parts is a tuple (and therefore immutable) so we need to create
        # a new url_parts with the new query string.
        # <part>   - <index>
        # scheme   - 0
        # netloc   - 1
        # path     - 2
        # query    - 3  <-- we're replacing this.
        # fragment - 4
        p = url_parts
        new_url_parts = (p[0], p[1], p[2], new_query_string, p[4])
        request.url = urlunsplit(new_url_parts)

    def _inject_signature_to_request(self, request, signature):
        # Rather than calculating an "Authorization" header, for the query
        # param quth, we just append an 'X-Amz-Signature' param to the end
        # of the query string.
        request.url += '&X-Amz-Signature=%s' % signature


class S3SigV4QueryAuth(SigV4QueryAuth):
    """S3 SigV4 auth using query parameters.

    This signer will sign a request using query parameters and signature
    version 4, i.e a "presigned url" signer.


    """
    def _normalize_url_path(self, path):
        # For S3, we do not normalize the path.
        return path

    def payload(self, request):
        # From the doc link above:
        # "You don't include a payload hash in the Canonical Request, because
        # when you create a presigned URL, you don't know anything about the
        # payload. Instead, you use a constant string "UNSIGNED-PAYLOAD".
        return "UNSIGNED-PAYLOAD"


class S3SigV4PostAuth(SigV4Auth):
    """
    Presigns a s3 post

    """
    def add_auth(self, request):
        datetime_now = datetime.datetime.utcnow()
        request.context['timestamp'] = datetime_now.strftime(SIGV4_TIMESTAMP)

        fields = {}
        if request.context.get('s3-presign-post-fields', None) is not None:
            fields = request.context['s3-presign-post-fields']

        policy = {}
        conditions = []
        if request.context.get('s3-presign-post-policy', None) is not None:
            policy = request.context['s3-presign-post-policy']
            if policy.get('conditions', None) is not None:
                conditions = policy['conditions']

        policy['conditions'] = conditions

        fields['x-amz-algorithm'] = 'AWS4-HMAC-SHA256'
        fields['x-amz-credential'] = self.scope(request)
        fields['x-amz-date'] = request.context['timestamp']

        conditions.append({'x-amz-algorithm': 'AWS4-HMAC-SHA256'})
        conditions.append({'x-amz-credential': self.scope(request)})
        conditions.append({'x-amz-date': request.context['timestamp']})

        if self.credentials.token is not None:
            fields['x-amz-security-token'] = self.credentials.token
            conditions.append({'x-amz-security-token': self.credentials.token})

        # Dump the base64 encoded policy into the fields dictionary.
        fields['policy'] = base64.b64encode(
            json.dumps(policy).encode('utf-8')).decode('utf-8')

        fields['x-amz-signature'] = self.signature(fields['policy'], request)

        request.context['s3-presign-post-fields'] = fields
        request.context['s3-presign-post-policy'] = policy


AUTH_TYPE_MAPS = {
    'v4': SigV4Auth,
    'v4-query': SigV4QueryAuth,
    's3v4': S3SigV4Auth,
    's3v4-query': S3SigV4QueryAuth,
    's3v4-presign-post': S3SigV4PostAuth,

}



if __name__ == '__main__':
    access_key = "AKLTJZEjW05lQEGx1Z_g07AazA"
    secret_key = "OAcfe1+lkHucQoaVMUbIhlaDK2D8QuFMv4jHiRRtgtNqYVaEOWLv3MaRZAlk565hRg=="
    credentials = Credentials(access_key, secret_key)
    v4 = SigV4Auth(credentials,"iam", "cn-beijing-6")
    request_dict = {'context': '', 'url': 'http://10.100.50.90', 'headers': {}, 'method': 'GET', 'params': '', 'body': ''}
    request = create_request_object(request_dict)
    print(v4.add_auth(request))
