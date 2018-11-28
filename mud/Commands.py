from mud.world.characters import world
from mud.world.mechanics import ordinal_and_name, pick, is_ordinal


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
    if len(words) > 1:
        result = []
        for w in words:
            cmd = find_command(w)
            if cmd is None:
                result.append(w+" is an unknown command")
            else:
                result.append(cmd.description())
    else:
        result = ["Hi "+protagonist.name(),
                  "Your commands are: " + ", ".join([c.keyword() for c in commands]),
                  "Type 'help {command}' for more info"]
    return result


def leave(words, protagonist):
    protagonist.leave()
    return words


def myself(words, protagonist):
    return protagonist.describe(everything=True)


def call(words, protagonist):
    item = protagonist.items_named(words[1])
    if len(item) > 0:
        item[0].rename(words[2])
        return ["You renamed " + words[1] + " as " + words[2]]
    elif words[1] == 'myself' or words[1] == protagonist.name():
        protagonist.rename(words[2])
        return ["You are now called " + words[2]]
    else:
        return ["Can't find " + words[1]]


def look(words, protagonist):
    if len(words) == 1 or words[1] == "around" or words[1] == "here":
        return protagonist.location().describe()
    else:
        if words[1] in protagonist.location().exits():
            return protagonist.location().exit(words[1]).describe(inside=False)
        else:
            return ["Not an exit: " + words[1]]


def equip(words, protagonist):
    ordinal, name = ordinal_and_name(words)
    items = protagonist.location().items_named(name)
    if len(items) > 0:
        item = pick(items, ordinal)
        if item is None:
            return ["Can't find " + ordinal + " " + name]
        else:
            protagonist.equip(item)
            return ["You equipped " + name]
    else:
        return ["Can't find " + words[1]]


def go(words, protagonist):
    if words[1] in protagonist.location().exits():
        protagonist.move(protagonist.location().exit(words[1]))
        return protagonist.location().describe()
    else:
        return ["Not an exit:" + words[1]]


def inspect(words, protagonist):
    ordinal, name = ordinal_and_name(words)
    things = protagonist.location().characters_named(name) + \
             protagonist.location().items_named(name) + \
             protagonist.items_named(name)
    if things:
        thing = pick(things, ordinal)
        if thing is None:
            result = ["Can't find " + ordinal + " " + name]
        else:
            result = thing.describe()
        if len(things) > 1:
            result.append("Note that there are "+str(len(things))+" things called '"+name+"' here.")
        return result
    else:
        return ["Can't find " + words[1]+", or not specific enough"]


def take(words, protagonist):
    ordinal, name = ordinal_and_name(words)
    items = protagonist.location().items_named(name)
    if len(items) > 0:
        item = pick(items, ordinal)
        if item is None:
            return ["Can't find " + ordinal + " " + name]
        else:
            protagonist.location().remove_item(item)
            protagonist.acquire(item)
            return ["You took " + item.name()]
    else:
        return ["Can't find " + name]


# all commands
commands = [
    Command("help", 0, 1,
            "help [{command}]    offers more help about a command", help_me),
    Command("quit", 0, 0,
            "quit                lets you quit the game", leave),
    Command("myself", 0, 0,
            "myself              describes yourself, your attributes, and your inventory", myself),
    Command("call", 2, 2,
            "call {x} {y}        renames 'myself' or first item 'x' in belongings (use quotes to make 2 words)", call),
    Command("look", 0, 1,
            "look [{somewhere}]  looks at current room or in a given direction", look),
    Command("equip", 1, 100,
            "equip {something}   equips an item in your possession (you may use ordinals: first, second, ...)", equip),
    Command("go", 1, 1,
            "go {somewhere}      goes in given direction", go),
    Command("inspect", 1, 100,
            "inspect {something} inspects item or character named 'something'" 
            "(you may use ordinals: first, second, ...)", inspect),
    Command("take", 1, 100,
            "take {something}    takes something in the room (you may use ordinals: first, second, ...)", take)
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
            return["Unknown command: "+words[0], "If unsure, try to type 'help'"]
        elif not command.may_execute(words):
            return ["Wrong number of arguments for " + words[0], command.description()]
        else:
            return command.execute(words, protagonist)
