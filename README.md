## Algorand Mini-Game


### Overview

This is a simple game built with Algorand's Pyteal where a user plays as a warrior fighting a monster boss. This makes use of Pyteal's `global and local states` to store values that will be used in the game. The player's and the boss' stats are kept at default values at level 1. They both have `Health`, `Attack`, and `Defense`. Once the player defeats a boss, their level will be increased by 1. Every time a player increases levels, they can spend `twenty (20) points` to add to their stats, while the boss' stats increase steadily with the player's level.

### Application ID

The smart contract's application ID deployed on Algorand's testnet: `145743400`

## How the Smart Contract works

### Defining the States

`Global states` were used to store the initial Boss Stats, this would be where the Boss' stats will be based off depending on the current level of the player as it increases based on player level. Each level increases the boss' `Health` by 30, `Defense` by 5, and `Attack Damage` by 5. Global states were also used to store the variables for the `linear congruential recurrence relation` to generate pseudo-random number for the critical chance.

#### Global States
- boss_health (int)
- boss_attack (int)
- boss_defense (int)
- a (int)
- x (int)
- c (int)
- m (int)

`Local states` were used to store the player's stats. Once a player opts-in or later on upgrades their stats, those values will be added into their local states to ensure that the values are different from each user. The local states were also used to determine if they are currently in a battle, or if they are under upgrading their stats. The player's current level is also stored as a local state.

Also since the boss stats are based on the player's level, these values are also stored as local states.

#### Local States
- level (int)
- hp (int)
- health (int)
- attack (int)
- defense (int)
- local_boss_hp (int)
- local_boss_health (int)
- local_boss_attack (int)
- local_boss_defense (int)
- upgrade_player (int)
- in_match (int)

### Lifecycle

#### App Creation

Upon creation of the app, the initial values for the states used to generate our pseudo-random number are stored. Also the initial stats for the boss are stored.

### Account Opt In

Once an account opts-in into the smart contract, their initial stats such as hp, health, attack, defense, and level are set. We also. set their upgrade_player state to be `false` or `0` since this is the initial setup.

### Fight Boss

This will call the `set_boss_stats` subroutine, which checks first if they are ready to be in the battle, meaning they are not currently in another battle, or they are not currently in the upgrading state.

If both conditions are true, the boss' stats will be initialized for the level and the in_match state is set to `true` or `1` which signifies that the player is now currently in battle.

### Attack Boss

This will call the `attack` subroutine, it checks first if both the player and the boss have hp `greater than 0` to proceed. Once the check passes, the boss and player's stats are stored into their respective `scratch variables` including the generated pseudo-random number. 

Next is a series of conditions that would determine if the player or boss would hit a critical strike. 

The first condition checks if the generated pseudo-random number matches with the selected attack type of the user (a number from 1 to 4). If this is true, then their damage is multiplied by 3. If it's false, then another condition would check if the pseudo-random number matches with the randomly generated number that was passed as argument together with the selected attack type. If this is true, then the player's damage is multiplied by 2. If none of the conditions were met, the damage remains the same (multiplied by 1).

The next condition checks if the argument passed for the boss' critical chance (which is also a generated number from 1 to 4) is met. If this is true, the boss' attack would be multiplied by 2. If not, it's damage will remain the same (multiplied by 1).

Next series of conditions calculates and stores the damage the player and boss receive from each other.

First is a condition that checks whether the boss' `current HP` is `greater than` the player's `attack stats` minus the boss' `defense stats` multiplied by the player's critical strike to ensure that the smart contract won't encounter `underflows`. If true, the boss' hp is deducted by the player's `attack stats` minus the boss' `defense stats` multiplied by the player's critical strike. If false, the boss' hp would be set as 0, the player's `upgrade status` will be set to `true` the player will get out of the match, and the player's level will increase by 1.

First is a condition that checks whether the player's `current HP` is `greater than` the boss' `attack stats` minus the player's `defense stats` multiplied by the boss' critical strike to ensure that the smart contract won't encounter `underflows`. If true, the player's hp is deducted by the boss' `attack stats` minus the player's `defense stats` multiplied by the boss' critical strike. If false, the player's hp would be set as 0, and they will get out of the match. This will also indicate that the player was defeated.

### Reset Stats

This will call the `reset` subroutine, where it replenishes the player's and boss' HP to full and the player enters the battle to try again.

### Upgrade Stats

However, if the player defeats the boss and enters the upgrade status, they are given the chance to add `20 points` to their current stats which they can equally divide among their `Health`, `Attack`, and `Defense` stats based on their preference. First is the arguments passed by the user will be totaled and then checked if it's equal to `20` to ensure that the values entered has reached and does not exceed the upgrade points that we set per level ups.

The smart contract also checks if the player's current upgrade status is set to true, and if they are not currently inside a match. To make sure that the player really is eligible for a stat upgrade.

Once those are met, the values of the stats are subsequently added into their respective states and the player's upgrade status is set to false.

And the player can then proceed by choosing to fight the next boss.

## Frontend 

Here's the [link](https://github.com/rbjamaca/pyteal-minigame-frontend) to the dApp's frontend.

## Demo

Here's a [video recording](https://drive.google.com/file/d/1Ge7zA-Hh-pm_73wtl7JKeRwSADdsyjC3/view?usp=sharing) demonstrating the user's interactions with the dApp.

[![IMAGE ALT TEXT HERE](https://user-images.githubusercontent.com/58159983/204121220-7d4ddbf1-d255-4bae-8842-2e81f2fe8cdf.png)](https://drive.google.com/file/d/1Ge7zA-Hh-pm_73wtl7JKeRwSADdsyjC3/view?usp=sharing)

Here is the [demo link](https://pyteal-minigame-frontend-rbjamaca.vercel.app/) hosted in vercel to try it out.
