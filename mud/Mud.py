from mud.world.characters import world
from mud.Commands import do_command
from mud.world.mechanics import percent_roll
import shlex


def messages(message_list):
    for m in message_list:
        print(m)


def events(the_protagonist):
    for c in the_protagonist.location().characters():
        if c != the_protagonist and c.is_alive():
            if percent_roll(c.aggressiveness()):
                c.set_hostile(True)
            if c.is_hostile():
                messages(c.attack(the_protagonist))


protagonist = world.spawn_player()
messages(protagonist.location().describe())
while protagonist.is_alive() and not protagonist.left_world():
    command = input("> ")
    messages(do_command(shlex.split(command), protagonist))
    events(protagonist)
if not protagonist.is_alive():
    print("You died.")
