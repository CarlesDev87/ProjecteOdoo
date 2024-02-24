import random

noms_humans = ["Alaric", "Aric", "Cedric", "Eleanor", "Elara", "Gareth", "Isabella", "Isolde", "Lorna", "Lyra", "Roland", "Rowan", "Seraphina", "Theron"]
cognoms_humans = ["Dawnblade", "Flamecaster", "Frostheart", "Ironhammer", "Lightbringer", "Silverhand", "Stormforge", "Stormwatcher", "Swiftwind", "Thunderstrike"]

noms_orcos = ["Durotan", "Garrosh", "Grommash", "Grok", "Gul'dan", "Hellscream", "Kargath", "Kilrogg", "Makar", "Nazgrim", "Orgrim", "Saurfang", "Thrall", "Zugor"]
cognoms_orcos = ["Blackhand", "Bloodfury", "Doomhammer", "Frostwolf", "Gorehowl", "Hellscream", "Makar", "Rend", "Skullcrusher", "Stonefist", "Thunderlord", "Warsong", "Wolfheart", "Zugor"]


def name_human_generator():
    return f"{random.choice(noms_humans)} {random.choice(cognoms_humans)}"


def name_orcs_generator():
    return f"{random.choice(noms_orcos)} {random.choice(cognoms_orcos)}"

