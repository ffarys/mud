import json
import random
from mud.world.mechanics import Dice, contest, attr_base, noun_with_article


attributes = ["max_health",    # max amount to take damage
              "stamina",       # resist exhaustion, disease
              "magic",         # power of spells
              "strength",      # damage done and soaked, carrying maximum
              "agility",       # land and evade attacks, avoid traps, grace of movement
              "dexterity",     # ability to do precise tasks (untie knot, open lock, sew, ...)
              "intelligence",  # solving capacity
              "perception",    # see, hear, smell things
              "wounds",        # damage taken
              "armor",         # soaks damage (Dice)
              "damage"]        # natural weapon's damage


class World:
    def __init__(self):
        self.__enchantments = dict()
        self.__races = dict()
        self.__weapon_types = dict()
        self.__locations = list()

    def new_race(self, name, max_health, stamina, magic, strength, agility, dexterity, intelligence, perception,
                 armor, damage):
        r = Race(name, max_health, stamina, magic, strength, agility, dexterity, intelligence, perception,
                 armor, damage)
        self.__races.update({name: r})
        return r

    def races(self):
        return self.__races

    def race(self, name):
        return self.__races[name]

    def new_enchantment(self, name, effects):
        e = Enchantment(name, effects)
        self.__enchantments.update({name: e})
        return e

    def enchantments(self):
        return self.__enchantments

    def enchantment(self, name):
        if name != '?':
            result = self.__enchantments[name]
            if result is None:
                raise ValueError("unknown enchantement name: " + str(result))
        else:
            result = random.choice(list(self.__enchantments.values()))
        return result

    def new_weapon_type(self, name, weight, damage_dice, offence, hands):
        wt = WeaponType(name, weight, damage_dice, offence, hands)
        self.__weapon_types.update({name: wt})
        return wt

    def weapon_types(self):
        return self.__weapon_types

    def weapon_type(self, name):
        return self.__weapon_types[name]

    def new_location(self, name, description, obscured=False):
        l = Location(name, description, obscured)
        self.__locations.append(l)
        return l

    def location(self, num):
        return self.__locations[num]

    def spawn_player(self):
        result = Character(race="human", name="Protagonist", hero=True)
        result.acquire(Weapon("club"))
        result.acquire(Weapon("dagger"))
        result.move(self.location(0))
        return result


world = World()


class Container:
    def __init__(self):
        self.__items = list()  # we want to retain order

    def add_item(self, item):
        if item not in self.__items:
            self.__items.append(item)

    def remove_item(self, item):
        self.__items.remove(item)

    def items(self):
        return self.__items

    def contains_item(self, item):
        return item in self.__items

    def items_named(self, name):
        return [c for c in self.__items if c.name() == name]


class Location(Container):
    def __init__(self, name, description, obscured):
        Container.__init__(self)
        self.__name = name
        self.__description = description
        self.__characters = list()  # we want to retain order
        self.__exits = dict()
        self.__obscured = obscured

    def name(self):
        return self.__name

    def description(self):
        return self.__description

    def characters(self):
        return self.__characters

    def add_character(self, c):
        if c not in self.__characters:
            self.__characters.append(c)

    def remove_character(self, c):
        self.__characters.remove(c)

    def characters_named(self, name):
        return [c for c in self.__characters if c.name() == name or c.race().name() == name]

    def exits(self):
        return self.__exits

    def add_exit(self, direction, exit_loc, back_direction=None):
        self.__exits.update({direction: exit_loc})
        if back_direction is not None:
            exit_loc.add_exit(back_direction, self)

    def exit(self, exit_name):
        return self.__exits[exit_name]

    def describe(self, inside=True):
        if not inside and self.__obscured:
            result = ["Your can't see anything!"]
        else:
            if inside:
                result = ["You are in the "+self.__name]
            else:
                result = ["You see the "+self.__name]
            result.append(self.__description)
            if inside:
                if self.items():  # not empty
                    result.append("Items: " + (", ".join([i.name() for i in self.items()])))
            if self.characters():  # not empty
                result.append("Characters: " + (", ".join([c.name() for c in self.characters()])))
            if inside:
                result.append("Exits: " + (", ".join(self.exits().keys())))
        return result


# Alle objecten op de wereld
class WorldObject:
    def __init__(self, name):
        self.__name = name

    def name(self):
        return self.__name

    def rename(self, name):
        self.__name = name


