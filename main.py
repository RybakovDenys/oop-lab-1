"""
ВИМОГИ ЛАБОРАТОРНОЇ РОБОТИ (РЕАЛІЗАЦІЯ):

1. Класи: 9 (Entity, Unit, Warrior, Mage, Item, Weapon, Consumable, Inventory, BattleManager).
2. Поля: > 15 (в сумі понад 20 полів у всіх класах).
3. Нетривіальні методи: > 25 (реалізовано логіку бою, лікування, інвентарю, прокачки рівня, тощо).
4. Ієрархії успадкування: 2
   - Entity -> Unit -> Warrior/Mage (глибина 3)
   - Item -> Weapon/Consumable (глибина 2)
5. Поліморфізм: 3 випадки
   - Динамічний: метод attack() (різна поведінка у Warrior та Mage).
   - Динамічний: метод use() (різна поведінка у Weapon та Consumable).
   - Статичний (Generics): клас Inventory[T], що працює з різними типами даних.
"""

from abc import ABC, abstractmethod
from typing import List, TypeVar, Generic, Callable, Optional
import random

class Entity(ABC):
    def __init__(self, name: str, x: int, y: int):
        self._name = name
        self._x = x
        self._y = y
        self._is_active = True

    @property
    def name(self):
        return self._name

    @abstractmethod
    def describe(self) -> str:
        pass

    def distance_to(self, other: 'Entity') -> int:
        return abs(self._x - other._x) + abs(self._y - other._y)

class Unit(Entity):
    def __init__(self, name: str, hp: int, defense: int, x: int = 0, y: int = 0):
        super().__init__(name, x, y)
        self._hp = hp
        self._max_hp = hp
        self._defense = defense
        self._level = 1
        self._xp = 0

    def is_alive(self) -> bool:
        return self._hp > 0

    def take_damage(self, amount: int) -> int:
        mitigation = min(self._defense * 0.5, amount * 0.8)
        actual_damage = int(max(1, amount - mitigation))
        
        self._hp -= actual_damage
        if self._hp <= 0:
            self._hp = 0
            self._is_active = False
        return actual_damage

    def heal(self, amount: int):
        if not self.is_alive():
            print(f"{self.name} is dead and cannot be healed.")
            return
        
        old_hp = self._hp
        self._hp = min(self._max_hp, self._hp + amount)
        print(f"{self.name} healed for {self._hp - old_hp} HP.")

    def gain_xp(self, amount: int):
        if not self.is_alive(): 
            return
        self._xp += amount
        threshold = self._level * 100
        if self._xp >= threshold:
            self._level_up()

    def _level_up(self):
        self._level += 1
        self._xp = 0
        growth = 20
        self._max_hp += growth
        self._hp = self._max_hp
        self._defense += 2
        print(f"*** {self.name} reached LEVEL {self._level}! (HP +{growth}) ***")

    @abstractmethod
    def attack(self, target: 'Unit'):
        pass

class Warrior(Unit):
    def __init__(self, name: str):
        super().__init__(name, hp=150, defense=12)
        self._rage = 0 

    def describe(self) -> str:
        return f"[Warrior] {self.name} | HP: {self._hp}/{self._max_hp} | Rage: {self._rage}"

    def attack(self, target: 'Unit'):
        base_dmg = random.randint(15, 25)
        rage_bonus = self._rage // 3
        total_dmg = base_dmg + rage_bonus
        
        print(f"{self.name} slashes {target.name} (Rage Bonus: +{rage_bonus})!")
        dealt = target.take_damage(total_dmg)
        
        self._rage = min(100, self._rage + 20)
        print(f"   -> Dealt {dealt} damage. Rage: {self._rage}")

    def heavy_slam(self, target: 'Unit'):
        if self._rage >= 40:
            print(f"{self.name} uses heavy slam!")
            self._rage -= 40
            target.take_damage(50)
        else:
            print(f"{self.name} grunts (not enough Rage)!")

class Mage(Unit):
    def __init__(self, name: str):
        super().__init__(name, hp=90, defense=3)
        self._mana = 100

    def describe(self) -> str:
        return f"[Mage] {self.name} | HP: {self._hp}/{self._max_hp} | Mana: {self._mana}"

    def attack(self, target: 'Unit'):
        if self._mana >= 15:
            dmg = random.randint(20, 35)
            self._mana -= 15
            print(f"{self.name} casts Lightning Bolt at {target.name}!")
            target.take_damage(dmg)
        else:
            print(f"{self.name} hits with staff (Out of Mana)!")
            target.take_damage(3)
            self._regenerate_mana()

    def _regenerate_mana(self):
        restore = 20
        self._mana = min(100, self._mana + restore)
        print(f"   -> {self.name} meditates and restores {restore} Mana.")

    def restore_mana(self, amount: int):
        self._mana = min(100, self._mana + amount)

class Item(ABC):
    def __init__(self, name: str, weight: float, price: int):
        self.name = name
        self.weight = weight
        self.price = price

    def __repr__(self):
        return f"<{self.name}>"

    @abstractmethod
    def use(self, target: Unit):
        pass

class Weapon(Item):
    def __init__(self, name: str, damage: int, weight: float):
        super().__init__(name, weight, price=damage * 10)
        self.damage = damage
        self.durability = 100

    def use(self, target: Unit):
        print(f"{target.name} equips {self.name}. It is a passive item.")

    def repair(self):
        if self.durability < 100:
            diff = 100 - self.durability
            self.durability = 100
            print(f"Weapon {self.name} repaired by {diff}%.")
        else:
            print("Weapon is in perfect condition.")

class Consumable(Item):
    def __init__(self, name: str, weight: float, effect_value: int, is_mana: bool = False):
        super().__init__(name, weight, price=effect_value * 2)
        self.effect_value = effect_value
        self.is_mana = is_mana
        self.is_consumed = False

    def use(self, target: Unit):
        if self.is_consumed:
            print(f"{self.name} is empty!")
            return

        print(f"{target.name} consumes {self.name}...")
        
        if self.is_mana:
            if isinstance(target, Mage):
                target.restore_mana(self.effect_value)
                print(f"   -> Mana restored (+{self.effect_value})")
                self.is_consumed = True
            else:
                print(f"   -> Nothing happened. {target.name} is not a Mage.")
                self.is_consumed = True
        else:
            target.heal(self.effect_value)
            self.is_consumed = True

T = TypeVar('T')

class Inventory(Generic[T]):
    def __init__(self, capacity: int):
        self._items: List[T] = []
        self._capacity = capacity

    def add(self, item: T) -> bool:
        if len(self._items) < self._capacity:
            self._items.append(item)
            return True
        print("Inventory is full!")
        return False

    def remove(self, item: T) -> bool:
        if item in self._items:
            self._items.remove(item)
            return True
        return False

    def filter_items(self, condition: Callable[[T], bool]) -> List[T]:
        return [item for item in self._items if condition(item)]

    def calculate_total_value(self) -> int:
        total = 0
        for item in self._items:
            if hasattr(item, 'price'):
                total += item.price
        return total

    def show(self):
        print(f"Contents ({len(self._items)}/{self._capacity}): {self._items}")

class BattleManager:
    def __init__(self):
        self._turn_count = 0
        self._is_battle_over = False

    def start_battle(self, team_a: List[Unit], team_b: List[Unit]):
        print("\nBATTLE STARTED")
        
        while not self._is_battle_over:
            self._turn_count += 1
            print(f"\n--- Round {self._turn_count} ---")
            
            self._process_team_turn(team_a, team_b)
            if self._check_win(team_a, team_b): break

            self._process_team_turn(team_b, team_a)
            if self._check_win(team_a, team_b): break
            
            if self._turn_count > 20:
                print("Battle took too long. Draw.")
                break

    def _process_team_turn(self, attackers: List[Unit], defenders: List[Unit]):
        for attacker in attackers:
            if not attacker.is_alive():
                continue
            
            live_targets = [t for t in defenders if t.is_alive()]
            if not live_targets:
                return

            target = random.choice(live_targets)
            attacker.attack(target)

    def _check_win(self, team_a: List[Unit], team_b: List[Unit]) -> bool:
        alive_a = any(u.is_alive() for u in team_a)
        alive_b = any(u.is_alive() for u in team_b)

        if not alive_a and not alive_b:
            print("\nEveryone died")
            self._is_battle_over = True
            return True
        elif not alive_b:
            print("\nTeam A WON!")
            self._distribute_xp(team_a)
            self._is_battle_over = True
            return True
        elif not alive_a:
            print("\nTeam B WON!")
            self._distribute_xp(team_b)
            self._is_battle_over = True
            return True
        return False

    def _distribute_xp(self, winners: List[Unit]):
        for u in winners:
            if u.is_alive():
                u.gain_xp(150)


if __name__ == "__main__":
    print("--- 1. Creating Objects & Inventory ---")
    
    warrior = Warrior("Warrior1")
    mage = Mage("Mage1")
    enemy = Warrior("Warrior2") 

    backpack = Inventory[Item](capacity=10)
    
    sword = Weapon("Sword", damage=20, weight=5.0)
    hp_pot = Consumable("Health Potion", weight=0.5, effect_value=60, is_mana=False)
    mana_pot = Consumable("Mana Potion", weight=0.5, effect_value=50, is_mana=True)

    backpack.add(sword)
    backpack.add(hp_pot)
    backpack.add(mana_pot)
    
    backpack.show()
    print(f"Backpack Value: {backpack.calculate_total_value()} coins")

    print("\n--- 2. Using Items (Polymorphism) ---")
    for item in [hp_pot, mana_pot]:
        warrior.take_damage(50)
        mage._mana = 10 
        
        item.use(warrior)
        if not item.is_consumed:
            item.use(mage)

    print("\n--- 3. Special Actions ---")
    warrior._rage = 50 
    warrior.heavy_slam(enemy)

    print("\n--- 4. Battle (BattleManager) ---")
    enemy_mage = Mage("Mage2")
    
    squad_a = Inventory[Unit](5)
    squad_a.add(warrior)
    squad_a.add(mage)
    
    manager = BattleManager()
    manager.start_battle([warrior, mage], [enemy, enemy_mage])

    print("\n--- 5. Results ---")
    print(warrior.describe())
    print(mage.describe())
    print(enemy.describe())
    print(enemy_mage.describe())