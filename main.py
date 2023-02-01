from boosting import *
from colorama import Fore
import discord, time, json, os, httpx
import sys
import hashlib
from keyauth import *
if os.name == 'nt':
    import ctypes

from auto import *

def cls(): #clears the terminal
    os.system('cls' if os.name =='nt' else 'clear')

    
config = json.load(open("config.json", encoding="utf-8"))

def getchecksum():
    md5_hash = hashlib.md5()
    file = open(''.join(sys.argv), "rb")
    md5_hash.update(file.read())
    digest = md5_hash.hexdigest()
    return digest


keyauthapp = api(
    name = "",
    ownerid = "",
    secret = "",
    version = "1.0",
    hash_to_check = getchecksum()
)

cls()

if keyauthapp.checkblacklist():
    print(Fore.RED + "You are blacklisted from our system." + Fore.RESET)
    quit()
    
def validate():
    if keyauthapp.license(config["license_key"]):
        quit()
    else:
        print(Fore.GREEN + "Successfully Logged Into License" + Fore.RESET)
        time.sleep(2)
        

def answer():
    try:
        key = input(Fore.CYAN + """License Key: """+ Fore.RESET)
        x = {"license_key": key}
        config.update(x)
        json.dump(config, open("config.json", "w"), indent = 4)

    except KeyboardInterrupt:
        os._exit(1)

if "license_key" not in str(config):
    answer()

validate()

fingerprints = json.load(open("fingerprints.json", encoding="utf-8"))
config = json.load(open("config.json", encoding="utf-8"))

client_identifiers = ['safari_ios_16_0', 'safari_ios_15_6', 'safari_ios_15_5', 'safari_16_0', 'safari_15_6_1', 'safari_15_3', 'opera_90', 'opera_89', 'firefox_104', 'firefox_102']

class logger():
    def __init__(self):
        self.times = time.strftime("%H:%M:%S")

    def success(self, msg: str):
        print(f"{Fore.WHITE}[{Fore.CYAN}{self.times}{Fore.RESET}]({Fore.MAGENTA}*{Fore.RESET}) {Fore.LIGHTGREEN_EX}{msg}{Fore.RESET}")

    def error(self, msg: str):
        print(f"{Fore.WHITE}[{Fore.CYAN}{self.times}{Fore.RESET}]({Fore.MAGENTA}*{Fore.RESET}) {Fore.LIGHTRED_EX}{msg}{Fore.RESET}")

class Utils():
    @staticmethod
    async def isWhitelisted(ctx) -> bool:
        if (
            str(ctx.author.id) in open("whitelist.txt", "r").read().splitlines()
            or str(ctx.author.id) == config["owner"]
        ):
            return True
        else:
            return False

activity = discord.Activity(type=discord.ActivityType.playing, name="-.-")

bot = discord.Bot(command_prefix="*", activity=activity, status=discord.Status.idle)

os.system(f"title Boost Bot")

@bot.slash_command(
    guild_ids=[config["guild_id"]],
    name="stock",
    description="Allows you to see the current token stock!",
)
async def stock(ctx):
    embed = discord.Embed(
        title="Stock",
        description=f"**3 Months Token Stock:** {len(open('input/3m_tokens.txt', 'r').read().splitlines())} \n**3 Month Boosts Stock:** {len(open('input/3m_tokens.txt', 'r').read().splitlines()) * 2}\n\n**1 Months Token Stock:** {len(open('input/1m_tokens.txt', 'r').read().splitlines())}\n**1 Month Boosts Stock:** {len(open('input/1m_tokens.txt', 'r').read().splitlines()) * 2}",
        color=0x00A5FF
    )

    await ctx.respond(embed=embed)

@bot.slash_command(guild_ids=[config["guild_id"]], name="restock", description="Allows one to restock 1 month or 3 month nitro tokens.")
async def restock(ctx, code: discord.Option(str, "Paste.ee link", required = True),type: discord.Option(int, "Type of tokens you are restocking, 3 months or 1 month", required=True)):
    if not (str(ctx.author.id) in open("whitelist.txt", "r").read().splitlines())  and str(ctx.author.id) != config["owner"]:
        return await ctx.respond(embed = discord.Embed(title = f"Contact {await bot.fetch_user(int(config['owner']))}", description = "You are currently not the owner. Please contact the respective owner to become the owner.", color = discord.Colour.red()))
    if type != 1 and type != 3 and type != 0:
        return await ctx.respond(embed = discord.Embed(title = "**Invalid Input**", description = "Type can either be 3 (months), 1 (month) or empty", color = discord.Colour.red()))
    if type == 1:
        file = "input/1m_tokens.txt"
    elif type == 3:
        file = "input/3m_tokens.txt"
        
    code = code.replace("https://paste.ee/p/", "")
    temp_stock = requests.get(f"https://paste.ee/d/{code}", headers={ "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.61 Safari/537.36"}).text
    
    f = open(file, "a", encoding="utf-8")
    f.write(f"{temp_stock}\n")
    f.close()
    lst = temp_stock.split("\n")
    return await ctx.respond(embed = discord.Embed(title = "**Success**", description = f"Successfully added {len(lst)} tokens to {file}", color = 0x00A5FF))    

@bot.slash_command(
    guild_ids=[config["guild_id"]],
    name="whitelist",
    description="Whitelist a user with ease.",
)
async def whitelist(
    ctx, user: discord.Option(discord.Member, "Member to whitelist", required=True)
):
    if str(ctx.author.id) != config["owner"]:
        return await ctx.respond(
            embed=discord.Embed(
                title=f"Contact {await bot.fetch_user(int(config['owner']))}",
                description="You are currently not the owner. Please contact the respective owner to become the owner.",
                color=discord.Colour.red()
            )
        )

    if (
        not (str(user.id) in open("whitelist.txt", "r").read().splitlines())
        and str(user.id) != config["owner"]
    ):
        with open("whitelist.txt", "a") as whitelist:
            whitelist.write(str(user.id) + "\n")

        embed = discord.Embed(
            title="Successfully Whitelisted",
            description=f"Successfully whitelisted {user}",
            color=0x00A5FF
        )

        return await ctx.respond(embed=embed)

    elif str(user.id) == config["owner"]:
        return await ctx.respond(
            embed=discord.Embed(
                title=f"Already Owner!",
                description=f"_You are not allowed to use the bot, please contact the respective owner._",
                color=discord.Colour.red()
            )
        )

    else:
        return await ctx.respond(
            embed=discord.Embed(
                title=f"Already whitelisted!",
                description=f"{user} is already whitelisted!",
                color=discord.Colour.red()
            )
        )


@bot.slash_command(
    guild_ids=[config["guild_id"]],
    name="unwhitelist",
    description="Unwhitelist a user with ease.",
)
async def unwhitelist(
    ctx, user: discord.Option(discord.Member, "Member to unwhitelist", required=True)
):
    if str(ctx.author.id) != config["owner"]:
        return await ctx.respond(
            embed=discord.Embed(
                title=f"Contact {await bot.fetch_user(int(config['owner']))}",
                description="You are currently not the owner. Please contact the respective owner to become the owner.",
                color=discord.Colour.red()
            )
        )

    if (
        not (str(user.id) in open("whitelist.txt", "r").read().splitlines())
        and str(user.id) != config["owner"]
    ):
        embed = discord.Embed(
            title="User Not Whitelisted!",
            description=f"{user} is currently not whitelisted.",
            color=discord.Colour.red()
        )

        return await ctx.respond(embed=embed)

    elif str(user.id) == config["owner"]:
        return await ctx.respond(
            embed=discord.Embed(
                title=f"Already Owner!",
                description=f"You are currently the owner! You cannot unwhitelist yourself.",
                color=discord.Colour.red()
            )
        )

    else:
        with open("whitelist.txt", "r+") as whitelist:
            whitelisted = whitelist.readlines()
            whitelist.seek(0)
            for line in whitelisted:
                if not (str(user.id) in line):
                    whitelist.write(line)
            whitelist.truncate()

        embed = discord.Embed(
            title="Successfully Unwhitelisted",
            description=f"Successfully Unwhitelisted {user}",
            color=0x00A5FF
        )

        return await ctx.respond(embed=embed)

@bot.slash_command(
    guild_ids=[config["guild_id"]], name="boost", description="Boosts a discord server."
)
async def boost(
    ctx: discord.ApplicationContext,
    invite: discord.Option(
        str,
        "Invite Link",
        required=True,
    ),
    amount: discord.Option(
        int, "Amount of boosts you want (Must be even)", required=True
    ),
    months: discord.Option(int, "Uses 1m or 3m stock to boost servers", required=True
    ),
    nick: discord.Option(str,"nickname", required=False)
):
    if not await Utils.isWhitelisted(ctx):
        return await ctx.respond(
            embed=discord.Embed(
                title="Not Whitelisted",
                description="_You are not allowed to use the bot, please contact the respective owner._",
                color=discord.Colour.red()
            )
        )

    if ".gg/" in invite:
        invite = str(invite).split(".gg/")[1]
    elif "invite/" in invite:
        invite = str(invite).split("invite/")[1]

    if (
        '{"message": "Unknown Invite", "code": 10006}'
        in httpx.get(f"https://discord.com/api/v9/invites/{invite}").text
    ):
        return await ctx.respond(
            embed=discord.Embed(
                title="Invalid Invite",
                description=f"discord.gg/{invite} is invalid. Please set a valid invite.",
                color=discord.Colour.red()
            )
        )


    if amount % 2 != 0:
        return await ctx.respond(
            embed=discord.Embed(
                title="Error!",
                description="`amount` must be even.",
                color=discord.Colour.red()
            )
        )
    else:
        numTokens = amount / 2  # gets number of accounts needed

    await ctx.respond(
        embed=discord.Embed(
            title="Boosts Started",
            description=f"**Amount:** {amount}\n**Months:** {months}\n**Invite Link:** https://discord.gg/{invite}",
            color=0x00A5FF
        )
    )  

    go = time.time()
    thread_boost(invite, amount, months, nick)
    end = time.time()
    time_went = round(end - go, 5)

    await ctx.respond(
        embed=discord.Embed(
            title="Boosts Successful",
            description=f"**Boost Type: **Manual\n**Order ID: **N/A\n**Product Name: **{amount} Server Boosts [{months} Months]\n**Customer Email: **N/A\n\n**Invite Link: **https://discord.gg/{invite}\n**Amount: **{amount} Boosts\n**Months: **{months} Months\n\n**Time Taken: **{time_went} seconds\n**Successful Tokens: **{len(variables.success_tokens)}\n**Successful Boosts: **{len(variables.success_tokens)*2}\n\n**Failed Tokens: **{len(variables.failed_tokens)}\n**Failed Boosts: **{len(variables.failed_tokens)*2}",
            color=0x00A5FF
        )
    )
    
keep_alive()
bot.run(config["token"])