class Character(WorldObject, Container):
    def __init__(self, race, name=None, max_health=None, stamina=None, magic=None, strength=None,
                 agility=None, dexterity=None, intelligence=None, perception=None, armor=None,
                 damage=None, wounds=0, hero=False):
        if type(race) is Race:
            self.__race = race
        else:
            self.__race = world.race(race)
        WorldObject.__init__(self, self.__race.default_name() if name is None else name)
        Container.__init__(self)
        self.__attributes = {"max_health":   self.__race.roll_max_health(hero) if max_health is None else max_health,
                             "stamina":      self.__race.roll_stamina(hero) if stamina is None else stamina,
                             "magic":        self.__race.roll_magic(hero) if magic is None else magic,
                             "wounds":       wounds,
                             "strength":     self.__race.roll_strength(hero) if strength is None else strength,
                             "agility":      self.__race.roll_agility(hero) if agility is None else agility,
                             "dexterity":    self.__race.roll_dexterity(hero) if dexterity is None else dexterity,
                             "intelligence": self.__race.roll_intelligence(hero) if intelligence is None else intelligence,
                             "perception":   self.__race.roll_perception(hero) if perception is None else perception,
                             "armor":        self.__race.armor() if armor is None else armor,
                             "damage":       self.__race.damage() if damage is None else damage}
        self.__effects = list()
        self.__hero = hero
        self.__location = None
        self.__left_world = False

    def __str__(self):
        result = self.name() + " (" + self.__race.name()
        for a in attributes:
            result += ", "+a+": "+str(self.attribute(a))
        return result + ")"

    def attribute(self, attr, bonus=None):
        value = self.__attributes[attr]
        for effect in self.__effects:
            value = effect.apply_attribute(attr, value)
            if bonus is not None:
                value = effect.apply_attribute(bonus, value)
        # geen attribuut kan ooit onder 0
        if type(value) is int and value < 0:
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

    def agility(self):
        return self.attribute("agility")

    def perception(self):
        return self.attribute("perception")

    def damage(self):
        return self.attribute("damage")

    def offence(self):
        return self.attribute("agility", bonus="offence")

    def defence(self):
        return self.attribute("agility", bonus="defence")

    def strength(self):
        return self.attribute("strength")

    def armor(self):
        return self.attribute("armor")

    def race(self):
        return self.__race

    def add_effect(self, effect):
        if effect.permanent():
            for attr in attributes:
                value = effect.apply_attribute(attr, self.__attributes[attr])
                if type(value) is int and value < 0:
                    value = 0
                self.__attributes[attr] = value
        else:
            if effect is not None:
                self.__effects.append(effect)

    def remove_effect(self, effect):
        if effect is not None:
            self.__effects.remove(effect)

    def as_dict(self):
        result = {}
        result.update(self.__attributes)
        result.update({"effects": [e.as_dict() for e in self.__effects]})
        return result

    def acquire(self, item):
        self.add_item(item)

    def drop(self, item):
        if item in self.items():
            if item.is_equipped():
                self.unequip(item)
            self.remove_item(item)

    def consume(self, item):
        if item in self.items():
            if item.consumable():
                self.drop(item)
                for e in item.effects():
                    self.add_effect(e)

    def equip(self, item):
        if item in self.items():
            if item.equippable():
                item.set_equipped(True)
                for e in item.effects():
                    self.add_effect(e)

    def unequip(self, item):
        if item in self.items():
            if item.is_equipped():
                item.set_equipped(False)
                for e in item.effects():
                    self.remove_effect(e)

    def equipped_weapon(self):
        result = None
        for i in self.items():
            if type(i) is Weapon and i.is_equipped():
                result = i
        return result

    def describe(self, everything=False):
        heading = "You see "+noun_with_article(self.__race.name())+" named '"+self.name()+"'"
        w = self.equipped_weapon()
        if w is not None:
            heading += " armed with " + noun_with_article(w.weapon_type())
        result = [heading]
        if everything:
            result.append("; ".join([a + " " + str(self.attribute(a)) for a in attributes]))
            if self.items():
                result.append("Inventory: "+(", ".join([i.name() for i in self.items()])))
        return result

    def attack(self, other):
        if contest(self.offence(), other.defence()):
            damage_done = self.damage().roll() + self.strength() // 2 - other.armor().roll()
            if damage_done > 0:
                print(self.name(), "attacks", other.name(), "and hits, damage:", damage_done)
                other.add_effect(damage_effect(damage_done))
            else:
                print(self.name(), "attacks", other.name(), "and hits, but fails to do damage")
        else:
            print(self.name(), "attacks", other.name(), "but misses")

    def move(self, location):
        if self.__location is not None:
            self.__location.remove_character(self)
        location.add_character(self)
        self.__location = location

    def location(self):
        return self.__location

    def is_alive(self):
        return self.health() - self.wounds() > 0

    def leave(self):
        self.__left_world = True

    def left_world(self):
        return self.__left_world


