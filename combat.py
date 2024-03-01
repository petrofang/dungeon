from random import random
from commands import parse
from time import sleep
from mobiles import Mobile
from dice import d
from dungeon_data import session
import threading, traceback

class Combat:
    player=None
    enemy=None
    engaged=False
    combat_command=None
    combat_lock=threading.Lock()
    round=0

    def __init__(self, player, enemy):
        self.player=player
        self.enemy=enemy
        self.engaged=True
        
         # determine initiative:
        if enemy.dex > player.dex: 
            
            print(f"{enemy} gains initiative.")
            attacker=enemy
            defender=player
        else:
            print(f"{player} gains initiative.")
            attacker=player
            defender=enemy

        combat_input=threading.Thread(target=self.combat_user_input, args=(self.player, self.enemy))
        combat_loop=threading.Thread(target=self.combat_turn, args=(attacker, defender))
        combat_input.start()
        combat_loop.start()
        combat_input.join()
        combat_loop.join()
        
    @property 
    def COMBAT_PROMPT(self):
         return f"You: {self.player.hp}/{self.player.hp_max}HP; {self.enemy.name}: {self.enemy.hp}/{self.enemy.hp_max}HP\n >> "
        
    def combat_user_input(self, player:Mobile, enemy:Mobile):
        while self.engaged==True:
            print(f"{self.COMBAT_PROMPT}")
            command = input()
            if not self.engaged:
                parse(self.player, command)
                return
            if command: 
                self.combat_lock.acquire()
                self.combat_command=parse_combat_command(self.player, self.enemy, command, self)
                self.combat_lock.release()

    def combat_turn(self, attacker:Mobile, defender:Mobile):
        self.combat_lock.acquire()
        try:
            if self.combat_command:
                if not self.combat_command(player=self.player, enemy=self.enemy, combat=self):
                    self.standard_attack(attacker, defender)
                self.combat_command=None
            else:
                self.standard_attack(attacker, defender)
        except Exception as e:
            print(f"COMBAT ERROR: {e}")
            traceback.print_exc() 
            self.disengage()
            self.combat_lock.release()
            return
        finally:
            # Always release the lock even if an exception occurs
            self.combat_lock.release()
        self.status_check(attacker, defender)
        if self.engaged:
            print(f"{self.COMBAT_PROMPT}")   
            sleep(6)
            self.combat_turn(defender, attacker)
 
    def standard_attack(self, attacker:Mobile, defender:Mobile):
        # determine if a hit was made:
        #   hit = attacker.dex +d20 vs defender.dex +d20
        attacker_d20, defender_d20 = d(20), d(20)
        hit = (attacker.dex + attacker_d20) - (defender.dex+defender_d20)
        print(f"{attacker.name.capitalize()} makes an attack at {defender}.")
        print(f"hit roll: [ dex({attacker.dex})+d20({attacker_d20}) v. dex({defender.dex})+d20({defender_d20}) ] = {hit}")
        # add combat skills for accuracy, dodge
        
        if hit<0:
            print(f"{defender} dodges the attack!")
        else:
            print(f"{attacker} makes contact!")

        #   determine damage:   
            if not attacker.weapon: damage_rating=4
            else: damage_rating=attacker.weapon.rating
            damage_roll=d(damage_rating)
            if not defender.armor: armor_rating=0
            else: armor_rating=defender.armor.rating
            damage = (attacker.str //4 + damage_roll) - (defender.str // 4 + armor_rating)
            print(f"dmg roll: [ str/4({attacker.str //4}) + 1d({damage_rating})={damage_roll} vs str/4({defender.str // 4}) + AR({armor_rating}) ] ")
            print(f"{damage} damage inflicted!")
            defender.hp -=damage
            session.commit

    def status_check(self, attacker=None, defender=None):
        # check status and handle apprropriately (eg, death if hp <= 0)
        if defender.hp <= 0:
            defender.die()
            self.disengage()

    def disengage(self):
        # end combat
        self.engaged=False
        print(" >> ", end="")

def parse_combat_command(player:Mobile, enemy:Mobile, args:str, combat:Combat):
    if not args: 
        print("Huh?")
        return None
    else:
        command, *args = args.split()
#        if args[0].lower()=="cast":pass # magic spell handler
        arg=' '.join(args) if args else None
        command_action = getattr(CombatCommands, command, None)
        if command_action:
            return command_action(player=player, enemy=enemy, arg=arg, combat=combat)
        else:
            print(f"Unknown combat action: '{command}.'")
            return None
    
class CombatCommands:
    def flee(player:Mobile=None, combat=None, **kwargs):
        ACTION="flee"
        if not player.room.exits:
            print("There is no direction in which to flee.")
            return None
        else:
            print("You try to find a way way out...")
            return CombatAction._do(action=ACTION)
    

class CombatAction: #P.E.A.C.A.  :: Player, Enemy, Action, Arguement, Combat
    """
    for combat actions, return value is     True    if it blocks standard attack
                                            False   if it allows standard attack
    """

    def _do(player:Mobile=None, enemy:Mobile=None, action:str=None, arg:str=None, combat:Combat=None):
        combat_action=getattr(CombatAction, action, None)
        if combat_action: return combat_action
        else: print(f"*** BUG *** : CombatAction '{action}' not implemented.")    

    def flee(player:Mobile=None, combat:Combat=None, **kwargs):
        for exit in player.room.exits:
            if exit.is_open and not exit.hidden:  
                if d(20) < player.dex/len(player.room.exits):
                    combat.disengage()
                    print("You flee to fight another day.")
                    player.goto(exit.to_room_id)
                    return True
                else:
                    print("You try to move toward the exit but your path is cut off...")
                    return False
            
            