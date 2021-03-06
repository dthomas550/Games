from character_object.character import Character
from game_files.output import gprint, print_header

# ========== Characters
class Slime(Character):
    name = 'Slime'
    level = 1
    appearance = 'Slimey slime!'
    description = '''One of the weakest Monsters known to exist.
        They lack hunger and simply dine on magical energy, and thus have no need for physical nourishment. 
        In areas with poor magical energy concentration, monsters and small animals serve as an alternative.

        Slime bodies are a composition of identical cells.
        Every cell can serve as a brain cell, nerve ending, and muscle at the same time.
        Thus, as the thought process is undertaken by different cells at different times, sleep is unnecessary.
        Slime bodies move with magical energy. Since oxygen is unnecessary, no form of breathing occurs.
        
        The Slimes of energy-deprived regions are extremely violent and strong since there is a need for survival.
        Self-awareness is something impossible for a Slime.
        Slime species are typically thoughtless creatures that only absorb, split, and regenerate.
        They also usually never leave their territories.
        It is possible for an intelligent Slime to naturally come into existence as a Unique Monster, 
        though there hasn't been any such occurrence as of yet.'''
    evolution = 'Slime > ???'

class Rimuru_Tempest(Slime, Character):
    canon_name = 'Rimuru Tempest'
    shared_protection = 'Protection of Tempest'
    level = 2
    current_mimic = None
    current_mimic_species = 'Slime'
    starting_state = ['Sage', 'Predator', 'Mimic', 'Self-Regeneration', 'Absorb/Dissolve', 'Pain Resist', 'Melee Resist', 'Electricity Resist']

    # ========== Predator Functions
    def mimic_generator(self):
        """
        Yields available mimic mob objects.

        Returns:
            mimic: Yields character objects that are in acquired_mimicries dictionary.
        """

        if not self.mimic_object(): return None

        for _mob_rank, mimics in self.acquired_mimicries.items():
            for _mob_name, mimic in mimics.items(): yield mimic

    def mimic_object(self, update_status=None):
        """
        Return mimic ability's game object, and can also set active status.

        Args:
            update_status str(None): Sets whether mimic is being used or not.

        Returns:
            mimic: Mimic game object from character.
        """

        try:
            mimic_object = self.attributes['Unique Skill']['Mimic']
            if update_status is not None:
                mimic_object.status = update_status
            return mimic_object
        except: pass

    def show_mimics(self, *args):
        """Lists acquired mimicries by species."""

        print_header('Mimicries')
        for mob_rank, mobs in self.acquired_mimicries.items():
            print(f'    {mob_rank}:')
            for mob_name, _mob_obj in mobs.items():
                print(f'        {mob_name}')
        print("\n    Note: Reset mimic with 'mimic reset'.")

    def add_mimic(self, mob, show_msg=True):
        """
        Adds new monster mimicry.

        Args:
            mob str/obj: Character object to add to acquired_mimicries list
            show_msg bool(True): Show acquired message.
        """

        if type(mob) is str:
            mob = self.get_object(mob, new=True)()
        if not mob: return False

        # Basically checks if self is the rimuru object (player).
        if not self.mimic_object(): return False

        # Checks if already acquired.
        if mob.name in self.acquired_mimicries[mob.rank]: return None

        # Adds new mob object to usable mimicries dict.
        self.acquired_mimicries[mob.rank][mob.name] = mob

        if show_msg: gprint(f"<< Information, analysis on [{mob.name}] completed. New mimicry available. >>")

    def use_mimic(self, character):
        """
        Use mimicry ability.

        Args:
            character str: Game monster to mimic.

        Usage:
            > mimic tempest serpent
        """

        # Resets mimic state (default Slime).
        if character == 'reset':
            self.current_mimic_species = 'Slime'
            self.current_mimic = None
            self.mimic_object(update_status='')
            gprint("< Mimicry Reset >")
        else:
            # Get's character game object from acquired_mimicries dictionary.
            if new_mimic := self.get_object(character, [*self.mimic_generator()]):
                # Can't mimic items/skills, only mobs that you have acquried.
                try: self.current_mimic_species = new_mimic.species
                except: pass
                else:
                    # Updates relevant player information when mimicry is activated.
                    self.current_mimic = new_mimic
                    self.mimic_object(update_status='Active')
                    gprint(f'< Now Mimicking [{new_mimic.name}] >')

    def check_mimic(self, match=''):
        """
        Return name (str) of character currently mimicking, can also check if using specific mimic.

        Args:
            match str(None): Check if currently mimicking specified mob by name.

        Returns:
            str: Returns name of mob currently mimicking.
        """

        if m_object := self.current_mimic:
            if self.current_mimic.name.lower() in match.lower():
                return m_object.name
        return False

    def eat_targets(self, *args):
        """
        Predates targets that are being targeted. Also adds new mimicry.

        Args:
            args: Catch all for use from game_action function.

        Usage:
            > eat
        """

        for target in self.targeted_mobs:
            if not target[0]: continue  # If no game object found.
            # Check if target has specific game object to be used when using predation.
            #if target[0].predation_return: target = target[0].predation_return

            if target[0].game_object_type == 'item':
                self.add_inventory(target[0])
            elif target[0].game_object_type == 'attribute':
                self.add_attribute(target[0])
            elif target[0].game_object_type == 'character':
                # Can only eat targeted mobs that are dead.
                if target[0].is_alive is False:
                    self.add_mimic(target[0])
                    # Adds dead mob to inventory.
                    self.add_inventory(target[0], target[1], show_analysis_msg=False)
                    # Removes mob from targeted and active mobs lists.
                    self.targeted_mobs.remove(target)
                    try: self.active_mobs.remove(target)
                    except: pass

        # For some reason I need this to check if it cleared out all dead mobs.
        # If not it'll just run this function again. Have not ran into bugged looping, yet. Should probably change this huh?
        for i in self.targeted_mobs:
            if i[0].is_alive is False: self.eat_targets()

