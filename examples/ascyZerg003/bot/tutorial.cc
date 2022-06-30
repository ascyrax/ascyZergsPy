// ascyrax

#include <sc2api/sc2_api.h>
#include "sc2lib/sc2_lib.h"
#include "sc2utils/sc2_manage_process.h"
#include <iostream>
#include <vector>

#include "sc2api/sc2_unit_filters.h"
#include "./LadderInterface.h"

//#define std::endl std::std::endl
//#define std::cout std::std::cout
//#define std::vector std::std::vector
//#define std::string std::std::string
//#define std::pair std::std::pair
//#define std::make_pair std::std::make_pair
//#define std::unordered_map std::std::unordered_map

#include "sc2utils/sc2_arg_parser.h"

using namespace sc2;

class Bot : public Agent
{
public:
	// GAME VARIABLES

	// LOCATION AND BASES
	std::vector<Point3D> expansions;
	std::vector<Point3D> bases;
	int nBases = 0;
	Point3D base1, base2, base3, base4, base5, base6;
	Point3D opBase1, opBase2, opBase3, opBase4, opBase5, opBase6; // opponents starting base
	Point3D stagingLocation;									  // unused for now

	// UNITS AND BUILDINGS AND RESOURCES
	Units larvas, eggs, drones, overlords, zergs, queens, roaches, hydras, lurkers;
	Units hatcheries, spawningPools, extractors;
	int gameLoop = 0;
	int minerals = 0, vespene = 0;
	int maxSupply = 0, currentSupply = 0, armySupply = 0, armyCnt = 0;
	int extractorCnt = 0, spawningPoolCnt = 0, hatcheryCnt = 0;
	int overlordCnt = 0, droneCnt = 0, larvaCnt = 0, eggCnt = 0;

	// MISCELLANEOUS
	std::vector<UpgradeID> upgrades;

	// EARLY_A
	bool overlord14Trained = false; // build an overlord at 14 supply
	bool firstOverlordScoutSent = false;
	bool overlord2Sent = false;
	const Unit *naturalDrone;	   // drone used to build natural
	bool naturalDroneSent = false; // whether natural drone is sent towards the natural at 200 mineral mark or not.
	const Unit *overlord1;
	const Unit *overlord2;

	// EARLY_B
	int spineCrawlerCnt = 0, sporeCrawlerCnt = 0, lairCnt = 0, hiveCnt = 0,
		roachWarrenCnt = 0, hydraDenCnt = 0, evoChamberCnt = 0, queenCnt = 0;
	Units spineCrawlers, sporeCrawlers, roachWarrens, hydraDens, lairs, hives, evoChambers;
	bool zergTimingAttackSent = false;

	// EARLY_C
	Units injectorQueens, creepQueens;
	int injectorQueenCnt = 0, creepQueenCnt = 0;
	bool roachTimingAttack1Sent = false;
	int roachCnt = 0;

	Units infestPits;
	int infestPitCnt = 0;

	// EARLY_D
	bool roachHydraTimingAttack1Sent = false;
	// EARLY_E
	bool roachHydraTimingAttack2Sent = false;
	// EARLY_F
	bool roachHydraTimingAttack3Sent = false;
	// EARLY_G
	bool roachHydraTimingAttack4Sent = false;

	virtual void OnGameStart() final
	{
		std::cout << std::endl
				  << std::endl
				  << "HELLO ASCYRAX..................................................." << std::endl
				  << std::endl;

		if (!Observation())
		{
			return;
		}

		// std::cout << "checking and caching the possible expansions." << std::endl;
		expansions = search::CalculateExpansionLocations(Observation(), Query());

		// getting all the bases
		// std::cout << "getting all the bases." << std::endl;
		getBases();
		getValues();
	}

	virtual void OnUnitIdle(const Unit *unit)
	{
		; // do nothing for now
	}

	virtual void OnUnitCreated(const Unit *unit)
	{
		// std::cout << "A " << UnitTypeToName(unit->unit_type) << " was created during gameLoop: "<<gameLoop<<"." << std::endl;
	}

	virtual void OnGameEnd()
	{
		std::cout << std::endl
				  << std::endl
				  << "BYE ASCYRAX....................................................." << std::endl
				  << std::endl;
	}

	// coordinator.update() forwards the game by a certain amount of game steps
	// after a step is completed, an observation is received => client events are run
	// Our OnStep function is run after the client events.

	void getBases()
	{
		base1 = Observation()->GetStartLocation();

		std::vector<std::pair<double, int>> v;
		for (int i = 0; i < expansions.size(); i++)
		{
			if (expansions[i].x == 0 && expansions[i].y == 0)
				continue;
			double dist = Distance2D(base1, expansions[i]);
			v.push_back(std::make_pair(dist, i));
		}

		sort(v.begin(), v.end());

		for (auto el : v)
			bases.push_back(expansions[el.second]);
		nBases = bases.size();
		base2 = bases[0];
		base3 = bases[1];
		base4 = bases[2];
		base5 = bases[3];
		base6 = bases[4];
		opBase1 = bases[nBases - 1];
		opBase2 = bases[nBases - 2];
		opBase3 = bases[nBases - 3];
		opBase4 = bases[nBases - 4];
		opBase5 = bases[nBases - 5];
		opBase6 = bases[nBases - 6];
	}