class Race:
    def __init__(self, name, max_health, stamina, magic, strength, agility, dexterity, intelligence, perception,
                 armor, damage):
        self.__name = name
        self.__max_health = max_health
        self.__stamina = stamina
        self.__perception = perception
        self.__intelligence = intelligence
        self.__agility = agility
        self.__dexterity = dexterity
        self.__strength = strength
        self.__magic = magic
        self.__armor = armor
        self.__damage = damage

    def name(self):
        return self.__name

    def roll_max_health(self, heroic=False):
        return self.__max_health.roll_best_of(2 if heroic else 1)

    def roll_stamina(self, heroic=False):
        return self.__stamina.roll_best_of(2 if heroic else 1)

    def roll_magic(self, heroic=False):
        return self.__magic.roll_best_of(2 if heroic else 1)

    def roll_strength(self, heroic=False):
        return self.__strength.roll_best_of(2 if heroic else 1)

    def roll_agility(self, heroic=False):
        return self.__agility.roll_best_of(2 if heroic else 1)

    def roll_dexterity(self, heroic=False):
        return self.__dexterity.roll_best_of(2 if heroic else 1)

    def roll_intelligence(self, heroic=False):
        return self.__intelligence.roll_best_of(2 if heroic else 1)

    def roll_perception(self, heroic=False):
        return self.__perception.roll_best_of(2 if heroic else 1)

    def armor(self):
        return self.__armor

    def damage(self):
        return self.__damage

    def default_name(self):
        return noun_with_article(self.name())


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
    def __init__(self, name, weight, equippable=False, consumable=False, effects=None, enchantments=None):
        super().__init__(name)
        self.__equippable = equippable
        self.__consumable = consumable
        self.__weight = weight
        self.__effects = [] if effects is None else effects
        self.__equipped = False
        self.__enchanted = False
        if enchantments is not None:
            for e in enchantments:
                self.enchant(e)

    def __str__(self):
        return self.name()

    def effects(self):
        return self.__effects

    def consumable(self):
        return self.__consumable

    def equippable(self):
        return self.__equippable

    def is_equipped(self):
        return self.__equipped

    def is_enchanted(self):
        return self.__enchanted

    def set_equipped(self, true_or_false):
        self.__equipped = true_or_false

    def enchant(self, enchantment="?"):
        if self.__equipped:
            raise ValueError("Equipped items can not be enchanted.")
        if type(enchantment) != Enchantment:
            enchantment = world.enchantment(enchantment)
        self.__effects = self.__effects + enchantment.effects()
        self.rename(enchantment.name() % self.name())
        self.__enchanted = True
        return self

    def describe(self, fully=True):
        result = ["You see '" + self.__name + "'"]
        if self.is_equipped():
            result.append("It is equipped")
        if fully:
            if self.__enchanted:
                result.append("It is enchanted")
        return result


class WeaponType:
    def __init__(self, name, weight, damage_dice, offence, hands):
        self.__name = name
        self.__weight = weight
        self.__damage_dice = damage_dice
        self.__offence = offence
        self.__hands = hands

    def stats(self):
        return self.__weight, self.__damage_dice, self.__offence, self.__hands


class Ring(Item):
    def __init__(self, enchantments=None):
        super().__init__("ring", 0, equippable=True, enchantments=enchantments)
        if enchantments is not None:
            for e in enchantments:
                self.enchant(e)


class Weapon(Item):
    def __init__(self, weapon_type, name=None, weight=None, damage_dice=None, offence=None, hands=None,
                 enchantments=None):
        self.__weapon_type = weapon_type
        if weight is None or damage_dice is None or offence is None or hands is None:
            wt = world.weapon_type(weapon_type)
            weight, damage_dice, offence, hands = wt.stats()
            name = weapon_type
        effects = [ReplaceAttributeEffect("damage", damage_dice)]
        if offence > 0:
            effects.append(ModifyAttributeEffect("offence", offence))
        super().__init__(name, weight, equippable=True, effects=effects, enchantments=enchantments)
        self.__hands = hands
        self.__weapon_type = weapon_type
        self.__offence = offence
        self.__damage_dice = damage_dice

    def weapon_type(self):
        return self.__weapon_type

    def describe(self, fully=True):
        if self.name() == self.__weapon_type:
            result = ["You see " + noun_with_article(self.name())]
        else:
            result = ["You see '"+self.name()+"', which is a "+noun_with_article(self.__weapon_type)]
        if self.is_equipped():
            result.append("It is equipped")
        if fully:
            result.append(("It is one handed" if self.__hands == 1 else "It is two handed")
                          + "; base offence bonus: "+str(self.__offence)
                          + "; base damage: "+self.__damage_dice.range_string())
            if self.is_enchanted():
                result.append("It is enchanted")
        return result


