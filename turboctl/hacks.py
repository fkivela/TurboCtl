"""This module contains some temporary inelegant fixes that hopefully can be
removed later.
"""
import weakref

import urwid


def monkeypatch_urwid():
    """Monkey-patch a bug in Urwid.

    Urwid has a bug that causes a memory leak; the issue is documented here:
    https://github.com/urwid/urwid/issues/451
    The issue is still open on 2024-05-07 and apparently the simple fix here
    breaks something else, but it seems to work for the purposes of TurboCtl. 
    """

    # The CanvasCache.store method, copied from urwid, with only one line
    # altered.
    # It might be possible to only patch that single line by modifying the code
    # with the ast or inspect modules, but this is much easier. 
    def store(cls, wcls, canvas):
        """
        Store a weakref to canvas in the cache.
    
        wcls -- widget class that contains render() function
        canvas -- rendered canvas with widget_info (widget, size, focus)
        """
        if not canvas.cacheable:
            return
    
        assert canvas.widget_info, "Can't store canvas without widget_info"
        widget, size, focus = canvas.widget_info
        def walk_depends(canv):
            """
            Collect all child widgets for determining who we
            depend on.
            """
            # FIXME: is this recursion necessary?  The cache
            # invalidating might work with only one level.
            depends = []
            for x, y, c, pos in canv.children:
                if c.widget_info:
                    depends.append(c.widget_info[0])
                elif hasattr(c, 'children'):
                    depends.extend(walk_depends(c))
            return depends
    
        # use explicit depends_on if available from the canvas
        depends_on = getattr(canvas, 'depends_on', None)
        if depends_on is None and hasattr(canvas, 'children'):
            depends_on = walk_depends(canvas)
        if depends_on:
            for w in depends_on:
                if w not in cls._widgets:
                    return
            for w in depends_on:
                # The patched part is here.
                # The original line:
                # cls._deps.setdefault(w,[]).append(widget)
                # The patched line: 
                cls._deps.setdefault(w,set()).add(widget)
    
        ref = weakref.ref(canvas, cls.cleanup)
        cls._refs[ref] = (widget, wcls, size, focus)
        cls._widgets.setdefault(widget, {})[(wcls, size, focus)] = ref
    store = classmethod(store)
    
    # Replace the original store method with the modified version.
    urwid.CanvasCache.store = store