	void getValues()
	{
		gameLoop = Observation()->GetGameLoop();

		minerals = Observation()->GetMinerals();
		vespene = Observation()->GetVespene();

		maxSupply = Observation()->GetFoodCap();
		currentSupply = Observation()->GetFoodUsed();
		armySupply = Observation()->GetFoodArmy();
		armyCnt = Observation()->GetArmyCount();

		overlords = getUnits(UNIT_TYPEID::ZERG_OVERLORD);
		drones = getUnits(UNIT_TYPEID::ZERG_DRONE);
		hatcheries = getUnits(UNIT_TYPEID::ZERG_HATCHERY);
		larvas = getUnits(UNIT_TYPEID::ZERG_LARVA);
		eggs = getUnits(UNIT_TYPEID::ZERG_EGG);

		droneCnt = drones.size();
		overlordCnt = overlords.size();
		hatcheryCnt = hatcheries.size();
		larvaCnt = larvas.size();
		eggCnt = eggs.size();

		lairs = getUnits(UNIT_TYPEID::ZERG_LAIR);
		lairCnt = lairs.size();
		for (auto el : hatcheries)
		{
			if (!el->orders.empty())
			{
				if (el->orders.front().ability_id == ABILITY_ID::MORPH_LAIR)
					lairCnt++;
			}
		}
		hives = getUnits(UNIT_TYPEID::ZERG_HIVE);
		hiveCnt = hives.size();
		for (auto el : lairs)
		{
			if (!el->orders.empty())
			{
				if (el->orders.front().ability_id == ABILITY_ID::MORPH_HIVE)
					hiveCnt++;
			}
		}

		// conting the drones which are still egg
		for (auto el : eggs)
		{
			if (!el->orders.empty())
			{
				if (el->orders.front().ability_id == ABILITY_ID::TRAIN_DRONE)
					droneCnt++;
			}
		}

		// counting the overlords which are still egg
		for (auto el : eggs)
		{
			if (!el->orders.empty())
			{
				if (el->orders.front().ability_id == ABILITY_ID::TRAIN_OVERLORD)
					overlordCnt++;
			}
		}

		upgrades = Observation()->GetUpgrades();
		spawningPools = getUnits(UNIT_TYPEID::ZERG_SPAWNINGPOOL);
		spawningPoolCnt = spawningPools.size();
		roachWarrens = getUnits(UNIT_TYPEID::ZERG_ROACHWARREN);
		roachWarrenCnt = roachWarrens.size();
		evoChambers = getUnits(UNIT_TYPEID::ZERG_EVOLUTIONCHAMBER);
		evoChamberCnt = evoChambers.size();
		hydraDens = getUnits(UNIT_TYPEID::ZERG_HYDRALISKDEN);
		hydraDenCnt = hydraDens.size();
		extractors = getUnits(UNIT_TYPEID::ZERG_EXTRACTOR);
		extractorCnt = extractors.size();

		// EARLY_B
		spineCrawlers = getUnits(UNIT_TYPEID::ZERG_SPINECRAWLER);
		spineCrawlerCnt = spineCrawlers.size();

		sporeCrawlers = getUnits(UNIT_TYPEID::ZERG_SPORECRAWLER);
		sporeCrawlerCnt = sporeCrawlers.size();

		queens = getUnits(UNIT_TYPEID::ZERG_QUEEN);
		queenCnt = queens.size();
		// townhall is training queens -> queenCnt++
		Units townHalls = Observation()->GetUnits(Unit::Alliance::Self, IsTownHall());
		for (auto &el : townHalls)
		{
			if (!el->orders.empty())
			{
				if (el->orders.front().ability_id == ABILITY_ID::TRAIN_QUEEN)
				{
					queenCnt++;
				}
			}
		}

		// EARLY_C

		infestPits = getUnits(UNIT_TYPEID::ZERG_INFESTATIONPIT);
		infestPitCnt = infestPits.size();
	}

	Units getUnits(UNIT_TYPEID unitType)
	{
		return Observation()->GetUnits(Unit::Alliance::Self, IsUnit(unitType));
	}

	bool trainDrone()
	{
		getValues();
		if (larvaCnt == 0)
			return false;
		// Units larvas = getUnits(UNIT_TYPEID::ZERG_LARVA);
		Actions()->UnitCommand(GetRandomEntry(larvas), ABILITY_ID::TRAIN_DRONE);
		getValues();
		return true;
	}

	bool trainOverlord()
	{
		getValues();
		if (larvaCnt == 0)
			return false;
		Actions()->UnitCommand(GetRandomEntry(larvas), ABILITY_ID::TRAIN_OVERLORD);
		getValues();
		return true;
	}

	bool trainQueen()
	{
		// Units townHalls = Observation()->GetUnits(Unit::Alliance::Self, IsTownHall());

		if (hiveCnt > 0)
		{
			for (auto &hive : hives)
			{
				if (hive->orders.empty())
				{
					Actions()->UnitCommand(hive, ABILITY_ID::TRAIN_QUEEN);
					return true;
				}
			}
		}

		if (lairCnt > 0)
		{
			for (auto &lair : lairs)
			{
				if (lair->orders.empty())
				{
					Actions()->UnitCommand(lair, ABILITY_ID::TRAIN_QUEEN);
					return true;
				}
			}
		}

		if (hatcheryCnt > 0)
		{
			for (auto &hatchery : hatcheries)
			{
				if (hatchery->orders.empty())
				{
					Actions()->UnitCommand(hatchery, ABILITY_ID::TRAIN_QUEEN);
					return true;
				}
			}
		}

		return false;
	}

	bool TryBuildStructure(AbilityID ability_type_for_structure, UnitTypeID unit_type, Point2D location, Point3D base, double minDistFromTownHall, double maxDistFromTownHall, bool isExpansion = false)
	{
		const ObservationInterface *observation = Observation();
		Units workers = observation->GetUnits(Unit::Alliance::Self, IsUnit(unit_type));

		// if we have no workers Don't build
		if (workers.empty())
		{
			return false;
		}

		// Check to see if there is already a worker heading out to build it
		for (const auto &worker : workers)
		{
			for (const auto &order : worker->orders)
			{
				if (order.ability_id == ability_type_for_structure)
				{
					return false;
				}
			}
		}

		// If no worker is already building one, get a random worker to build one
		const Unit *unit = GetRandomEntry(workers);

		// Check to see if unit can make it there
		if (Query()->PathingDistance(unit, location) < 0.1f)
		{
			return false;
		}
		if (!isExpansion)
		{
			if ((Distance2D(location, Point2D(base.x, base.y)) < minDistFromTownHall) || (Distance2D(location, Point2D(base.x, base.y)) > maxDistFromTownHall))
			{
				return false;
			}
		}
		// Check to see if unit can build there
		if (Query()->Placement(ability_type_for_structure, location))
		{
			Actions()->UnitCommand(unit, ability_type_for_structure, location);
			return true;
		}
		return false;
	}

	bool TryBuildOnCreep(AbilityID ability_type_for_structure, UnitTypeID unit_type, Point3D base, double minDistFromTownHall, double maxDistFromTownHall)
	{
		// maxDistFromTownHall = max distance of the structure from the hatchery(base centre).
		// for(int i=0;i<1000;i++) {
		float rx = GetRandomScalar();
		float ry = GetRandomScalar();
		Point2D build_location = Point2D(base.x + rx * 15, base.y + ry * 15);
		// std::cout << ", build_location: " << build_location.x << " " << build_location.y;
		if (Observation()->HasCreep(build_location))
		{
			if (TryBuildStructure(ability_type_for_structure, unit_type, build_location, base, minDistFromTownHall, maxDistFromTownHall, false))
			{
				return true;
			}; // false => this is not an expansion
		}
		//}

		return false;
	}

