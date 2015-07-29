API Definition
==============

.. automodule:: ramlfications

Main functions
--------------

The following three functions are meant for you to use primarily when parsing a
RAML file/string.


.. autofunction:: parse
.. autofunction:: load
.. autofunction:: loads
.. autofunction:: validate


Core
----

.. note::
    The following documentation is meant for understanding the underlying
    ``ramlfications`` API.  No need to interact directly with the modules,
    classes, & functions below.

parser
^^^^^^


.. autofunction:: ramlfications.parser.parse_raml

.. autofunction:: ramlfications.parser.create_root

.. autofunction:: ramlfications.parser.create_sec_schemes

.. autofunction:: ramlfications.parser.create_traits

.. autofunction:: ramlfications.parser.create_resource_types

.. autofunction:: ramlfications.parser.create_resources

.. autofunction:: ramlfications.parser.create_node


raml
^^^^

.. automodule:: ramlfications.raml
   :members:

Parameters
^^^^^^^^^^

.. note::

    The :py:class:`.URIParameter`, :py:class:`.QueryParameter`,
    :py:class:`.FormParameter`, and :py:class:`.Header` objects all share the
    same attributes.

.. py:class:: ramlfications.parameters.URIParameter

    URI parameter with properties defined by the RAML specification's \
    "Named Parameters" section, e.g.: ``/foo/{id}`` where ``id`` is the \
    name of the URI parameter.

.. py:class:: ramlfications.parameters.QueryParameter

    Query parameter with properties defined by the RAML specification's \
    "Named Parameters" section, e.g. ``/foo/bar?baz=123`` where ``baz`` \
    is the name of the query parameter.

.. py:class:: ramlfications.parameters.FormParameter

    Form parameter with properties defined by the RAML specification's
    "Named Parameters" section. Example:

        ``curl -X POST https://api.com/foo/bar -d baz=123``

    where ``baz`` is the Form Parameter name.

.. py:class:: ramlfications.parameters.Header

    Header with properties defined by the RAML spec's 'Named Parameters'
    section, e.g.:

        ``curl -H 'X-Some-Header: foobar' ...``

    where ``X-Some-Header`` is the Header name.


    .. py:attribute:: name

        ``str`` of the name of parameter.

    .. py:attribute:: raw

        ``dict`` of all raw data associated with the parameter from
        the RAML file/string.

    .. py:attribute:: description

        ``str`` parameter description, or ``None``.


    .. py:attribute:: display_name

        ``str`` of a user-friendly name for display or documentation purposes.

        If ``displayName`` is not specified in RAML data, defaults to ``name``.

    .. py:attribute:: min_length

        ``int`` of the parameter's minimum number of characters, or
        ``None``.

        .. note:: Only applies when the parameter's primative ``type`` is ``string``.

    .. py:attribute:: max_length

        ``int`` of the parameter's maximum number of characters, or ``None``.

        .. note:: Only applies when the parameter's primative ``type`` is ``string``.

    .. py:attribute:: minimum

        ``int`` of the parameter's minimum value, or ``None``.

        .. note::

            Only applies when the parameter's primative ``type`` is
            ``integer`` or ``number``.

    .. py:attribute:: maximum

        ``int`` of the parmeter's maximum value, or ``None``.

        .. note::

            Only applies when the parameter's primative ``type`` is
            ``integer`` or ``number``.

    .. py:attribute:: example

        Example value for parameter, or ``None``.

        .. note:: Attribute type of  ``example`` will match that of ``type``.

    .. py:attribute:: default

        Default value for parameter, or ``None``.

        .. note:: Attribute type of ``default`` will match that of ``type``.

    .. py:attribute:: repeat

        ``bool`` if parameter can be repeated.  Defaults to ``False``.

    .. py:attribute:: pattern

        ``str`` of a regular expression that parameter of type ``string``
        must match, or ``None`` if not set.

    .. py:attribute:: enum

        ``list`` of valid parameter values, or ``None``.

        .. note:: Only applies when parameter's primative ``type`` is ``string``.

    .. py:attribute:: type

        ``str`` representation of the primative type of parameter. Defaults
        to ``string`` if not set.

    .. py:attribute:: required

        ``bool`` if parameter is required.

        .. note::

            Defaults to ``True`` if :py:class:`.URIParameter`, else defaults to ``False``.


.. py:class:: ramlfications.parameters.Body

    Body of the request/response.

    .. py:attribute:: mime_type

        ``str`` of the accepted MIME media types for the body of the
        request/response.

    .. py:attribute:: raw

        ``dict`` of all raw data associated with the ``Body`` from
        the RAML file/string

    .. py:attribute:: schema

        ``dict`` of body schema definition, or ``None`` if not set.

        .. note::
            Can not be set if ``mime_type`` is ``multipart/form-data`` or \
            ``application/x-www-form-urlencoded``

    .. py:attribute:: example

        ``dict`` of example of schema, or ``None`` if not set.

        .. note::
            Can not be set if ``mime_type`` is ``multipart/form-data`` or \
            ``application/x-www-form-urlencoded``

    .. py:attribute:: form_params

        ``list`` of :py:class:`.FormParameter` objects accepted in the
        request body.

        .. note::
            Must be set if ``mime_type`` is ``multipart/form-data`` or \
            ``application/x-www-form-urlencoded``.  Can not be used when \
            schema and/or example is defined.

.. py:class:: ramlfications.parameters.Response

    Expected response parameters.

    .. py:attribute:: code

        ``int`` of HTTP response code.

    .. py:attribute:: raw

        ``dict`` of all raw data associated with the ``Response`` from
        the RAML file/string

    .. py:attribute:: description

        ``str`` of the response description, or ``None``.

    .. py:attribute:: headers

        ``list`` of :py:class:`.Header` objects, or ``None``.

    .. py:attribute:: body

        ``list`` of :py:class:`.Body` objects, or ``None``.

    .. py:attribute:: method

        ``str`` of HTTP request method associated with response.

.. py:class:: ramlfications.parameters.Documentation

    User documentation for the API.

    .. py:attribute:: title

        ``str`` title of documentation

    .. py:attribute:: content

        ``str`` content of documentation

.. py:class:: ramlfications.parameters.SecurityScheme

    Security scheme definition.

    .. py:attribute:: name

        ``str`` name of security scheme.

    .. py:attribute:: raw

        ``dict`` of all raw data associated with the ``SecurityScheme`` from
        the RAML file/string

    .. py:attribute:: type

        ``str`` of type of authentication

    .. py:attribute:: described_by

        :py:class:`.Header` s, :py:class:`.Response` s,
        :py:class:`.QueryParameter` s, etc. that is needed/can be expected
        when using security scheme.

    .. py:attribute:: description

        ``str`` description of security scheme.

    .. py:attribute:: settings

        ``dict`` of security schema-specific information


.. autoclass:: ramlfications.parameters.Content
    :members:


Loader
^^^^^^

.. automodule:: ramlfications.loader

.. autoclass:: ramlfications.loader.RAMLLoader
    :members:

Validate
^^^^^^^^

Functions are used when instantiating the classes from ``ramlfications.raml``.

.. automodule:: ramlfications.validate
    :members:

Tree
^^^^

.. automodule:: ramlfications.tree
    :members:
