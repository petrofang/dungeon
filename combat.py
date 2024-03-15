from random import random
from commands import parse
from time import sleep
from mobiles import Mobile
from players import PlayerCharacter
from dice import d
from dungeon_data import session
import threading, traceback
from actions import echo, echo_at, echo_around
import server

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
            
            echo(player, f"{enemy} gains initiative.")
            attacker=enemy
            defender=player
        else:
            echo_around(player, f"{player} gains initiative.")
            echo_at(player, "You gain initiative.")
            attacker=player
            defender=enemy

        combat_input=threading.Thread(
            target=self.combat_user_input, 
            args=(self.player, self.enemy))
        combat_loop=threading.Thread(
            target=self.combat_turn, 
            args=(attacker, defender))
        combat_input.start()
        combat_loop.start()
        combat_input.join()
        combat_loop.join()
        
    @property 
    def COMBAT_PROMPT(self):
         prompt = (f"You: {self.player.hp}/{self.player.hp_max}HP;",
            f" {self.enemy.name}: {self.enemy.hp}/{self.enemy.hp_max}HP",
            "\n >> ")
         return ''.join(prompt)
        
    def combat_user_input(self, player:PlayerCharacter, enemy:Mobile):
        while self.engaged==True:
            echo_at(player, f"{self.COMBAT_PROMPT}")
            command = server.receive(player.socket)
            if not self.engaged:
                parse(self.player, command)
                return
            if command: 
                self.combat_lock.acquire()
                self.combat_command=parse_combat_command(self.player, 
                                                         self.enemy, 
                                                         command, 
                                                         self)
                self.combat_lock.release()

    def combat_turn(self, attacker, defender):
        self.combat_lock.acquire()
        try:
            if self.combat_command:
                if not self.combat_command(player=self.player,
                                           enemy=self.enemy, combat=self):
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
            echo_at(self.player, f"{self.COMBAT_PROMPT}")   
            sleep(6)
            self.combat_turn(defender, attacker)
 
    def standard_attack(self, attacker, defender):
        """
        a standard attack sequence:
            1. determine if a hit was made:
               hit = attacker.dex +d20 vs defender.dex +d20
            2. calculate damage (if hit)
               damage dice determined by attacker weapon rating 
               or unarmed (d4)
               dmg = attacker.str//4 + dice 
               vs. defender.str//4 + armor rating
            3. subtract max(dmg,0) from defender.hp
        """
        echo_around(self.player, f"{attacker.name.capitalize()} attacks {defender}.")
        if self.player==attacker:
            echo_at(self.player, f"You attack {defender}.")
        else:
            echo_at(self.player, f"{attacker.name.capitalize()} attacks you.")

        
        sleep(1)

        attacker_d20, defender_d20 = d(20), d(20)
        hit = (attacker.dex + attacker_d20) - (defender.dex+defender_d20)
        echo_at(self.player, f"hit roll: [ dex({attacker.dex})+d20({attacker_d20}) ",
              f"v. dex({defender.dex})+d20({defender_d20}) ] = {hit}")
        # TODO: add combat skills for accuracy, dodge
        
        sleep(1)
        if hit <= 0: # ( if miss )
            if defender is self.player:
                if hit<=-10: 
                    echo_at(self.player, f"You easily evade the attack.")
                    echo_around(self.player, f"{defender} easily evades the attack.")
                elif hit<0: 
                    echo_at(self.player, f"You evade the attack.") 
                    echo_around(self.player, f"{defender} evades the attack.")
                elif hit==0: 
                    echo_at(self.player, f"You narrowly evade the attack!")
                    echo_around(self.player, f"{defender} narrowly evades the attack!")
            

            else:
                if hit<=-10: echo(self.player, f"{defender} easily evades the attack.")
                elif hit<0: echo(self.player, f"{defender} evades the attack.")
                elif hit==0: echo(self.player, f"{defender} narrowly evades the attack!")
            
            
            sleep(4)

        else:
            # TODO: fix this mess, describe armor mitigation better
            if attacker==self.player:
                echo_at(self.player, f"You make contact!")
                echo_around(self.player, f"{attacker} makes contact!")
            else:
                echo(self.player, f"{attacker} makes contact!")
            sleep(1) 

            # determine damage roll
            if not attacker.equipment['weapon']: 
                damage_rating=4
            else: 
                damage_rating=attacker.equipment['weapon'].rating
            damage_roll=d(damage_rating)

            # determine damage mitigation
            if not defender.equipment['armor']: 
                armor_rating=0
            else: 
                armor_rating=defender.equipment['armor'].rating
            
            damage = ((attacker.str //4 + damage_roll) - 
                      (defender.str // 4 + armor_rating))
            echo_at(self.player, f"{max(damage, 0)} damage inflicted!")
            defender.hp -= max(damage,0)
            session.commit

    def status_check(self, attacker=None, defender=None):
        # check status and handle apprropriately (eg, death if hp <= 0)
        if defender.hp <= 0:
            defender.die()
            self.disengage()

    def disengage(self):
        # end combat
        self.engaged=False
        echo_at(self.player, " >> ", end="")

def parse_combat_command(player:Mobile, enemy:Mobile, 
                         args:str, combat:Combat):
    if not args: 
        echo_at(player, "Huh?")
        return None
    else:
        command, *args = args.split()
#        if args[0].lower()=="cast":pass # magic spell handler
        arg=' '.join(args) if args else None
        command_action = getattr(CombatCommands, command, None)
        if command_action:
            return command_action(player=player, 
                                  enemy=enemy, 
                                  arg=arg, 
                                  combat=combat)
        else:
            echo_at(player, f"Unknown combat action: '{command}.'")
            return None
    

class CombatCommands:
    def flee(player:Mobile=None, combat=None, **kwargs):
        action="flee"
        if not player.room.exits:
            echo_at(player,"There is no direction in which to flee.")
            return None
        else:
            echo_at(player,"You try to find a way way out...")
            echo_around(player, f"{player} is trying to escape!")
            return CombatAction._do(action=action)
    

class CombatAction: #P.E.A.A.C. :: Player, Enemy, Action, Arguement, Combat
    """
    for combat actions, return value is     
        True    if it BLOCKS standard attack
        False   if it ALLOWS standard attack
    """

    def _do(player:Mobile=None, enemy:Mobile=None, 
            action:str=None, arg:str=None, combat:Combat=None):
        combat_action=getattr(CombatAction, action, None)
        if combat_action: return combat_action
        else: 
            print(f"* BUG * : CombatAction '{action}' not implemented.")  
            raise NotImplementedError  

    def flee(player:Mobile=None, combat:Combat=None, **kwargs):
        for exit in player.room.exits:
            if exit.is_open and not exit.hidden:  
                if d(20) < player.dex/len(player.room.exits):
                    combat.disengage()
                    echo_at(player, "You see an opening and make a break for it!")
                    echo_around(player, f"{player} sees an opening and makes a break for it!") 
                    player.goto(exit.to_room_id)
                    echo_around(player, f"{player} comes huffing in.")
                    return True
                else:
                    echo_at(player, "You try to move toward the exit but your path is cut off.")
                    echo_around(player, f"{player} is out-maneuvered by {combat.enemy}!")
                    return False
            
            