	// EARLY_A.....EARLY_A.....EARLY_A.....EARLY_A.....EARLY_A.....EARLY_A.....EARLY_A.....EARLY_A.....EARLY_A.....
	// SCOUTING
	void scoutOpponentsNatural(const Unit *scoutingUnit)
	{
		// assuming opponent's natural is the second farthest expansion from my starting expansion
		std::cout << "1st overlord sent to opponent's natural: " << opBase2.x << " " << opBase2.y << " " << opBase2.z << std::endl;
		Actions()->UnitCommand(scoutingUnit, ABILITY_ID::SMART, opBase2);
	}

	void scoutMyNatural(const Unit *scoutingUnit)
	{
		Actions()->UnitCommand(scoutingUnit, ABILITY_ID::SMART, bases[0]);
	}

	// BUILDING

	bool buildMyNatural(const Unit *buildingUnit)
	{
		if (Query()->Placement(ABILITY_ID::BUILD_HATCHERY, bases[1], buildingUnit))
		{
			Actions()->UnitCommand(buildingUnit, ABILITY_ID::BUILD_HATCHERY, bases[0]);
			return true;
		}
		return false;
	}

	// bool buildSpawningPool(const Unit* buildingUnit, Point3D hatcheryLocation) {
	//     return TryBuildOnCreep(ABILITY_ID::BUILD_SPAWNINGPOOL, UNIT_TYPEID::ZERG_DRONE,base1,10);
	// }

	bool buildExtractor(Point3D targetHatcheryLocation)
	{
		if (drones.size() == 0)
			return false;
		// return back if a drone has already been given the order
		for (auto drone : drones)
		{
			if (!drone->orders.empty())
			{
				for (auto order : drone->orders)
				{
					if (order.ability_id == ABILITY_ID::BUILD_EXTRACTOR)
					{
						return false; // since order already given.
					}
				}
			}
		}
		const Unit *buildingUnit = GetRandomEntry(drones);
		// find the closest geyser(neutral unit) to the target base and build on it.
		Units geysers = Observation()->GetUnits(Unit::Alliance::Neutral, IsGeyser());

		if (geysers.size() == 0)
			return false;

		double minDist = 1e9;
		const Unit *closestVespeneGeyser;
		for (const Unit *el : geysers)
		{
			if (Query()->Placement(ABILITY_ID::BUILD_EXTRACTOR, el->pos, buildingUnit))
			{
				double dist = Distance2D(el->pos, targetHatcheryLocation);
				if (dist < minDist)
				{
					minDist = dist;
					closestVespeneGeyser = el;
				}
			}
		}
		if (Query()->Placement(ABILITY_ID::BUILD_EXTRACTOR, closestVespeneGeyser->pos, buildingUnit))
		{
			Actions()->UnitCommand(buildingUnit, ABILITY_ID::BUILD_EXTRACTOR, closestVespeneGeyser);
			return true;
		}
		return false;
	}

	// EARLY_A.....EARLY_A.....EARLY_A.....EARLY_A.....EARLY_A.....EARLY_A.....EARLY_A.....EARLY_A.....EARLY_A.....

	const Unit *FindNearestMineralPatch(const Point2D &start)
	{
		Units units = Observation()->GetUnits(Unit::Alliance::Neutral);
		float distance = std::numeric_limits<float>::max();
		const Unit *target = nullptr;
		for (const auto &u : units)
		{
			if (u->unit_type == UNIT_TYPEID::NEUTRAL_MINERALFIELD)
			{
				float d = DistanceSquared2D(u->pos, start);
				if (d < distance)
				{
					distance = d;
					target = u;
				}
			}
		}
		// If we never found one return false;
		if (distance == std::numeric_limits<float>::max())
		{
			return target;
		}
		return target;
	}

	// Mine the nearest mineral to Town hall.
	// If we don't do this, probes may mine from other patches if they stray too far from the base after building.
	void MineIdleWorkers(const Unit *worker, AbilityID worker_gather_command, UnitTypeID vespene_building_type)
	{
		Units townHalls = Observation()->GetUnits(Unit::Alliance::Self, IsTownHall());
		Units geysers = Observation()->GetUnits(Unit::Alliance::Self, IsUnit(vespene_building_type));

		const Unit *valid_mineral_patch = nullptr;

		if (townHalls.empty())
		{
			return;
		}

		// Search for a base that is missing workers.
		for (const auto &base : townHalls)
		{
			// If we have already mined out here skip the base.
			if (base->ideal_harvesters == 0 || base->build_progress != 1)
			{
				continue;
			}
			if (base->assigned_harvesters < base->ideal_harvesters)
			{
				valid_mineral_patch = FindNearestMineralPatch(base->pos);
				Actions()->UnitCommand(worker, worker_gather_command, valid_mineral_patch);
				return;
			}
		}

		for (const auto &geyser : geysers)
		{
			if (geyser->assigned_harvesters < geyser->ideal_harvesters)
			{
				Actions()->UnitCommand(worker, worker_gather_command, geyser);
				return;
			}
		}

		if (!worker->orders.empty())
		{
			return;
		}

		// If all workers are spots are filled just go to any base.
		const Unit *random_base = GetRandomEntry(townHalls);
		valid_mineral_patch = FindNearestMineralPatch(random_base->pos);
		Actions()->UnitCommand(worker, worker_gather_command, valid_mineral_patch);
	}

	// To ensure that we do not over or under saturate any base.
	void ManageWorkers(UNIT_TYPEID worker_type, AbilityID worker_gather_command, UNIT_TYPEID vespene_building_type)
	{
		const ObservationInterface *observation = Observation();
		Units townHalls = observation->GetUnits(Unit::Alliance::Self, IsTownHall());
		Units geysers = observation->GetUnits(Unit::Alliance::Self, IsUnit(vespene_building_type));

		// if any idle worker found -> manage it.
		Units workers = Observation()->GetUnits(Unit::Alliance::Self, IsUnit(UNIT_TYPEID::ZERG_DRONE));

		for (const auto &worker : workers)
		{
			if (worker->orders.empty())
			{
				MineIdleWorkers(worker, worker_gather_command, vespene_building_type);
			}
		}

		if (townHalls.empty())
		{
			return;
		}

		for (const auto &base : townHalls)
		{
			// If we have already mined out or still building here skip the base.
			if (base->ideal_harvesters == 0 || base->build_progress != 1)
			{
				continue;
			}
			// if base is
			if (base->assigned_harvesters > base->ideal_harvesters)
			{
				Units workers = observation->GetUnits(Unit::Alliance::Self, IsUnit(worker_type));

				for (const auto &worker : workers)
				{
					if (!worker->orders.empty())
					{
						// if this worker belong to this base
						if (worker->orders.front().target_unit_tag == base->tag)
						{
							// This should allow them to be picked up by mineidleworkers()
							MineIdleWorkers(worker, worker_gather_command, vespene_building_type);
							return;
						}
					}
					else if (worker->orders.empty())
					{
						// idle worker
						MineIdleWorkers(worker, worker_gather_command, vespene_building_type);
					}
				}
			}
			/*else if (base->assigned_harvesters < base->ideal_harvesters) {
				Units workers = Observation()->GetUnits(Unit::Alliance::Self, IsUnit(UNIT_TYPEID::ZERG_DRONE));

				for (const auto& worker : workers) {
					if (worker->orders.empty()) {
						MineIdleWorkers(worker, worker_gather_command, vespene_building_type);
					}
				}
			}*/
		}
		workers = observation->GetUnits(Unit::Alliance::Self, IsUnit(worker_type));
		for (const auto &geyser : geysers)
		{
			if (geyser->ideal_harvesters == 0 || geyser->build_progress != 1)
			{
				continue;
			}
			if (geyser->assigned_harvesters > geyser->ideal_harvesters)
			{
				for (const auto &worker : workers)
				{
					if (!worker->orders.empty())
					{
						if (worker->orders.front().target_unit_tag == geyser->tag)
						{
							// This should allow them to be picked up by mineidleworkers()
							MineIdleWorkers(worker, worker_gather_command, vespene_building_type);
							return;
						}
					}
					else if (worker->orders.empty())
					{
						MineIdleWorkers(worker, worker_gather_command, vespene_building_type);
					}
				}
			}
			// else if (geyser->assigned_harvesters < geyser->ideal_harvesters) {
			//     for (const auto& worker : workers) {
			//         if (!worker->orders.empty()) {
			//             //This should move a worker that isn't mining gas to gas
			//             const Unit* target = observation->GetUnit(worker->orders.front().target_unit_tag);
			//             if (target == nullptr) {
			//                 continue;
			//             }
			//             if (target->unit_type != vespene_building_type) {
			//                 //This should allow them to be picked up by mineidleworkers()
			//                 MineIdleWorkers(worker, worker_gather_command, vespene_building_type);
			//                 return;
			//             }
			//         }
			//         else if (worker->orders.empty())
			//             MineIdleWorkers(worker, worker_gather_command, vespene_building_type);
			//     }
			// }
		}
	}

	bool trainArmy(AbilityID abilId, UnitTypeID unitId)
	{
		Units targetUnits = getUnits(unitId);
		if (targetUnits.size() == 0)
			return false;
		Actions()->UnitCommand(GetRandomEntry(targetUnits), abilId);
		return true;
	}

	bool saturateDrones(int nBases)
	{
		Units townHalls = Observation()->GetUnits(Unit::Alliance::Self, IsTownHall());
		Units geysers = Observation()->GetUnits(Unit::Alliance::Self, IsUnit(UNIT_TYPEID::ZERG_EXTRACTOR));
		int idealDroneCnt = 0;
		for (int i = 0; i < std::min((int)townHalls.size(), nBases); i++)
		{
			if (townHalls[i]->build_progress != 1)
				continue;
			idealDroneCnt += townHalls[i]->ideal_harvesters;
		}
		for (int i = 0; i < std::min((int)geysers.size(), 2 * nBases); i++)
		{
			if (geysers[i]->build_progress != 1)
				continue;
			idealDroneCnt += geysers[i]->ideal_harvesters;
		}
		// std::cout << droneCnt << " " << idealDroneCnt << std::endl;
		if (droneCnt < idealDroneCnt)
		{
			trainDrone();
			return false; // not saturated yet.
		}
		else
			return true; // saturated
						 // std::cout << townHalls.size() << " " << geysers.size() << " " << idealDroneCnt << std::endl;
	}

	bool saturateGeysers(int nBases)
	{
		Units townHalls = Observation()->GetUnits(Unit::Alliance::Self, IsTownHall());
		Units geysers = Observation()->GetUnits(Unit::Alliance::Self, IsUnit(UNIT_TYPEID::ZERG_EXTRACTOR));

		if (geysers.size() < nBases * 2)
		{
			buildExtractor(base1);
			return false;
		}
		else
			return true;
	}

	void manageOverlords()
	{
		// eggs was last calculated in the getValues function
		int overlordEggs = 0; // overlords on the way.
		for (auto &egg : eggs)
		{
			if (!egg->orders.empty())
			{
				if (egg->orders.front().ability_id == ABILITY_ID::TRAIN_OVERLORD)
				{
					overlordEggs++;
				}
			}
		}

		if ((maxSupply + overlordEggs * 8 - currentSupply) < 5 * (1 + maxSupply / 30))
			trainOverlord();
	}

	bool manageQueens()
	{
		Units townHalls = Observation()->GetUnits(Unit::Alliance::Self, IsTownHall());
		Units geysers = Observation()->GetUnits(Unit::Alliance::Self, IsUnit(UNIT_TYPEID::ZERG_EXTRACTOR));
		int idealQueenCnt = 0;
		for (int i = 0; i < std::min((int)townHalls.size(), nBases); i++)
		{
			if (townHalls[i]->build_progress != 1)
				continue;
			idealQueenCnt += 3;
		}

		if (queenCnt < idealQueenCnt)
		{
			trainQueen();
			return false; // not saturated yet.
		}
		else
			return true; // saturated
	}

