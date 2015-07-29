# -*- coding: utf-8 -*-
# Copyright (c) 2015 Spotify AB

from __future__ import absolute_import, division, print_function

import attr
import markdown2 as md
from six import iteritems, iterkeys, itervalues

from .utils import load_schema
from .validate import (body_example, body_form, body_mime_type, body_schema,
                       defined_sec_scheme_settings, header_type,
                       integer_number_type_parameter, response_code,
                       string_type_parameter)

HTTP_METHODS = [
    "get", "post", "put", "delete", "patch", "options",
    "head", "trace", "connect"
]

NAMED_PARAMS = [
    "desc", "type", "enum", "pattern", "minimum", "maximum", "example",
    "default", "required", "repeat", "display_name", "max_length",
    "min_length"
]


class Content(object):
    """
    Returns documentable content from the RAML file (e.g. Documentation
    content, description) in either raw or parsed form.

    :param str data: The raw/marked up content data.
    """
    def __init__(self, data):
        self.data = data

    @property
    def raw(self):
        """
        Return raw Markdown/plain text written in the RAML file
        """
        return self.data

    @property
    def html(self):
        """
        Returns parsed Markdown into HTML
        """
        return md.markdown(self.data)

    def __repr__(self):
        return self.raw


@attr.s
class BaseParameter(object):
    """
    Base parameter with properties defined by the RAML spec's \
    'Named Parameters' section.

    :param str name: The item name of parameter
    :param dict raw: All defined data of the item
    :param str description: Parameter description, or ``None``.
    :param str display_name: User-friendly name for display or documentation \
        purposes.  If ``displayName`` is not specified in RAML file, defaults \
        to ``name``.
    :param int min_length: Parameter value's minimum number of characters, or \
        ``None``. Only applies when primative ``type`` is ``string``.
    :param int max_length: Parameter value's maximum number of characters, or \
        ``None``. Only applies when primative ``type`` is ``string``.
    :param int minimum: Parameter's minimum value, or ``None``.  Only applies \
        when primative ``type`` is ``integer`` or ``number``.
    :param int maximum: Parmeter's maximum value, or ``None``.  Only applies \
        when primative ``type`` is ``integer`` or ``number``.
    :param example: Example value for property, or ``None``.  Type of \
        ``example`` will match that of ``type``.
    :param default: Default value for property, or ``None``. Type of \
        ``default`` will match that of ``type``.
    :param bool repeat: If parameter can be repeated.  Defaults to ``False``.
    :param str pattern: A regular expression that parameter of type \
        ``string`` must match, or ``None`` if not set.
    :param list enum: Array of valid parameter values, or ``None``.  Only \
        applies when primative ``type`` is ``string``.
    :param str type: Primative type of parameter. Defaults to ``string`` if \
        not set.
    """
    name         = attr.ib()
    raw          = attr.ib(repr=False,
                           validator=attr.validators.instance_of(dict))
    desc         = attr.ib(repr=False)
    display_name = attr.ib(repr=False)
    min_length   = attr.ib(repr=False, validator=string_type_parameter)
    max_length   = attr.ib(repr=False, validator=string_type_parameter)
    minimum      = attr.ib(repr=False, validator=integer_number_type_parameter)
    maximum      = attr.ib(repr=False, validator=integer_number_type_parameter)
    example      = attr.ib(repr=False)
    default      = attr.ib(repr=False)
    config       = attr.ib(repr=False,
                           validator=attr.validators.instance_of(dict))
    errors       = attr.ib(repr=False)
    repeat       = attr.ib(repr=False, default=False)
    pattern      = attr.ib(repr=False, default=None,
                           validator=string_type_parameter)
    enum         = attr.ib(repr=False, default=None,
                           validator=string_type_parameter)

    @property
    def description(self):
        if self.desc:
            return Content(self.desc)
        return None

    def _inherit_type_properties(self, inherited_param):
        for param in inherited_param:
            name = getattr(param, "name", getattr(param, "code", None))
            if name == self.name:
                for n in NAMED_PARAMS:
                    attr = getattr(self, n, None)
                    if attr is None:
                        attr = getattr(param, n, None)
                        setattr(self, n, attr)

    @staticmethod
    def _get(data, item, default=None):
        """
        Helper function to catch empty mappings in RAML. If item is optional
        but not in the data, or data is ``None``, the default value is returned.

        :param data: RAML data
        :param str item: RAML key
        :param default: default value if item is not in dict
        :param bool optional: If RAML item is optional or needs to be defined
        :ret: value for RAML key
        """
        try:
            return data.get(item, default)
        except AttributeError:
            return default

    @classmethod
    def init(cls, name, data, config, errors=[], **kwargs):
        if cls is URIParameter:
            required = cls._get(data, "required", default=True)
        else:
            required = cls._get(data, "required", default=False)
        arguments = dict(
            name=name,
            raw={name: data},
            desc=cls._get(data, "description"),
            display_name=cls._get(data, "displayName", name),
            min_length=cls._get(data, "minLength"),
            max_length=cls._get(data, "maxLength"),
            minimum=cls._get(data, "minimum"),
            maximum=cls._get(data, "maximum"),
            default=cls._get(data, "default"),
            enum=cls._get(data, "enum"),
            example=cls._get(data, "example"),
            required=required,
            repeat=cls._get(data, "repeat", False),
            pattern=cls._get(data, "pattern"),
            type=cls._get(data, "type", "string"),
            config=config,
            errors=errors
        )
        if cls is Header:
            arguments["method"] = cls._get(kwargs, "method")
        return cls(**arguments)

    @classmethod
    def init_list(cls, data, config, errors=[], **kwargs):
        """Initialise a list of BaseParameters out of a list of attributes."""
        objects = []

        for key, value in list(iteritems(data)):
            objects.append(cls.init(key, value, config, errors, **kwargs))

        return objects or None


