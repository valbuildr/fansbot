from requests import get
import config
import datetime
from zoneinfo import ZoneInfo
import utils
import discord
from discord.ext import commands


def get_schedule(sid: str):
    resp = get("https://programmes.api.bbc.com/nitro/api/broadcasts",
            params={
                "api_key": config.nitro_secret,
                "sid": sid,
                "schedule_day": datetime.datetime.now(ZoneInfo("Europe/London")).strftime("%Y-%m-%d"),
                "page_size": 100, # just grab the whole schedule because i cba to do pagination 🥰
                "page": 1
            },
            headers={
                "Accept": "application/json"
            })
    
    if resp.status_code >= 200 and not resp.status_code > 299:
        json = resp.json()
        if json["nitro"]["results"]["total"] > 0:
            listing = {
                "sid": sid,
                "date": datetime.datetime.now(ZoneInfo("Europe/London")).strftime("%Y-%m-%d"),
                "items": [],
                "total_items": json['nitro']['results']['total']
            }

            for i in json["nitro"]["results"]["items"]:
                try:
                    title = i['ancestors_titles']['brand']
                except:
                    try:
                        title = i['ancestors_titles']['series']
                    except:
                        title = i['ancestors_titles']['episode']

                starttime = utils.dt_to_timestamp(datetime.fromisoformat(i['published_time']['start']), "z")
                endtime = utils.dt_to_timestamp(datetime.fromisoformat(i['published_time']['end']), "z")

                listing["items"].append({
                    "title": title["title"],
                    "pid": i["pid"],
                    "time": [starttime, endtime]
                })

                return listing
        else:
            return "No results found."
    else:
        return "No valid response."


def get_bbc_one_london_schedule():
    sid = "bbc_one_london"

    return_val = get_schedule(sid)
    return return_val


def get_bbc_two_hd_schedule():
    sid = "bbc_two_hd"

    return_val = get_schedule(sid)
    return return_val


def get_bbc_three_hd_schedule():
    sid = "bbc_three_hd"

    return_val = get_schedule(sid)
    return return_val


def get_bbc_four_hd_schedule():
    sid = "bbc_four_hd"

    return_val = get_schedule(sid)
    return return_val


def get_bbc_news_uk_schedule():
    sid = "bbc_news24" # yes its still called news 24 in nitro

    return_val = get_schedule(sid)
    return return_val


def get_bbc_news_na_schedule():
    sid = "bbc_world_news_north_america" # yes its still called world news in nitro

    return_val = get_schedule(sid)
    return return_val


def get_bbc_parliament_schedule():
    sid = "bbc_parliament"

    return_val = get_schedule(sid)
    return return_val



def get_r1_schedule():
    sid = "bbc_radio_one"

    return_val = get_schedule(sid)
    return return_val


def get_r1x_schedule():
    sid = "bbc_1xtra"

    return_val = get_schedule(sid)
    return return_val


def get_r1d_schedule():
    sid = "bbc_radio_one_dance"

    return_val = get_schedule(sid)
    return return_val


def get_r2_schedule():
    sid = "bbc_radio_two"

    return_val = get_schedule(sid)
    return return_val


def get_r3_schedule():
    sid = "bbc_radio_three"

    return_val = get_schedule(sid)
    return return_val


def get_r4_schedule():
    sid = "bbc_radio_fourfm"

    return_val = get_schedule(sid)
    return return_val


def get_r4e_schedule():
    sid = "bbc_radio_four_extra"

    return_val = get_schedule(sid)
    return return_val


def get_r5l_schedule():
    sid = "bbc_radio_five_live"

    return_val = get_schedule(sid)
    return return_val


def get_r5se_schedule():
    sid = "bbc_radio_five_live_sports_extra"

    return_val = get_schedule(sid)
    return return_val


def get_r6m_schedule():
    sid = "bbc_6music"

    return_val = get_schedule(sid)
    return return_val


def get_asian_network_schedule():
    sid = "bbc_asian_network"

    return_val = get_schedule(sid)
    return return_val


def get_ws_online_schedule():
    sid = "bbc_world_service"

    return_val = get_schedule(sid)
    return return_val




class SchedulesCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.command()
    async def sched(self, ctx: commands.Context):
        r = get_bbc_news_na_schedule()

        await ctx.send(r)


async def setup(bot: commands.Bot):
    await bot.add_cog(SchedulesCog(bot))