class Effect:
    def __init__(self, permanent=False):
        self.__permanent = permanent

    def apply_attribute(self, attribute, value):
        return value

    def as_dict(self):
        pass

    def permanent(self):
        return self.__permanent


class Enchantment:
    def __init__(self, name, effects):
        self.__name = name
        self.__effects = effects

    def name(self):
        return self.__name

    def effects(self):
        return self.__effects


def effect_from_dict(effect_dict):
    type = effect_dict["type"]
    effect_dict.pop("type")  # pop removes and returns last object from the list
    if type == "ModifyAttributeEffect":
        return ModifyAttributeEffect(effect_dict["attribute"], effect_dict["modifier"])
    else:
        raise ValueError("Type unknown: "+type)


class ModifyAttributeEffect(Effect):
    def __init__(self, attribute, modifier, permanent=False):
        super().__init__(permanent)
        self.__attribute = attribute
        self.__modifier = modifier

    def apply_attribute(self, attribute, value):
        if attribute == self.__attribute:
            value = value + self.__modifier
        return value

    def as_dict(self):
        return {"type": "ModifyAttributeEffect",
                "attribute": self.__attribute,
                "modifier": self.__modifier}


class ReplaceAttributeEffect(Effect):
    def __init__(self, attribute, modifier):
        super().__init__(False)
        self.__attribute = attribute
        self.__modifier = modifier

    def apply_attribute(self, attribute, value):
        if attribute == self.__attribute:
            value = self.__modifier
        return value

    def as_dict(self):
        return {"type": "ReplaceAttributeEffect",
                "attribute": self.__attribute,
                "modifier": self.__modifier}


def damage_effect(number):
    return ModifyAttributeEffect("wounds", number, permanent=True)


def healing_effect(number):
    return ModifyAttributeEffect("wounds", -number, permanent=True)


world.new_weapon_type("arming sword", 10, 2*Dice(10), 6, 1)
world.new_weapon_type("scimitar", 10, 3*Dice(6)+1, 5, 1)
world.new_weapon_type("long sword", 20, 2*Dice(12), 6, 2)
world.new_weapon_type("short sword", 5, 2*Dice(8), 4, 1)
world.new_weapon_type("dagger", 2, 2*Dice(6), 2, 1)
world.new_weapon_type("spear", 15, Dice(20), 8, 2)
world.new_weapon_type("war hammer", 20, 4*Dice(6), 0, 1)
world.new_weapon_type("great hammer", 45, 4*Dice(8), 2, 2)
world.new_weapon_type("war axe", 20, 3*Dice(6)+2, 2, 1)
world.new_weapon_type("great axe", 40, 3*Dice(8)+2, 2, 2)
world.new_weapon_type("halberd", 50, 2*Dice(12), 10, 2)
world.new_weapon_type("club", 15, 3*Dice(4)+2, 0, 1)

world.new_enchantment("eagle %s", [ModifyAttributeEffect("perception", 10)])
world.new_enchantment("wise %s", [ModifyAttributeEffect("intelligence", 10)])
world.new_enchantment("conduit %s", [ModifyAttributeEffect("magic", 5)])
world.new_enchantment("elven %s", [ModifyAttributeEffect("magic", 10)])
world.new_enchantment("defender %s", [ModifyAttributeEffect("defence", 5)])
world.new_enchantment("aggressive %s", [ModifyAttributeEffect("offence", 5)])
world.new_enchantment("cat %s", [ModifyAttributeEffect("agility", 5)])
world.new_enchantment("crafting %s", [ModifyAttributeEffect("dexterity", 10)])
world.new_enchantment("bull %s", [ModifyAttributeEffect("max health", 50)])
world.new_enchantment("orc %s", [ModifyAttributeEffect("strength", 10)])
world.new_enchantment("ogre %s", [ModifyAttributeEffect("strength", 20)])
world.new_enchantment("shielding %s", [ModifyAttributeEffect("shielding", Dice(6))])
world.new_enchantment("warrior %s", [ModifyAttributeEffect("defence", 5), ModifyAttributeEffect("offence", 5)])
world.new_enchantment("berserk %s", [ModifyAttributeEffect("defence", -5), ModifyAttributeEffect("offence", 10)])