@attr.s
class URIParameter(BaseParameter):
    """
    URI parameter with properties defined by the RAML specification's \
    "Named Parameters" section, e.g.: ``/foo/{id}`` where ``id`` is the \
    name of the URI parameter.
    """
    required    = attr.ib(repr=False, default=True)
    type        = attr.ib(repr=False, default="string")


@attr.s
class QueryParameter(BaseParameter):
    """
    Query parameter with properties defined by the RAML specification's \
    "Named Parameters" section, e.g. ``/foo/bar?baz=123`` where ``baz`` \
    is the name of the query parameter.
    """
    required    = attr.ib(repr=False, default=False)
    type        = attr.ib(repr=False, default="string")


@attr.s
class FormParameter(BaseParameter):
    """
    Form parameter with properties defined by the RAML specification's
    "Named Parameters" section. Example:

        ``curl -X POST https://api.com/foo/bar -d baz=123``

    where ``baz`` is the Form Parameter name.
    """
    required    = attr.ib(repr=False, default=False)
    type        = attr.ib(repr=False, default="string")


class Documentation(object):
    """
    User documentation for the API.

    :param str title: Title of documentation.
    :param str content: Content of documentation.
    """
    def __init__(self, _title, _content):
        self._title = _title
        self._content = _content

    @property
    def title(self):
        return Content(self._title)

    @property
    def content(self):
        return Content(self._content)

    def __repr__(self):  # NOCOV
        return "Documentation(title='{0}')".format(self.title)


