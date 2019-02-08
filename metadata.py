from spatialmedia import mpeg
import xml.etree
import xml.etree.ElementTree
from pymediainfo import MediaInfo
import mp4_utils
import cv2
from kivy.graphics.texture import Texture

def get_first_frame(url):
    vidcap = cv2.VideoCapture(url)
    success, frame = vidcap.read()
    if (success):
        # convert it to texture
        buf1 = cv2.flip(frame, 0)
        buf = buf1.tostring()
        texture1 = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        texture1.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        return texture1
def parse_mpeg4(input_file):
    with open(input_file,"rb") as in_fh:
        mpeg4_file = mpeg.load(in_fh)
        uuid_box = None
        for element in mpeg4_file.contents:
            
            if type(element) is mpeg.Box:
                print(element.name)
            elif type(element) is mpeg.Container:
                element.print_structure()

            
            if element.name == mpeg.constants.TAG_MOOV:
                for moov_element in element.contents:
                    if moov_element.name == mpeg.constants.TAG_TRAK:
                        for trak_element in moov_element.contents:
                            if trak_element.name == mpeg.constants.TAG_MDIA:
                                for mdia_element in trak_element.contents:
                                    if mdia_element.name == mpeg.constants.TAG_MINF:
                                        for minf_element in mdia_element.contents:
                                            if isinstance(minf_element,mpeg.Box):
                                                print(minf_element.name)
                                                print_box(in_fh,minf_element)
                            if trak_element.name == mpeg.constants.TAG_UUID:
                                uuid_box = trak_element
        if uuid_box.contents == None:
            in_fh.seek(uuid_box.content_start())
            id = in_fh.read(16)
            contents = in_fh.read(uuid_box.content_size - 16)
            print(contents)
            parsed_xml = xml.etree.ElementTree.XML(contents)
def print_box(fh, box):
    fh.seek(box.content_start())
    #id = fh.read(16)
    contents = fh.read(box.content_size)
    print(contents)
    #parsed_xml = xml.etree.ElementTree.XML(contents)
    #print(prettify(parsed_xml))
def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = xml.etree.ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="\t")

def get_dimensions(input_file):
    media_info = MediaInfo.parse(input_file)
    for track in media_info.tracks:
        if track.track_type == 'Video':
            track = track.to_data()
            return track['width'], track['height']
    #mediainfo = MediaInfoDLL3.MediaInfo()

if __name__ == "__main__":
    pass
#parse_mpeg4("Peach Lake Sunrise 3k mono.mp4")
#get_dimensions("Peach Lake Sunrise 3k mono.mp4")
#mp4_utils.get_first_frame("Peach Lake Sunrise 3k mono.mp4")