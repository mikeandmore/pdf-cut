from gi.repository import Gtk as gtk
from gi.repository import Poppler as poppler
from view import View
import cairo
import os

class MainWindow(object):
    UI_XML = './ui.xml'
    
    def __init__(self):
        self.view = View()
        
        self.builder = gtk.Builder()
        self.builder.add_from_file(self.UI_XML)
        self.builder.connect_signals(self)
        
        self.wnd = self.builder.get_object('main')
        container = self.builder.get_object('container')
        container.add(self.view)

        self.wnd.connect('delete-event', gtk.main_quit, None)
        
    def show(self):
        self.wnd.show_all()

    def quit(self, *args):
        gtk.main_quit()

    def open(self, *args):
        dlg = self.builder.get_object('open_dlg')
        dlg.parent = self.wnd

        if dlg.run():
            uri = dlg.get_uri()
            self.load_document(poppler.Document.new_from_file(uri, None))
            
        dlg.hide()

    def load_file(self, filename):
        self.load_document(poppler.Document.new_from_file('file://' + filename,
                                                          None))

    def load_document(self, doc):
        if not doc:
            return
        self.doc = doc
        self.current_page = 0

        self.builder.get_object('next').set_sensitive(doc.get_n_pages() > 1)
        self.builder.get_object('prev').set_sensitive(False)
        self.view.set_page(self.doc, 0)

    def next(self, action):
        self.current_page += 1
        self.view.set_page(self.doc, self.current_page)
        action.set_sensitive(self.doc.get_n_pages() > (self.current_page + 1))
        self.builder.get_object('prev').set_sensitive(self.current_page > 0)
            
    def prev(self, action):
        self.current_page -= 1
        self.view.set_page(self.doc, self.current_page)
        action.set_sensitive(self.current_page > 0)
        self.builder.get_object('next').set_sensitive(
            self.doc.get_n_pages() > (self.current_page + 1))
        
    def zoom_in(self, *args):
        self.view.zoom_in()

    def zoom_out(self, *args):
        self.view.zoom_out()

    def zoom_reset(self, *args):
        self.view.zoom_reset()

    def toggle_snap_to_grid(self, *args):
        self.view.snap_to_grid = not self.view.snap_to_grid

    def clip(self, *args):
        if hasattr(self.view, 'selection_start') and hasattr(self.view, 'selection_end') and self.view.page:
            dlg = self.builder.get_object('clip_save_dlg')
            dlg.parent = self.wnd
            if dlg.run():
                filename = dlg.get_filename()
                if not filename.endswith(".pdf"):
                    filename = filename + '.pdf'
                if os.path.exists(filename):
                    os.remove(filename)
                self.clip_pdf_page(self.view.page, self.view.selection_start,
                               self.view.selection_end, filename)
            dlg.hide()

    def clip_pdf_page(self, page, start, end, output):
        x = min(end[0], start[0])
        y = min(end[1], start[1])
        width = abs(end[0] - start[0])
        height = abs(end[1] - start[1])
        surface = cairo.PDFSurface(output, width, height)
        ctx = cairo.Context(surface)
        ctx.rectangle(0, 0, width, height)
        ctx.clip()
        ctx.translate(-x, -y)
        page.render(ctx)
        surface.flush()
        surface.finish()