class Veldora_Tempest(Character):
    name = "Veldora"
    titles = ['Storm Dragon']
    canon_name = 'Veldora Tempest'
    species = 'True Dragon'
    protections = ['Protection of the Storm']
    starting_state = ['investigator']
    shared_protection = 'Storm Crest'
    is_alive = True
    level = 11
    inv_capacity_add = 10


# ===== Adventurers
class Human(Character):
    name = 'Human'
    species = 'Human'
    level = 2
    appearance = 'A featherless biped.'
    evolution = 'Human > ???'
    #evolution = '''
    #    Human > Enlightened > Saint
    #          > Maijin'''

class Eren_Grimwold(Human, Character):
    name = "Eren Grimwold"
    level = 5
    species = 'Human'
    occupations = ['Adventurer']
    affiliations = ['Freedom Association', "Kaval's Party", "Brumund"]
    description = "A Mage part of Cabal's Party."
    appearance = "A blonde, 16y/o, green eyed adventurer from the Freedom Association."
    abilities = ['Mud Hand', 'Cleaning Magic', 'Elemental Magic']

class Kaval(Human, Character):
    name = "Kaval"
    level = 5
    species = 'Human'
    occupations = ['Adventurer']
    affiliations = ["Kaval's Party", "Freedom Association"]
    description = """Leader of his adventure's party, where he serves as the 'fighter' role. Alongside Gido,
        he is also tasked as the secret bodyguard of Lady Elyune under the guise of an adventurer.'"""
    appearance = 'A young man with medium length hair, seemingly in his prime.'
    abilities = ['Fighting Spirit', 'Heavy Collision']

class Gido(Human, Character):
    name = 'Gido'
    level = 5
    species = 'Human'
    occupations = ['Adventurer']
    affiliations = ["Kaval's Party", "Freedom Association"]
    description = """A member of Kaval's Party who serves as the 'thief' role. However,
        he is actually serving as one of the bodyguards of Lady Elyune secretly while under the guise of an adventurer."""
    appearance = """Gido has a tall and strong build and a rectangular head. 
        His brown hair is cut short and has a goatee, whereas his cheeks have distinct depressions."""
    abilities = ['Stealth']


# ========== Low Level
class Tempest_Serpent(Character):
    name = 'Tempest Serpent'
    species = 'Black Serpent'
    level = 6
    appearance = 'The snake has a large, jet-black body with thorned scales and tough skin.'
    description = 'Found in the Sealed cave, spawned from the massive amount of magic essence emanating from the sealed Veldora.'
    starting_state = ['sense heat source', 'poisonous breath']

