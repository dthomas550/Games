import pickle, sys, os
from game_files.output import gprint, show_help, show_history, show_settings
from game_files.extra import set_action_subs, get_any, mob_list_adder, off_subs, on_subs, game_error
from game_files.characters import Rimuru_Tempest

# Initiates new Rimuru_Tempest object which will be updated with save if save exists.
rimuru = Rimuru_Tempest()
successful_attack = False

#                    ========== Level Functions ==========
def game_hud(playable_actions):
    """Show game HUD, includes current mimic, mobs targeted, and available actions."""

    # Formats actions to be displayed to user.
    hud_actions = playable_actions[:]
    for action in hud_actions:
        # Removes action from HUD if not playable.
        if action_playable(action) is False: hud_actions.remove(action)
        # If action has x_ in it's name it'll parse that out to be displayed to user.
        elif 'x_' in action[:3]:
            hud_actions.remove(action)
            hud_actions = [' '.join(list(filter(None, action.split('_')))[1:])] + hud_actions

    if rimuru.show_actions is False or rimuru.hardcore is True: return False

    if rimuru.current_mimic or rimuru.targeted_mobs or rimuru.show_actions: print()  # Adds extra space when needed.

    if rimuru.current_mimic:
        print(f"Mimic: [{rimuru.current_mimic.name}]")  # Only show if currently using mimic.

    if rimuru.targeted_mobs:
        # Adds X status to corresponding targets that are dead.
        targets = ', '.join([(f'x{mob[1]}({mob[0].name})' if mob[0].is_alive else f'Dead-x{mob[1]}({mob[0].name})') for mob in rimuru.targeted_mobs])
        print(f'Target: {targets}')

    if rimuru.show_actions:
        # Formats playable_actions available to user. Replaces _ with spaces and adds commas when needed.
        actions_for_hud = ' '.join([f"({action.replace('_', ' ').strip()})" for action in hud_actions if 'hfunc' not in action])
        print(f"Actions: {actions_for_hud}", end='')

def actions(level=None):
    """
    Updates player's location, Shows HUD, takes user input and runs corresponding actions.

    Args:
        level obj: Current story progress class object.

    Usage:
        > inv
        > stats
        > attack tempest serpent with water blade
    """

    global successful_attack

    # Updates player's location.
    rimuru.update_location(rimuru.get_location_variable(level))

    # Get's playable actions from parsing inputted class subclasses.
    playable_actions = []
    for action in dir(level):  # Gets subclass functions.
        if action_playable(action) is False: continue
        if '__' in action: continue  # Filters out unwanted variables and functions.
        # Hides any action with 'x_' in name, unless action_playable() return True.
        if 'x_' in action[:3] and action_playable(action) is not True: continue
        playable_actions.append(action)

    game_hud(playable_actions)

    # ========== Debug Mode
    # Runs first available action that will progress the storyline.
    if rimuru.fast_mode is True:
        for action in playable_actions:
            if action[0] == '_':
                user_input = action.replace('_', ' ').strip()
    else:
        user_input = input("\n> ").strip().lower()
        if 'hfunc' in user_input: actions(level)  # So user can't so easily activate 'hfunc' actions.
        # Removes anything that's not alpha-numeric, easier for making __subs.
        user_input = ''.join(i for i in user_input if i.isalnum() or ' ')
        print()

    # Separates user input into command and command arguments.
    split_user_input = user_input.split(' ')
    command, parameters = split_user_input[0], ' '.join(split_user_input[1:])
    user = rimuru

    # [correspond_game_function, [optional_parameters], ['user_input_to_match_to']
    game_actions = [
        [rimuru.show_info, ['info']],
        [rimuru.show_inventory, ['inv']],
        [rimuru.show_attributes, ['stats']],
        [set_targets, ['target']],
        [rimuru.attack, [parameters], ['attack']],
        [rimuru.use, [parameters, user], ['use']],
        [rimuru.craft_item, ['craft']],
        [rimuru.remove_inventory, ['remove']],
        [rimuru.eat_targets, ['eat', 'predate']],
        [rimuru.use_mimic, ['mimic']],
        [rimuru.show_mimics, ['mimics', 'mimicries']],
        [rimuru.use, ['magic sense'], ['nearby']],
        [rimuru.get_location, ['location']],
        [rimuru.show_subordinates, ['subs', 'subordinates']],
        [rimuru.show_reputations, ['rep', 'reps', 'reputations', 'standings']],
        [show_help, ['/help']],
        [change_settings, ['/settings', '/options']],
        [show_history, ['/history', '/log']],
        [restart, ['/restart']],
        [save_reset, ['/reset']],
        [game_exit, ['/exit']],
    ]

    # Passes in user inputted arguments as parameters and runs corresponding action.
    for action in game_actions:
        if 'attack' in command:
            # Used for check_attack_success().
            successful_attack = rimuru.attack(parameters)
            break

        # If action needs custom parameters passed in.
        if len(action) == 3 and command in action[2]:
            action[0](*action[1])

        # Run matched corresponding game function and pass rest of user input as parameter.
        if command in action[1]: action[0](parameters)

    for action in playable_actions:
        # Currently need two evals to find __subs for action.
        try: action_subs = eval(f"level.{action}.{action}__subs")
        except: action_subs = []
        try: action_subs = eval(f"level.{action}._{action}__subs")
        except: pass

        # Able to activate a hfunc or _hfunc action without needing to add redundant item to __subs.
        # E.g. 'hfunc_attack' action you would've needed to add __subs = ['attack'], if not for this line.
        if 'hfunc' in action: action_subs.append(' '.join([i for i in action.split('_') if i][1:]))

        # Usually used for when you want an action to be used only once.
        if 'ACTIONBLOCKED' in action_subs: continue

        # Adds action's class name to subs list, so you don't have to add it yourself.
        action_subs = set_action_subs(action, action_subs)

        # play game action if matching from player input.
        if get_any(user_input, action_subs, strict_match=False):
            # So you can check if action has been played using game.conditions('action_name') function.
            rimuru.add_action_played(action_subs[-1])
            eval(f"level.{action}()")

    actions(level)

