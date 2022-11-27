from pyteal import *
from pyteal.ast.bytes import Bytes
from pyteal_helpers import program

UINT64_MAX = 0xFFFFFFFFFFFFFFFF

def approval():
    # locals
    local_upgrade = Bytes("upgrade_player") #int
    local_in_match = Bytes("in_match") #int

    local_level = Bytes("level") #int
    local_hp = Bytes("hp") #int

    local_health = Bytes("health") #int
    local_attack = Bytes("attack") #int
    local_defense = Bytes("defense") #int

    local_boss_hp = Bytes("local_boss_hp") #int
    local_boss_health = Bytes("local_boss_health") #int
    local_boss_attack = Bytes("local_boss_attack") #int
    local_boss_defense = Bytes("local_boss_defense") #int

    global_boss_health = Bytes("boss_health") #int
    global_boss_attack = Bytes("boss_attack") #int
    global_boss_defense = Bytes("boss_defense") #int

    op_attack = Bytes("attack_boss")
    op_upgrade = Bytes("upgrade_stats")
    op_start = Bytes("fight_boss")
    op_reset = Bytes("reset_stats")

    scratch_level = ScratchVar(TealType.uint64)
    scratch_hp = ScratchVar(TealType.uint64)
    scratch_health = ScratchVar(TealType.uint64)
    scratch_attack = ScratchVar(TealType.uint64)
    scratch_defense = ScratchVar(TealType.uint64)

    scratch_boss_hp = ScratchVar(TealType.uint64)
    scratch_boss_attack = ScratchVar(TealType.uint64)
    scratch_boss_defense = ScratchVar(TealType.uint64)

    scratch_total_stats = ScratchVar(TealType.uint64)

    gen_number = ((App.globalGet(Bytes("a"))*App.globalGet(Bytes("x")))+App.globalGet(Bytes("c")))%App.globalGet(Bytes("m"))
    rand = ScratchVar(TealType.uint64)
    crit = ScratchVar(TealType.uint64)
    boss_crit = ScratchVar(TealType.uint64)

    @Subroutine(TealType.none)
    def upgrade_stats():
        return Seq(
            # basic sanity checks
            program.check_self(
                group_size=Int(1),
                group_index=Int(0),
            ),
            program.check_rekey_zero(1),
            scratch_total_stats.store(Btoi(Txn.application_args[1]) + Btoi(Txn.application_args[2]) + Btoi(Txn.application_args[3])),
            Assert(
                And(
                    scratch_total_stats.load() == Int(20),
                    App.localGet(Int(0), local_upgrade) == Int(1),
                    App.localGet(Int(0), local_in_match) == Int(0)
                )
            ),
            scratch_health.store(App.localGet(Int(0), local_health)),
            scratch_attack.store(App.localGet(Int(0), local_attack)),
            scratch_defense.store(App.localGet(Int(0), local_defense)),
            App.localPut(Int(0), local_hp, scratch_health.load() + Btoi(Txn.application_args[1])),
            App.localPut(Int(0), local_health, scratch_health.load() + Btoi(Txn.application_args[1])),
            App.localPut(Int(0), local_attack, scratch_attack.load() + Btoi(Txn.application_args[2])),
            App.localPut(Int(0), local_defense, scratch_defense.load() + Btoi(Txn.application_args[3])),
            App.localPut(Int(0), local_upgrade, Int(0)),
            Approve(),
        )

    @Subroutine(TealType.none)
    def reset():
        return Seq(
            # basic sanity checks
            program.check_self(
                group_size=Int(1),
                group_index=Int(0),
            ),
            program.check_rekey_zero(1),
            scratch_health.store(App.localGet(Int(0), local_health)),
            App.localPut(Int(0), local_hp, scratch_health.load()),
            set_boss_stats(),
            Approve(),
        )

    @Subroutine(TealType.none)
    def set_boss_stats():
        return Seq(
            # basic sanity checks
            program.check_self(
                group_size=Int(1),
                group_index=Int(0),
            ),
            program.check_rekey_zero(1),
            Assert(
                And(
                    App.localGet(Int(0), local_upgrade) == Int(0),
                    App.localGet(Int(0), local_in_match) == Int(0)
                )
            ),
            scratch_level.store(App.localGet(Txn.sender(), local_level)),
            App.localPut(Int(0), local_boss_hp, App.globalGet(global_boss_health) + (Int(30) * scratch_level.load())),
            App.localPut(Int(0), local_boss_health, App.globalGet(global_boss_health) + (Int(30) * scratch_level.load())),
            App.localPut(Int(0), local_boss_attack, App.globalGet(global_boss_attack) + (Int(5) * scratch_level.load())),
            App.localPut(Int(0), local_boss_defense, App.globalGet(global_boss_defense) + (Int(5) * scratch_level.load())),
            App.localPut(Int(0), local_in_match, Int(1)),
            Approve(),
        )

    @Subroutine(TealType.none)
    def attack():
        return Seq(
            # basic sanity checks
            program.check_self(
                group_size=Int(1),
                group_index=Int(0),
            ),
            program.check_rekey_zero(1),
            Assert(
                And(
                    App.localGet(Int(0), local_boss_hp) > Int(0),
                    App.localGet(Int(0), local_hp) > Int(0),
                )
            ),
            scratch_boss_hp.store(App.localGet(Int(0), local_boss_hp)),
            scratch_boss_attack.store(App.localGet(Int(0), local_boss_attack)),
            scratch_boss_defense.store(App.localGet(Int(0), local_boss_defense)),
            scratch_hp.store(App.localGet(Int(0), local_hp)),
            scratch_attack.store(App.localGet(Int(0), local_attack)),
            scratch_defense.store(App.localGet(Int(0), local_defense)),
            App.globalPut(Bytes("x"), gen_number), # update random value
            rand.store(App.globalGet(Bytes("x")) % Int(4)), # reduce to four chances for crit
            If(rand.load() == Btoi(Txn.application_args[1]))
            .Then(crit.store(Int(3)))
            .ElseIf(rand.load() == Btoi(Txn.application_args[2]))
            .Then(crit.store(Int(2)))
            .Else(crit.store(Int(1))),
            If(
                rand.load() == Btoi(Txn.application_args[3]),
                boss_crit.store(Int(2)),
                boss_crit.store(Int(1))
            ),
            If(scratch_boss_hp.load() > crit.load() * scratch_attack.load() - scratch_boss_defense.load())
            .Then(
                App.localPut(Int(0), local_boss_hp, scratch_boss_hp.load() - (crit.load() * scratch_attack.load() - scratch_boss_defense.load())),
            )    
            .Else(
                Seq(
                    scratch_level.store(App.localGet(Int(0), local_level)),
                    App.localPut(Int(0), local_boss_hp, Int(0)),
                    App.localPut(Int(0), local_upgrade, Int(1)),
                    App.localPut(Int(0), local_in_match, Int(0)),
                    App.localPut(Int(0), local_level, scratch_level.load() + Int(1)),
                )
            ),
            If(scratch_hp.load() > scratch_boss_attack.load() - scratch_defense.load())
            .Then(
                App.localPut(Int(0), local_hp, scratch_hp.load() - (scratch_boss_attack.load() - scratch_defense.load())),
            )
            .Else(
                Seq(
                    App.localPut(Int(0), local_hp, Int(0)),
                    App.localPut(Int(0), local_in_match, Int(0)),
                )
            ),
            Approve(),
        )


    return program.event(
        init=Seq(
            # initial values for pseudo random generator
            App.globalPut(Bytes("a"), Int(75)),
            App.globalPut(Bytes("c"), Int(74)),
            App.globalPut(Bytes("m"), Int(65537)),
            App.globalPut(Bytes("x"), Int(28652)),
            #
            App.globalPut(global_boss_health, Int(25)),
            App.globalPut(global_boss_attack, Int(6)),
            App.globalPut(global_boss_defense, Int(0)),
            #
            Approve()
        ),
        opt_in=Seq(
            App.localPut(Int(0), local_hp, Int(45)),
            App.localPut(Int(0), local_health, Int(45)),
            App.localPut(Int(0), local_attack, Int(13)),
            App.localPut(Int(0), local_defense, Int(8)),
            App.localPut(Int(0), local_level, Int(1)),
            App.localPut(Int(0), local_upgrade, Int(0)),
            Approve(),
        ),
        no_op=Seq(
            Cond(
                [
                    Txn.application_args[0] == op_start,
                    set_boss_stats(),
                ],
                [
                    Txn.application_args[0] == op_attack,
                    attack(),
                ],
                [
                    Txn.application_args[0] == op_upgrade,
                    upgrade_stats(),
                ],
                [
                    Txn.application_args[0] == op_reset,
                    reset(),
                ],
            ),
            Reject(),
        ),
    )

def clear():
    return Approve()