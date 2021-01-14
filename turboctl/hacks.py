"""This module contains some temporary inelegant fixes that hopefully can be
removed later.
"""

from functools import singledispatch, update_wrapper
import weakref

import urwid


def singledispatchmethod(func):
    """The functools.singledispatchmethod decorator is included in Python 3.8,
    but not in 3.7.
    Because the support for 3.8 is not very widespread yet,
    TurboCtl still uses 3.7.
    The singledispatchmethod decorator is therefore defined here until TurboCtl is
    updated to Python 3.8, at which point this can be removed.
    
    The code here was copied from StackOverflow with slight alterations. 
    """
    dispatcher = singledispatch(func)
    def wrapper(*args, **kwargs):
        try:
            return dispatcher.dispatch(args[1].__class__)(*args, **kwargs)
        except IndexError:
            raise TypeError('at least 1 positional argument is required')
    wrapper.register = dispatcher.register
    update_wrapper(wrapper, func)
    return wrapper


def monkeypatch_urwid():
    """Urwid seems to have a bug that causes a memory leak.
    This function monkey-patches that leak.
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