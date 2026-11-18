class q995e_0:
    def render(self):
        pass

def q995e_1():
    pass

widget = q995e_0()
widget.render = q995e_1
widget.render()
delattr(widget, "render")
widget.render()