	void tryInjectLarva()
	{
		Units townHalls = Observation()->GetUnits(Unit::Alliance::Self, IsTownHall());

		injectorQueens.clear();
		creepQueens.clear();

		int finishedBaseCnt = 0;
		for (auto &base : townHalls)
		{
			if (base->build_progress != 1)
				continue;
			finishedBaseCnt++;
		}

		int queensInTraining = 0;
		for (auto &el : townHalls)
		{
			if (!el->orders.empty())
			{
				if (el->orders.front().ability_id == ABILITY_ID::TRAIN_QUEEN)
				{
					queensInTraining++;
				}
			}
		}

		// std::cout << "queens: "; for (auto queen : queens)std::cout << queen->tag << " "; std::cout << std::endl;
		std::vector<long long> queenTags;
		for (auto queen : queens)
		{
			queenTags.push_back(queen->tag);
		}
		sort(queenTags.begin(), queenTags.end());

		for (int i = 0; i < std::min(finishedBaseCnt, queenCnt - queensInTraining); i++)
		{
			injectorQueens.push_back(Observation()->GetUnit(queenTags[i])); // error. i have counted birthing queens too
		}
		injectorQueenCnt = injectorQueens.size();
		creepQueenCnt = (queenCnt - queensInTraining - injectorQueenCnt);
		for (int i = injectorQueenCnt; i < injectorQueenCnt + creepQueenCnt; i++)
		{
			creepQueens.push_back(Observation()->GetUnit(queenTags[i]));
		}

		// std::cout << "injectorQueens: "<<injectorQueens.size()<<" "; for (auto queen : injectorQueens)std::cout << queen->tag << " ";
		// std::cout << std::endl;

		if (injectorQueens.empty() || hatcheries.empty())
			return;
		/*int ptrTownHall = 0;
		for (int i = 0; i < injectorQueenCnt; i++) {
			for (; ptrTownHall < townHalls.size(); ptrTownHall++) {
				if (townHalls[i]->build_progress != 1)
					continue;
				else
				{
					Actions()->UnitCommand(injectorQueens[i], ABILITY_ID::EFFECT_INJECTLARVA, townHalls[ptrTownHall]);
					ptrTownHall++;
					break;
				}
			}
		}*/
		for (int i = 0; i < injectorQueenCnt; i++)
		{
			Actions()->UnitCommand(injectorQueens[i], ABILITY_ID::EFFECT_INJECTLARVA, townHalls[i]);
		}
	}

	void creepQueenPatrol()
	{
		for (auto queen : creepQueens)
		{
			if (queen->orders.empty())
			{
				Actions()->UnitCommand(creepQueens, ABILITY_ID::GENERAL_PATROL, bases[std::max(0, hatcheryCnt + lairCnt + hiveCnt - 2)]);
			}
			if (queen->energy >= 75)
			{
				Actions()->UnitCommand(queen, ABILITY_ID::BUILD_CREEPTUMOR, queen->pos);
				// Actions()->UnitCommand(creepQueens, ABILITY_ID::BUILD_CREEPTUMOR, creepTumorLocation);
			}
		}
	}

	// first zergling only timing attack
	void manageZergAttack()
	{
		Units enemyUnits = Observation()->GetUnits(Unit::Alliance::Enemy);

		Units armyUnits = Observation()->GetUnits(Unit::Alliance::Enemy);
		for (auto armyUnit : armyUnits)
		{
			if (!armyUnit->orders.empty())
				if (armyUnit->orders.front().ability_id == ABILITY_ID::ATTACK)
				{
					Actions()->UnitCommand(armyUnit, ABILITY_ID::ATTACK, enemyUnits.front()->pos);
				}
		}
	}

	void TryExpand()
	{
		// std::cout << "trying to expand: " << gameLoop << std::endl;
		Units townHalls = Observation()->GetUnits(Unit::Alliance::Self, IsTownHall());
		if (drones.size() > 0)
		{
			Actions()->UnitCommand(GetRandomEntry(drones), ABILITY_ID::BUILD_HATCHERY, bases[std::max((int)townHalls.size() - 1, 0)]);
			// std::cout << drones.size() << std::endl;;
		}
	}

	void buildLair()
	{
		if (queenCnt >= 2 && lairCnt + hiveCnt == 0)
		{
			if (hatcheries.size() > 0)
				Actions()->UnitCommand(hatcheries[0], ABILITY_ID::MORPH_LAIR);
		}
	}

	void buildHive()
	{
		if (hiveCnt == 0)
		{
			if (infestPitCnt == 0)
			{
				if (drones.size() > 0)
					TryBuildOnCreep(ABILITY_ID::BUILD_INFESTATIONPIT, UNIT_TYPEID::ZERG_DRONE, base1, 7, 10);
				return;
			}
			else if (infestPits[0]->build_progress != 1)
				return;

			if (lairs.size() > 0)
				Actions()->UnitCommand(lairs[0], ABILITY_ID::MORPH_HIVE);
		}
	}

	void earlyA()
	{
		// rally townHall units to base2.
		if (hatcheries.size() > 0)
			Actions()->UnitCommand(hatcheries, ABILITY_ID::RALLY_UNITS, base2);
		if (lairs.size() > 0)
			Actions()->UnitCommand(lairs, ABILITY_ID::RALLY_UNITS, base2);
		if (hives.size() > 0)
			Actions()->UnitCommand(hives, ABILITY_ID::RALLY_UNITS, base2);

		// std::cout << "droneCnt:  " << droneCnt << std::endl;
		//  send 1st overlord as scout to opponent's natural
		if (!firstOverlordScoutSent && overlords.size() >= 1)
		{
			overlord1 = overlords[0];
			scoutOpponentsNatural(overlord1);
			firstOverlordScoutSent = true;
		}
		// send 2nd overlord to my natural
		if (!overlord2Sent && overlords.size() == 2)
		{
			for (auto el : overlords)
			{
				if (el == overlord1)
					continue;
				else
				{
					overlord2 = el;
					break;
				}
			}
			scoutMyNatural(overlord2);
			overlord2Sent = true;
		}

		if (hatcheryCnt == 1)
		{
			// build drone as soon as the game starts
			if (droneCnt < 13)
			{
				if (minerals >= 50)
					trainDrone();
				return;
			}

			// build an overlord next
			if (overlordCnt == 1)
			{
				// get a larva
				if (minerals >= 100)
					trainOverlord();
				return;
			}
			if (overlordCnt == 2 && maxSupply == 14 && droneCnt == 13)
			{
				if (minerals >= 50)
					trainDrone();
			}

			// draw drones till 16
			if (overlordCnt == 2 && maxSupply == 22 && droneCnt < 16)
			{
				if (minerals >= 50)
					trainDrone();
				return;
			}

			// expansion time

			// move towards to the natural at 200 mineral mark
			if (droneCnt == 16 && minerals >= 160 && !naturalDroneSent)
			{
				// get a drone to build the hatchery at natural
				naturalDrone = drones[0];
				scoutMyNatural(naturalDrone);
				naturalDroneSent = true;
				return;
			}
			// build the natural at 300 mineral mark
			if (minerals >= 300)
			{
				buildMyNatural(naturalDrone);
				return;
			}
		}
		else if (hatcheryCnt == 2)
		{
			if (droneCnt < 18)
			{
				if (minerals >= 50)
					trainDrone();
				return;
			}

			// hatchery==2 && droneCnt==18
			if (spawningPoolCnt == 0)
			{
				if (minerals >= 150 && TryBuildOnCreep(ABILITY_ID::BUILD_SPAWNINGPOOL, UNIT_TYPEID::ZERG_DRONE, base1, 7, 12))
					;
				return;
			}

			if (spawningPoolCnt == 1 && droneCnt < 20)
			{
				if (minerals >= 50)
					trainDrone();
				return;
			}

			if (extractorCnt == 0)
			{
				if (minerals >= 30 && buildExtractor(base1))
					;
				return;
			}
		}

		// EARLY_A PHASE OF VIBE'S ZERG BUILD ENDS.
	}

