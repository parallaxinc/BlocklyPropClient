from kivy.uix.boxlayout import BoxLayout

__author__ = 'Michel'

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.lang import Builder


class BlocklyProp(BoxLayout):
    def build(self):
        self.add_widget(Builder.load_file('BlocklyProp.kv'))

class BlocklyPropApp(App):
    def build(self):
        return BlocklyProp()


if __name__ == '__main__':
    BlocklyPropApp().run()