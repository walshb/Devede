import io
import cPickle
import ConfigParser

class DevedeFileException(Exception):
    pass

class NotDevedeFileException(Exception):
    pass

_title_prop_defaults = {'jumpto': 'menu',
    'nombre': ''}

_title_info_aliases = {'name' : 'nombre'}

_file_prop_defaults = {'adelay': 0.0,
    'arate': 224,
    'aspect': 1.7777777699999999,
    'blackbars': 0,
    'copy_audio': False,
    'cutting': 0,
    'deinterlace': 'none',
    'force_subs': False,
    'fps': 25,
    'gop12': True,
    'height': 576,
    'hmirror': False,
    'ismpeg': False,
    'isvob': False,
    'lchapters': 5.0,
    'mbd': 2,
    'params': '',
    'params_lame': '',
    'params_lavc': '',
    'params_vf': '',
    'path': '',
    'resolution': 0,
    'rotate': 0,
    'sound51': False,
    'sub_list': [],
    'subfont_size': 28,
    'swap_fields': False,
    'trellis': True,
    'turbo1stpass': False,
    'twopass': False,
    'vmirror': False,
    'volume': 100,
    'vrate': 0,
    'width': 720}

_sub_prop_defaults = {'sub_codepage' : 'ASCII',
    'subtitles_up' : False,
    'subtitles' : '',
    'sub_language' : 'EN (ENGLISH)'}

_output_prop_defaults = {'PAL': True,
    'action_todo': 2,
    'disctocreate': 'dvd',
    'do_menu': True,
    'finalfolder': '',
    'fontname': 'Sans 12',
    'menu_alignment': 2,
    'menu_bg': '/home/walshb/opt/devede-head/share/devede/backgrounds/default_bg.png',
    'menu_bgcolor': [0, 0, 0, 49152],
    'menu_font_color': [65535, 65535, 65535, 65535],
    'menu_halignment': 2,
    'menu_selc_color': [0, 65535, 65535, 65535],
    'menu_shadow_color': [0, 0, 0, 0],
    'menu_sound': '/home/walshb/opt/devede-head/share/devede/silence.ogg',
    'menu_title_color': [0, 0, 0, 65535],
    'menu_title_fontname': 'Sans 14',
    'menu_title_shadow': [0, 0, 0, 0],
    'menu_title_text': '',
    'menu_widescreen': False,
    'outputname': '',
    'titlecounter': 3,
    'with_menu': True}

def _val_like(v, default):
    if isinstance(default, (bool, list)):
        return eval(v)
    return type(default)(v)


def _conv_and_defaults(d, defaults, aliases):
    res = {}

    for key in d:
        reskey = aliases.get(key, key)
        if reskey in defaults:
            res[reskey] = _val_like(d[key], defaults[reskey])

    _set_defaults(res, defaults)

    return res


def _set_defaults(d, defaults):
    for key in defaults:
        if key not in d:
            d[key] = defaults[key]


def _section_dict(conf, section_name):
    try:
        items = conf.items(section_name)
    except ConfigParser.NoSectionError:
        return None

    return dict(items)


def _multiple_sections(conf, section_prefix):
    res = []

    idx = 0
    while True:
        section_name = '%s%s' % (section_prefix, idx)
        d = _section_dict(conf, section_name)
        if d is None:
            if idx >= 2:
                break
        else:
            res.append((section_name, d))
        idx += 1

    return res


def read_new(fp):
    conf = ConfigParser.ConfigParser()
    conf.readfp(fp)

    structure = []
    for title_sec_name, title_d in _multiple_sections(conf, 'title'):
        title_data = [_conv_and_defaults(title_d, _title_prop_defaults, _title_info_aliases)]

        for file_sec_name, file_d in _multiple_sections(conf, title_sec_name + '.file'):
            sub_list = []
            for subs_sec_name, subs_d in _multiple_sections(conf, file_sec_name + '.subtitles'):
                sub_list.append(_conv_and_defaults(subs_d, _sub_prop_defaults, {}))

            file_props = _conv_and_defaults(file_d, _file_prop_defaults, {})
            file_props['sub_list'] = sub_list

            title_data.append(file_props)

        structure.append(title_data)

    output_d = _section_dict(conf, 'output')
    output_props = _conv_and_defaults(output_d, _output_prop_defaults, {})

    return structure, output_props


def read_old(fp):
    idstr = cPickle.load(fp)
    if idstr != 'DeVeDe':
        raise NotDevedeFileException()

    structure = cPickle.load(fp)
    output_props = cPickle.load(fp)

    # update dictionaries to contain missing default values
    for title_data in structure:
        _set_defaults(title_data[0], _title_prop_defaults)
        for file_props in title_data[1:]:
            _set_defaults(file_props, _file_prop_defaults)

    _set_defaults(output_props, _output_prop_defaults)

    return structure, output_props


def read(fp):
    if fp.peek(10)[:10] == "S'DeVeDe'\n":
        res = read_old(fp)
    else:
        res = read_new(fp)

    return res


def _write_dict(fp, d, defaults, minimal):
    keys = d.keys()
    keys.sort()
    for key in keys:
        if not minimal or key in defaults and d[key] != defaults[key]:
            fp.write('%s = %s\n' % (key, d[key]))


def write(fp, structure, output_props, minimal=False):
    # only write output-specific things
    output_props = dict([(key, output_props[key]) for key in _output_prop_defaults if key in output_props])

    fp.write('# DeVeDe\n')

    for title_idx, title_data in enumerate(structure):
        fp.write('\n[title%s]\n' % (title_idx + 1))
        _write_dict(fp, title_data[0], _title_prop_defaults, minimal)

        for file_idx, file_props in enumerate(title_data[1:]):
            fp.write('\n[title%s.file%s]\n' % (title_idx + 1, file_idx + 1))
            file_props = file_props.copy()

            if 'path' in file_props:
                fp.write('path = %s\n' % (file_props['path'],))
                del file_props['path']

            sub_list = file_props.get('sub_list')
            if sub_list is not None:
                del file_props['sub_list']

            _write_dict(fp, file_props, _file_prop_defaults, minimal)

            if sub_list is not None:
                for subs_idx, subs_props in enumerate(sub_list):
                    fp.write('\n[title%s.file%s.subtitles%s]\n' % (title_idx + 1, file_idx + 1, subs_idx + 1))
                    _write_dict(fp, subs_props, _sub_prop_defaults, minimal)

    fp.write('\n[output]\n')
    _write_dict(fp, output_props, _output_prop_defaults, minimal)