@attr.s
class Header(BaseParameter):
    """
    Header with properties defined by the RAML spec's 'Named Parameters'
    section, e.g.:

        ``curl -H 'X-Some-Header: foobar' ...``

    where ``X-Some-Header`` is the Header name.


    :param str name: The item name of parameter
    :param str description: Parameter description, or ``None``.
    :param dict raw: All defined data of the item
    :param str display_name: User-friendly name for display or documentation \
        purposes.  If ``displayName`` is not specified in RAML file, defaults \
        to ``name``.
    :param example: Example value for property, or ``None``.  Type of \
        ``example`` will match that of ``type``.
    :param default: Default value for property, or ``None``. Type of \
        ``default`` will match that of ``type``.
    :param int min_length: Parameter value's minimum number of characters, or \
        ``None``. Only applies when primative ``type`` is ``string``.
    :param int max_length: Parameter value's maximum number of characters, or \
        ``None``. Only applies when primative ``type`` is ``string``.
    :param int minimum: Parameter's minimum value, or ``None``.  Only applies \
        when primative ``type`` is ``integer`` or ``number``.
    :param int maximum: Parmeter's maximum value, or ``None``.  Only applies \
        when primative ``type`` is ``integer`` or ``number``.
    :param str type: Primative type of parameter. Defaults to ``string`` if \
        not set.
    :param list enum: Array of valid parameter values, or ``None``.  Only \
        applies when primative ``type`` is ``string``.
    :param bool repeat: If parameter can be repeated.  Defaults to ``False``.
    :param str pattern: A regular expression that parameter of type \
        ``string`` must match, or ``None`` if not set.
    :param str method: HTTP method for header, or ``None``
    :param bool required: If parameter is required. Defaults to ``False``.
    """
    type         = attr.ib(repr=False, default="string", validator=header_type)
    method       = attr.ib(repr=False, default=None)
    required     = attr.ib(repr=False, default=False)

    @property
    def description(self):
        if self.desc:
            return Content(self.desc)
        return None

    def _inherit_type_properties(self, inherited_param):
        params = NAMED_PARAMS + ["method"]
        for param in inherited_param:
            for n in params:
                attr = getattr(self, n, None)
                if attr is None:
                    attr = getattr(param, n, None)
                    setattr(self, n, attr)


@attr.s
class Body(object):
    """
    Body of the request/response.

    :param str mime_type: Accepted MIME media types for the body of the \
        request/response.
    :param dict raw: All defined data of the item
    :param dict schema: Body schema definition, or ``None`` if not set. \
        Can not be set if ``mime_type`` is ``multipart/form-data`` \
        or ``application/x-www-form-urlencoded``
    :param dict example: Example of schema, or ``None`` if not set. \
        Can not be set if ``mime_type`` is ``multipart/form-data`` \
        or ``application/x-www-form-urlencoded``
    :param dict form_params: Form parameters accepted in the body.
        Must be set if ``mime_type`` is ``multipart/form-data`` or \
        ``application/x-www-form-urlencoded``.  Can not be used when \
        schema and/or example is defined.
    """
    mime_type   = attr.ib(init=True, validator=body_mime_type)
    raw         = attr.ib(repr=False, init=True,
                          validator=attr.validators.instance_of(dict))
    schema      = attr.ib(repr=False, validator=body_schema)
    example     = attr.ib(repr=False, validator=body_example)
    form_params = attr.ib(repr=False, validator=body_form)
    config      = attr.ib(repr=False,
                          validator=attr.validators.instance_of(dict))
    errors      = attr.ib(repr=False)

    def _inherit_type_properties(self, inherited_param):
        body_params = ["schema", "example", "form_params"]
        for param in inherited_param:
            if param.mime_type != self.mime_type:
                continue
            for n in body_params:
                attr = getattr(self, n, None)
                if attr is None:
                    attr = getattr(param, n, None)
                    setattr(self, n, attr)

    @classmethod
    def init(cls, name, data, config, errors=[], **kwargs):
        arguments = dict(
            mime_type=name,
            raw=data,
            schema=load_schema(BaseParameter._get(data, "schema")),
            example=load_schema(BaseParameter._get(data, "example")),
            form_params=BaseParameter._get(data, "formParameters"),
            config=config,
            errors=errors
        )

        return cls(**arguments)

    @classmethod
    def init_list(cls, data, config, errors=[], **kwargs):
        # TODO Remove this redundant code that is already in BaseParameter
        # BaseParameter needs to be reworked.
        bodies = []
        for key, value in list(iteritems(data)):
            bodies.append(cls.init(key, value, config, errors, **kwargs))
        return bodies


