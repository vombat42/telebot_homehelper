import copy

class Rectangle:
    number_side = 4
    number_vertex = 4
    number_corner = 4

    def __init__(self, a=1, b=1, color='Red'):
        self.a = a
        self.b = b
        self.perim = 2 * (a + b)
        self.color = color


    def area(self):
        return self.a * self.b

    def dlina(self):
        return self.a

    def shirina(self):
        return self.b

    def info(self):
        print(f' Я прямоугольник с параметрами:')
        print(f' Длина {self.dlina()}')
        print(f' Ширина {self.shirina()}')
        print(f' Периметр {self.perim}')
        print(f' Площадь {self.area()}')
        print(f' Цвет {self.color}')


rect = Rectangle(5, 6, 'Green')
#rect = Rectangle(3,2,)
#rect2=copy.deepcopy(rect)
rect2=copy.copy(rect)
rect.info()
rect.color = 'blue'
rect.info()
rect2.info()


