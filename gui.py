from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.properties import BooleanProperty, ObjectProperty
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout
from kivy.factory import Factory
from kivy.config import Config
from kivy.utils import platform
from kivy.uix.screenmanager import ScreenManager, Screen
from os import listdir
import os
import metadata
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
        OpenVideo.handle_file(filename)
        self.dismiss_popup()

    def save(self, path, filename):

        self.dismiss_popup()
    def on_enter(self, *args):
        print("Entered")
    def on_leave(self, *args):
        print("Left")
    def handle_file(filename):
        #app= App.get_running_app()
        Header.set_title(str(filename[0]))
        
        width, height = metadata.get_dimensions(filename[0])
        VideoPanel.set_screen('VideoPreview')
        VideoPanel.preview(str(filename[0]))

    pass
class MetadataPanel(GridLayout):
    pass
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
        print(file_path)
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