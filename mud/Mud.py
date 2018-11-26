from mud.world.characters import world


def interpret(command, world, protagonist):
    result = True
    words = command.split()
    if len(words) == 0 or words == ["help"]:
        print("commands: quit, go {exit}, look")
    elif words == ["quit"]:
        result = False
    elif words[0] == "look" and len(words) < 3:
        if len(words) == 1 or words[1] == "around":
            print(protagonist.location().describe())
        else:
            if words[1] in protagonist.location().exits():
                print(protagonist.location().exit(words[1]).describe(inside=False))
            else:
                print("Not an exit:", words[1])
    elif words[0] == "go" and len(words) == 2:
        if words[1] in protagonist.location().exits():
            protagonist.move(protagonist.location().exit(words[1]))
            print(protagonist.location().describe())
        else:
            print("Not an exit:", words[1])
    else:
        print("Not a valid command:", command, " (but 'help' is!)")
    return result


protagonist = world.start()
print(protagonist.location().describe())
running = True
#loop
while protagonist.is_alive() and running:
    command = input("> ")
    running = interpret(command, world, protagonist)
if not protagonist.is_alive():
    print("You died.")
