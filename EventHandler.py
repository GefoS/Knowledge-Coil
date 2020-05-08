import warnings

from PySide2 import QtCore
from PySide2.QtCore import Qt
from PySide2.QtGui import QKeySequence

from global_params import KeyShortcuts


def hook_mouse_event(event):
    if event.button() == Qt.MouseButton.LeftButton:
        return (KeyShortcuts.MOUSE_LEFT[2])
    elif event.button() == Qt.MouseButton.RightButton:
        return (KeyShortcuts.MOUSE_RIGHT[2])


def invert_mouse_event(event):
    if event.button() == Qt.MouseButton.LeftButton:
        return KeyShortcuts.MOUSE_LEFT[2]
    elif event.button() == Qt.MouseButton.RightButton:
        return KeyShortcuts.MOUSE_RIGHT[2]


def hook_key_event(event):
    key = event.key()

    if key == Qt.Key_unknown:
        warnings.warn("Unknown key from a macro probably")
        return True

    if key in (Qt.Key_Shift, Qt.Key_Control, Qt.Key_Alt, Qt.Key_Meta):
        return True

    modifiers = event.modifiers()
    if modifiers & QtCore.Qt.ShiftModifier:
        key += QtCore.Qt.SHIFT
    if modifiers & QtCore.Qt.ControlModifier:
        key += QtCore.Qt.CTRL
    if modifiers & QtCore.Qt.AltModifier:
        key += QtCore.Qt.ALT
    if modifiers & QtCore.Qt.MetaModifier:
        key += QtCore.Qt.META

    #k_seq = QKeySequence(key)

    if QKeySequence(key) in KeyShortcuts.reserved_shortcuts:
        return True

    return key