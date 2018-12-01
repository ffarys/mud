from mud.world.characters import world, build_example_world
from mud.Commands import do_command
from mud.world.mechanics import percent_roll, ActionResult
import shlex


def events(the_protagonist, time):
    if time > 0:
        for c in the_protagonist.location().characters():
            if c != the_protagonist and c.is_alive():
                if percent_roll(c.aggressiveness()):
                    c.set_hostile(True)
                if c.is_hostile():
                    ActionResult(c.attack(the_protagonist)).print_action_by_other()


build_example_world()
protagonist = world.spawn_player()
ActionResult(protagonist.location().describe()).print_action_by_player()
while protagonist.is_alive() and not protagonist.left_world():
    command = input("> ")
    result = do_command(shlex.split(command), protagonist)
    result.print_action_by_player()
    events(protagonist, result.time())
if not protagonist.is_alive():
    print("You died.")
