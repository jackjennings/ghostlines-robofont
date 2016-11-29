from vanilla import Button

class CounterButton(Button):

    def __init__(self, dimensions, label, **kwargs):
        self.label = label[0]
        self.count_label = label[1]
        super(CounterButton, self).__init__(dimensions, label, **kwargs)

    @property
    def amount(self):
        return self._amount

    @amount.setter
    def amount(self, value):
        self._amount = value

        if self._amount is 0:
            self.setTitle(self.label)
        else:
            self.setTitle(self.count_label.format(self._amount))

        return self.amount