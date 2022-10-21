import aiosqlite

from cgitb import reset

class DBManager():
    def __init__(self, dbase_path):
        self.dbase_path = dbase_path
    
    async def dbase_init(self):
        self.dbase = await aiosqlite.connect(self.dbase_path)
    
    async def dbase_close(self):
        await self.dbase.close()

    async def increment_region_point(self, region_name):
        query = 'UPDATE regions SET points = points + 1 WHERE name = ?'
        await self.dbase.execute(query, (region_name,))
        await self.dbase.commit()

    async def increment_point_region_battle(self, region_name):
        query = 'UPDATE regions SET battle_points = battle_points + 1 WHERE name = ?'
        await self.dbase.execute(query, (region_name,))
        await self.dbase.commit()

    async def delete_path_of_losing_region(self, winner_region_name):
        #stuff
        pass
    async def reset_points(self):
        query = "UPDATE regions SET points = 0"
        await self.dbase.execute(query)
        await self.dbase.commit()

    async def reset_dbase(self):
        query = 'UPDATE regions SET points = 0, in_battle = 0, eliminated = 0, battle_points = 0'
        await self.dbase.execute(query)
        await self.dbase.commit()

    async def reset_battle_points(self):
        query = "UPDATE regions SET battle_points = 0"
        await self.dbase.execute(query)
        await self.dbase.commit()
    
    async def reset_in_battle_status(self):
        query = "UPDATE regions SET in_battle = 0"
        await self.dbase.execute(query)
        await self.dbase.commit()

    async def fill_region_as_in_battle(self):
        #svg stuff
        pass
    async def get_region_points(self, region_name):
        query = 'SELECT points FROM regions WHERE name = ?'
        cursor = await self.dbase.execute(query, (region_name,))
        row = await cursor.fetchone()
        await cursor.close()
        return row[0]

    async def get_region_battle_points(self, region_name):
        query = 'SELECT battle_points FROM regions WHERE name = ?'
        cursor = await self.dbase.execute(query, (region_name,))
        row = await cursor.fetchone()
        await cursor.close()
        return row[0]

    async def set_region_as_in_battle(self, region_name):
        query = 'UPDATE regions SET in_battle = 1 WHERE name = ?'
        await self.dbase.execute(query, (region_name,))
        await self.dbase.commit()

    async def is_the_region_currently_in_battle(self, region_name):
        query = 'SELECT EXISTS(SELECT 1 FROM regions WHERE name = ? and in_battle = 1)'
        cursor = await self.dbase.execute(query , (region_name,))
        row = await cursor.fetchone()
        await cursor.close()
        return row[0]

    async def is_the_region_eliminated(self, region_name):
        query = 'SELECT EXISTS(SELECT 1 FROM regions WHERE name = ? AND eliminated = 1)'
        cursor = await self.dbase.execute(query , (region_name,))
        row = await cursor.fetchone()
        await cursor.close()
        return row[0]

    async def get_number_of_regions_in_battle(self):
        #minimum of 0 maximum of 2
        query = 'SELECT COUNT (*) FROM regions WHERE in_battle = 1'
        cursor = await self.dbase.execute(query)
        row = await cursor.fetchone()
        await cursor.close()
        return row[0]

    async def set_eliminated_region_who_fighted_with_region_name(self, winner_region_name):
        query = 'UPDATE regions SET eliminated = 1 WHERE in_battle = 1 AND name != ?'
        await self.dbase.execute(query, (winner_region_name,))
        await self.dbase.commit()

    async def get_region_names_actually_in_battle(self):
        query = 'SELECT name FROM regions WHERE in_battle = 1'
        cursor = await self.dbase.execute(query)
        row = await cursor.fetchall()
        await cursor.close() 
        return row