def action_played(match, amount=1):
    """
    Checks if game action has been played.

    Args:
        match obj: Pass game level object to check if it has been played already.

    Returns:
        bool True: Returns True if game action has been played.

    Usage:
        action_played(self)
    """

    # Extracts and parses level action name from passed in level object.
    # E.g. Extracts "speak now" from "<class 'chapters.tensei_1.ch1_cave.<locals>.wake_up.speak_now'>"
    match_action = str(match.__class__).split('.')[-1].replace('_', ' ')[:-2].strip()

    # Checks if action has been played more than once.
    if conditions(match_action) > amount: return True

def conditions(game_var, new_value=None):
    """
    Set and fetch game variables.

    Args:
        game_var str: Gameplay variable to find and return.

    Returns:
        str, bool, int, obj: Returns gameplay variable if found or if new one was set.
    """

    # Set new value to a game conditional.
    if new_value:
        rimuru.game_conditions[game_var] = new_value
        return new_value

    # Return game conditional data if found.
    if game_var in rimuru.game_conditions:
        return rimuru.game_conditions[game_var]
    if game_var in rimuru.actions_played:
        return rimuru.actions_played[game_var][0]
    return False

def action_playable(match, status=None):
    """
    Checks and sets if action is playable. If action is disabled, it's also hidden on HUD.
    hfunc_action is for hidden action from HUD, but still playable. x_action are hidden and unplayable until enabled with this function.

    Args:
        match: Action to check/set playability.
        status: Optionally set new status of playability of action.

    Returns:
        bool: Returns True/False if action is playable.
    """

    for action, data in rimuru.actions_played.items():
        if action in match:
            # If function received new status to set to action playability.
            if status is not None: data[1] = status

            return data[1]

    rimuru.actions_played[match] = [0, status]
    return status

def last_use_skill(skill):
    """
    Checks what was the last successfully used skill.

    Args:
        skill str: Skill to check if that was the last skill used.

    Returns:
        obj: Returns game skill object if match.
        bool False: If not match.
    """

    # If last_use_skill var is not set.
    if not rimuru.last_use_skill: return False

    if skill.lower() in rimuru.last_use_skill.name.lower():
        return rimuru.last_use_skill
    return False

def check_attack_success():
    """Check if last attack was successful."""

    return successful_attack

