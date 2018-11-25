from random import randint


class Dice:
    def __init__(self, faces, next_dice=None):
        self.__faces = faces
        self.__next = next_dice

    def roll(self):
        result = randint(1, self.__faces)
        if self.__next is not None:
            if type(self.__next) is Dice:
                result += self.__next.roll()
            else:
                result += self.__next
        return result

    def range(self):
        lower, upper = 1, self.__faces
        if self.__next is not None:
            if type(self.__next) is Dice:
                other_lower, other_upper = self.__next.range()
                lower += other_lower
                upper += other_upper
            else:
                lower += self.__next
                upper += self.__next
        return lower, upper

    def range_string(self):
        lower, upper = self.range()
        return str(lower) + "-" + str(upper)

    def roll_best_of(self, num):
        result = 0
        for tries in range(num):
            result = max(result, self.roll())
        return result

    def __str__(self):
        result = "d"+str(self.__faces)
        if self.__next is not None:
            result = result + "+" + str(self.__next)
        return result

    def __sub__(self, next):
        if type(next) is int:
            return self + (-next)
        else:
            raise ValueError("Only integers can be subtracted.")

    def __add__(self, next):
        if self.__next is None:
            self.__next = next
        else:
            # toevoegen op het einde
            self.__next = self.__next + next
        return self # toelaten om Dice(6) + Dice(4) + Dice(6) + ...

    def __mul__(self, times):
        result = self
        for i in range(times-1):
            result = Dice(self.__faces, result)
        return result

    def __rmul__(self, other):
        return self * other

    def __radd__(self, other):
        return self + other


def attr_base(num):
    return 2*Dice(num) + num


def contest(attribute, difficulty):
    roll = Dice(20).roll()
    return roll == 20 or (roll != 1 and roll + attribute - 10 > difficulty)


def test():
    bunch = 3 * Dice(6) + 2 * Dice(4) + 2
    print(bunch)
    print(bunch.range_string())
