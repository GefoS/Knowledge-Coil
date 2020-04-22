'''def hex_to_key(hex):
    switcher = {
        16777249: 'Control',
        16777251: 'Alt',
        16777248: "Shift"
    }
    if hex in switcher.keys():
		return -1
				else:
	return -2
'''


class KeyHistory:
    def __init__(self):
        self.is_present = True
        self.present_history = []
        self.past_history = []

    def draw(self, key):
        if self.is_present:
            self.present_history.append(key)
        else:
            self.present_history = self.past_history.append(key)
            self.past_history.clear()
            self.is_present = True

    def undo(self):
        if self.is_present and self.present_history:
            self.past_history = self.present_history[:-1]
            self.is_present = False
        elif self.past_history:
            self.past_history = self.past_history[:-1]

    def redo(self):
        if not self.is_present:
            if len(self.past_history) + 1 == len(self.present_history):
                self.is_present = True
                self.past_history.clear()
            else:
                self.past_history = self.present_history[:len(self.past_history) + 1]

    def printer(self):
        if self.is_present:
            print('we are in present: ', self.present_history)
        else:
            print('we are in past: ', self.past_history)
            print('our future: ', self.present_history)


def main():
    h = KeyHistory()

    h.draw(1)
    h.draw(228)
    h.draw(322)
    h.draw(-1)

    h.undo()
    h.undo()
    h.undo()
    h.undo()
    h.undo()
    h.undo()
    h.undo()
    h.printer()


if __name__ == '__main__':
    main()
