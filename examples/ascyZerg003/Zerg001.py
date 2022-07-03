import random

import sc2
from sc2 import Race, Difficulty, maps, run_game
from sc2.constants import *
from sc2.player import Bot, Computer, Player
#from micros import micros as micros

class ZergBot(sc2.BotAI):
    def __init__(self):
        self.actions_count = 0
        self.not_end_fl = True
        self.gather_gas = False
        self.workers_on_gas = False

        self.enemy_expand_loc = []# базы отсортированные по расстоянию от противника [0] = base
        self.ally_expand_loc = []# базы отсортированные по расстоянию от нашего старта [0] = base

        self.Scout_Ovik = 0 #развед овик tag
        self.Scout_Ovik_Found = 0 #про экспанды противника
        self.if_enemy_workers_scout = 0 # рабочие разведчики или пушеры
        self.enemy_wall = 0 # наличие стенки на мейне
        self.enemy_base1 = 0 # наличие natural
        self.enemy_base2 = 0# наличие второго экспанда
        self.enemy_base0 = 0# статус базы
        self.point_of_grouping = 0#точка группирвки
        self.protocol_scout_all = 0
        self.protocol_trade_face = 0
        self.engage_muta = 0
        self.upgradecountArmor = 0
        self.upgradecountWeapon = 0
        self.LAIR = 0

        self.rampEnWall = None # ramp of enemy
        self.d1 = None  # клетка с крайним бараком
        self.d2 = None      # клетка с крайним бараком
        self.d3 = None   # клетка с центральным бараком   

        self.main_structures = {NEXUS, COMMANDCENTER, HATCHERY, HIVE, LAIR, ORBITALCOMMAND, PLANETARYFORTRESS} 
        

        self.debug = 0
        



        

    
    async def on_step(self, iteration):
        self.debug = iteration
        if iteration == 0:
            
        # базы отсортированные по расстоянию от противника [0] = base
            for el in self.expansion_locations:
                self.enemy_expand_loc.append(el)
            self.enemy_expand_loc.sort(key=lambda pos: self.enemy_start_locations[0]._distance_squared(pos))
        # базы отсортированные по расстоянию от противника [0] = base

        # базы отсортированные по расстоянию от нашего старта [0] = base
            for el in self.expansion_locations:
                self.ally_expand_loc.append(el)
            self.ally_expand_loc.sort(key=lambda pos: self.start_location._distance_squared(pos))
        # базы отсортированные по расстоянию от нашего старта [0] = base
        
        # Локация точек рампы, где стенка
            moved = self.ally_expand_loc[0].to2.towards(self.game_info.map_center, 4)
            x = moved.x
            y = moved.y
            s_pathable = self._game_info.pathing_grid[[round(x), round(y)]] != 0
            print("location : ", s_pathable)
            
            rampes = self.game_info.map_ramps
            distant = 75
            for ramp in self.game_info.map_ramps:
                if ramp.top_center.distance_to_point2(self.enemy_expand_loc[0]) < distant:
                    self.rampEnWall = ramp
                    distant = ramp.top_center.distance_to_point2(self.enemy_expand_loc[0])
                   # print("location : ", self.rampEnWall.top_center)
            if len(self.rampEnWall.upper2_for_ramp_wall) == 2 and len(self.rampEnWall.upper)  in {2, 5}:
                depot_placement_positions = self.rampEnWall.corner_depots
                self.d1 = depot_placement_positions.pop()
                self.d2 = depot_placement_positions.pop()
                self.d3 = self.rampEnWall.depot_in_middle
            else: #убогая рампа
                self.enemy_wall = 2
            if self.rampEnWall.top_center.distance_to_point2(self.enemy_expand_loc[2])<self.rampEnWall.top_center.distance_to_point2(self.enemy_expand_loc[1]): #лечит неправильные экспанды противника
                sdfsgh = self.enemy_expand_loc[2]
                self.enemy_expand_loc[2] = self.enemy_expand_loc[1]
                self.enemy_expand_loc[1] = sdfsgh
        # Локация точек рампы, где стенка

            await self.chat_send("Strategy zerg rush")
            target =  self.enemy_expand_loc[0]
            ovlords = self.units(OVERLORD).first
            self.Scout_Ovik = ovlords.tag
            await self.do(ovlords.move(target))
            rally = await self.get_next_expansion()#self.enemy_start_locations[0].to2.towards(self.game_info.map_center, 36)
            self.point_of_grouping = rally.to2.towards(self.game_info.map_center, 10)
            hach = self.units(HATCHERY).first
            await self.do(hach(RALLY_HATCHERY_UNITS, self.point_of_grouping))

        # разведение рабов (сортим по расстоянию до газа)
            hachi = self.units(HATCHERY).first
            gas = self.state.vespene_geyser.closer_than(8.0, hachi).first
            mfs = self.state.mineral_field.closer_than(15.0, gas).closer_than(12.0, hachi)
            workers = self.units(DRONE).closer_than(15.0, gas)
            workers = workers.sorted_by_distance_to(gas)
            mfs = mfs.sorted_by_distance_to(gas)
            count = 0
            for resource in mfs:
                await self.do(workers[count].gather(resource))
                count = count + 1
                if count == 1 or count == 4 or count == 8 or count == 11:
                    await self.do(workers[count].gather(resource))
                    count = count + 1
        # разведение рабов

        await self.Ling_Rush()
        await self.Work_Manager()
        await self.Overlord_Manager()
        await self.Scout_Manager()
        await self.I_need_to_use_my_head()
        await self.Micro_QM()
