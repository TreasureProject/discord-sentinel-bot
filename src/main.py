### imports
import os
import time
import discord
from discord.ext import commands
import constants
import asyncio

###SENTINEL BOT START###
### intents (double check dev portal)
intents = discord.Intents.default()  # allows the use of custom intents
intents.members = True  # allows to pull member roles among other things
intents.presences = True
discord.MemberCacheFlags.none
sentinel_bot = commands.Bot(command_prefix="oly!", intents=intents)
### log in
@sentinel_bot.event
async def on_ready():
    print(f"Logged in as {sentinel_bot.user.name}")
    print("------")

### role kicker
@sentinel_bot.command(pass_context=True)
@commands.has_role(constants.ADMIN_ROLE)  # requires user to have this role
async def masskick(ctx, role: discord.Role):

    total = len(role.members)
    kicked = 0

    await ctx.message.add_reaction('🧠')  # lets user know command is processing

    print(f"queued for kick: {total}")  #console
    for member in role.members:
        await ctx.guild.kick(member)
        await ctx.channel.send(
            f"[{kicked}/{total}] kicked: {member.name} | <@{member.id}>"
        )  # discord
        print(
            f"[{kicked}/{len(role.members)}] kicked: {member.name} | <@{member.id}>"
        )  # console
        kicked += 1  #increment
        await asyncio.sleep(1)  # sleep call between interactions to avoid 429 rate limit

    await ctx.message.clear_reaction('🧠')  # remove processing reaction
    await ctx.message.add_reaction('✅')  # add finished reaction
    time.sleep(1)
    await ctx.message.reply(f"kicked {total} users in given role.")  # let user know

### lets you know how many users exist in a role
@sentinel_bot.command(pass_context=True)
@commands.has_role(constants.ADMIN_ROLE)  # requires user to have this role
async def listzero(ctx, role: discord.Role):
    
    members = filter(lambda m: len(m.roles) == 1, role.members)
    try:
      await ctx.send(" ".join(str(member.id) for member in members))
    except:
      await ctx.send("No members found")

### lets you know how many users exist in a role
@sentinel_bot.command(pass_context=True)
@commands.has_role(constants.ADMIN_ROLE)  # requires user to have this role
async def bulkrole(ctx, role: discord.Role, *users):
    guild = sentinel_bot.get_guild(ctx.guild.id)
    count = 0
    await ctx.message.add_reaction('🧠')  # lets user know command is processing
    for user in users:
        try:
          member = await guild.fetch_member(user)
          await member.add_roles(role)
          count += 1
        except:
          pass
        await asyncio.sleep(1)

    await ctx.message.add_reaction('✅')  # add finished reaction
  
    await ctx.send("Added {} to {} users".format(role,count))

### Bot function #1
@sentinel_bot.event
async def on_member_update(before, after):
    guild = sentinel_bot.get_guild(before.guild.id)
    g_role = discord.utils.get(guild.roles, name=constants.NEW_USER_ROLE) # role object for new users
    if (g_role not in before.roles and g_role in after.roles):
        print(f"Detected new user, {after.name}|{after.id}")
        for (channel_id, message) in constants.NEW_USER_FLOW:
            channel = sentinel_bot.get_channel(channel_id)
            await channel.send(message.replace("<user_id>", str(after.id)), delete_after=constants.EXPIRATION)
            await asyncio.sleep(constants.PAUSE)

### Bot function #2
# check for role assignment, kick after X seconds if no roles selected
@sentinel_bot.event
async def on_member_join(member):
    
    await asyncio.sleep(360)
    
    guild = sentinel_bot.get_guild(member.guild.id)
    e_role = discord.utils.get(guild.roles, name="@everyone")
    #use fetch_member because get_member pulls from cache
    try:
        member_check = await guild.fetch_member(member.id)
    except:
        member_check = None
        print(f"Couldn't locate member {member.id} | {member.name}")
    if member_check:
        if (len(member_check.roles) == 1 and e_role in member_check.roles):
             print(f"Kicking, {member_check.name} | {member_check.id}")
             print("------")
            #  channel = sentinel_bot.get_channel(constants.LOG_CHANNEL)
            #  await channel.send(
            #     f"Notified and kicked user that verified and selected no roles, {member_check.name}|{member_check.id}")
             try:
                await member_check.send(
               f"You have been kicked from {guild.name} because you did not assign roles within 6 minutes of joining the server, please rejoin and select roles to avoid being kicked.")
             except:
                pass
    
             await guild.kick(member_check)

###SENTINEL BOT END###

sentinel_bot.run(os.environ['SENTINEL_BOT_TOKEN'])
