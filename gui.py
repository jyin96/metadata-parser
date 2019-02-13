from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.recycleview import RecycleView
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


class MetadataType:
    def __init__(self, field_name, options):
        self.field_name = field_name
        self.options = options
        pass
#Guesses parse the metadata, and return <guess>, [options] 
def guess_spherical(metadata):
    options = [True, False]
    if (metadata == None) or not metadata['Spherical']:
        disable_spherical_options()
        return False, options

    return True, [True, False]

def handle_spherical_changed(selection):
    pass

def guess_projection(metadata):
    options = ['Equirectangular','Fisheye','Cubemap']
    if 'ProjectionType' not in metadata:
        return 'Unknown', options
    return metadata['ProjectionType'], options 
def handle_projection_changed(selection):
    pass
def guess_degrees(metadata):
    options = [360,180]
    if ('CroppedAreaLeftPixels' not in metadata) or metadata['CroppedAreaLeftPixels'] == 0:
        return 360, options
    
    return 180, options
    pass
def handle_degrees_changed(selection):
    pass

    #if metadata 


#disable the other 
def disable_spherical_options():
    return

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

    def dismiss_popup(self):
        self._popup.dismiss()

    def show_load(self):
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def show_save(self):
        content = SaveDialog(save=self.save, cancel=self.dismiss_popup)
        self._popup = Popup(title="Save file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def load(self, path, filename):
        OpenVideo.handle_file(str(filename[0]))
        self.dismiss_popup()

    def save(self, path, filename):

        self.dismiss_popup()
    def on_enter(self, *args):
        print("Entered")
    def on_leave(self, *args):
        print("Left")
    def handle_file(filename):
        #app= App.get_running_app()
        Header.set_title(filename)
        
        width, height = metadata.get_dimensions(filename)
        Logger.info("Width: "+str(width))
        Logger.info("Height: "+str(height))
        VideoPanel.set_screen('VideoPreview')
        VideoPanel.preview(filename)
        xml = metadata.parse_mpeg4(filename)
        metadata_list, metadata_dict = metadata.parse_xml(xml)
        MetadataPanel.populate(metadata_list, metadata_dict)
        if xml == None:
            return
        for child in xml:
            Logger.info("XML: {0}: {1}".format(child.tag.split("}")[-1],child.text))
    pass
dropdowns = {}
class MetadataPanel(ScrollView):
    def populate(metadata_list, metadata_dict):
        panel = app.root.ids.list_content
        panel.clear_widgets()
        Logger.info("Running: Populate")
        is_spherical, spherical_options = guess_spherical(metadata_dict)
        Logger.info("Spherical: "+str(is_spherical))

        if is_spherical:
            projection, projection_options = guess_projection(metadata_dict)
            Logger.info("Projection: "+str(projection))

        #layout = BoxLayout(orientation='vertical')
        #layout.add_widget(MetadataBox(key="Test1", value="value1"))
        dropdowns = {}
        #for item in metadata_list:
        #    panel.add_widget(MetadataBox(key=item[0], value=item[1]))
        panel.add_widget(MetadataBox(key="Spherical", value=is_spherical,options=spherical_options))
        
        panel.bind(minimum_height=panel.setter("height"))
        app.root.ids.metadata_panel.height = app.root.ids.video_panel.height
        
        #app.root.ids.metadata_panel.height = Window.height
    
    pass
class MetadataBox(BoxLayout):
    def __init__(self, **kwargs):
        super(MetadataBox, self).__init__()
        
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
        dropdowns[key] = dropdown
        options = kwargs["options"]
        #for loop
        for option in options:
            btn = Button(text=str(option), size_hint_y = None, height = 44, border=(10,0,10,0), background_color=(.3,.3,.3,1))
            btn.bind(on_release=lambda btn: dropdown.select(btn.text))
            dropdowns[key].add_widget(btn)

        value_button = self.ids.value
        value_button.bind(on_release=dropdown.open)
        dropdown.bind(on_select=lambda instance, x: setattr(value_button,'text',x))
        

class Footer(BoxLayout):
    pass
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