def set_targets(targets):
    """
    Adds inputted targets to targeted_mobs list from user input.

    Separates user inputted targets by ',' then checks to see if mob is in active_mobs list.
    If so, adds to setTargets list.

    Args:
        targets str: String of target(s) to add to targeted_mobs (list)

    Usage:
        > target tempest serpent, giant bat
    """

    targets = targets.lower()

    # Clears currently targeted.
    if get_any(targets, ['reset', 'clear']):
        rimuru.targeted_mobs.clear()
    # Target all nearby targetable mobs.
    elif 'all' in targets:
        rimuru.targeted_mobs = rimuru.active_mobs[:]
    else:
        for target in targets.split(','):
            # Only able to target mobs in active_mobs list.
            for mob in rimuru.active_mobs:
                if mob[0].name.lower() == target.strip().lower():
                    mob_list_adder(mob, rimuru.targeted_mobs)

def mobs_add(add_mobs):
    """
    Add new mob to current level, and able to set name at creation.

    Args:
        add_mobs str: Adds mob objects to active_mobs list.
            'X*mob': Number of that mob to add.
            'mob:name': Set mob's name when game character object is initialized.

    Usage:
        mobs_new(['tempest serpent'])
        mobs_new(['tempest serpent', 'giant bat'])
        mobs_new(['10* goblin', 'goblin: Goblin Chief'])
        mobs_new(['50* goblin: Goblinas'])
    """

    for new_mob in add_mobs:
        amount = 1
        # Add multiple of same mob, e.g. ['5*goblin']
        if '*' in new_mob:
            amount, new_mob = new_mob.split('*')
            try: amount = int(amount)
            except: pass

        # Sets mob name when creating new Character object, e.g. ['tempest serpent: john']
        if ':' in new_mob:
            new_mob, new_name = new_mob.split(':')
        else: new_name = ''

        if mob_object := rimuru.get_object(new_mob.strip(), new=True):
            mob_list_adder([mob_object(new_name.strip()), amount], rimuru.active_mobs, amount_mode=True)

def mobs_remove(remove_mobs):
    """
    Removes mob(s) from active_mobs list.

    Args:
        remove_mobs list: Mobs to remove.

    Usage:
        mobs_remove(['tempest serpent'])
    """

    for mob in remove_mobs:
        for active_mob in rimuru.active_mobs:
            if mob.lower() in active_mob[0].name.lower():
                rimuru.active_mobs.remove(active_mob)

def mob_status(target, set_var=None):
    """
    Returns mob alive status mob in active_mobs list.
    Returns character objects is_alive variable.

    Args:
        target str: Target character to check is_alive status.

    Usage:
        mob_status('tempest serpent')

    Returns:
        Bool: Character's is_alive var.
    """

    for i in rimuru.active_mobs:
        if target.lower() == i[0].name.lower():
            if set_var is not None: i[0].is_alive = set_var
            return i[0].is_alive

def mobs_cleared():
    """
    Checks if mobs on current level are all dead.

    Returns:
        boolean: If all mobs in active_mobs are dead.

    Usage:
        if mobs_cleared():

    Returns:
        bool: If all mobs in active_mobs list are dead.
    """

    # If just one mob's is_alive boolean var is True this function will return False.
    for mob in rimuru.active_mobs:
        if mob[0].is_alive: return False
    return True

def mob_obj(mob):
    """
    Get's mob's game object from active_mobs list.

    Args:
        mob str: Name of mob in active_mobs list you want the object of.

    Returns:
        obj: Returns mob's game object if match found.
    """

    # Returns mob's game object. The second item in the list is the number of mobs in gameplay.
    for i in rimuru.active_mobs:
        if mob in i[0].name.lower(): return i[0]

def clear_subs(action):
    """
    Clears __subs list of passed in class.
    Adds 'ACTIONBLOCK' string to action's __subs list.
    game_action function will see that 'ACTIONBLOCK' string is in the __subs list and will not allow player to do action.

    Args:
        level: Playable action class object from chapter file.
    """

    for i in dir(action):
        if '__subs' in i: eval(f"action.{i}.append('ACTIONBLOCKED')")

def clear_all(clear_targeting=True, clear_mimic=True, clear_active_mobs=True):
    """Optionally reset targeted_mobs list, active_mobs list and/or current mimic."""

    if clear_targeting: rimuru.targeted_mobs.clear()
    if clear_active_mobs: rimuru.active_mobs.clear()
    # Only resets mimicry if it's active.
    if clear_mimic and rimuru.check_mimic(): rimuru.use_mimic('reset')


