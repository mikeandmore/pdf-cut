from gi.repository import Gtk as gtk
from gi.repository import Gdk as gdk
import cairo


class View(gtk.DrawingArea):
    def __init__(self):
        super(View, self).__init__()

        self.add_events(gdk.EventMask.POINTER_MOTION_MASK | gdk.EventMask.BUTTON_PRESS_MASK | gdk.EventMask.BUTTON_RELEASE_MASK)
        self.connect('draw', self.on_expose, None)
        self.connect('motion-notify-event', self.on_move, None)
        self.connect('button-press-event', self.on_button_press, None)
        self.connect('button-release-event', self.on_button_release, None)
        
        self.page = None
        self.zoom = 1.0
        self.snap_to_grid = True

    def refresh(self):
        if self.page:
            width, height = self.page.get_size()
            self.set_size_request(width * self.zoom, height * self.zoom)
        self.queue_draw()
        
    def zoom_in(self):
        if self.zoom < 8:
            self.zoom += 0.5
            self.refresh()

    def zoom_out(self):
        if self.zoom > 0.5:
            self.zoom -= 0.5
            self.refresh()

    def zoom_reset(self):
        self.zoom = 1.0
        self.refresh()

    def snap_grid(self, x, y):
        if not self.page:
            return (0, 0)
        
        rounded = 1
        if self.snap_to_grid:
            rounded = 5
        width, height = self.page.get_size()
        return (min(int(x / self.zoom / rounded) * rounded, width),
                min(int(y / self.zoom / rounded) * rounded, height))

    def on_move(self, widget, event, data):
        if hasattr(self, 'mouse_down'):
            new_selection_end = self.snap_grid(event.x, event.y)
            if (not hasattr(self, 'selection_end')) or (self.selection_end != new_selection_end):
                self.selection_end = new_selection_end
                self.queue_draw()

    def on_button_press(self, widget, event, data):
        if event.button != 1:
            return
        self.mouse_down = True
        self.selection_start = self.snap_grid(event.x, event.y)
        if hasattr(self, 'selection_end'):
            del self.selection_end

    def on_button_release(self, widget, event, data):
        if event.button != 1:
            return
        del self.mouse_down
        self.selection_end = self.snap_grid(event.x, event.y)
        print self.selection_start, self.selection_end
        if self.selection_end == self.selection_start:
            del self.selection_end
            del self.selection_start
        else:
            pass
        self.queue_draw()
        
    def on_expose(self, widget, cr, data):
        if not self.page:
            return
        # setup the zoom
        mtr = cairo.Matrix()
        mtr.scale(self.zoom, self.zoom)
        cr.transform(mtr)
        # setup the clip
        cr.set_source_rgba(1.0, 1.0, 1.0)
        width, height = self.page.get_size()
        cr.rectangle(0, 0, width, height)
        cr.clip()
        
        cr.paint()
        self.page.render(cr)
        if hasattr(self, 'selection_start') and hasattr(self, 'selection_end'):
            width = self.selection_end[0] - self.selection_start[0]
            height = self.selection_end[1] - self.selection_start[1]
            
            cr.rectangle(self.selection_start[0], self.selection_start[1],
                         width, height)
            path = cr.copy_path()
            cr.set_source_rgba(0.4, 0.4, 0.9, 0.4)
            cr.fill()
            cr.append_path(path)
            cr.set_source_rgba(0.3, 0.3, 1.0, 0.6)
            cr.stroke()

    def set_page(self, doc, page):
        self.page = doc.get_page(page)
        self.refresh()