	void earlyB()
	{

		if (queens.size() >= 2)
		{
			if (lairCnt + hiveCnt == 0)
			{
				buildLair();
				return;
			}
		}

		manageOverlords();

		if (droneCnt < 20)
		{
			trainDrone();
			return;
		}
		// build 1 spine crawler at my natural.
		if (spineCrawlerCnt == 0)
		{
			TryBuildOnCreep(ABILITY_ID::BUILD_SPINECRAWLER, UNIT_TYPEID::ZERG_DRONE, base2, 2, 5);
		}

		// currentSupply = 10
		if (!zergTimingAttackSent)
		{
			if (armySupply - queenCnt * 2 <= 15)
			{
				manageOverlords();
				trainArmy(ABILITY_ID::TRAIN_ZERGLING, UNIT_TYPEID::ZERG_LARVA);
				return;
			}
		}

		// armySupply except queens >=15
		// if all the zergs have finished training, then only send this attack
		int zergEggs = 0; // zergs which are still being trained
		for (auto &egg : eggs)
		{
			if (!egg->orders.empty())
			{
				if (egg->orders.front().ability_id == ABILITY_ID::TRAIN_ZERGLING)
				{
					zergEggs++;
				}
			}
		}
		if (!zergTimingAttackSent && armySupply - queenCnt * 2 >= 16 && zergEggs == 0)
		{
			std::cout << std::endl;
			std::cout << "ZERG TIMING ATTACK 1 SENT : " << gameLoop << std::endl;
			std::cout << "zergSupply: " << armySupply - 2 * queenCnt << std::endl;
			std::cout << "queenCnt : " << queenCnt << std::endl;
			// std::cout << "armyCnt: " << armyCnt << std::endl;
			// std::cout << "armySupply: " << armySupply << std::endl;

			Units zerglings = getUnits(UNIT_TYPEID::ZERG_ZERGLING);

			if (zerglings.size() > 0)
				Actions()->UnitCommand(zerglings, ABILITY_ID::ATTACK, opBase1);

			zergTimingAttackSent = true;
		}

		if (zergTimingAttackSent)
		{
			if (roachWarrenCnt == 0)
			{
				TryBuildOnCreep(ABILITY_ID::BUILD_ROACHWARREN, UNIT_TYPEID::ZERG_DRONE, base1, 7, 12);
			}
			// if (saturateDrones(2)) {
			//     saturateGeysers(2);
			// }
		}
	}

	void earlyC()
	{

		if (queens.size() >= 2)
		{
			if (lairCnt + hiveCnt == 0)
			{
				buildLair();
				return;
			}
		}

		// ENTERED AFTER ROACH WARREN COUNT = 1.

		// if 2 bases could not get saturated in the earlyB phase.
		if (saturateDrones(2))
		{
			if (saturateGeysers(2))
			{
				if (hatcheries.size() + lairs.size() + hives.size() <= 2)
					TryExpand();
			}
		}
		else
			return; // until the 2nd base gets fully saturated. dont do anything else.

		if (roachWarrens[0]->build_progress == 1)
		{
			// since 2 bases are saturated
			if (!roachTimingAttack1Sent)
			{
				if (armySupply - queenCnt * 2 < 50)
					trainArmy(ABILITY_ID::TRAIN_ROACH, UNIT_TYPEID::ZERG_LARVA);
			}
		}

		// if all the roaches have finished training, then only send this attack
		int roachEggs = 0; // roaches which are still being trained
		for (auto &egg : eggs)
		{
			if (!egg->orders.empty())
			{
				if (egg->orders.front().ability_id == ABILITY_ID::TRAIN_ROACH)
				{
					roachEggs++;
				}
			}
		}
		if (!roachTimingAttack1Sent && armySupply - queenCnt * 2 >= 50 && roachEggs == 0)
		{
			std::cout << std::endl;
			std::cout << "ROACH TIMING ATTACK 1 SENT: " << gameLoop << std::endl;
			std::cout << "roachSupply: " << armySupply - 2 * queenCnt << std::endl;
			std::cout << "queenCnt : " << queenCnt << std::endl;
			// std::cout << "armyCnt: " << armyCnt << std::endl;
			// std::cout << "armySupply: " << armySupply << std::endl;

			Units roaches = Observation()->GetUnits(Unit::Alliance::Self, IsUnit(UNIT_TYPEID::ZERG_ROACH));
			Units zerglings = getUnits(UNIT_TYPEID::ZERG_ZERGLING);

			if (roaches.size() > 0)
				Actions()->UnitCommand(roaches, ABILITY_ID::ATTACK, opBase1);
			if (zerglings.size() > 0)
				Actions()->UnitCommand(zerglings, ABILITY_ID::ATTACK, opBase1);

			roachTimingAttack1Sent = true;
		}

		if (roachTimingAttack1Sent)
		{
			if (hydraDenCnt == 0)
			{
				TryBuildOnCreep(ABILITY_ID::BUILD_HYDRALISKDEN, UNIT_TYPEID::ZERG_DRONE, base1, 7, 12);
			}
			// if (saturateDrones(3)) {
			//     saturateGeysers(3);
			// }
		}
	}

