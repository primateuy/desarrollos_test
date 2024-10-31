from odoo.http import Controller, Stream, route
from odoo.modules import get_resource_path


class EditorController(Controller):

    @route('/web/static/lib/ace/mode-json.js', type='http', auth='none')
    def mode_json(self, template='docs', **params):
        stream = Stream.from_path(get_resource_path(
            'muk_rest', 'static', 'lib', 'ace', 'mode-json.js'
        ))
        return stream.get_response()  
    