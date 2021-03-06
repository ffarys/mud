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


def contest(attribute, difficulty, dice=Dice(20)):
    min_roll, max_roll = dice.range()
    roll = dice.roll()
    return roll == max_roll or (roll != min_roll and roll + attribute - ((min_roll + max_roll) // 2) > difficulty)


def test():
    bunch = 3 * Dice(6) + 2 * Dice(4) + 2
    print(bunch)
    print(bunch.range_string())


def noun_with_article(word):
    result = str(word)
    if result[0] in ['a', 'e', 'i', 'o', 'u']:
        result = "an " + result
    else:
        result = "a " + result
    return result


ordinals = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eight", "ninth", "tenth", "eleventh",
            "twelfth", "thirteenth", "fourteenth", "fifteenth", "sixteenth", "seventeenth", "eighteenth"]


def pick(a_list, ordinal):
    if ordinal in ordinals:
        index = ordinals.index(ordinal)
        if index < len(a_list):
            return a_list[index]
        else:
            return None
    else:
        return None


def is_ordinal(ordinal):
    return ordinal in ordinals


def ordinal_and_name(words):
    if len(words) > 1 and is_ordinal(words[0]):
        ordinal = words[1]
        name = " ".join(words[1:])
    else:
        ordinal = "first"
        name = " ".join(words)
    return ordinal, name


def percent_roll(n):
    return n >= randint(1, 100)


class ActionResult:
    def __init__(self, sentences, time=1, error=False):
        self.__error = error
        # time elapsed doing the action
        self.__time = time
        if isinstance(sentences, str):
            self.__sentences = [sentences]
        else:
            self.__sentences = sentences

    def print_action(self, other_than_player=False):
        for s in self.__sentences:
            if self.__error:
                print("\033[91m"+s+"\033[0m")
            elif other_than_player:
                print("\033[93m" + s + "\033[0m")
            else:
                print(s)

    def time(self):
        return self.__time

    def append(self, sentence):
        self.__sentences.append(sentence)


class GameMechanicsError(Exception, ActionResult):
    def __init__(self, sentences):
        Exception.__init__(self, *sentences)
        ActionResult.__init__(self, sentences, time=0, error=True)
