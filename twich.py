from os import environ
from unittest.mock import patch
from twitchio.ext import commands
import aiosqlite
from db2 import *
from svgmanager import *
import dotenv
import aiohttp

env = dotenv.dotenv_values()

NUM_REGION_CHOSED_TO_FIGHT= int(env["NUM_REGION_CHOSED_TO_FIGHT"])
NUM_VICTORY_IN_BATTLE= int(env["NUM_VICTORY_IN_BATTLE"])
MAX_MESSAGES_IN_A_ROW = int(env['MAX_MESSAGES_IN_A_ROW'])

regions = ['abruzzo', 'basilicata', 'calabria', 'campania', 'emilia romagna', 'friuli venezia giulia',
'lazio', 'liguria', 'lombardia', 'marche', 'molise', 'piemonte', 'puglia','sardegna', 'sicilia',
'toscana', 'trentino alto adige', 'umbria', "valle d'aosta", 'veneto']

class Bot(commands.Bot):

    def __init__(self):
        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        self.dbase = DBManager(env)
        self.svgmanager = SVGManager(env)
        super().__init__(token=env["TWITCH_TOKEN"], prefix=env["TWITCH_BOT_PREFIX"], initial_channels=[env["TWITCH_BOT_INITIAL_CHANNELS"]])

        self.last_message_author = None
        self.author_messages_counter = 0

    async def send_telegram_log(self,text):
        link = 'https://api.telegram.org/bot' + env["TELEGRAM_BOT_TOKEN"] + '/sendMessage'
        params = {'chat_id': env["TELEGRAM_USER_ID_TO_NOTIFY"], 'text': text}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(link, params=params) as response: pass
            except:
                pass

    #overwriting the original run function to make sure the dbase is closed right before event loop is killed
    def run(self):
        """
        A blocking function that starts the asyncio event loop,
        connects to the twitch IRC server, and cleans up when done.
        """
        try:
            self.loop.create_task(self.connect())
            self.loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            if not self._closing.is_set():
                self.loop.run_until_complete(self.close())
            
            self.loop.run_until_complete(self.dbase.dbase_close())
            self.loop.close()

    async def event_ready(self):
        # We are logged in and ready to chat and use commands...
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')

    async def event_message(self, message):
        # Messages with echo set to True are messages sent by the bot...
        # For now we just want to ignore them...
        if message.echo:
            return

        self.loop.create_task(self.send_telegram_log(text='{twitch_user} sent: {message_text} -> {msgs_in_row}'.format(twitch_user=message.author.name, 
                                                                                                                        message_text=message.content,
                                                                                                                        msgs_in_row=self.author_messages_counter)))

        # Do stuff with my received message
        msg = (message.content).lower()
        if msg in regions:
            region_name = msg
            
            #an user is allowed to send max MAX_MESSAGES_IN_A_ROW messages in a row
            if self.author_messages_counter == MAX_MESSAGES_IN_A_ROW: return
            if self.last_message_author == message.author.name: 
                self.author_messages_counter += 1
            else:
                self.author_messages_counter = 0
                self.last_message_author = message.author.name
        else:
            return

        

        if (await self.dbase.is_the_region_eliminated(region_name)): return

        if (await self.dbase.get_number_of_regions_in_battle()) == 2:
            await self.dbase.reset_points() #there is currently a battle so the normal points are reset
            if (await self.dbase.is_the_region_currently_in_battle(region_name)):
                await self.dbase.increment_point_region_battle(region_name)
                region_battle_points = await self.dbase.get_region_battle_points(region_name)

                self.svgmanager.set_points_to_region(region_battle_points, region_name)
                await self.svgmanager.updatesvg()

                if (region_battle_points) == NUM_VICTORY_IN_BATTLE:

                    #await self.dbase.delete_path_of_losing_region(region_name)
                    region_names_in_battle = await self.dbase.get_region_names_actually_in_battle()

                    #region_name is the name of the winner region
                    loser_region_name = region_names_in_battle[0][0] if region_names_in_battle[0][0] != region_name else region_names_in_battle[1][0]
       
                    self.svgmanager.set_region_as_eliminated(loser_region_name)
                    self.svgmanager.reset_region_style(region_name)


                    await self.dbase.set_eliminated_region_who_fighted_with_region_name(region_name)
                    #await self.dbase.reset_points() already done
                    await self.dbase.reset_battle_points()
                    await self.dbase.reset_in_battle_status()

                    #if it's the only one is the winner
                    if (await self.dbase.get_number_of_region_eliminated()) == 19:
                        self.svgmanager.set_region_as_winner(region_name)
                        await self.svgmanager.updatesvg() #update one last time
                        self.svgmanager.stop_updating()

                    self.svgmanager.reset_all_points()
        else:
            region_points = await self.dbase.get_region_points(region_name) 
            if (region_points) == NUM_REGION_CHOSED_TO_FIGHT-1:
                await self.dbase.set_region_as_in_battle(region_name)

                self.svgmanager.set_region_as_in_battle(region_name)
                self.svgmanager.set_points_to_region(0,region_name)
            else:
                await self.dbase.increment_region_point(region_name)
                self.svgmanager.set_points_to_region(region_points+1, region_name)
        await self.svgmanager.updatesvg()

    # Since we have commands and are overriding the default `event_message`
    # We must let the bot know we want to handle and invoke our commands...
        await self.handle_commands(message)

    @commands.command()
    async def hello(self, ctx: commands.Context):
        # Send a hello back!
        await ctx.send(f'Hello {ctx.author.name}!')

if __name__ == '__main__':
    bot = Bot()
    bot.loop.run_until_complete(bot.dbase.dbase_init())
    #make sure the database is empty before we start
    #bot.loop.run_until_complete(bot.dbase.reset_dbase())

    #get current database state
    data_rows = bot.loop.run_until_complete(bot.dbase.get_all_region_data())
    #sync the svg with the database
    bot.svgmanager.initsvg(data_rows=data_rows)
    #save the new updated svg
    bot.loop.run_until_complete(bot.svgmanager.updatesvg())
    bot.run()