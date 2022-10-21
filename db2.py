import aiosqlite

'''from cgitb import reset'''

import asyncio
import asyncpg

class DBManager():
    def __init__(self, dbase_path):
        self.dbase_path = dbase_path
    
    async def dbase_init(self):
        self.dbase = await asyncpg.connect(user='postgres', password='admin',
                                 database='twitchitaliabattle', host='127.0.0.1')
    
    async def dbase_close(self):
        await self.dbase.close()

    async def increment_region_point(self, region_name):
        query = 'UPDATE regions SET points = points + 1 WHERE name = $1'
        await self.dbase.execute(query, region_name)


    async def increment_point_region_battle(self, region_name):
        query = 'UPDATE regions SET battle_points = battle_points + 1 WHERE name = $1'
        await self.dbase.execute(query, region_name)

    async def reset_points(self):
        query = "UPDATE regions SET points = 0"
        await self.dbase.execute(query)

    async def reset_dbase(self):
        query = 'UPDATE regions SET points = 0, in_battle = 0, eliminated = 0, battle_points = 0'
        await self.dbase.execute(query)

    async def reset_battle_points(self):
        query = "UPDATE regions SET battle_points = 0"
        await self.dbase.execute(query)
    
    async def reset_in_battle_status(self):
        query = "UPDATE regions SET in_battle = 0"
        await self.dbase.execute(query)

    async def get_region_points(self, region_name):
        query = 'SELECT points FROM regions WHERE name = $1'
        return (await self.dbase.fetch(query, region_name))[0][0]

    async def get_region_battle_points(self, region_name):
        query = 'SELECT battle_points FROM regions WHERE name = $1'
        return (await self.dbase.fetch(query, region_name))[0][0]

    async def set_region_as_in_battle(self, region_name):
        query = 'UPDATE regions SET in_battle = 1 WHERE name = $1'
        await self.dbase.execute(query, region_name)

    async def is_the_region_currently_in_battle(self, region_name):
        query = 'SELECT COUNT(*) FROM regions WHERE name = $1 and in_battle = 1'
        return (await self.dbase.fetch(query, region_name))[0][0]

    async def is_the_region_eliminated(self, region_name):
        query = 'SELECT COUNT(*) FROM regions WHERE name = $1 AND eliminated = 1'
        return (await self.dbase.fetch(query, region_name))[0][0]

    async def get_number_of_regions_in_battle(self):
        #minimum of 0 maximum of 2
        query = 'SELECT COUNT (*) FROM regions WHERE in_battle = 1'
        return (await self.dbase.fetch(query))[0][0]
    
    async def get_number_of_region_eliminated(self):
        query = 'SELECT COUNT(*) FROM regions WHERE eliminated = 1'
        return (await self.dbase.fetch(query))[0][0]

    async def set_eliminated_region_who_fighted_with_region_name(self, winner_region_name):
        query = 'UPDATE regions SET eliminated = 1 WHERE in_battle = 1 AND name != $1'
        await self.dbase.execute(query, winner_region_name)

    async def get_region_names_actually_in_battle(self):
        query = 'SELECT name FROM regions WHERE in_battle = 1'
        return (await self.dbase.fetch(query))

    async def get_all_region_data(self):
        query = 'SELECT * FROM regions'
        return (await self.dbase.fetch(query))
