import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
from discord_slash.utils.manage_components import create_button, create_actionrow
from discord_buttons_plugin import *
from discord.utils import get
from discord_slash import SlashCommand, SlashContext
from discord_slash.model import ButtonStyle
from discord_slash.utils.manage_components import ComponentContext
import asyncio 

bot = commands.Bot(command_prefix='/',help_command=None)
slash_client = SlashCommand(bot, sync_commands=True)
Token = "OTcwNzE1NDg1MzAzODgxODY4.GWcUCp.ErJI0ETWnf9kuC3HsAqqCCpZzUx273U3wLOgYg"
max_ticket = 3

@slash_client.slash(
    name='set_ticket',
    description='チケットパネルを設置します',
    options=[
        {
            "name": "category",
            "description": "チケットを作成するカテゴリー",
            "type": 7,
            "required": False
        }
    ]
)
@has_permissions(administrator=True)
async def set_ticket(ctx: SlashContext,category=None):
    if category == None:
        category = get(ctx.guild.categories, name="チケット")
        if category == None:
            category = await ctx.guild.create_category("チケット")
    await ctx.reply("設置しました", hidden=True)
    embed = discord.Embed(
        color=0x00FFFF,
        title="チケット",
        description="下のボタンを押してチケットを作成します"
        )
    buttons = [
        create_button(
            style=ButtonStyle.red, 
            label="お問合せ",
            custom_id=f"create{category.id}"
            )
        ]
    action_row = create_actionrow(*buttons)
    await ctx.channel.send(embed=embed, components=[action_row])

async def create(ctx):
    name = (f"🎫-{ctx.author.name}")
    if len([i for i in ctx.guild.channels if i.name==name])>=max_ticket:
        await ctx.reply('```チケットを開きすぎています。チケットを閉じてから新しいチケットを作成してください```',flags = MessageFlags().EPHEMERAL)
        return
    category_id = int(ctx.custom_id.replace('create', ''))
    category = ctx.guild.get_channel(category_id)
    if category == None:
        category = discord.utils.get(ctx.guild.categories,name='チケット')
        if category == None:
            await ctx.guild.create_category("チケット")
            category = discord.utils.get(ctx.guild.categories,name='チケット')
    else:
        category
    guild = bot.get_guild(ctx.guild.id)
    permission = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        ctx.author: discord.PermissionOverwrite(read_messages=True)
        }
    ticketch = await category.create_text_channel(name=f"{name}", overwrites=permission)
    await ctx.reply(f"{ticketch.mention}作成しました",hidden=True)
    await ticketch.send(ctx.author.mention)
    embed = discord.Embed(
        title="チケット",
        description="下のボタンを押すとチケットが閉じます",
        color=0x5AFF19
        )
    buttons = [
        create_button(
            style=ButtonStyle.red, 
            label="閉じる",
            custom_id=f"question_del"
            )
        ]
    action_row = create_actionrow(*buttons)
    await ticketch.send(embed=embed, components=[action_row])

async def question_del(ctx):
    await ctx.reply('```チケットを削除します```',hidden=True)
    await asyncio.sleep(3)
    await ctx.channel.delete()
    
@bot.event
async def on_component(ctx: ComponentContext):
    if 'create' in ctx.custom_id:
        await create(ctx)

    elif ctx.custom_id == 'question_del':
        await question_del(ctx)
    
bot.run(Token)
