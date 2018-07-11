import npyscreen, sys

class PointBox(npyscreen.CheckBox):
    False_box = "   "
    True_box = "  •"

class SideSelector(npyscreen.BoxTitle):
    _contained_widget = npyscreen.SelectOne

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.entry_widget._contained_widgets = PointBox

    def when_value_edited(self):
        if(self.value != []):
            event = npyscreen.Event("event_album_selected", payload=self.value)
            self.parent.parentApp.queue_event(event)
    
    def resize(self):
        self.entry_widget._resize()
        self.entry_widget.display()
        self.display()

class SongSelector(npyscreen.BoxTitle):
    _contained_widget = npyscreen.MultiSelect

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.entry_widget._contained_widgets = PointBox

    def resize(self):
        self.entry_widget._resize()
        self.entry_widget.display()
        self.display()

class ExitButton(npyscreen.MiniButtonPress):
    def whenPressed(self):
        sys.exit(0)