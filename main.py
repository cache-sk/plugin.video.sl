import sys
import inputstreamhelper
import logger
import skylink
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import replay
import live
import library
import utils

_id = int(sys.argv[1])
_addon = xbmcaddon.Addon()
_profile = utils.dec_utf8(xbmc.translatePath(_addon.getAddonInfo('profile')))
_user_name = xbmcplugin.getSetting(_id, 'username')
_password = xbmcplugin.getSetting(_id, 'password')
_provider = 'skylink.sk' if int(xbmcplugin.getSetting(_id, 'provider')) == 0 else 'skylink.cz'
_pin_protected_content = 'false' != xbmcplugin.getSetting(_id, 'pin_protected_content')
_a_show_live = 'false' != xbmcplugin.getSetting(_id, 'a_show_live')


def play(channel_id, askpin):
    logger.log.info('play: ' + channel_id)
    sl = skylink.Skylink(_user_name, _password, _profile, _provider)

    if askpin != 'False':
        pin_ok = utils.ask_for_pin(sl)
        if not pin_ok:
            xbmcplugin.setResolvedUrl(_id, False, xbmcgui.ListItem())
            return
    try:
        info = utils.call(sl, lambda: sl.channel_info(channel_id))
    except skylink.StreamNotResolvedException as e:
        xbmcgui.Dialog().ok(heading=_addon.getAddonInfo('name'), line1=_addon.getLocalizedString(e.id))
        xbmcplugin.setResolvedUrl(_id, False, xbmcgui.ListItem())
        return

    if info:
        is_helper = inputstreamhelper.Helper(info['protocol'], drm=info['drm'])
        if is_helper.check_inputstream():
            playitem = xbmcgui.ListItem(path=info['path'])
            playitem.setProperty('inputstreamaddon', is_helper.inputstream_addon)
            playitem.setProperty('inputstream.adaptive.manifest_type', info['protocol'])
            playitem.setProperty('inputstream.adaptive.license_type', info['drm'])
            playitem.setProperty('inputstream.adaptive.license_key', info['key'])
            xbmcplugin.setResolvedUrl(_id, True, playitem)


if __name__ == '__main__':
    args = utils.parse_qs(sys.argv[2][1:])
    if 'id' in args:
        play(str(args['id'][0]), str(args['askpin'][0]) if 'askpin' in args else 'False')
    elif 'replay' in args:
        replay.router(args, skylink.Skylink(_user_name, _password, _profile, _provider, _pin_protected_content))
    elif 'live' in args:
        live.router(args, skylink.Skylink(_user_name, _password, _profile, _provider, _pin_protected_content))
    elif 'library' in args:
        library.router(args, skylink.Skylink(_user_name, _password, _profile, _provider, _pin_protected_content))
    else:
        xbmcplugin.setPluginCategory(_id, '')
        xbmcplugin.setContent(_id, 'videos')
        if _a_show_live:
            xbmcplugin.addDirectoryItem(_id, live.get_url(live='channels'), xbmcgui.ListItem(label=_addon.getLocalizedString(30700)), True)
        xbmcplugin.addDirectoryItem(_id, replay.get_url(replay='channels'), xbmcgui.ListItem(label=_addon.getLocalizedString(30600)), True)
        xbmcplugin.addDirectoryItem(_id, library.get_url(library='root'), xbmcgui.ListItem(label=_addon.getLocalizedString(30800)), True)
        xbmcplugin.endOfDirectory(_id)
