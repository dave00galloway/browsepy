import os.path

from flask import Blueprint, render_template
from werkzeug.exceptions import NotFound

from browsepy import OutsideDirectoryBase, get_cookie_browse_sorting, browse_sortkey_reverse, stream_template
from browsepy.plugin.feature_browser.behaveable import detect_behaveable_mimetype, BehaveAbleFile, BehaveAbleDir

__basedir__ = os.path.dirname(os.path.abspath(__file__))

browser = Blueprint(
    'browser',
    __name__,
    url_prefix='/browse',
    template_folder=os.path.join(__basedir__, 'templates'),
    static_folder=os.path.join(__basedir__, 'static'),
)


@browser.route('/summarise-feature/<path:path>')
def summarise_feature(path):
    try:
        feature = BehaveAbleFile.from_urlpath(path)
        if feature.is_file:
            template = render_template('audio.player.html', file=feature)
            # feature = BehaveAbleFile(file=file)
            feature.summarise()
            return template
    except OutsideDirectoryBase:
        pass
    return NotFound()


@browser.route("/summarise-directory", defaults={"path": ""})
@browser.route('/summarise-directory/<path:path>')
def summarise_directory(path):
    sort_property = get_cookie_browse_sorting(path, 'text')
    sort_fnc, sort_reverse = browse_sortkey_reverse(sort_property)
    try:
        suite = BehaveAbleDir.from_urlpath(path)
        if suite.is_directory:
            summary = suite.summarise()
            return stream_template(
                'audio.player.html',
                file=suite,
                sort_property=sort_property,
                sort_fnc=sort_fnc,
                sort_reverse=sort_reverse,
                playlist=True
            )
    except OutsideDirectoryBase:
        pass
    return NotFound()


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

    # register action buttons
    manager.register_widget(
        place='entry-actions',
        css='play',
        type='button',
        endpoint='browser.summarise_feature',
        filter=BehaveAbleFile.detect
    )

    # register header button
    manager.register_widget(
        place='header',
        type='button',
        endpoint='browser.summarise_directory',
        text='Summarise directory',
        filter=BehaveAbleDir.detect
    )