class Giant_Bat(Character):
    name = 'Giant Bat'
    species = 'Bat'
    level = 4
    appearance = '''It's a giant bat...
        Due to its wings that regulate its own gravity, it's capable of flight'''
    description = 'Found in the Sealed cave, spawned from the massive amount of magic essence emanating from the sealed Veldora.'
    starting_state = ['ultrasound waves', 'vampirism']

class Evil_Centipede(Character):
    name = 'Evil Centipede'
    species = 'Centipede'
    level = 5
    appearance = 'Centipede monstrosity, a giant centipede.'
    description = 'Found in the Sealed cave, spawned from the massive amount of magic essence emanating from the sealed Veldora.'
    starting_state = ['paralyzing breath']

class Black_Spider(Character):
    name = 'Black Spider'
    species = 'Spider'
    level = 5
    appearance = 'Most of the body is yellow-ish, while the legs are black.'
    description = 'Found in the Sealed cave, spawned from the massive amount of magic essence emanating from the sealed Veldora.'
    starting_state = ['sticky thread', 'steel thread']


# ========== Wolves
class Direwolf(Character):
    name = 'Direwolf'
    species = 'Direwolf'
    level = 4
    appearance = """They have silver-blue fur, with the exception of the Direwolf Leader's Son, 
        who also has star mark on his forehead in a darker shade of blue, and a silver-white mane and snout."""
    description = """The wolves did not require food to survive. Their sustenance lay in the world's magicules.
        By attacking stronger monsters or slaughtering droves of humans, they can evolve into calamity-level creatures, although none of these options was feasible for them.
        The Forest of Jura was bountiful of magic and had no monsters strong enough to threaten the wolves.
        However, Veldora's overwhelming magical force prevented them from entering.
        As individuals they're C rank, and B if as a pack."""
    evolution = 'Direwolf > ???'
    starting_state = ['keen smell', 'coercion', 'thought communication']

class Direwolf_Leader(Direwolf, Character):
    name = 'Direwolf Leader'
    level = 4

class Tempest_Wolf(Direwolf, Character):
    name = 'Tempest Wolf'
    species = 'Tempest Wolf'
    level = 5
    appearance = '''Tempest Wolves have jet black fur, which gives a feeling of bewitching gloss and a glossy finish.
        The storm element gave the wolf pack an ever-so-slight purplish shine to their black color.'''

    evolution = """
       Direwolf > Black Direwolf
                > Tempest Wolf > ???"""
    # evolution = """
    #    Direwolf > Black Direwolf
    #             > Tempest Wolf > Star Wolf > Tempest Star Wolf
    #                            > Star Leader"""

class Tempest_Star_Wolf(Tempest_Wolf, Character):
    name = 'Tempest Star Wolf'
    level = 5
    starting_state = Tempest_Wolf.starting_state + ['shadow step']
    evolution = """
       Direwolf > Black Direwolf
                > Tempest Wolf > Star Wolf > Tempest Star Wolf > ???
                               > Star Leader"""

# ========== Goblins
class Goblin(Character):
    name = 'Goblin'
    species = 'Goblin'
    level = 2
    appearance = 'They have green skin and a big nose. Their average height is 150 centimeters.'
    description = '''Goblins are of the monsters that populate The Great Jura Forest, with many different tribes dotting around the forest. 
        Although there are many different tribes of goblins, they will usually stand together in the face of great danger.
        Many of the goblins revere the Storm Dragon as their God and protector of the forest.
        For goblins, deaths are very common, to the point they have evolved to reproduce as much as possible to maintain their population.
        '''
    evolution = 'Goblin > ???'



class Hobgoblin(Goblin, Character):
    name = 'Hobgoblin'
    species = 'Hobgoblin'
    level = 3
    appearance = 'They have green skin like their pre-evolved form, but their average height is improved and his height now reaches around 180 centimeters.'
    description = 'Hobglins are evolved form of Gobins.'
    evolution = 'Goblin > Hobgoblin > ???'
    #evolution = '''
    #    Goblin > Hobgoblin > Ogre > Kijin > Fair Oni
    #                                      > Wicked Oni'''
