import discord
from discord import app_commands, ui
from discord.ext import commands
import mysql.connector
from mysql.connector import Error
from datetime import datetime, date, timedelta
import calendar


class CalendarPaginationView(ui.View):
    def __init__(self, bot, get_db_connection, month, year, get_emoji_func):
        super().__init__(timeout=60)
        self.bot = bot
        self.get_db_connection = get_db_connection
        self.month = month
        self.year = year
        self.get_emoji_func = get_emoji_func

    async def create_embed(self):
        conn = await self.get_db_connection()
        if conn is None:
            return discord.Embed(title="Error", description="Database connection error.")

        try:
            cursor = conn.cursor(dictionary=True)
            start_date = f"{self.year}-{self.month:02d}-01"
            last_day = calendar.monthrange(self.year, self.month)[1]
            end_date = f"{self.year}-{self.month:02d}-{last_day}"

            cursor.execute(
                "SELECT * FROM academic_calendar WHERE event_date BETWEEN %s AND %s ORDER BY event_date ASC", (start_date, end_date))
            events = cursor.fetchall()

            cal = calendar.monthcalendar(self.year, self.month)
            month_name = calendar.month_name[self.month]
            now = datetime.now()

            embed = discord.Embed(
                title=f"📅 Academic Calendar - {month_name} {self.year}", color=0x3498db)

            calendar_text = "```\n"
            calendar_text += "Mo Tu We Th Fr Sa Su\n"

            event_dates = {e['event_date'].day: e for e in events}

            for week in cal:
                week_text = ""
                for day in week:
                    if day == 0:
                        week_text += "   "
                    else:
                        if day == now.day and self.month == now.month and self.year == now.year:
                            week_text += f"{day:2}*"
                        elif day in event_dates:
                            week_text += f"{day:2}+"
                        else:
                            week_text += f"{day:2} "
                    week_text += " "
                calendar_text += week_text.rstrip() + "\n"
            calendar_text += "```"

            embed.description = calendar_text

            if events:
                event_list = ""
                for e in events:
                    d = e['event_date'].day
                    type_emoji = self.get_emoji_func(e['type'])
                    event_list += f"**{d}**: {type_emoji} {e['title']}\n"
                embed.add_field(name="Events", value=event_list, inline=False)
            else:
                embed.add_field(
                    name="Events", value="No events scheduled.", inline=False)

            embed.set_footer(text="* = Today | + = Event scheduled")
            return embed
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    @ui.button(label="Prev", style=discord.ButtonStyle.grey)
    async def prev_month(self, interaction: discord.Interaction, button: ui.Button):
        self.month -= 1
        if self.month < 1:
            self.month = 12
            self.year -= 1
        embed = await self.create_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @ui.button(label="Next", style=discord.ButtonStyle.grey)
    async def next_month(self, interaction: discord.Interaction, button: ui.Button):
        self.month += 1
        if self.month > 12:
            self.month = 1
            self.year += 1
        embed = await self.create_embed()
        await interaction.response.edit_message(embed=embed, view=self)


class AcademicCalendar(commands.Cog):
    def __init__(self, bot, get_db_connection):
        self.bot = bot
        self.get_db_connection = get_db_connection

    @app_commands.command(name="calendar", description="View the academic calendar for a specific month")
    @app_commands.describe(month="Month (1-12)", year="Year (e.g. 2026)")
    async def calendar_view(self, interaction: discord.Interaction, month: int = None, year: int = None):
        now = datetime.now()
        if month is None:
            month = now.month
        if year is None:
            year = now.year

        if not (1 <= month <= 12):
            await interaction.response.send_message("Invalid month. Please use 1-12.", ephemeral=True)
            return

        view = CalendarPaginationView(
            self.bot, self.get_db_connection, month, year, self.get_type_emoji)
        embed = await view.create_embed()
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="upcoming-events", description="List upcoming academic events")
    async def upcoming_events(self, interaction: discord.Interaction):
        conn = await self.get_db_connection()
        if conn is None:
            await interaction.response.send_message("Database connection error.", ephemeral=True)
            return

        try:
            cursor = conn.cursor(dictionary=True)
            now = date.today()
            query = "SELECT * FROM academic_calendar WHERE event_date >= %s ORDER BY event_date ASC LIMIT 10"
            cursor.execute(query, (now,))
            events = cursor.fetchall()

            if not events:
                await interaction.response.send_message("No upcoming events found.")
                return

            embed = discord.Embed(
                title="🚀 Upcoming Academic Events", color=0x2ecc71)
            for e in events:
                date_str = e['event_date'].strftime("%d %b %Y (%a)")
                type_emoji = self.get_type_emoji(e['type'])
                embed.add_field(
                    name=f"{date_str}",
                    value=f"{type_emoji} **{e['title']}** ({e['type']})",
                    inline=False
                )

            await interaction.response.send_message(embed=embed)

        except Error as e:
            print(f"Error fetching upcoming events: {e}")
            await interaction.response.send_message("An error occurred.", ephemeral=True)
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def get_type_emoji(self, event_type):
        mapping = {
            'Academic': '📚',
            'Exam': '📝',
            'Assignment': '📂',
            'Meeting': '🤝',
            'Activity': '🎨',
            'Holiday': '🌴'
        }
        return mapping.get(event_type, '🔹')


async def setup(bot, get_db_connection):
    await bot.add_cog(AcademicCalendar(bot, get_db_connection))
