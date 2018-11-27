from mud.world.characters import world
from mud.Commands import do_command
import shlex


def interpret(command, world, protagonist):
    words = shlex.split(command)
    if len(words) == 0:
        print("commands: quit, go, look, myself, call, equip")
        print("Type 'help' for more info")
    elif words == ["help"]:
        print("quit:         leaves the game")
        print("go {exit}     moves to another location")
        print("look          looks around")
        print("look {exit}   look toward a near location")
        print("myself        describes yourself, your attributes and your inventory")
        print("call {x} {y}  renames yourself or an item in your possession")
        print("equip {x}     equip an item in your possession")
        print("Note: include spaces in arguments using single or double quotes; e.g. call Protagonist 'Peter Parker'")
    elif words == ["quit"]:
        protagonist.leave()
    elif words == ["myself"]:
        print(protagonist.describe(everything=True))
    elif words[0] == "call" and len(words) == 3 and words[2] != '':
        if words[1] == protagonist.name():
            protagonist.rename(words[2])
            print("You are now called "+words[2])
        else:
            item = protagonist.item(words[1])
            if item is not None:
                item.rename(words[2])
                print("You renamed " + words[1] + " as " + words[2])
            else:
                print("Can't find", words[1])
    elif words[0] == "look" and len(words) < 3:
        if len(words) == 1 or words[1] == "around":
            print(protagonist.location().describe())
        else:
            if words[1] in protagonist.location().exits():
                print(protagonist.location().exit(words[1]).describe(inside=False))
            else:
                print("Not an exit:", words[1])
    elif words[0] == "equip" and len(words) == 2:
        item = protagonist.item(words[1])
        if protagonist.item(words[1]):
            protagonist.equip(item)
            print("You equipped " + words[1])
        else:
            print("Can't find", words[1])
    elif words[0] == "go" and len(words) == 2:
        if words[1] in protagonist.location().exits():
            protagonist.move(protagonist.location().exit(words[1]))
            print(protagonist.location().describe())
        else:
            print("Not an exit:", words[1])
    else:
        print("Not a valid command:", command, " (but 'help' is!)")


protagonist = world.spawn_player()
for s in protagonist.location().describe():
    print(s)
while protagonist.is_alive() and not protagonist.left_world():
    command = input("> ")
    messages = do_command(shlex.split(command), protagonist)
    for message in messages:
        print(message)
if not protagonist.is_alive():
    print("You died.")
