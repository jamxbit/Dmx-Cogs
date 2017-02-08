from discord.ext import commands
from cogs.utils import checks
from cogs.utils.dataIO import fileIO
import discord
import asyncio
import os
from random import choice, randint

inv_settings = {"Channel": None, "joinmessage": None, "leavemessage": None, "Embed": False, "leave": False, "botroletoggle": False, "botrole" : None, "join": False, "Invites": {}}


class Welcomer:
    def __init__(self, bot):
        self.bot = bot
        self.direct = "data/welcomer/settings.json"

    @checks.admin_or_permissions(administrator=True)
    @commands.group(name='welcomer', pass_context=True, no_pm=True, aliases=["wel","welcome"])
    async def welcome(self, ctx):
        """Welcome and leave message, with invite link. Make sure to start first by settings the welcomer joinmessage, then continue to toggle, set leave ETC
        If you need anyhelp join the support server which can be found by doing ~invite"""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @welcome.command(name='joinmessage', pass_context=True, no_pm=True, aliases=["jm"])
    async def joinmessage(self, ctx, *, message: str):
        """
        Set a message when a user joins
        {0} is the user
        {1} is the invite that he/her joined using
        {2} is the server {2.name} <-
        Example formats:
            {0.mention} this will mention the user when he joins
            {2.name} is the name of the server
            {1.inviter} is the user that made the invite
            {1.url} is the invite link the user joined with
        Message Examples:
        {0.mention} Welcome to {2.name}, User joined with {1.url} referred by {1.inviter}
        Welcome to {2.name} {0}! I hope you enjoy your stay
        """
        server = ctx.message.server
        db = fileIO(self.direct, "load")
        if server.id in db:
            db[server.id]['joinmessage'] = message
            fileIO(self.direct, "save", db)
            await self.bot.say(":thumbsup: **Done** I've Successfully set the welcome greeting too :\n`{}`".format(message))
            return
        if not ctx.message.server.me.permissions_in(ctx.message.channel).manage_channels:
            await self.bot.say(":x: **I dont have the manage channels permission.** :x:")
            return
        if ctx.message.server.me.permissions_in(ctx.message.channel).send_messages:
            if not server.id in db:
                db[server.id] = inv_settings
                db[server.id]['joinmessage'] = message
                invlist = await self.bot.invites_from(server)
                db[server.id]["Channel"] = ctx.message.channel.id
                for i in invlist:
                    db[server.id]["Invites"][i.url] = i.uses
                fileIO(self.direct, "save", db)
                await self.bot.say("**I will now Welcome New users.** ***(If toggled)***:thumbsup:")
        else:
            return

    @welcome.command(name='leavemessage', pass_context=True, no_pm=True, aliases=["lm"])
    async def leavemessage(self, ctx, *, message: str):
        """
        Set a message when a user leaves
        {0} is the user
        {1} is the server
        Example formats:
            {0.mention} this will mention the user when he joins
            {1.name} is the name of the server
            {0.name} is the name
        Message Examples:
            Sad to see {0.mention} leave us in {1.name}
            Crap we lost another ONE {0.name} lEFT!!
        """
        server = ctx.message.server
        db = fileIO(self.direct, "load")
        if server.id in db:
            db[server.id]['leavemessage'] = message
            fileIO(self.direct, "save", db)
            await self.bot.say("**Leave message** ***changed.***:thumbsup:")
            return
        if ctx.message.server.me.permissions_in(ctx.message.channel).send_messages:
            if not server.id in db:
                db[server.id]['leavemessage'] = message
                db[server.id]["Channel"] = ctx.message.channel.id
                fileIO(self.direct, "save", db)
                await self.bot.say("**I will now send leave notifications here.** ***(If toggled)***:thumbsup:")

    @welcome.command(name='botrole', pass_context=True, no_pm=True, aliases=["br"])
    async def botrole(self, ctx, *, role : discord.Role):
        """sets the botrole to auto assign roles to bots"""
        server = ctx.message.server
        db = fileIO(self.direct, "load")
        if not server.id in db:
            await self.bot.say(":no_good: :x: **Server** ***not found***\n**Use** ***welcome joinmessage***  **to set a channel.**")
            return
        if ctx.message.server.me.permissions_in(ctx.message.channel).manage_roles:
            db[server.id]['botrole'] = role.id
            fileIO(self.direct, "save", db)
            await self.bot.say(":raising_hand: ***OI OI*** **Bot role** ***Saved***:punch:")
        else:
            await self.bot.say(":no_good: :x: **I do not have the manage_roles permission :x: :no_good:")

    @welcome.command(name='botroletoggle', pass_context=True, no_pm=True, aliases=["brt"])
    async def botroletoggle(self, ctx):
        """toggles bot role du"""
        server = ctx.message.server
        db = fileIO(self.direct, "load")
        if not server.id in db:
            await self.bot.say("Server not found, use ~welcome joinmessage to set a channel.")
            return
        if db[server.id]['botrole'] == None:
            await self.bot.say(":no_good:***Role Not Found***:no_good:\n***__```set it with ~welcomer botrole```__***")
        if db[server.id]["botroletoggle"] == False:
            db[server.id]["botroletoggle"] = True
            fileIO(self.direct, "save", db)
            await self.bot.say("***Bot role enabled*** :thumbsup:")
        elif db[server.id]["botroletoggle"] == True:
            db[server.id]["botroletoggle"] = False
            fileIO(self.direct, "save", db)
            await self.bot.say("***Bot roledisabled*** :thumbsup:")


    @welcome.command(name='toggleleave', pass_context=True, no_pm=True, aliases=["tl"])
    async def toggleleave(self, ctx):
        """toggle leave message"""
        server = ctx.message.server
        db = fileIO(self.direct, "load")
        if db[server.id]["leave"] == False:
            db[server.id]["leave"] = True
            fileIO(self.direct, "save", db)
            await self.bot.say("**Leave messages** ***enabled*** :thumbsup:")
        elif db[server.id]["leave"] == True:
            db[server.id]["leave"] = False
            fileIO(self.direct, "save", db)
            await self.bot.say(":x:***Leave messages disabled*** :thumbsup:")

    @welcome.command(name='togglejoin', pass_context=True, no_pm=True, aliases=["tj"])
    async def togglejoin(self, ctx):
        """toggle join message"""
        server = ctx.message.server
        db = fileIO(self.direct, "load")
        if db[server.id]["join"] == False:
            db[server.id]["join"] = True
            fileIO(self.direct, "save", db)
            await self.bot.say(":punch:***Join messages enabled***:thumbsup:")
        elif db[server.id]["join"] == True:
            db[server.id]["join"] = False
            fileIO(self.direct, "save", db)
            await self.bot.say(":bangbang::no_good:**Join messages disabled**:no_good::bangbang:")

    @welcome.command(name='embed', pass_context=True, no_pm=True, aliases=["em"])
    async def embed(self, ctx):
        """Opt into making all welcome and leave messages embeded"""
        server = ctx.message.server
        db = fileIO(self.direct, "load")
        if not server.id in db:
            await self.bot.say(":raised_hand: **Server not found, use welcomer joinmessage to set a channel.** :raised_hand:")
            return
        if db[server.id]["Embed"] == False:
            db[server.id]["Embed"] = True
            fileIO(self.direct, "save", db)
            await self.bot.say("***Embeds enabled***:thumbsup:")
        elif db[server.id]["Embed"] == True:
            db[server.id]["Embed"] = False
            fileIO(self.direct, "save", db)
            await self.bot.say(":bangbang: :x: **Embeds disabled** :x: :bangbang:")

    @welcome.command(name='disable', pass_context=True, no_pm=True)
    async def disable(self, ctx):
        """disables the welcomer"""
        server = ctx.message.server
        channel = ctx.message.channel
        db = fileIO(self.direct, "load")
        if not server.id in db:
            await self.bot.say(":raised_hand: **Server not found, use welcomer joinmessage to set a channel.** :raised_hand:")
            return
        del db[server.id]
        fileIO(self.direct, "save", db)
        await self.bot.say(":bangbang::no_good:**I will no longer send welcome messages to** ***{}***:x:".format(channel.name))

    async def on_member_join(self, member):
        server = member.server
        db = fileIO(self.direct, "load")
        if not server.id in db:
            return
        if member.bot:
            if db[server.id]['botroletoggle'] == True:
                roleobj = [r for r in server.roles if r.id == db[server.id]['botrole']]
                await self.bot.add_roles(member, roleobj[0])
        await asyncio.sleep(1)
        if db[server.id]['join'] == False:
            return
        channel = db[server.id]["Channel"]
        inv_channel = None
        message = db[server.id]['joinmessage']
        json_list = db[server.id]["Invites"]
        inv_list = await self.bot.invites_from(server)
        avatar = member.avatar_url if member.avatar else server.icon_url
        for a in inv_list:
            try:
                if int(a.uses) > int(json_list[a.url]):
                    if db[server.id]["Embed"] == True:
                        color = ''.join([choice('0123456789ABCDEF') for x in range(6)])
                        color = int(color, 16)
                        data = discord.Embed(description=message.format(member, a, server),
                                             colour=discord.Colour(value=color))
                        data.set_author(name="New User!!", icon_url=server.icon_url)
                        data.set_footer(text="ID: {}".format(member.id), icon_url=self.bot.user.avatar_url)
                        data.set_thumbnail(url=avatar)
                        await self.bot.send_message(server.get_channel(channel), embed=data)
                    else:
                        await self.bot.send_message(server.get_channel(channel), message.format(member, a, server))
            except KeyError:
                if db[server.id]["Embed"] == True:
                    color = ''.join([choice('0123456789ABCDEF') for x in range(6)])
                    color = int(color, 16)
                    data = discord.Embed(description=message.format(member, a, server),
                                         colour=discord.Colour(value=color))
                    data.set_author(name="New User!!", icon_url=server.icon_url)
                    data.set_footer(text="ID: {}".format(member.id), icon_url=self.bot.user.avatar_url)
                    data.set_thumbnail(url=avatar)
                    await self.bot.send_message(server.get_channel(channel), embed=data)
                else:
                    await self.bot.send_message(server.get_channel(channel), message.format(member, a, server))
                break
            else:
                pass
        invlist = await self.bot.invites_from(server)
        for i in invlist:
            db[server.id]["Invites"][i.url] = i.uses
        fileIO(self.direct, "save", db)

    async def on_member_remove(self, member):
        server = member.server
        db = fileIO(self.direct, "load")
        if not server.id in db:
            return
        if db[server.id]['leave'] == False:
            return
        message = db[server.id]['leavemessage']
        channel = db[server.id]["Channel"]
        avatar = member.avatar_url if member.avatar else server.icon_url
        if db[server.id]["Embed"] == True:
            color = ''.join([choice('0123456789ABCDEF') for x in range(6)])
            color = int(color, 16)
            data = discord.Embed(description=message.format(member, server), icon_url=server.icon_url, colour=discord.Colour(value=color))
            data.set_author(name="", icon_url=server.icon_url)
            data.set_footer(text="ID: {}".format(member.id), icon_url=self.bot.user.avatar_url)
            await self.bot.send_message(server.get_channel(channel), embed=data)
        else:
            await self.bot.send_message(server.get_channel(channel), message.format(member, server))


def check_folder():
    if not os.path.exists('data/welcomer'):
        print('Creating data/welcomer folder...')
        os.makedirs('data/welcomer')


def check_file():
    f = 'data/welcomer/settings.json'
    if not fileIO(f, 'check'):
        print('Creating default settings.json...')
        fileIO(f, 'save', {})


def setup(bot):
    check_folder()
    check_file()
    bot.add_cog(Welcomer(bot))