def continue_to(next_location):
    """
    Saves game and continues to next location.

    Args:
        next_location: Next chapter to play.
    """

    rimuru.current_location_object = next_location
    save()

    # Loads next story chapter.
    try: next_location(rimuru)
    except: gprint("< Error Loading Next Location >")

#                    ========== Extra Functionality ==========
def multi_attr_adder(mobs, attrs):
    """
    Add multiple attributes to multiple characters.
    Only works on self or subordinates.

    Args:
        mobs list:
        attrs list:

    Returns:

    """

    characters = []
    if 'rimuru' in mobs: characters.append(rimuru)

    # Get's game character's objects to add attributes to, if fails calls game_error().
    for char_name in mobs:
        if char_object := rimuru.get_subordinate(char_name):
            characters.append(char_object)

    # Loops through characters and adds each attribute.
    for char_object in characters:
        for attr_name in attrs:
            char_object.add_attribute(attr_name, show_acquired_msg=False)


#                    ========== Game Save/Settings ==========
def game_exit(*args):
    """Saves game using pickle, then exits."""

    #save()
    exit(0)

def restart(*args):
    """Restart game."""

    gprint("< Restarting Game... >")
    os.execl(sys.executable, sys.executable, *sys.argv)

def save(level=None, show_msg=True):
    """
    Pickels Rimuru_Tempest object.

    Args:
        level (bool): Update rimuru.current_location_object
        show_msg (bool True): Show Game Saved message.
    """

    global rimuru

    # Can specify what level to save at.
    if level: rimuru.current_location_object = level

    # If called from game_over function, the save will no longer be usable.
    if rimuru.valid_save is None: rimuru.valid_save = True

    pickle.dump(rimuru, open(rimuru.save_path, 'wb'))

    if show_msg: gprint("\n< Game Saved >\n")

def save_load(path):
    """
    Load game save.

    Args:
        path: Path of game save.

    Returns:
        obj: Loaded game save object.
    """

    global rimuru

    # Tries loading game. If can't, creates new Rimuru_Tempest object which contains all game data that will be picked.
    if os.path.isfile(path):
        rimuru = pickle.load(open(path, 'rb'))
        return rimuru

    import chapters.tensei_1 as tensei1
    rimuru.current_location_object = tensei1.ch1_cave
    rimuru.save_path = path

    # If game save is invalid (using game_over function), save file will be deleted and game will restart.
    if rimuru.valid_save is False:
        os.remove(rimuru.save_path)
        save_load(path)

    return rimuru

def save_reset(*args):
    """Deletes game.save file and restarts game."""

    try: os.remove(rimuru.source_folder_path + '/game.save')
    except: pass
    restart()

def game_over():
    """Player died, deletes pickle save file after invalidates it.."""

    global rimuru
    rimuru.valid_save = False  # So you can't use this save file anymore.
    save(show_msg=False)

    # Deletes player's save file.
    try: os.remove(rimuru.save_path)
    except: pass

    print("\n    < GAME OVER >\n\nPlay again?")
    if str(input('No / Yes or Enter > ')).lower() in ['n', 'no']: exit(0)
    else: restart()

def change_settings(user_input):
    """
    Show or change game settings.

    Args:
        user_input: Get input from game_action function.

    Usage:
        > settings
        > settings hud on
        > options hud hints off
    """

    new_value = None
    # Tries to extract game settings and on/off section from user_input.
    try:
        split_input = user_input.split()
        # Checks if player wants to enable/disable a setting.
        if get_any(split_input[-1], off_subs): new_value = False
        elif get_any(split_input[-1], on_subs): new_value = True
        # User can change multiple game settings with one go.
        settings_input = ''.join(user_input[:-1])
    except: new_value = None

    # If not detected game settings with usable on/off data from user_input.
    if not user_input or new_value is None:
        show_settings()
        return

    if 'textcrawl' in settings_input: rimuru.textcrawl = new_value
    if 'hardcore' in settings_input: rimuru.hardcore = new_value
    # strict_match is false so user can change multiple game settings in one go.
    if get_any(settings_input, ['hud', 'interface'], strict_match=False): rimuru.show_actions = new_value
    if get_any(settings_input, ['art', 'ascii'], strict_match=False): rimuru.show_art = new_value
    if get_any(settings_input, ['hints', 'clues'], strict_match=False): rimuru.show_hints = new_value

    show_settings()
