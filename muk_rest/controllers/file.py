import base64

from odoo import http, exceptions
from odoo.http import request
from odoo.tools import misc, replace_exceptions

from odoo.addons.web.controllers import main
from odoo.addons.muk_rest.tools.http import build_route
from odoo.addons.muk_rest import core


class FileController(http.Controller):
    
    #----------------------------------------------------------
    # Components
    #----------------------------------------------------------
    
    @property
    def API_DOCS_COMPONENTS(self):
        return {
            'schemas': {
                'FileContent': {
                    'type': 'object',
                    'properties': {
                        'content': {
                            'type': 'string',
                        },
                        'content_disposition': {
                            'type': 'string',
                        },
                        'content_length': {
                            'type': 'integer',
                        },
                        'content_type': {
                            'type': 'string',
                        },
                        'filename': {
                            'type': 'string',
                        },
                    },
                    'description': 'The file content information.'
                },
                'UploadContent': {
                    'type': 'object',
                    'properties': {
                        'ufile': {
                            'type': 'array',
                            'items': {
                                'type': 'string',
                                'format': 'binary',
                            }
                        }
                    },
                    'description': 'File content to upload.'
                },
                'UploadResult': {
                    'oneOf': [
                        {'type': 'boolean'},
                        {'$ref': '#/components/schemas/RecordTuples'}
                    ],
                    'description': 'Result of the file upload.'
                },
            }
        }
        
    #----------------------------------------------------------
    # Helper
    #----------------------------------------------------------
        
    def _get_stream_response(
        self, stream, filename=None, unique=False, nocache=False, type='stream'
    ):
        if type == 'file':
            stream_content = stream.read()
            headers = [
                ('Content-Type', stream.mimetype), 
                ('X-Content-Type-Options', 'nosniff'), 
                ('Content-Security-Policy', "default-src 'none'"),
                ('Content-Length', len(stream_content)),
            ]
            if filename or stream.download_name:
                headers.append((
                    'Content-Disposition', 
                    http.content_disposition(
                        filename or stream.download_name
                    )
                ))
            if unique:
                headers.append((
                    'Cache-Control', 
                    f'max-age={http.STATIC_CACHE_LONG if unique else 0}'
                ))
            return request.make_response(stream_content, headers)
        elif type == 'base64':
            stream_content = stream.read()
            fname = filename or stream.download_name
            return request.make_json_response({
                'filename': fname,
                'content': stream_content,
                'content_type': stream.mimetype,
                'content_length': len(stream_content),
                'content_disposition': (
                    fname and http.content_disposition(fname)
                ),
            })
        send_file_kwargs = {
            'as_attachment': True
        }
        if unique:
            send_file_kwargs['max_age'] = http.STATIC_CACHE_LONG
            send_file_kwargs['immutable'] = True
        if nocache:
            send_file_kwargs['max_age'] = None
        return stream.get_response(**send_file_kwargs)
        
    #----------------------------------------------------------
    # Files
    #----------------------------------------------------------
    
    @core.http.rest_route(
        routes=build_route([
            '/download',        
            '/download/<string:xmlid>',
            '/download/<string:xmlid>/<string:filename>',
            '/download/<int:id>',
            '/download/<int:id>/<string:filename>',
            '/download/<string:model>/<int:id>/<string:field>',
            '/download/<string:model>/<int:id>/<string:field>/<string:filename>'
        ]), 
        methods=['GET'],
        protected=True,
        docs=dict(
            tags=['File'], 
            summary='File Download', 
            description='Returns the file content.',
            parameter={
                'xmlid': {
                    'name': 'xmlid',
                    'description': 'XML ID',
                    'schema': {
                        'type': 'string'
                    },
                },
                'model': {
                    'name': 'model',
                    'description': 'Model',
                    'schema': {
                        'type': 'string'
                    },
                },
                'id': {
                    'name': 'id',
                    'description': 'ID',
                    'schema': {
                        'type': 'integer'
                    },
                },
                'field': {
                    'name': 'field',
                    'description': 'Field',
                    'schema': {
                        'type': 'string'
                    },
                },
                'unique': {
                    'name': 'unique',
                    'description': 'Cache Control',
                    'schema': {
                        'type': 'boolean'
                    },
                },
                'nocache': {
                    'name': 'nocache',
                    'description': 'Disable Cache Control',
                    'schema': {
                        'type': 'boolean'
                    },
                },
                'filename': {
                    'name': 'filename',
                    'description': 'Filename',
                    'schema': {
                        'type': 'string'
                    },
                },
                'filename_field': {
                    'name': 'filename_field',
                    'description': 'Filename Field',
                    'schema': {
                        'type': 'string'
                    },
                },
                'mimetype': {
                    'name': 'mimetype',
                    'description': 'Mimetype',
                    'schema': {
                        'type': 'string'
                    },
                },
                'type': {
                    'name': 'type',
                    'description': 'Return the Response as a File, Stream or Base64',
                    'schema': {
                        'type': 'string',
                        'enum': ['stream', 'file', 'base64'],
                    }
                },
            },
            responses={
                '200': {
                    'description': 'File Content', 
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/FileContent'
                            },
                            'example': {
                                'content': 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=',
                                'content_disposition': 'attachment; filename*=UTF-8''image.png',
                                'content_length': 128,
                                'content_type': 'image/png',
                                'filename': 'image.png'
                            }
                        },
                        'application/octet-stream': {
                            'schema': {
                                'type': 'string',
                                'format': 'binary'
                            }
                        }
                        
                    }
                }
            },
            default_responses=['400', '401', '500'],
        ),
    )
    def download(
        self, 
        xmlid=None, 
        model='ir.attachment', 
        id=None, 
        field='raw', 
        filename=None, 
        filename_field='name', 
        mimetype=None, 
        unique=False, 
        nocache=False, 
        type='stream',
        **kw
    ):  
        with replace_exceptions(exceptions.UserError, by=request.not_found()):
            record = request.env['ir.binary']._find_record(
                xmlid, model, id and int(id)
            )
            stream = request.env['ir.binary']._get_stream_from(
                record, field, filename, filename_field, mimetype
            )
        return self._get_stream_response(
            stream, 
            filename, 
            misc.str2bool(unique), 
            misc.str2bool(nocache), 
            type
        )
    
    @core.http.rest_route(
        routes=build_route([
            '/image',
            '/image/<string:xmlid>',
            '/image/<string:xmlid>/<string:filename>',
            '/image/<string:xmlid>/<int:width>x<int:height>',
            '/image/<string:xmlid>/<int:width>x<int:height>/<string:filename>',
            '/image/<string:model>/<int:id>/<string:field>',
            '/image/<string:model>/<int:id>/<string:field>/<string:filename>',
            '/image/<string:model>/<int:id>/<string:field>/<int:width>x<int:height>',
            '/image/<string:model>/<int:id>/<string:field>/<int:width>x<int:height>/<string:filename>',
            '/image/<int:id>',
            '/image/<int:id>/<string:filename>',
            '/image/<int:id>/<int:width>x<int:height>',
            '/image/<int:id>/<int:width>x<int:height>/<string:filename>',
            '/image/<int:id>-<string:unique>',
            '/image/<int:id>-<string:unique>/<string:filename>',
            '/image/<int:id>-<string:unique>/<int:width>x<int:height>',
            '/image/<int:id>-<string:unique>/<int:width>x<int:height>/<string:filename>'
        ]), 
        methods=['GET'],
        protected=True,
        docs=dict(
            tags=['File'], 
            summary='Image Download', 
            description='Returns the image content.',
            parameter={
                'xmlid': {
                    'name': 'xmlid',
                    'description': 'XML ID',
                    'schema': {
                        'type': 'string'
                    },
                },
                'model': {
                    'name': 'model',
                    'description': 'Model',
                    'schema': {
                        'type': 'string'
                    },
                },
                'id': {
                    'name': 'id',
                    'description': 'ID',
                    'schema': {
                        'type': 'integer'
                    },
                },
                'field': {
                    'name': 'field',
                    'description': 'Field',
                    'schema': {
                        'type': 'string'
                    },
                },
                'unique': {
                    'name': 'unique',
                    'description': 'Cache Control',
                    'schema': {
                        'type': 'boolean'
                    },
                },
                'nocache': {
                    'name': 'nocache',
                    'description': 'Disable Cache Control',
                    'schema': {
                        'type': 'boolean'
                    },
                },
                'filename': {
                    'name': 'filename',
                    'description': 'Filename',
                    'schema': {
                        'type': 'string'
                    },
                },
                'filename_field': {
                    'name': 'filename_field',
                    'description': 'Filename Field',
                    'schema': {
                        'type': 'string'
                    },
                },
                'mimetype': {
                    'name': 'mimetype',
                    'description': 'Mimetype',
                    'schema': {
                        'type': 'string'
                    },
                },
                'width': {
                    'name': 'width',
                    'description': 'Width',
                    'schema': {
                        'type': 'integer'
                    },
                },
                'height': {
                    'name': 'height',
                    'description': 'Height',
                    'schema': {
                        'type': 'integer'
                    },
                },
                'crop': {
                    'name': 'crop',
                    'description': 'Crop',
                    'schema': {
                        'type': 'boolean'
                    },
                },
                'quality': {
                    'name': 'quality',
                    'description': 'Quality',
                    'schema': {
                        'type': 'integer'
                    },
                },
                'type': {
                    'name': 'type',
                    'description': 'Return the Response as a File, Stream or Base64',
                    'schema': {
                        'type': 'string',
                        'enum': ['stream', 'file', 'base64'],
                    }
                },
            },
            responses={
                '200': {
                    'description': 'Image Content', 
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/FileContent'
                            },
                            'example': {
                                'content': 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=',
                                'content_disposition': 'attachment; filename*=UTF-8''image.png',
                                'content_length': 128,
                                'content_type': 'image/png',
                                'filename': 'image.png'
                            }
                        },
                        'application/octet-stream': {
                            'schema': {
                                'type': 'string',
                                'format': 'binary'
                            }
                        }
                        
                    }
                }
            },
            default_responses=['400', '401', '500'],
        ),
    )
    def image(
        self, 
        xmlid=None, 
        model='ir.attachment', 
        id=None, 
        field='raw', 
        filename=None, 
        filename_field='name',
        mimetype=None, 
        unique=False, 
        nocache=False,  
        width=0, 
        height=0, 
        crop=False, 
        quality=0, 
        type=False, 
        **kw
    ):  
        with replace_exceptions(exceptions.UserError, by=request.not_found()):
            record = request.env['ir.binary']._find_record(
                xmlid, model, id and int(id)
            )
            stream = request.env['ir.binary']._get_image_stream_from(
                record, field, filename, filename_field, mimetype,
                width=int(width), height=int(height), crop=misc.str2bool(crop)
            )
        return self._get_stream_response(
            stream, 
            filename, 
            misc.str2bool(unique), 
            misc.str2bool(nocache), 
            type
        )

    @core.http.rest_route(
        routes=build_route([
            '/upload',        
            '/upload/<string:model>/<int:id>',
            '/upload/<string:model>/<int:id>/<string:field>',
        ]), 
        methods=['POST'],
        protected=True,
        docs=dict(
            tags=['File'], 
            summary='File Upload', 
            description='Uploads file content.',
            parameter={
                'model': {
                    'name': 'model',
                    'description': 'Model',
                    'required': True,
                    'schema': {
                        'type': 'string'
                    },
                },
                'id': {
                    'name': 'id',
                    'description': 'ID',
                    'required': True,
                    'schema': {
                        'type': 'integer'
                    },
                },
                'field': {
                    'name': 'field',
                    'description': 'Field',
                    'schema': {
                        'type': 'string'
                    },
                },
            },
            requestBody={
                'description': 'Files',
                'required': True,
                'content': {
                    'multipart/form-data': {
                        'schema': {
                            '$ref': '#/components/schemas/UploadContent'
                        }
                    }
                }
            },
            responses={
                '200': {
                    'description': 'Upload Result', 
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/UploadResult'
                            },
                            'example': [[1, 'image.png']]
                        },
                    }
                }
            },
            default_responses=['400', '401', '500'],
        ),
    )
    def upload(self, model, id, field=None, **kw):
        files = request.httprequest.files.getlist('ufile')
        if field is not None and len(files) == 1:
            return request.make_json_response(
                request.env[model].browse(int(id)).write({
                    field: base64.encodebytes(files[0].read())
                })
            )
        attachment_ids = []
        for ufile in files:
            attachment = request.env['ir.attachment'].create({
                'datas': base64.encodebytes(ufile.read()),
                'name': ufile.filename,
                'res_model': model,
                'res_id': int(id),
            })
            attachment_ids.append(attachment.id)
        attachments = request.env['ir.attachment'].browse(attachment_ids)
        return request.make_json_response(
            [(attachment.id, attachment.display_name) for attachment in attachments]
        )