world.new_race("human", max_health=5*Dice(8)+40, stamina=5*Dice(10)+50, magic=attr_base(4),
               strength=attr_base(6), agility=attr_base(6), dexterity=attr_base(10), intelligence=attr_base(10),
               perception=attr_base(6), armor=Dice(2), damage=Dice(4))
world.new_race("muskrat", max_health=5*Dice(4)+10, stamina=5*Dice(8)+40, magic=attr_base(1),
               strength=attr_base(2), agility=attr_base(6), dexterity=attr_base(2), intelligence=attr_base(2),
               perception=attr_base(8), armor=Dice(2), damage=2*Dice(4))
world.new_race("goblin", max_health=5*Dice(6)+30, stamina=5*Dice(10)+40, magic=attr_base(4),
               strength=attr_base(4), agility=attr_base(7), dexterity=attr_base(10), intelligence=attr_base(8),
               perception=attr_base(6), armor=Dice(6), damage=2*Dice(4))
world.new_race("bear", max_health=5*Dice(12)+60, stamina=5*Dice(8)+40, magic=Dice(2),
               strength=attr_base(12), agility=attr_base(8), dexterity=attr_base(2), intelligence=attr_base(4),
               perception=attr_base(6), armor=Dice(6)+3, damage=2*Dice(10))

start = world.new_location("inn's saloon", "The main room of the adventurer's inn: the saloon.")
main_street = world.new_location("iain street", "The downtown main street is a busy place.")
kitchen = world.new_location("inn's kitchen", "The inn's kitchen is a mess.")
alley = world.new_location("brown alley", "The alley is filthy.")
cellar = world.new_location("inn's cellar", "The cellar is a good training ground for beginning adventurers.",
                            obscured=True)
cellar.add_character(Character("muskrat"))
cellar.add_item(Weapon("short sword"))
sleeping_room = world.new_location("sleeping room", "The innkeeper is your friend, you can sleep here for free.")
start.add_exit("outside", main_street, "inn")
start.add_exit("kitchen", kitchen, "saloon")
start.add_exit("up", sleeping_room, "down")
kitchen.add_exit("outside", alley, "inn")
kitchen.add_exit("down", cellar, "up")


def test():
    fred = Character(race="human", name="Fred", hero=True)
    print(fred)

    bear1 = Character(race="bear")
    print(bear1)

    g = Character(race="goblin")
    print(g)

    print(fred.name(), "has max_health: ", fred.max_health(), "and wounds:", fred.wounds(), "health is ", fred.health())

    i = Item("Max health potion", 1, consumable=True, effects=[ModifyAttributeEffect("max_health", +50)])
    fred.acquire(i)
    fred.consume(i)
    print(fred.name(), "has max_health: ", fred.max_health(), "and wounds:", fred.wounds(), "health is ", fred.health())

    fred.add_effect(damage_effect(25))
    print(fred.name(), "has max_health: ", fred.max_health(), "and wounds:", fred.wounds(), "health is ", fred.health())

    i2 = Item("Healing potion", 1, consumable=True, effects=[healing_effect(50)])
    fred.acquire(i2)
    fred.consume(i2)
    print(fred.name(), "has max_health: ", fred.max_health(), "and wounds:", fred.wounds(), "health is ", fred.health())

    print(fred.name(), "has magic: ", fred.magic())
    fred.add_effect(ModifyAttributeEffect("magic", -10))
    print(fred.name(), "has magic: ", fred.magic())

    magic_sword = Weapon("arming sword").enchant()
    magic_ring = Ring().enchant()
    print("Fred found", noun_with_article(magic_sword), "and", noun_with_article(magic_ring))
    fred.acquire(magic_sword)
    fred.equip(magic_sword)
    fred.acquire(magic_ring)
    fred.equip(magic_ring)
    print(fred)

    fred.attack(bear1)
    bear1.attack(fred)
    fred.attack(bear1)
    bear1.attack(fred)
    fred.attack(bear1)
    bear1.attack(fred)

    # str = json.JSONEncoder().encode(c.as_dict())
    # copy_c = character_from_dict(json.JSONDecoder().decode(str))
    # print(copy_c.max_health())
    # print(copy_c.name())