	void earlyD()
	{

		if (queens.size() >= 2)
		{
			if (lairCnt + hiveCnt == 0)
			{
				buildLair();
				return;
			}
		}
		if (hiveCnt == 0)
		{
			buildHive();
			return;
		}

		// ENTERED AFTER HYDRALISK-DEN COUNT = 1.

		// if 2 bases could not get saturated in the earlyB phase.
		if (saturateDrones(3))
		{
			if (saturateGeysers(3))
			{
				if (hatcheries.size() + lairs.size() + hives.size() <= 2)
					TryExpand();
			}
		}
		else
			return; // until 3rd base gets full saturated. dont do anything else.

		roaches = Observation()->GetUnits(Unit::Alliance::Self, IsUnit(UNIT_TYPEID::ZERG_ROACH));
		hydras = getUnits(UNIT_TYPEID::ZERG_HYDRALISK);
		// if all the hydras have finished training, then only send this attack
		int hydraEggs = 0; // hydras which are still being trained
		for (auto &egg : eggs)
		{
			if (!egg->orders.empty())
			{
				if (egg->orders.front().ability_id == ABILITY_ID::TRAIN_HYDRALISK)
				{
					hydraEggs++;
				}
			}
		}
		// if all the roaches have finished training, then only send this attack
		int roachEggs = 0; // roaches which are still being trained
		for (auto &egg : eggs)
		{
			if (!egg->orders.empty())
			{
				if (egg->orders.front().ability_id == ABILITY_ID::TRAIN_ROACH)
				{
					roachEggs++;
				}
			}
		}

		if (hydraDens[0]->build_progress == 1)
		{
			// since 2 bases are saturated
			if (!roachHydraTimingAttack1Sent)
			{
				if (hydras.size() + hydraEggs < 20)
					trainArmy(ABILITY_ID::TRAIN_HYDRALISK, UNIT_TYPEID::ZERG_LARVA);
				if (roaches.size() + roachEggs < 15)
					trainArmy(ABILITY_ID::TRAIN_ROACH, UNIT_TYPEID::ZERG_LARVA);
			}
		}

		if (!roachHydraTimingAttack1Sent && armySupply - queenCnt * 2 >= 60 && hydraEggs == 0 && roachEggs == 0)
		{
			std::cout << std::endl;
			std::cout << "ROACH + HYDRA TIMING ATTACK 1 SENT: " << gameLoop << std::endl;
			std::cout << "roachSupply: " << roaches.size() * 2 << std::endl;
			std::cout << "hydraSupply: " << hydras.size() * 2 << std::endl;
			std::cout << "queenCnt : " << queenCnt << std::endl;
			// std::cout << "armyCnt: " << armyCnt << std::endl;
			// std::cout << "armySupply: " << armySupply << std::endl;

			roaches = Observation()->GetUnits(Unit::Alliance::Self, IsUnit(UNIT_TYPEID::ZERG_ROACH));
			hydras = getUnits(UNIT_TYPEID::ZERG_HYDRALISK);

			if (roaches.size() > 0)
				Actions()->UnitCommand(roaches, ABILITY_ID::ATTACK, opBase1);
			if (hydras.size() > 0)
				Actions()->UnitCommand(hydras, ABILITY_ID::ATTACK, opBase1);

			roachHydraTimingAttack1Sent = true;
		}
	}

	void earlyE()
	{
		if (queens.size() >= 2)
		{
			if (hiveCnt == 0)
			{
				buildHive();
				return;
			}
		}

		// ENTERED AFTER HYDRALISK-DEN COUNT = 1.

		// if 2 bases could not get saturated in the earlyB phase.
		if (saturateDrones(3))
		{
			if (saturateGeysers(3))
			{
				if (hatcheries.size() + lairs.size() + hives.size() <= 3)
					TryExpand();
			}
		}
		else
			return; // until 3rd base gets full saturated. dont do anything else.

		roaches = Observation()->GetUnits(Unit::Alliance::Self, IsUnit(UNIT_TYPEID::ZERG_ROACH));
		hydras = getUnits(UNIT_TYPEID::ZERG_HYDRALISK);
		// if all the hydras have finished training, then only send this attack
		int hydraEggs = 0; // hydras which are still being trained
		for (auto &egg : eggs)
		{
			if (!egg->orders.empty())
			{
				if (egg->orders.front().ability_id == ABILITY_ID::TRAIN_HYDRALISK)
				{
					hydraEggs++;
				}
			}
		}
		// if all the roaches have finished training, then only send this attack
		int roachEggs = 0; // roaches which are still being trained
		for (auto &egg : eggs)
		{
			if (!egg->orders.empty())
			{
				if (egg->orders.front().ability_id == ABILITY_ID::TRAIN_ROACH)
				{
					roachEggs++;
				}
			}
		}

		if (hydraDens[0]->build_progress == 1)
		{
			// since 2 bases are saturated
			if (!roachHydraTimingAttack2Sent)
			{
				if (hydras.size() + hydraEggs < 20)
					trainArmy(ABILITY_ID::TRAIN_HYDRALISK, UNIT_TYPEID::ZERG_LARVA);
				if (roaches.size() + roachEggs < 20)
					trainArmy(ABILITY_ID::TRAIN_ROACH, UNIT_TYPEID::ZERG_LARVA);
			}
		}

		if (!roachHydraTimingAttack2Sent && armySupply - queenCnt * 2 >= 70 && hydraEggs == 0 && roachEggs == 0)
		{
			std::cout << std::endl;
			std::cout << "ROACH + HYDRA TIMING ATTACK 2 SENT: " << gameLoop << std::endl;
			std::cout << "roachSupply: " << roaches.size() * 2 << std::endl;
			std::cout << "hydraSupply: " << hydras.size() * 2 << std::endl;
			std::cout << "queenCnt : " << queenCnt << std::endl;
			// std::cout << "armyCnt: " << armyCnt << std::endl;
			// std::cout << "armySupply: " << armySupply << std::endl;

			roaches = Observation()->GetUnits(Unit::Alliance::Self, IsUnit(UNIT_TYPEID::ZERG_ROACH));
			hydras = getUnits(UNIT_TYPEID::ZERG_HYDRALISK);

			if (roaches.size() > 0)
				Actions()->UnitCommand(roaches, ABILITY_ID::ATTACK, opBase1);
			if (hydras.size() > 0)
				Actions()->UnitCommand(hydras, ABILITY_ID::ATTACK, opBase1);

			roachHydraTimingAttack2Sent = true;
		}
	}