# направлять рабов в начале ++
# mikro for zerglings
# понять почему не работает в нармальной скорости ++
# дрон, который идет на экспанд не должен попасть на добычу веспена ++
# снимать дронов оптимально?
# overlords manager
    async def Micro_QM(self):
        allies = self.units(ZERGLING)
        enemy = self.known_enemy_units.not_structure
        enemy = enemy.filter(lambda unit: not unit.is_flying)
        if self.protocol_trade_face == 0:
            for ally in allies:
                if enemy.exists:
                    if ally.distance_to(enemy.closest_to(ally))<9:
                        await self.do(ally.attack(enemy.closest_to(ally).position.towards(ally, -4)))#автоматически дефает раш рабочими + окружают зерлинги
                if ally.health_percentage < 0.4:
                    if enemy.exists:
                        if ally.distance_to(enemy.closest_to(ally)) < enemy.closest_to(ally).ground_range+1:
                            await self.do(ally.move(ally.position.to2.towards(enemy.closest_to(ally), -enemy.closest_to(ally).ground_range-5)))
                    if ally.is_idle:
                            await self.do(ally.move(self.point_of_grouping))
        if self.protocol_trade_face == 1:
            traget = self.enemy_expand_loc[0].to2.towards(self.game_info.map_center, -4)
            for ally in self.units(ZERGLING).closer_than(30, self.enemy_expand_loc[0]):
                if ally.position.distance_to_point2(traget)>8:
                    await self.do(ally.move(traget))
                else:
                    await self.do(ally.attack(traget))
            if self.units(ZERGLING).closer_than(30, self.enemy_expand_loc[0]).amount<6 or (enemy.filter(lambda unit: unit.type_id in {PROBE, DRONE, SCV}).amount < 5 and self.units(ZERGLING).closer_than(7, self.enemy_expand_loc[0]).exists):
                self.protocol_trade_face = 2
                self.engage_muta = 1
                await self.chat_send("Muta stuff")
            

    async def I_need_to_use_my_head(self):
        if self.units(ZERGLING).idle.amount > 15 and self.engage_muta == 0:
            target = self.known_enemy_structures.random_or(self.enemy_start_locations[0]).position
            if self.enemy_base1 == 1 and self.enemy_wall == 1:
                target = self.enemy_expand_loc[1]
                rally = await self.enemy_expand_loc[2]#self.enemy_start_locations[0].to2.towards(self.game_info.map_center, 36)
                self.point_of_grouping = rally.to2.towards(self.game_info.map_center, 5)
            if self.enemy_base1 in {2,-1,0} and self.enemy_wall == 1:
                target = self.enemy_expand_loc[1].to2.towards(self.game_info.map_center, 5)
                self.point_of_grouping = self.enemy_expand_loc[1].to2.towards(self.game_info.map_center, 5)#-----------------------------------------------------------------mutya
                self.engage_muta = 1
                await self.chat_send("Muta stuff")
            if self.enemy_wall == 0 and self.enemy_base1 in {-1,2}:
                self.protocol_trade_face = 1
                await self.chat_send("Face")
            if self.enemy_base2 == 1:
                target = self.enemy_expand_loc[2]
            if self.enemy_base0 == 2:
                if self.known_enemy_structures.exists:
                    target = self.known_enemy_structures.first.position
                else:
                    self.protocol_scout_all = 1 # поискать везде
            for zl in self.units(ZERGLING).idle:
                await self.do(zl.attack(target))
        else:
            if self.units(MUTALISK).idle.amount > 20 and self.engage_muta == 1:
                await self.chat_send("Attack!!")
                self.point_of_grouping = self.ally_expand_loc[0].to2.towards(self.game_info.map_center, 5)
                target = self.known_enemy_structures.random_or(self.enemy_start_locations[0]).position
                for mutalik in self.units(MUTALISK).idle:
                    await self.do(mutalik.attack(target))

    async def Scout_Manager(self):
        # Понять как понять есть ли стенка
        en = self.known_enemy_units
    # Main ACTivities check for third base and check for wall
        e_bases = en.filter(lambda unit: unit.type_id in self.main_structures) #хаты противника
        es = en.filter(lambda x: x.is_structure == True) #enemy structures
        if self.units.closer_than(7,self.enemy_expand_loc[1]) and not e_bases .closer_than(1, self.enemy_expand_loc[0]).exists and self.enemy_base1!=2:
            self.enemy_base1 = -1
        if not e_bases .closer_than(5, self.enemy_expand_loc[0]).exists and self.enemy_base0== 1:
            self.enemy_base0 = 2                      # Сломали базу
            self.protocol_trade_face = 2
            await self.chat_send("Enemy has no base")
        if not e_bases .closer_than(5, self.enemy_expand_loc[1]).exists and self.enemy_base1 == 1:
            self.enemy_base1 = 2                             #сломали натурал
            await self.chat_send("Enemy has no 1 expand")
        if e_bases.closer_than(5, self.enemy_expand_loc[2]).exists and self.enemy_base2 != 1:
            self.enemy_base2 = 1                            #наличие второго экспанда
            await self.chat_send("Enemy has expand")
        if not e_bases.closer_than(5, self.enemy_expand_loc[2]).exists and self.enemy_base2 == 1:
            self.enemy_base2 = 2                            #break второго экспанда
            await self.chat_send("Enemy has no expand")
        if e_bases.closer_than(5, self.enemy_expand_loc[2]).exists and self.enemy_base2 != 1:
            self.enemy_base2 = 1# 3-я база
            await self.chat_send("Town_Hall_3_Detected")
        if self.enemy_wall != 2:
            if es.closer_than(2.5, self.d1).exists and es.closer_than(2.5, self.d2).exists and es.closer_than(2.5, self.d3).exists and self.enemy_wall != 1: #стенка на рампе
                self.enemy_wall = 1
                await self.chat_send("MAIN BASE WALL DETECTED")
        if self.protocol_scout_all == 1:
            if self.units(ZERGLING).amount > 15:
                count = 0
                self.protocol_scout_all = 2
                for expa in self.enemy_expand_loc:
                    asd = self.units(ZERGLING)[count]
                    await self.do(asd.move(expa))
                    count = count + 1 
        
    # Ovik manager
        if self.Scout_Ovik_Found != -1:
            if self.units(OVERLORD).filter(lambda x: x.tag == self.Scout_Ovik).exists:
                DatOvik = self.units(OVERLORD).filter(lambda x: x.tag == self.Scout_Ovik).first
                if DatOvik.health_percentage<1 and self.Scout_Ovik_Found != 4:
                    self.Scout_Ovik_Found = 4                                #Спасение рядового овик
                    target = self.enemy_expand_loc[0].to2.towards(self.game_info.map_center, 26)
                    await self.do(DatOvik.move(target))
                    await self.chat_send("OV is under attack")
            else:
                self.Scout_Ovik_Found = -1                             #овик мёртв :()
                await self.chat_send("Scouting OVERLORD_is not with us")                # чекаем на смерть до получения развед данных или смерти   

        if (self.Scout_Ovik_Found == 2 or self.Scout_Ovik_Found == 3) and self.enemy_wall != 2:
            if es.closer_than(2.5, self.d1).exists and es.closer_than(2.5, self.d2).exists and es.closer_than(2.5, self.d3).exists and self.enemy_wall != 1: #стенка на рампе
                target = self.enemy_expand_loc[0].to2.towards(self.game_info.map_center, 26)
                self.enemy_wall = 1
                self.Scout_Ovik_Found = 5
                await self.do(DatOvik.move(target))
                await self.chat_send("MAIN BASE WALL DETECTED")

        if self.Scout_Ovik_Found == 1: 
            if e_bases.closer_than(5, self.enemy_expand_loc[1]).exists: #хаты противника
                if self.enemy_wall != 2:
                    target = self.d3.to2.towards(self.game_info.map_center, 9)
                else:
                    target = self.enemy_expand_loc[0].to2.towards(self.game_info.map_center, 26)
                self.Scout_Ovik_Found = 2                           # вторая хата, если она фейковая, то эт очень круто
                self.enemy_base1 = 1 # наличие natural
                await self.do(DatOvik.move(target))              
                await self.chat_send("Enemy expand")

            if (DatOvik.position.x- self.enemy_expand_loc[1].x)**2+(DatOvik.position.y- self.enemy_expand_loc[1].y)**2<121:
                if self.enemy_wall != 2:
                    target = self.d3.to2.towards(self.game_info.map_center, 9)
                else:
                    target = self.enemy_expand_loc[0].to2.towards(self.game_info.map_center, 26)
                await self.do(DatOvik.move(target))
                self.Scout_Ovik_Found = 3                                              # поздняя вторая, one base rabbish или чиз
                self.enemy_base1 = -1
                await self.chat_send("Enemy noexpand")

        if self.Scout_Ovik_Found == 0:                                # пока летим
            e_workers = en.filter(lambda unit: unit.type_id in {DRONE, PROBE, SCV}) # рабочие противника
            e_workers_insight = e_workers.closer_than(11, DatOvik.position).further_than(17, self.enemy_expand_loc[0]). amount # овик видит этих рабочих не около мейна противника
            if e_workers_insight > 0:
                if e_workers_insight == 1:
                    if self.if_enemy_workers_scout == 0:
                       await self.chat_send("Scouting worker_Found")
                    self.if_enemy_workers_scout = 1                                       # Развед дрон или пробка или scv  
                if e_workers_insight == 2:
                    if self.if_enemy_workers_scout != 2:
                        await self.chat_send("Probably Proxi smthng or some Cheese")
                    self.if_enemy_workers_scout = 2                                      # Раш рабочими или чиз в звз или прокси что-то
                if e_workers_insight > 2:
                    if self.if_enemy_workers_scout != 3:
                        await self.chat_send("Workers rush?")
                    self.if_enemy_workers_scout = 3                                      # Раш рабочими
            
            e_bases = en.filter(lambda unit: unit.type_id in self.main_structures) #хаты противника
            if e_bases.closer_than(5, self.enemy_expand_loc[0]).exists:
                target = self.enemy_expand_loc[1]
                await self.do(DatOvik.move(target))
                self.Scout_Ovik_Found = 1                                               # нашли первую хату
                self.enemy_base0 = 1
                await self.chat_send("Enemy base")
    # Ovik manager
        
        
    async def build_extractor(self):
        for hatchery in self.units(HATCHERY).ready:
            vaspenes = self.state.vespene_geyser.closer_than(15.0, hatchery)
            for vaspene in vaspenes:
                if not self.can_afford(EXTRACTOR):
                    break
                worker = self.select_build_worker(vaspene.position)
                if worker is None:
                    break
                if not self.units(EXTRACTOR).closer_than(1.0, vaspene).exists:
                    await self.do(worker.build(EXTRACTOR, vaspene))

    async def build_overlord(self):
        for larvae in self.units(LARVA):
            if self.supply_left < 3 and self.already_pending(OVERLORD) < 2 and self.supply_cap < 195:
                if self.can_afford(OVERLORD):
                    await self.do(larvae.train(OVERLORD))
        

    async def Overlord_Manager(self):
        if self.units(OVERLORD).ready.amount > 1:
            target = self.ally_expand_loc[0].to2.towards(self.game_info.map_center, -20)
            for ovik in self.units(OVERLORD).closer_than(5.0, self.ally_expand_loc[0]):
                await self.do(ovik.move(target))
        if self.actions_count == 23:
            for larvae in self.units(LARVA):
                if self.can_afford(OVERLORD) and self.supply_left<7 and not self.already_pending(OVERLORD):
                    await self.do(larvae.train(OVERLORD))    

    async def Work_Manager(self):
        if self.engage_muta == 0:
            if  self.gather_gas and not self.workers_on_gas:
                if self.units(EXTRACTOR).ready.exists:
                    self.workers_on_gas = True
                    mf = self.units(EXTRACTOR).first
                    workers123 = self.units(DRONE).sorted_by_distance_to(mf)
                    count = 0
                    for worker in workers123:
                        if (count < 3) and worker.is_gathering:
                            count = count + 1
                            await self.do(worker.gather(mf))
                        if count == 3:
                            self.workers_on_gas = True
        else:
            await self.distribute_workers()
            if self.supply_workers < self.townhalls.amount*22 and self.supply_workers < 80:
                if self.can_afford(DRONE) and self.units(LARVA).exists:
                    await self.do(self.units(LARVA).first.train(DRONE))
            if self.minerals > 600 and self.can_afford(HATCHERY) and not self.already_pending(HATCHERY):
                await self.expand_now()
            await self.build_extractor()
            await self.build_overlord()
    #            hachi = self.units(HATCHERY).ready.first 
     #           count = 0
      #          for worker in self.units(DRONE).closer_than(8.0, mf).further_than(1,hachi):
       #             if count < 3:
        #                count = count + 1
         #               await self.do(worker.gather(mf))
          #          if count == 3:
           #             self.workers_on_gas = True




    async def Ling_Rush(self):
        
        if self.actions_count == 23:
            if self.engage_muta == 0:
                for larvae in self.units(LARVA):
                    if self.can_afford(ZERGLING):
                        await self.do(larvae.train(ZERGLING))
            else:
                if self.units(SPIRE).ready.exists:
                    for larvae in self.units(LARVA):
                        if self.can_afford(MUTALISK):
                            await self.do(larvae.train(MUTALISK))
                    if self.upgradecountWeapon == 0:
                        if self.can_afford(RESEARCH_ZERGFLYERATTACKLEVEL1):
                            spire = self.units(SPIRE)
                            await self.do(spire.first(RESEARCH_ZERGFLYERATTACKLEVEL1))
                            self.upgradecountWeapon = 1
                    if self.already_pending_upgrade(UpgradeId.ZERGFLYERWEAPONSLEVEL1)==1 and self.already_pending_upgrade(UpgradeId.ZERGFLYERWEAPONSLEVEL2)==0:
                        if self.can_afford(RESEARCH_ZERGFLYERATTACKLEVEL2):
                            spire = self.units(SPIRE)
                            await self.do(spire.first(RESEARCH_ZERGFLYERATTACKLEVEL2))
                    if self.already_pending_upgrade(UpgradeId.ZERGFLYERWEAPONSLEVEL2)==1 and self.already_pending_upgrade(UpgradeId.ZERGFLYERWEAPONSLEVEL3)==0:
                        if self.can_afford(RESEARCH_ZERGFLYERATTACKLEVEL3):
                            spire = self.units(SPIRE)
                            await self.do(spire.first(RESEARCH_ZERGFLYERATTACKLEVEL3))
                    if self.upgradecountArmor == 0:
                        if self.can_afford(RESEARCH_ZERGFLYERARMORLEVEL1):
                            spire = self.units(SPIRE)
                            await self.do(spire.first(RESEARCH_ZERGFLYERARMORLEVEL1))
                            self.upgradecountArmor = 1
                    if self.already_pending_upgrade(UpgradeId.ZERGFLYERARMORSLEVEL1)==1 and self.already_pending_upgrade(UpgradeId.ZERGFLYERARMORSLEVEL2)==0:
                        if self.can_afford(RESEARCH_ZERGFLYERARMORLEVEL2):
                            spire = self.units(SPIRE)
                            await self.do(spire.first(RESEARCH_ZERGFLYERARMORLEVEL2))
                    if self.already_pending_upgrade(UpgradeId.ZERGFLYERARMORSLEVEL2)==1 and self.already_pending_upgrade(UpgradeId.ZERGFLYERARMORSLEVEL3)==0:
                        if self.can_afford(RESEARCH_ZERGFLYERARMORLEVEL3):
                            spire = self.units(SPIRE)
                            await self.do(spire.first(RESEARCH_ZERGFLYERARMORLEVEL3))
                if self.LAIR == 0:
                    if self.can_afford(AbilityId.UPGRADETOLAIR_LAIR):
                        hachi = self.units(HATCHERY).closest_to(self.ally_expand_loc[0])
                        await self.do(hachi(UPGRADETOLAIR_LAIR))
                        self.LAIR = 1
                else:
                    #print("Lair started")
                    if self.can_afford(SPIRE) and self.units(LAIR).ready.exists:
                       # print("can afford spire")
                        if self.units(SPIRE).amount < 1 and not self.already_pending(SPIRE):
                            hatchery = self.units(LAIR).ready.first
                            pos = hatchery.position.to2.towards(self.game_info.map_center, 5)
                            await self.build(SPIRE, near = pos)

            for queens in self.units(QUEEN).idle:
                abilities = await self.get_available_abilities(queens)
                if AbilityId.EFFECT_INJECTLARVA in abilities:
                    hatchery = self.units(HATCHERY).closer_than(20.0, queens).ready
                    for hachi in hatchery:
                        await self.do(queens(EFFECT_INJECTLARVA, hachi))
                        await self.do(hachi(RALLY_HATCHERY_UNITS, self.point_of_grouping))

        if self.actions_count == 22:
            self.not_end_fl = True
            if self.can_afford(QUEEN):
                hatchery = self.units(HATCHERY).ready.first
                await self.do(hatchery.train(QUEEN))
                self.actions_count = 23 #17                    
                self.not_end_fl = False

        if self.actions_count == 21:
            self.not_end_fl = True
            if self.units(QUEEN).idle.exists:
                queens = self.units(QUEEN).idle.first
                target = self.units(HATCHERY).furthest_to(queens).position
                await self.do(queens.move(target))
                self.actions_count = 22

        if self.actions_count == 20:
            self.not_end_fl = True
            if self.units(QUEEN).idle.exists:
                queens = self.units(QUEEN).idle.first
                abilities = await self.get_available_abilities(queens)
                if AbilityId.EFFECT_INJECTLARVA in abilities:
                    hatchery = self.units(HATCHERY).closer_than(7.0, queens).ready.first
                    await self.do(queens(EFFECT_INJECTLARVA, hatchery))
                    self.actions_count = 21

        if self.actions_count == 19:
            if not self.not_end_fl and not self.can_afford(ZERGLING):
                self.not_end_fl = True
                self.actions_count = 20
            if self.can_afford(ZERGLING) and self.not_end_fl and self.units(LARVA).exists:
                larvae = self.units(LARVA).first
                await self.do(larvae.train(ZERGLING))
                self.not_end_fl = False
                    
        if self.actions_count == 18:
            if not self.not_end_fl and not self.can_afford(ZERGLING):
                self.not_end_fl = True
                self.actions_count = 19
            if self.can_afford(ZERGLING) and self.not_end_fl and self.units(LARVA).exists:
                larvae = self.units(LARVA).first
                await self.do(larvae.train(ZERGLING))
                self.not_end_fl = False

        if self.actions_count == 17:                                     #+
            if not self.not_end_fl and not self.can_afford(ZERGLING):
                self.not_end_fl = True
                self.actions_count = 18
            if self.can_afford(ZERGLING) and self.not_end_fl and self.units(LARVA).exists:
                larvae = self.units(LARVA).first
                await self.do(larvae.train(ZERGLING))
                self.not_end_fl = False
                

        if self.actions_count == 16:                                     #+
            if not self.not_end_fl and self.already_pending(OVERLORD):
                self.actions_count = 17 #17
                self.not_end_fl = True
            if self.not_end_fl:
                if self.can_afford(OVERLORD):
                    larvae = self.units(LARVA).first
                    await self.do(larvae.train(OVERLORD))     
                    self.not_end_fl = False

        if self.actions_count == 15:                                     #+
            if not self.not_end_fl and self.already_pending_upgrade(UpgradeId.ZERGLINGMOVEMENTSPEED)>0:
                self.actions_count = 16 #17
                self.not_end_fl = True
            if self.units(SPAWNINGPOOL).ready.exists and self.can_afford(RESEARCH_ZERGLINGMETABOLICBOOST):
                sp = self.units(SPAWNINGPOOL)
                await self.do(sp.first(RESEARCH_ZERGLINGMETABOLICBOOST))
                self.not_end_fl = False

        if self.actions_count == 14:
            self.not_end_fl = True
            if self.vespene == 100:
                hatchery = self.units(HATCHERY).ready.first
                extract = self.units(EXTRACTOR).ready.first
                dist = self.units(HATCHERY).closest_distance_to(extract)
                drones = self.units(DRONE).closer_than(dist-2.7, extract)
                drone = drones.closest_to(hatchery)
                mf = self.state.mineral_field.closest_to(drone)
                await self.do(drone.gather(mf))
                self.actions_count = 15 #17

        if self.actions_count == 13:
            self.not_end_fl = True
            if self.vespene == 96:
                hatchery = self.units(HATCHERY).ready.first
                extract = self.units(EXTRACTOR).ready.first
                dist = self.units(HATCHERY).closest_distance_to(extract)
                drones = self.units(DRONE).closer_than(dist-2.7, extract)
                drone = drones.closest_to(hatchery)
                mf = self.state.mineral_field.closest_to(drone)
                await self.do(drone.gather(mf))
                self.actions_count = 14 #17

        if self.actions_count == 12:
            self.not_end_fl = True
            if self.vespene == 92:
                hatchery = self.units(HATCHERY).ready.first
                extract = self.units(EXTRACTOR).ready.first
                dist = self.units(HATCHERY).closest_distance_to(extract)
                drones = self.units(DRONE).closer_than(dist-2.7, extract)
                drone = drones.closest_to(hatchery)
                mf = self.state.mineral_field.closest_to(drone)
                await self.do(drone.gather(mf))
                self.actions_count = 13 #17

        if self.actions_count == 11:
            self.not_end_fl = True
            if self.units(SPAWNINGPOOL).ready.exists:
                if self.can_afford(QUEEN):
                    hatchery = self.units(HATCHERY).ready.first
                    await self.do(hatchery.train(QUEEN))
                    self.actions_count = 12 #17
                    self.not_end_fl = False

        if self.actions_count == 10:
            self.not_end_fl = True
            larvae = self.units(LARVA).first
            if self.not_end_fl:
                if self.can_afford(DRONE):
                    await self.do(larvae.train(DRONE))
                    self.actions_count = 11 #17
                    self.not_end_fl = False

        if self.actions_count == 9:                                     #+
            if not self.not_end_fl and self.minerals<25:
                self.actions_count = 10 #16
                self.not_end_fl = True
            if self.not_end_fl:
                if  self.can_afford(HATCHERY):
                    target = await self.get_next_expansion()
                    dron = self.units(DRONE).closest_to(target)
                    await self.do(dron.build(HATCHERY, target))
                    self.not_end_fl = False
                    

        if self.actions_count == 8: #fill the gas-----------------------------------------------------------------
            if not self.already_pending(DRONE):
                self.gather_gas = True
                self.actions_count = 9

        if self.actions_count == 7:
            egg = self.units(EGG).first
            target = await self.get_next_expansion()
            await self.do(egg(RALLY_BUILDING, target))
            self.actions_count = 8 #17

        if self.actions_count == 6:                                     #+
            if not self.not_end_fl and self.minerals<25:
                self.actions_count = 7 #17
                self.not_end_fl = True
            if self.not_end_fl:
                if self.units(LARVA).exists:
                    if self.can_afford(DRONE) and self.minerals>=50:
                        larvae = self.units(LARVA).first
                        await self.do(larvae.train(DRONE))
                        self.not_end_fl = False
            

        if self.actions_count == 5:                                     #+
            if not self.not_end_fl and self.minerals<25:
                self.actions_count = 6 #16
                self.not_end_fl = True
            if self.can_afford(SPAWNINGPOOL) and self.not_end_fl:
                if self.units(SPAWNINGPOOL).amount < 1 and not self.already_pending(SPAWNINGPOOL):
                    hatchery = self.units(HATCHERY).ready.first
                    pos = hatchery.position.to2.towards(self.game_info.map_center, 3)
                    await self.build(SPAWNINGPOOL, near = pos)
                    self.not_end_fl = False
            

        if self.actions_count == 4:                                     #+
            if not self.not_end_fl and self.minerals<70:
                self.not_end_fl = True
                self.actions_count = 5 #16
            if self.units(LARVA).exists:
                if self.not_end_fl:
                    larvae = self.units(LARVA).first
                    if self.minerals>75:
                        vaspene = self.state.vespene_geyser.closer_than(10.0, larvae).first
                        if not self.units(EXTRACTOR).closer_than(1.0, vaspene).exists and not self.already_pending(EXTRACTOR):
                            worker = self.select_build_worker(vaspene.position)
                            await self.do(worker.build(EXTRACTOR, vaspene))
                            await self.do(larvae.train(DRONE))
                            self.not_end_fl = False
            

        if self.actions_count == 3:                                     #+
            if not self.not_end_fl and self.supply_left<7:
                self.actions_count = 4 #16
                self.not_end_fl = True
            if self.units(LARVA).exists:
                if self.not_end_fl:
                    larvae = self.units(LARVA).first
                    if self.can_afford(DRONE) and self.minerals>49:
                        await self.do(larvae.train(DRONE))
                        self.not_end_fl = False

        if self.actions_count == 2:                                     #+
            if not self.not_end_fl and self.supply_left<8:
                self.actions_count = 3 #15
                self.not_end_fl = True
            if self.not_end_fl:
                larvae = self.units(LARVA).first
                if self.can_afford(DRONE) and self.minerals>49:
                    await self.do(larvae.train(DRONE))
                    self.not_end_fl = False
            
        
        if self.actions_count == 1.5:                                     #+
            if not self.not_end_fl and self.minerals<25:
                self.not_end_fl = True
                self.actions_count = 2 #14
                self.not_end_fl = True
            if self.not_end_fl:
                larvae = self.units(LARVA).first
                if self.can_afford(DRONE) and self.minerals>50:
                    await self.do(larvae.train(DRONE))
                    self.not_end_fl = False
            

        if self.actions_count == 1:                                      #+
            if not self.not_end_fl and self.minerals<25:
                self.actions_count = 1.5 #13
                self.not_end_fl = True
            if self.not_end_fl:
                if self.can_afford(OVERLORD):
                    larvae = self.units(LARVA).first
                    await self.do(larvae.train(OVERLORD))     
                    self.not_end_fl = False
        
        if self.actions_count == 0:                                     #+
            if not self.not_end_fl and self.minerals<20:
                self.not_end_fl = True
                self.actions_count = 1 #13
            if self.not_end_fl:
                larvae = self.units(LARVA).first
                if self.can_afford(DRONE):
                    await self.do(larvae.train(DRONE))
                    self.not_end_fl = False
            

            




            










