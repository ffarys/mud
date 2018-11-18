import json, os, pathlib

# directory of all save.json files
savedir = "saves"


def save_name(savenum):  # build complete directory for the save
    return savedir + "/save" + str(savenum) + ".json"


def save(savenum, data):  # save the data in save#.json
    # variables
    savename = save_name(savenum)
    savelocation = savename
    # variables
    with open(savelocation, "w") as outfile:
        json.dump(data, outfile, indent=3)


def user_open_choice(q):  # asks user to give own input
    print(q)  # q as the question
    var = input()
    while var == "": # checks if input is not empty
        print("You cant enter an empty field!")
        print(q)
        var = input()
    return var


def user_choice(q,*option):  # multiple choice question

    print(q)

    for i in range(len(option)):  # prints all given arguments
        print(i+1, ": ", option[i])
    choice = int(input())

    while choice < 1 or choice > len(option ):  # checks for valid input
        print("Invalid input!, please choose a number between 1 and ", len(option))
        print(q)
        choice = int(input())
    choice -= 1
    return option[choice]


def assign_attributes(data,hp,sp,mp,str,defe,dex,wis,cha):  # assign given value to all atributes
    data["character"][0]["attributes"][0]["healthp"] = hp
    data["character"][0]["attributes"][0]["staminap"] = sp
    data["character"][0]["attributes"][0]["magicp"] = mp
    data["character"][0]["attributes"][0]["strength"] = str
    data["character"][0]["attributes"][0]["defence"] = defe
    data["character"][0]["attributes"][0]["dexterity"] = dex
    data["character"][0]["attributes"][0]["wisdom"] = wis
    data["character"][0]["attributes"][0]["charisma"] = cha

    return data

def assign_ability(data,type,abilityname,attribute):
    new = [{abilityname: attribute }]
    data["character"][0]["abilities"][0][abilityname][0][attribute]


def new_game():  # starts new game by making a new save file and procedure of making a character

    pathlib.Path(savedir).mkdir(parents=True, exist_ok=True)  # create directory if it not exists

    savenum = 1
    while os.path.isfile(save_name(savenum)):  # check if save file already exitst
        savenum += 1

    data = {
        "savenumber": savenum,
        "character": [{
            "gender": "male",
            "name": "0",
            "class": "0",
            "level": "1",
            "attributes": [{
                "healthp": "0",
                "staminap": "0",
                "magicp": "0",
                "strength": "0",
                "defence": "0",
                "dexterity": "0",
                "wisdom": "0",
                "charisma": "0",
                }],
            "abilities":[{


            }],
            "status_effects": [{

                }]
        }],
        "items": [{
            "key_items": [{

            }],
            "consumables": [{

            }],
            "weapons": [{

            }],
            "armor": [{

            }]
        }]
    }

    # get gender as string via input
    gender = user_open_choice("Give the gender of your hero: ")
    data["character"][0]["gender"] = gender
    save(savenum,data)

    # get name as string via input
    heroname = user_open_choice("Give a name for your hero: ")
    data["character"][0]["name"] = heroname
    save(savenum,data)

    # get class via multiple choice
    proffesion = user_choice("What class is your hero", "warrior", "mage", "hunter", "priest", "druid", "paladin")
    data["character"][0]["class"] = proffesion
    save(savenum, data)

    # based on class choice give build class -hp,sp,mp,str,defe,dex,wis,cha-
    if proffesion == "warrior":
        assign_attributes(data, 130, 120, 50, 14, 10, 8, 6, 10)
        assign_ability(data,"active", "shield bash", "ram your shield in to the enemy, stunning them for 1 turn" )
    elif proffesion == "mage":
        assign_attributes(data, 80, 80, 140, 8, 6, 10, 12, 14)
    elif proffesion == "hunter":
        assign_attributes(data, 110, 130, 60, 12, 8, 14, 8, 8)
    elif proffesion == "priest":
        assign_attributes(data, 70, 100, 130, 8, 8, 8, 14, 14)
    elif proffesion == "druid":
        assign_attributes(data, 110, 100, 90, 10, 10, 12, 12, 6)
    elif proffesion == "paladin":
        assign_attributes(data, 150, 80, 70, 8, 14, 8, 8, 12)

    save(savenum, data)

