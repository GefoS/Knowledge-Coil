import queue
from xml.etree import ElementTree as et
import os
from PySide2.QtCore import Qt
from PySide2.QtGui import QKeySequence

import random

q = queue.Queue()

for i in range(1, 10):
    q.put(i)

while not q.empty():
    print(q.get(q))
    if q.qsize() == 1:
        print('last element')
        print(q.get(q))
        q.put('heh')
        break
print(q.get())