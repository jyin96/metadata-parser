from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.properties import BooleanProperty, ObjectProperty
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout
from kivy.factory import Factory
from kivy.config import Config
from kivy.utils import platform
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.dropdown import DropDown
from kivy.logger import Logger
from os import listdir
import xml.etree
import xml.etree.ElementTree
import os
import metadata
import metadata_utils

"""
Mapping from multiple recognized names to an attribute type:
    Spherical
    Projection type
    Stereo mode

    Degrees is an abstract attribute

Ignored fields:
    stitched
    stitching software
    source count

Get the video dimensions using MediaInfo
    width, height

If CroppedAreaLeftPixels... is undefined, degrees is assumed to be 360
If CroppedAreaLeftPixels is non-zero, degrees is probably 180? We can calculate it as 

Templates:
Unknown:
    Spherical: False
Mono 360:
"""

ACCEPTED_EXTENSIONS = [".mp4",".mov"]
recent_path = ""
class MetadataType:
    def __init__(self, field_name, options):
        self.field_name = field_name
        self.options = options
        pass
#Guesses parse the metadata, and return <guess>, [options] 
def guess_spherical(metadata):
    options = [True, False]
    if (metadata == None) or not metadata['Spherical']:
        return False, options

    return True, [True, False]

def handle_spherical_changed(selection):
    Logger.info("OnChange:" +selection)
    if selection=='True':
        enable_spherical_options()
    else:
        disable_spherical_options()
    pass

def guess_projection(metadata):
    options = ['equirectangular','fisheye','cubemap']
    if (metadata == None) or ('ProjectionType' not in metadata):
        return 'Unknown', options
    return metadata['ProjectionType'], options 
def handle_projection_changed(selection):
    pass
def guess_degrees(metadata):
    options = [360,180]
    if metadata==None:
        return 'n/a', options
    if ('CroppedAreaLeftPixels' not in metadata) or metadata['CroppedAreaImageWidthPixels'] == metadata['FullPanoWidthPixels']:
        return 360, options
    
    return 180, options
    pass
def handle_degrees_changed(selection):
    pass

def guess_stereo_mode(metadata):
    options = ["monoscopic", "left-right","top-bottom"]
    if metadata==None:
        return "n/a", options
    if 'StereoMode' not in metadata:
        return "monoscopic", options
    return metadata['StereoMode'], options

    #if metadata 
def handle_stereo_mode_changed(selection):
    pass

def disable_spherical_options():
    projection_widget.disable()
    degrees_widget.disable()
    stereo_widget.disable()
def enable_spherical_options():
    projection_widget.enable()
    degrees_widget.enable()
    stereo_widget.enable()
    
os.environ["KIVY_NO_CONSOLELOG"] = "1"
Window.clearcolor = [x/255 for x in (35, 40, 48, 1)]
kv_path = "./kv/"
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
#Config.set('graphics','minimum_height',700)
Config.set('graphics', 'resizable', False)
for kv in listdir(kv_path):
    Builder.load_file(kv_path+kv)
app = None

class HoverBehavior(object):
    """Hover behavior.
    :Events:
        `on_enter`
            Fired when mouse enter the bbox of the widget.
        `on_leave`
            Fired when the mouse exit the widget 
    """

    hovered = BooleanProperty(False)
    border_point= ObjectProperty(None)
    '''Contains the last relevant point received by the Hoverable. This can
    be used in `on_enter` or `on_leave` in order to know where was dispatched the event.
    '''

    def __init__(self, **kwargs):
        self.register_event_type('on_enter')
        self.register_event_type('on_leave')
        Window.bind(mouse_pos=self.on_mouse_pos)
        super(HoverBehavior, self).__init__(**kwargs)
    
    def on_mouse_pos(self, *args):
        if not self.get_root_window():
            return # do proceed if I'm not displayed <=> If have no parent
        pos = args[1]
        #Next line to_widget allow to compensate for relative layout
        inside = self.collide_point(*self.to_widget(*pos))
        if self.hovered == inside:
            #We have already done what was needed
            return
        self.border_point = pos
        self.hovered = inside
        if inside:
            self.dispatch('on_enter')
        else:
            self.dispatch('on_leave')

    def on_enter(self):
        pass

    def on_leave(self):
        pass