	void earlyF()
	{
		if (queens.size() >= 2)
		{
			if (hiveCnt == 0)
			{
				buildHive();
				return;
			}
		}

		// ENTERED AFTER HYDRALISK-DEN COUNT = 1.

		// if 2 bases could not get saturated in the earlyB phase.
		if (saturateDrones(4))
		{
			if (saturateGeysers(4))
			{
				if (hatcheries.size() + lairs.size() + hives.size() <= 4)
					TryExpand();
			}
		}
		else
			return; // until 3rd base gets full saturated. dont do anything else.

		roaches = Observation()->GetUnits(Unit::Alliance::Self, IsUnit(UNIT_TYPEID::ZERG_ROACH));
		hydras = getUnits(UNIT_TYPEID::ZERG_HYDRALISK);
		// if all the hydras have finished training, then only send this attack
		int hydraEggs = 0; // hydras which are still being trained
		for (auto &egg : eggs)
		{
			if (!egg->orders.empty())
			{
				if (egg->orders.front().ability_id == ABILITY_ID::TRAIN_HYDRALISK)
				{
					hydraEggs++;
				}
			}
		}
		// if all the roaches have finished training, then only send this attack
		int roachEggs = 0; // roaches which are still being trained
		for (auto &egg : eggs)
		{
			if (!egg->orders.empty())
			{
				if (egg->orders.front().ability_id == ABILITY_ID::TRAIN_ROACH)
				{
					roachEggs++;
				}
			}
		}

		if (hydraDens[0]->build_progress == 1)
		{
			// since 2 bases are saturated
			if (!roachHydraTimingAttack3Sent)
			{
				if (hydras.size() + hydraEggs < 25)
					trainArmy(ABILITY_ID::TRAIN_HYDRALISK, UNIT_TYPEID::ZERG_LARVA);
				if (roaches.size() + roachEggs < 25)
					trainArmy(ABILITY_ID::TRAIN_ROACH, UNIT_TYPEID::ZERG_LARVA);
			}
		}

		if (!roachHydraTimingAttack3Sent && armySupply - queenCnt * 2 >= 90 && hydraEggs == 0 && roachEggs == 0)
		{
			std::cout << std::endl;
			std::cout << "ROACH + HYDRA TIMING ATTACK 3 SENT: " << gameLoop << std::endl;
			std::cout << "roachSupply: " << roaches.size() * 2 << std::endl;
			std::cout << "hydraSupply: " << hydras.size() * 2 << std::endl;
			std::cout << "queenCnt : " << queenCnt << std::endl;
			// std::cout << "armyCnt: " << armyCnt << std::endl;
			// std::cout << "armySupply: " << armySupply << std::endl;

			roaches = Observation()->GetUnits(Unit::Alliance::Self, IsUnit(UNIT_TYPEID::ZERG_ROACH));
			hydras = getUnits(UNIT_TYPEID::ZERG_HYDRALISK);

			if (roaches.size() > 0)
				Actions()->UnitCommand(roaches, ABILITY_ID::ATTACK, opBase2);
			if (hydras.size() > 0)
				Actions()->UnitCommand(hydras, ABILITY_ID::ATTACK, opBase2);

			roachHydraTimingAttack3Sent = true;
		}
	}

	virtual void OnStep() final
	{
		if (!Observation())
		{
			return;
		}
		getValues();

		if (extractorCnt < 1)
		{
			earlyA();
		}
		else if (hatcheryCnt <= 2 && extractorCnt <= 4 && roachWarrenCnt == 0)
		{
			earlyB();
		}
		else if (roachWarrenCnt == 1 && hydraDenCnt == 0)
		{
			earlyC();
		}
		else if (hydraDenCnt == 1 && !roachHydraTimingAttack1Sent)
		{
			earlyD();
		}
		else if (!roachHydraTimingAttack2Sent)
		{
			earlyE();
		}
		else if (!roachHydraTimingAttack3Sent)
		{
			earlyF();
		}

		buildLair();
		if (hydraDenCnt > 0)
			buildHive();

		// buildHive();

		if (maxSupply >= 28)
			manageOverlords();

		ManageWorkers(UNIT_TYPEID::ZERG_DRONE, ABILITY_ID::HARVEST_GATHER, UNIT_TYPEID::ZERG_EXTRACTOR);

		manageQueens();

		tryInjectLarva();

		// creepQueenPatrol();

		manageZergAttack();

		// ManageUpgrades();

		return;
	}
};

// Set this flag to true if you want to play against your bot.
static bool PlayerOneIsHuman = false;

class Human : public sc2::Agent
{
public:
	void OnGameStart() final
	{
		Debug()->DebugTextOut("Human");
		Debug()->SendDebug();
	}
};

int main(int argc, char *argv[])
{
	// code taken from https://github.com/ddelamare/BotWithAPlan/blob/master/src/BotWithAPlan/Launcher.cpp

	std::cout << "inside main" << std::endl;

	bool isLadder = false;
	std::cout << "argc: " << argc << std::endl;
	for (int i = 0; i < argc; i++)
	{
		// LOG(4) << argv[i] << std::endl;
		std::cout << argv[i] << std::endl;
	}
	if (argc > 5)
		isLadder = true;

	if (isLadder)
	{
		RunBot(argc, argv, new Bot(), sc2::Race::Zerg, false, true, false);
		return 0;
	}

	// if not a ladder match. eg. local game

	Coordinator coordinator;
	if (!coordinator.LoadSettings(argc, argv))
	{
		std::cout << "Unable to find or parse settings." << std::endl;
		return 1;
	}

	coordinator.SetStepSize(1);
	coordinator.SetMultithreaded(true);

	if (PlayerOneIsHuman)
	{
		coordinator.SetRealtime(true);
	}

	Bot bot1;
	Human human_bot;
	Agent *player_one = &bot1;
	if (PlayerOneIsHuman)
	{
		player_one = &human_bot;
	}

	coordinator.SetParticipants({CreateParticipant(Race::Zerg, player_one),
								 CreateComputer(Race::Random, Difficulty::Hard, AIBuild::RandomBuild)});
	coordinator.LaunchStarcraft();
	std::vector<char *> customMaps = {
		"Ladder/(2)Bel'ShirVestigeLE (Void).SC2Map",
		"Ladder/2000AtmospheresAIE.SC2Map",
		"Ladder/BerlingradAIE.SC2Map",
		"Ladder/BlackburnAIE.SC2Map",
		"Ladder/CuriousMindsAIE.SC2Map",
		"Ladder/Flat482Spawns.SC2Map",
		"Ladder/GlitteringAshesAIE.SC2Map",
		"Ladder/HardwireAIE.SC2Map"};
	// coordinator.StartGame(sc2::kMapBelShirVestigeLE);
	coordinator.StartGame(GetRandomEntry(customMaps));

	while (coordinator.Update())
	{
		// if (bot.gameLoop > 1500)
		//     SleepFor(15);
	}
	return 0;
}

// CONCEPTS
// droneCnt = dronesPresent + eggs(which are morphing into drones)
// hatcheryCnt = already built + currently building hatcheries
// GetUnits(Unit::Alliance::Self,IsUnit(UNIT_TYPEID::ZERG_DRONES)) -> will not give the eggs which are morphing into drones. It returns only the already built drones.

// Units geysers = Observation()->GetUnits(Unit::Alliance::Self, IsUnit(UNIT_TYPEID::ZERG_EXTRACTOR)); gave me 1 geyser
// Units geysers = Observation()->GetUnits(Unit::Alliance::Self, IsGeyser()); gave me 0 when it should have
// give 1 too. MAYBE IsGeyser() REFERS TO NEUTRAL GEYSERS ONLY.

// BUGS
//  //// bug. GetLarvaCnt always returns 0.
// larvaCnt = Observation()->GetLarvaCount();

// todo

// ALT + ENTER = FULLSCREEN (for sc2 bot window)
