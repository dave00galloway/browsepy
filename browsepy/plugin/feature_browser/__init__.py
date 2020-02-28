import os.path

from flask import Blueprint

from browsepy.plugin.feature_browser.behaveable import detect_behaveable_mimetype

__basedir__ = os.path.dirname(os.path.abspath(__file__))

browser = Blueprint(
    'browser',
    __name__,
    url_prefix='/browse',
    template_folder=os.path.join(__basedir__, 'templates'),
    static_folder=os.path.join(__basedir__, 'static'),
)


def register_arguments(manager):
    '''
    Register arguments using given plugin manager.

    This method is called before `register_plugin`.

    :param manager: plugin manager
    :type manager: browsepy.manager.PluginManager
    '''

    # Arguments are forwarded to argparse:ArgumentParser.add_argument,
    # https://docs.python.org/3.7/library/argparse.html#the-add-argument-method
    manager.register_argument('--<plugin-name>', action='store_true', help='h')
    # todo: define arguments to pass in e.g.
    # results dir to overlay current results


def register_plugin(manager):
    '''
    Register blueprints and actions using given plugin manager.

    :param manager: plugin manager
    :type manager: browsepy.manager.PluginManager
    '''
    manager.register_blueprint(browser)
    manager.register_mimetype_function(detect_behaveable_mimetype)
