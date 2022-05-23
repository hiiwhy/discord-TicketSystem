import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions
from discord_slash.utils.manage_components import create_button, create_actionrow
from discord_buttons_plugin import *
from discord.utils import get
from discord_slash import SlashCommand, SlashContext
from discord_slash.model import ButtonStyle
from discord_slash.utils.manage_components import ComponentContext

bot = commands.Bot(command_prefix='/',help_command=None)
slash_client = SlashCommand(bot,sync_commands=True)
buttons = ButtonsClient(bot)
Token = ""
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
async def set_ticket(ctx: SlashContext,category):
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
    member_name = (ctx.member.name)
    name = (f"🎫-{member_name}")
    if len([i for i in ctx.guild.channels if i.name==name])>=max_ticket:
        await ctx.reply('```チケットを開きすぎています```',flags = MessageFlags().EPHEMERAL)
        return
    category_id = int(ctx.custom_id.replace('ticket', ''))
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
        ctx.member: discord.PermissionOverwrite(read_messages=True)
        }
    ticketch = await category.create_text_channel(name=f"{name}", overwrites=permission)
    await ctx.reply(f"{ticketch.mention}作成しました", flags = MessageFlags().EPHEMERAL)
    await ticketch.send(ctx.member.mention)
    embed = discord.Embed(
        title="チケット",
        description="下のボタンを押すとチケットが閉じます",
        color=0x5AFF19
        )
    await buttons.send(
        embed = embed,
        channel = ticketch.id,
        components = [
            ActionRow([
                    Button(
                        label="閉じる", 
                        style=ButtonType().Success,
                        custom_id="question_del",
                        disabled = False
                        )
                    ])
                ]
            )

@buttons.click
async def question_del(ctx):
    await ctx.channel.delete()
    
@bot.event
async def on_component(ctx: ComponentContext):
    if 'create' in ctx.custom_id:
        await create(ctx)
    
bot.run(Token)