@attr.s
class Response(object):
    """
    Expected response parameters.

    :param int code: HTTP response code.
    :param dict raw: All defined data of item.
    :param str description: Response description, or ``None``.
    :param list headers: List of :py:class:`.Header` objects, or ``None``.
    :param list body: List of :py:class:`.Body` objects, or ``None``.
    :param str method: HTTP request method associated with response.
    """
    code     = attr.ib(validator=response_code)
    raw      = attr.ib(repr=False, init=True,
                       validator=attr.validators.instance_of(dict))
    desc     = attr.ib(repr=False)
    headers  = attr.ib(repr=False)
    body     = attr.ib(repr=False)
    config   = attr.ib(repr=False,
                       validator=attr.validators.instance_of(dict))
    errors   = attr.ib(repr=False)
    method   = attr.ib(default=None)

    @property
    def description(self):
        if self.desc:
            return Content(self.desc)
        return None

    def _inherit_type_properties(self, inherited_param):
        for param in inherited_param:
            for n in NAMED_PARAMS:
                attr = getattr(self, n, None)
                if attr is None:
                    attr = getattr(param, n, None)
                    setattr(self, n, attr)

    @classmethod
    def init(cls, name, data, config, errors=[], **kwargs):
        arguments = dict(
            code=name,
            raw=data,
            desc=data.get("description"),
            headers=Header.init_list(data.get("headers", {}), config),
            body=Body.init_list(data.get("body", {}), config),
            config=config,
            errors=errors
        )
        return cls(**arguments)

    @classmethod
    def init_list(cls, data, config, errors=[], **kwargs):
        responses = []
        for key, value in list(iteritems(data)):
            responses.append(cls.init(key, value, config, errors, **kwargs))
        return sorted(responses, key=lambda x: x.code)


@attr.s
class SecurityScheme(object):
    """
    Security scheme definition.

    :param str name: Name of security scheme
    :param dict raw: All defined data of item
    :param str type: Type of authentication
    :param dict described_by: :py:class:`.Header` s, :py:class:`.Response` s, \
        :py:class:`.QueryParameter` s, etc that is needed/can be expected \
        when using security scheme.
    :param str description: Description of security scheme
    :param dict settings: Security schema-specific information
    """
    name          = attr.ib()
    raw           = attr.ib(repr=False, init=True,
                            validator=attr.validators.instance_of(dict))
    type          = attr.ib(repr=False)
    described_by  = attr.ib(repr=False)
    desc          = attr.ib(repr=False)
    settings      = attr.ib(repr=False, validator=defined_sec_scheme_settings)
    config        = attr.ib(repr=False)
    errors        = attr.ib(repr=False)

    @property
    def description(self):
        if self.desc:
            return Content(self.desc)
        return None

    @classmethod
    def from_file(cls, raml, root):
        """
        Parse security schemes into ``SecurityScheme`` objects

        :param dict raml_data: Raw RAML data
        :param RootNode root: Root Node
        :returns: list of :py:class:`.parameters.SecurityScheme` objects
        """

        schemes = raml.get("securitySchemes", [])
        scheme_objs = []

        classes = {
            "headers": Header,
            "body": Body,
            "responses": Response,
            "queryParameters": ["query_params", QueryParameter],
            "uriParameters": ["uri_params", URIParameter],
            "formParameters": ["form_params", FormParameter]
        }

        other = {
            "usage": "usage",
            "mediaType": "media_type",
            "protocols": "protocols"
        }

        for s in schemes:
            name = list(iterkeys(s))[0]
            data = list(itervalues(s))[0]
            scheme = SecurityScheme(
                    name=name,
                    raw=data,
                    type=data.get("type"),
                    described_by=data.get("describedBy", {}),
                    desc=data.get("description"),
                    settings=data.get("settings"),
                    config=root.config,
                    errors=root.errors
                )

            for obj, scheme_data in list(iteritems(scheme.described_by)):
                if obj in classes:
                    value = classes[obj]
                    diff_name = isinstance(value, list)
                    attribute_name = value[0] if diff_name else obj
                    data_cls = value[1] if diff_name else value

                    setattr(scheme, attribute_name, data_cls.init_list(scheme_data, root.config))
                elif obj == "documentation":
                        assert isinstance(scheme_data, list), "Error parsing documentation"
                        scheme.documentation = [Documentation(i.get("title"), i.get("content")) for i in scheme_data] or None
                elif obj in other:
                    setattr(scheme, other[obj], scheme_data)
            scheme_objs.append(scheme)
        return scheme_objs or None
