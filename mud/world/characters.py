import json


attributes = {"max_health", "stamina", "magic", "wounds"}


# Alle objecten op de wereld
class WorldObject:
    def __init__(self, name):
        self.__name = name

    def name(self):
        return self.__name


class Character(WorldObject):
    def __init__(self, name, max_health, stamina, magic):
        super().__init__(name)
        self.__attributes = {"max_health": max_health, "stamina": stamina, "magic": magic, "wounds": 0}
        self.__effects = set()
        self.__items = set()

    def attribute(self, attr):
        value = self.__attributes[attr]
        for effect in self.__effects:
            value = effect.apply(attr, value)
        # geen attribuut kan ooit onder 0
        if value < 0:
            value = 0
        return value

    def max_health(self):
        return self.attribute("max_health")

    def wounds(self):
        return self.attribute("wounds")

    def magic(self):
        return self.attribute("magic")

    def health(self):
        return self.max_health() - self.wounds()

    def add_effect(self, effect):
        if effect.permanent():
            for attr in attributes:
                value = effect.apply(attr, self.__attributes[attr])
                if value < 0:
                    value = 0
                self.__attributes[attr] = value
        else:
            if effect is not None:
                self.__effects.add(effect)

    def as_dict(self):
        result = {}
        result.update(self.__attributes)
        result.update({"effects": [e.as_dict() for e in self.__effects]})
        return result

    def acquire(self, item):
        self.__items.add(item)

    def lose(self, item):
        self.__items.remove(item)

    def consume(self, item):
        self.lose(item)
        self.add_effect(item.effect())

def character_from_dict(character_dict):
    # attributen eruit halen
    attr = {k: character_dict[k] for k in attributes}
    result = Character(**attr)
    # effecten weer toewijzen
    effect_dicts = character_dict["effects"]
    for e in effect_dicts:
        effect = effect_from_dict(e)
        result.add_effect(effect)
    return result


class Item(WorldObject):
    def __init__(self, name, weight, equippable=False, consumable=False, effect=None):
        super().__init__(name)
        self.__equippable = equippable
        self.__consumable = consumable
        self.__weight = weight
        self.__effect = effect

    def effect(self):
        return self.__effect


class Effect:
    def __init__(self, permanent):
        self.__permanent = permanent

    def apply(self, attribute, value):
        pass

    def as_dict(self):
        pass

    def permanent(self):
        return self.__permanent


def effect_from_dict(effect_dict):
    type = effect_dict["type"]
    effect_dict.pop("type") # pop removes and returns last object from the list
    if type == "ModifyAttributeEffect":
        return ModifyAttributeEffect(effect_dict["attribute"], effect_dict["modifier"])
    else:
        raise ValueError("Type unknown: "+type)


class ModifyAttributeEffect(Effect):
    def __init__(self, attribute, modifier, permanent=False):
        super().__init__(permanent)
        self.__attribute = attribute
        self.__modifier = modifier

    def apply(self, attribute, value):
        if attribute == self.__attribute:
            value = value + self.__modifier
        return value

    def as_dict(self):
        return {"type": "ModifyAttributeEffect",
                "attribute": self.__attribute,
                "modifier": self.__modifier}


def damage(number):
    return ModifyAttributeEffect("wounds", number, permanent=True)


def healing(number):
    return ModifyAttributeEffect("wounds", -number, permanent=True)


c = Character("Fred", 200, 10, 5)
print(c.name(), "has max_health: ", c.max_health(), "and wounds:", c.wounds(),"health is ", c.health())

i = Item("Max health potion", 1, consumable=True, effect=ModifyAttributeEffect("max_health", +50))
c.acquire(i)
c.consume(i)
print(c.name(), "has max_health: ", c.max_health(), "and wounds:", c.wounds(),"health is ", c.health())

c.add_effect(damage(25))
print(c.name(), "has max_health: ", c.max_health(), "and wounds:", c.wounds(),"health is ", c.health())

i2 = Item("Healing potion", 1, consumable=True, effect=healing(50))
c.acquire(i2)
c.consume(i2)
print(c.name(), "has max_health: ", c.max_health(), "and wounds:", c.wounds(),"health is ", c.health())


print(c.name(), "has magic: ", c.magic())
c.add_effect(ModifyAttributeEffect("magic", -10))
print(c.name(), "has magic: ", c.magic())



# str = json.JSONEncoder().encode(c.as_dict())
# copy_c = character_from_dict(json.JSONDecoder().decode(str))
# print(copy_c.max_health())
# print(copy_c.name())
