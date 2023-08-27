class Widget:
    def __init__(self, text, x, y):
        self.y = y
        self.x = x
        self.text = text

    def print_info(selfself):
        print("Кнопка:", self.text)
        print("Розташування: (" + str(self.x) + ", " + str(self.y) + ")")


class Button(Widget):
    def __init__(self, text, x, y):
        super().__nit__(text, x, y)
        self.is_clicked = False

    def click(selfself):
        self.is_clicked = True
        print("Ви зареєстрован")


button = Button("Брати участь", 100, 100)
answer = input("хочете? так/ні\n").lower()
if answer =="":
    button.click()
else:
    print("Шкода!")