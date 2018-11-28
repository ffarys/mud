from mud.world.characters import world
from mud.Commands import do_command
import shlex


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
