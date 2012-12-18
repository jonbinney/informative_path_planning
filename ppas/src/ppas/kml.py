def make_kml_str(name, description, elements):
    kml_str = ''
    kml_str += '<?xml version="1.0" encoding="UTF-8"?>\n'
    kml_str += '<kml xmlns="http://www.opengis.net/kml/2.2">\n'
    kml_str += '<Document>\n'
    kml_str += ' <name>%s</name>\n' % name
    kml_str += '<description>%s</description>\n' % description
    for el in elements:
        if el['element_type'] == 'path':
            kml_str += make_path_str(el)
        else:
            dieeeee
    kml_str += '</Document>\n'
    kml_str += '</kml>\n'
    return kml_str

def make_path_str(el_dict):
    kml_str = ''
    kml_str += '<Style id="yellowLineGreenPoly">\n'
    kml_str += '<LineStyle>\n'
    kml_str += '<color>7f00ffff</color>\n'
    kml_str += '<width>4</width>\n'
    kml_str += '</LineStyle>\n'
    kml_str += '<PolyStyle>\n'
    kml_str += '<color>7f00ff00</color>\n'
    kml_str += '</PolyStyle>\n'
    kml_str += '</Style>\n'
    kml_str += '<Placemark>\n'
    kml_str += '<name>%s</name>\n' % el_dict['name']
    kml_str += '<description>%s</description>\n' % el_dict['description']
    kml_str += '<styleUrl>#yellowLineGreenPoly</styleUrl>\n'
    kml_str += '<LineString>\n'
    kml_str += '<tessellate>1</tessellate>\n'
    kml_str += '<altitudeMode>absolute</altitudeMode>\n'
    kml_str += '<coordinates>\n'
    for p in el_dict['points']:
        kml_str += '%.4f,%.4f,0\n' % (p[1], p[0])
    kml_str += '</coordinates>\n'
    kml_str += '</LineString>\n'
    kml_str += '</Placemark>\n'
    return kml_str
