from mud.world.characters import Box
from mud.world.mechanics import ordinal_and_name, pick, ActionResult, Error


class Command:
    def __init__(self, keyword, min_args, max_args, description, fn):
        self.__keyword = keyword
        self.__description = description
        self.__fn = fn
        self.__min_args = min_args
        self.__max_args = max_args

    def execute(self, words, protagonist):
        return self.__fn(words, protagonist)

    def keyword(self):
        return self.__keyword

    def description(self):
        return self.__description

    def may_execute(self, words):
        return self.__min_args <= len(words)-1 <= self.__max_args


def help_me(words, protagonist):
    if len(words) > 0:
        for w in words:
            cmd = find_command(w)
            if cmd is None:
                result = Error(w+" is an unknown command")
            else:
                result = ActionResult(cmd.description(), time=0)
    else:
        result = ActionResult(["Hi "+protagonist.name(),
                               "Your commands are: " + ", ".join([c.keyword() for c in commands]),
                               "Type 'help {command}' for more info"], time=0)
    return result


def leave(words, protagonist):
    protagonist.leave()
    return words


def myself(words, protagonist):
    return ActionResult(protagonist.describe(everything=True), time=0)


def _item_in_location(words, protagonist):
    ordinal, name = ordinal_and_name(words)
    items = protagonist.location().items_named(name)
    if len(items) > 0:
        item = pick(items, ordinal)
        if item is None:
            return Error("Can't find " + ordinal + " " + name)
        else:
            return item
    else:
        return Error("Can't find " + name)


def _find_something(words, collection, extra="."):
    ordinal, name = ordinal_and_name(words)
    items = [i for i in collection if i.matches(name)]
    if len(items) > 0:
        item = pick(items, ordinal)
        if item is None:
            return Error("Can't find " + ordinal + " " + name + extra)
        else:
            return item
    else:
        return Error("Can't find " + " ".join(words))


def call(words, protagonist):
    item = protagonist.items_named(words[0])
    if len(item) > 0:
        item[0].rename(words[1])
        return ActionResult("You renamed " + words[0] + " as " + words[1], time=0)
    elif words[0] == 'myself' or words[0] == protagonist.name():
        protagonist.rename(words[1])
        return ActionResult("You are now called " + words[1], time=0)
    else:
        return Error("Can't find " + words[0])


def look(words, protagonist):
    if len(words) == 0 or words[0] == "around" or words[0] == "here":
        return ActionResult(protagonist.location().describe())
    else:
        direction = " ".join(words)
        if direction in protagonist.location().exits():
            return ActionResult(protagonist.location().exit(direction).describe(inside=False))
        else:
            return Error("Not an exit: " + direction)


def equip(words, protagonist):
    item = _find_something(words, protagonist.items(), " (must be in possession).")
    if isinstance(item, Error):
        return item
    else:
        if item.equippable():
            protagonist.equip(item)
            return ActionResult("You equipped the " + item.name())
        else:
            return Error("You cannot equip the " + item.name())


def _split_and_find_box(words, protagonist, delimiter):
    if delimiter in words:
        position = words.index(delimiter)
        box_part_words = words[position+1:]
        first_part_words = words[:position]
        box = _find_something(box_part_words, protagonist.items() + protagonist.location().items())
        if not isinstance(box, Box):
            box = Error("Must be a box: "+box_part_words)
        return first_part_words, box
    else:
        return words, None


def drop(words, protagonist):
    words, container = _split_and_find_box(words, protagonist, "in")
    if isinstance(container, Error):
        return container
    else:
        item = _find_something(words, protagonist.items(), " (must be in possession).")
        if isinstance(item, Error):
            return item
        else:
            protagonist.drop(item, container)
            return ActionResult("You dropped the " + item.name())


def use(words, protagonist):
    item = _find_something(words, protagonist.items(), " (must be in possession).")
    if isinstance(item, Error):
        return item
    else:
        if item.consumable():
            protagonist.consume(item)
            return ActionResult("You drank the " + item.name())
        else:
            return Error("You cannot drink the " + item.name())


def go(words, protagonist):
    direction = " ".join(words)
    if direction in protagonist.location().exits():
        protagonist.move(protagonist.location().exit(direction))
        return ActionResult(protagonist.location().describe())
    else:
        return Error("Not an exit: " + direction)


def inspect(words, protagonist):
    item = _find_something(words, protagonist.location().characters() + \
                                  protagonist.location().items() + \
                                  protagonist.items())
    if isinstance(item, Error):
        return item
    else:
        return ActionResult(item.describe())


def take(words, protagonist):
    words, box = _split_and_find_box(words, protagonist, "from")
    if isinstance(box, Error):
        return Error
    else:
        item = _find_something(words, protagonist.location().items() if box is None else box.items())
        if isinstance(item, Error):
            return item
        else:
            if box is None:
                protagonist.location().remove_item(item)
            else:
                box.remove_item(item)
            protagonist.acquire(item)
            return ActionResult("You took " + item.name())


def attack(words, protagonist):
    if len(words) < 1:
        creatures = protagonist.location().characters()
        hostile = None
        for c in creatures:
            if c.is_hostile():
                hostile = c
                break
        if hostile is None:
            return Error("No hostiles here.")
        else:
            return ActionResult(protagonist.attack(hostile))
    else:
        creature = _find_something(words, protagonist.location().characters())
        if isinstance(creature, Error):
            return creature
        else:
            return ActionResult(protagonist.attack(creature))


may_use_ordinals = "\n                    If there are many, you can use ordinals: fist, second, ..."


# all commands
max_words = 100
commands = [
    Command("help", 0, max_words,
            "help [{command}]    offers more help about a command", help_me),
    Command("quit", 0, 0,
            "quit                lets you quit the game", leave),
    Command("myself", 0, 0,
            "myself              describes yourself, your attributes, and your inventory", myself),
    Command("call", 2, 2,
            "call {x} {y}        renames 'myself' or first item 'x' in belongings (use quotes to make 2 words)", call),
    Command("look", 0, 1,
            "look [{somewhere}]  looks at current room or in a given direction", look),
    Command("equip", 1, max_words,
            "equip {something}   equips an item in your possession"+may_use_ordinals, equip),
    Command("go", 1, 1,
            "go {somewhere}      goes in given direction (on of the exits)", go),
    Command("inspect", 1, max_words,
            "inspect {something} inspects item or character named 'something'"+may_use_ordinals, inspect),
    Command("take", 1, max_words,
            "take {something}    takes something in the room or [from] a box"+may_use_ordinals, take),
    Command("attack", 0, max_words,
            "attack {something}  attacks a character in the room with your equipped weapon"+may_use_ordinals +
            "                    you may also type 'attack' to attack the first hostile enemy", attack),
    Command("drop", 1, max_words,
            "drop {something}    drops an item in your possession on the floor or [in] a box"+may_use_ordinals, drop),
    Command("put", 1, max_words,
            "put {something}     puts an item in your possession on the floor or [in] a box"+may_use_ordinals, drop),
    Command("use", 1, max_words,
            "use {something}     use something (potion, scroll) in your possession" +
            may_use_ordinals, use)
]


def find_command(w):
    result = None
    for c in commands:
        if c.keyword() == w:
            result = c
            break
    return result


def do_command(words, protagonist):
    if len(words) == 0:
        help(words, protagonist)
    else:
        command = find_command(words[0])
        if command is None:
            return Error(["Unknown command: "+words[0], "If unsure, try to type 'help'"])
        elif not command.may_execute(words):
            return Error(["Wrong number of arguments for " + words[0], command.description()])
        else:
            return command.execute(words[1:], protagonist)

