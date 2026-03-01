
import discord
from discord import app_commands
from discord.ext import commands, tasks
import mysql.connector
from mysql.connector import Error
from datetime import datetime, time, timedelta
import asyncio

class TimetableManager(commands.Cog):
    def __init__(self, bot, get_db_connection):
        self.bot = bot
        self.get_db_connection = get_db_connection
        self.alert_channel_id = None # Set this via a command or config
        self.check_periods.start()

    def cog_unload(self):
        self.check_periods.cancel()

    @app_commands.command(name="timetable", description="Shows the timetable for a specific day")
    @app_commands.describe(day="Day of the week (Monday-Friday)")
    @app_commands.choices(day=[
        app_commands.Choice(name="Monday", value="Monday"),
        app_commands.Choice(name="Tuesday", value="Tuesday"),
        app_commands.Choice(name="Wednesday", value="Wednesday"),
        app_commands.Choice(name="Thursday", value="Thursday"),
        app_commands.Choice(name="Friday", value="Friday")
    ])
    async def timetable_view(self, interaction: discord.Interaction, day: str = None):
        if day is None:
            day = datetime.now().strftime("%A")
            if day in ["Saturday", "Sunday"]:
                day = "Monday"

        conn = await self.get_db_connection()
        if conn is None:
            await interaction.response.send_message("Database connection error.", ephemeral=True)
            return

        try:
            cursor = conn.cursor(dictionary=True)
            query = "SELECT * FROM timetable WHERE day_of_week = %s ORDER BY period_number ASC"
            cursor.execute(query, (day,))
            periods = cursor.fetchall()

            if not periods:
                await interaction.response.send_message(f"No classes found for {day}.")
                return

            embed = discord.Embed(title=f"📅 Timetable - {day}", color=0x3498db)
            
            # Group by period number to handle batches
            grouped_periods = {}
            for p in periods:
                p_num = p['period_number']
                if p_num not in grouped_periods:
                    grouped_periods[p_num] = []
                grouped_periods[p_num].append(p)

            for p_num in sorted(grouped_periods.keys()):
                p_list = grouped_periods[p_num]
                start = str(p_list[0]['start_time'])
                end = str(p_list[0]['end_time'])
                
                value = ""
                for p in p_list:
                    batch_info = f" [Batch {p['batch']}]" if p['batch'] else ""
                    value += f"**{p['subject_code']}**{batch_info}\n"
                
                embed.add_field(
                    name=f"Period {p_num} ({start[:5]} - {end[:5]})",
                    value=value,
                    inline=False
                )

            embed.set_footer(text="JOI - EVERYTHING YOU WANT TO SEE, EVERYTHING YOU WANT TO HEAR")
            await interaction.response.send_message(embed=embed)

        except Error as e:
            print(f"Error fetching timetable: {e}")
            await interaction.response.send_message("An error occurred while fetching the timetable.", ephemeral=True)
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    @app_commands.command(name="set-alert-channel", description="Set the channel for timetable alerts")
    async def set_alert_channel(self, interaction: discord.Interaction):
        self.alert_channel_id = interaction.channel_id
        await interaction.response.send_message(f"✅ Alert channel set to {interaction.channel.mention}")

    @tasks.loop(seconds=30)
    async def check_periods(self):
        if self.alert_channel_id is None:
            return

        now = datetime.now()
        day_name = now.strftime("%A")
        if day_name in ["Saturday", "Sunday"]:
            return

        current_time_str = now.strftime("%H:%M:00")
        
        conn = await self.get_db_connection()
        if conn is None: return

        try:
            cursor = conn.cursor(dictionary=True)
            
            # 1. Check for starting periods
            query = "SELECT * FROM timetable WHERE day_of_week = %s AND start_time = %s"
            cursor.execute(query, (day_name, current_time_str))
            starting_periods = cursor.fetchall()

            if starting_periods:
                channel = self.bot.get_channel(self.alert_channel_id)
                if channel:
                    # Check if it's the first period of the day
                    cursor.execute("SELECT MIN(period_number) as first FROM timetable WHERE day_of_week = %s", (day_name,))
                    first_period = cursor.fetchone()['first']
                    
                    p_num = starting_periods[0]['period_number']
                    greeting = "🌅 Good Morning! " if p_num == first_period else "🔔 "
                    
                    msg = f"{greeting}Period {p_num} is starting now!\n"
                    for p in starting_periods:
                        batch = f" (Batch {p['batch']})" if p['batch'] else ""
                        msg += f"📖 **{p['subject_code']}**{batch}\n"
                    
                    # Look ahead for next period
                    cursor.execute("SELECT * FROM timetable WHERE day_of_week = %s AND period_number = %s", (day_name, p_num + 1))
                    next_periods = cursor.fetchall()
                    if next_periods:
                        msg += f"\n*Next up: Period {p_num + 1} ({next_periods[0]['subject_code']})*"
                    
                    await channel.send(msg)

            # 2. Check for ending periods (specifically the last one)
            query = "SELECT * FROM timetable WHERE day_of_week = %s AND end_time = %s"
            cursor.execute(query, (day_name, current_time_str))
            ending_periods = cursor.fetchall()

            if ending_periods:
                cursor.execute("SELECT MAX(period_number) as last FROM timetable WHERE day_of_week = %s", (day_name,))
                last_period = cursor.fetchone()['last']
                
                if any(p['period_number'] == last_period for p in ending_periods):
                    channel = self.bot.get_channel(self.alert_channel_id)
                    if channel:
                        await channel.send("✨ **All classes for today are over!** Have a great evening! ✨")

        except Exception as e:
            print(f"Error in timetable background task: {e}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    @check_periods.before_loop
    async def before_check_periods(self):
        await self.bot.wait_until_ready()

async def setup(bot, get_db_connection):
    await bot.add_cog(TimetableManager(bot, get_db_connection))