Factory.register('HoverBehavior', HoverBehavior)

class Header(BoxLayout):
    def set_title(title):
        app.root.ids.header_title.text = title
    pass
class VideoPanel(ScreenManager):
    """
    def __init__(self, **kwargs):
        super(VideoPanel, self).__init__(**kwargs)
        pass
    """
    def instance():
        return app.root.ids.video_panel
    def set_screen(screen_name):
        app.root.ids.video_panel.current=screen_name
    def preview(filename):
        app.root.ids.video_panel.ids.video_preview_player.texture = metadata.get_first_frame(filename)
    pass
class VideoPreview(Screen):
    
    pass
class OpenVideoScreen(Screen):
    pass

class OpenVideo(Button, HoverBehavior):
    display = ObjectProperty()
    def instance():
        return VideoPanel.instance().ids.open_video_utils
    def dismiss_popup(self):
        self._popup.dismiss()

    def show_load(self):
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        if recent_path != "":
            content.path = recent_path
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def show_save(self):
        content = SaveDialog(save=self.save, cancel=self.dismiss_popup)
        if recent_path != "":
            content.ids.filechooser.path = recent_path
        self._popup = Popup(title="Save file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def load(self, path, filename):
        OpenVideo.handle_file(str(filename[0]))
        self.dismiss_popup()

    def save(self, path, filename):
        abs_path = os.path.join(path, filename)
        Footer.save_file(abs_path)
        self.dismiss_popup()
    def on_enter(self, *args):
        print("Entered")
    def on_leave(self, *args):
        print("Left")
    def handle_file(filename):
        global parsed_metadata, src_file, recent_path
        base_name, extension = os.path.splitext(filename)
        recent_path = os.path.dirname(filename)
        if extension.lower() not in ACCEPTED_EXTENSIONS:
            return OpenVideo.handle_invalid_file(filename)
        src_file = filename
        #app= App.get_running_app()
        Header.set_title(filename)
        Footer.enable_save_button()
        #width, height = metadata.get_dimensions(filename)
        track = metadata.get_track_info(filename)
        VideoPanel.set_screen('VideoPreview')
        VideoPanel.preview(filename)
        parsed_metadata = metadata.parse_mpeg4(filename)
        metadata_list, metadata_dict = metadata.parse_xml(parsed_metadata)
        MetadataPanel.populate(metadata_list, metadata_dict, track)
        for child in (parsed_metadata or []):
            Logger.info("XML: {0}: {1}".format(child.tag.split("}")[-1],child.text))
    def handle_invalid_file(filename):
        #TODO Show a notification
        Logger.info("Error: Invalid file "+filename)
        pass
dropdowns = {}
spherical_widget = None
projection_widget = None
degrees_widget = None
stereo_widget = None
track_info = None
parsed_metadata = None
src_file = None
class MetadataPanel(ScrollView):
    def populate(metadata_list, metadata_dict, track):
        global spherical_widget, projection_widget, degrees_widget, stereo_widget, track_info
        track_info = track
        width = track['width']
        height = track['height']
        frame_rate = track['frame_rate']
        encoding = track['internet_media_type']
        bit_rate = track['other_bit_rate'][0]
        duration = track['other_duration'][0]
        file_size = track['other_stream_size'][0]
        panel = app.root.ids.list_content
        panel.clear_widgets()
        Logger.info("Running: Populate")
        is_spherical, spherical_options = guess_spherical(metadata_dict)
        Logger.info("Spherical: "+str(is_spherical))
        spherical_callback = lambda text: handle_spherical_changed(text)
        
        projection, projection_options = guess_projection(metadata_dict)
        Logger.info("Projection: "+str(projection))
        projection_callback = lambda text: handle_projection_changed(text)

        degrees, degrees_options = guess_degrees(metadata_dict)
        Logger.info("Degrees: "+str(degrees))
        degrees_callback = lambda text: handle_degrees_changed(text)

        stereo, stereo_options = guess_stereo_mode(metadata_dict)
        Logger.info("StereoMode: "+str(stereo))
        stereo_callback = lambda text: handle_stereo_mode_changed(text)

        spherical_widget=MetadataBox(key="Spherical", value=is_spherical,options=spherical_options,callback = spherical_callback)
        projection_widget=MetadataBox(key="Projection", value=projection,options=projection_options,callback = projection_callback)
        degrees_widget = MetadataBox(key="Degrees", value=degrees,options=degrees_options,callback = degrees_callback)
        stereo_widget = MetadataBox(key="Stereo Mode", value=stereo, options=stereo_options, callback = stereo_callback)

        panel.add_widget(spherical_widget)
        panel.add_widget(projection_widget)
        panel.add_widget(stereo_widget)
        panel.add_widget(degrees_widget)
        if not is_spherical:
            disable_spherical_options()


        dropdowns = {}
        panel.add_widget(ReadOnlyMetadata(key="Width", value=width))
        panel.add_widget(ReadOnlyMetadata(key="Height", value=height))
        panel.add_widget(ReadOnlyMetadata(key="Frame Rate", value=frame_rate))
        panel.add_widget(ReadOnlyMetadata(key="Encoding", value=encoding))
        panel.add_widget(ReadOnlyMetadata(key="Bit Rate", value=bit_rate))
        panel.add_widget(ReadOnlyMetadata(key="Duration", value=duration))
        panel.add_widget(ReadOnlyMetadata(key="File Size", value=file_size))
        
        if metadata_list:
            for item in metadata_list:
                panel.add_widget(ReadOnlyMetadata(key=item[0], value=item[1]))
            
        
        panel.bind(minimum_height=panel.setter("height"))
        app.root.ids.metadata_panel.height = app.root.ids.video_panel.height
        
        #app.root.ids.metadata_panel.height = Window.height
    
    pass
class MetadataBox(BoxLayout):
    def __init__(self, **kwargs):
        super(MetadataBox, self).__init__()
        self.id = str(kwargs["key"])
        if "key" in kwargs.keys():
            self.ids.key.text = str(kwargs["key"])
        else:
            self.ids.key.text = "DefaultKey"
        if "value" in kwargs.keys():
            self.ids.value.text = str(kwargs["value"])
        else:
            self.ids.value.text = "DefaultValue"
        
        key = self.ids.key.text
        dropdown = DropDown()
        self.dropdown=dropdown
        dropdowns[key] = dropdown
        options = kwargs["options"]
        for option in options:
            btn = Button(text=str(option), size_hint_y = None, height = 44, border=(10,5,10,5), background_color=(.3,.3,.3,1))
            btn.bind(on_release=lambda btn: (dropdown.select(btn.text),kwargs["callback"](btn.text)))
            dropdowns[key].add_widget(btn)
        value_button = self.ids.value
        value_button.bind(on_release=dropdown.open)
        dropdown.bind(on_select=lambda instance, x: setattr(value_button,'text',x))
    def disable(self):
        value_button = self.ids.value
        value_button.unbind(on_release=self.dropdown.open)
        value_button.background_color = (.7,.7,.7,1)
    def enable(self):
        value_button = self.ids.value
        value_button.bind(on_release=self.dropdown.open)
        value_button.background_color = (1,1,1,1)
    def get_value(self):
        return self.ids.value.text


class ReadOnlyMetadata(BoxLayout):
    def __init__(self, **kwargs):
        super(ReadOnlyMetadata, self).__init__()
        self.id = str(kwargs["key"])
        self.ids.key.text = str(kwargs["key"]+":")
        self.ids.value.text = str(kwargs["value"])

class Footer(FloatLayout):
    def instance():
        return app.root.ids.display
    def enable_save_button():
        btn = app.root.ids.save_button
        btn.background_color = (1,1,1,1)
        btn.bind(on_release=lambda btn: Footer.show_save())
        pass
    def disable_save_button():
        pass
    

    def show_save():
        OpenVideo.instance().show_save()
    ### To do: 
    # Still need to handle:
    #   spherical=false, 
    #   projection != equi
    #   non-standard degrees
    #   spatial audio
    #
    ###
    def save_file(out_file):
        stereo = stereo_widget.get_value().lower()
        degrees = degrees_widget.get_value()
        crop = None
        if degrees == "180":
            full_pano_width = track_info["width"]
            full_pano_height = track_info["height"]
            if stereo== "monoscopic":
                full_pano_width *= 2
            elif stereo == "left-right":
                pass
            elif stereo == "top-bottom":
                full_pano_width *= 2
                full_pano_height /= 2
            cropped_width_pixels = full_pano_width/2
            cropped_height_pixels = full_pano_height
            # From Google's metadata utils:
            ##  We are pretty restrictive and don't allow anything strange. There
            ##  could be use-cases for a horizontal offset that essentially
            ##  translates the domain, but we don't support this (so that no
            ##  extra work has to be done on the client).
            cropped_area_left_pixels = cropped_width_pixels/2
            cropped_area_top_pixels = 0
            crop = "{0}:{1}:{2}:{3}:{4}:{5}".format(int(cropped_width_pixels),\
                                                    int(cropped_height_pixels),\
                                                    int(full_pano_width),\
                                                    int(full_pano_height),\
                                                    int(cropped_area_left_pixels),\
                                                    int(cropped_area_top_pixels))
        generated_metadata = metadata_utils.Metadata()
        generated_metadata.video = metadata_utils.generate_spherical_xml(stereo,crop)
        #generated_metadata.audio = GetAudio()
        metadata_utils.inject_metadata(src_file, out_file,generated_metadata,Logger.info)


        """
         crop region. Must specify 6 integers in the form of
                        "w:h:f_w:f_h:x:y" where w=CroppedAreaImageWidthPixels
                        h=CroppedAreaImageHeightPixels f_w=FullPanoWidthPixels
                        f_h=FullPanoHeightPixels x=CroppedAreaLeftPixels
                        y=CroppedAreaTopPixels
        """

        
        #metadata_utils.inject_metadata()

    pass
def GetAudio():
    spatial_audio_description = metadata_utils.get_spatial_audio_description(parsed_metadata.num_audio_channels)
    if spatial_audio_description.is_supported:
        metadata_audio = metadata_utils.get_spatial_audio_metadata(
            spatial_audio_description.order,
            spatial_audio_description.has_head_locked_stereo)
    else:
        Logger.info(("Audio has %d channel(s) and is not a supported spatial audio format." % (parsed_metadata.num_audio_channels)))
    return metadata_audio
class LoadDialog(FloatLayout):
    def __init__(self, **kwargs):
        super(LoadDialog, self).__init__(**kwargs)
        self.drives_list.adapter.bind(on_selection_change=self.drive_selection_changed)

    def get_win_drives(self):
        if platform == 'win':
            import win32api

            drives = win32api.GetLogicalDriveStrings()
            drives = drives.split('\000')[:-1]

            return drives
        else:    
            return []

    def drive_selection_changed(self, *args):
        selected_item = args[0].selection[0].text
        self.filechooser.path = selected_item

    load = ObjectProperty(None)
    cancel = ObjectProperty(None)


class SaveDialog(FloatLayout):
    save = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)
    


class Container(GridLayout):
    pass    

    


class MainApp(App):

    def build(self):
        Window.bind(on_dropfile=self.on_dropfile)
        self.title = 'VR Metadata'
        return Container()
    def on_dropfile(self, window, file_path):
        file_path = file_path.decode('utf-8')
        Logger.info('File drop: '+file_path)
        OpenVideo.handle_file(file_path)
        return
    
Factory.register('root', cls=Container)
Factory.register('LoadDialog', cls=LoadDialog)
Factory.register('SaveDialog', cls=SaveDialog)

if __name__ == "__main__":

    app = MainApp()
    app.run()
"""
class WindowFileDropExampleApp(App):
    def build(self):
        Window.bind(on_dropfile=self._on_file_drop)
        return

    def _on_file_drop(self, window, file_path):
        print(file_path)
        return

if __name__ == '__main__':
    WindowFileDropExampleApp().run()

"""