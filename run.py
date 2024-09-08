import discord
from discord.ext import commands
from discord import app_commands

print("""██╗░░██╗██╗░░░██╗██████╗░░█████╗░███╗░░░███╗██╗██╗░██████╗  ░██████╗████████╗██╗░░░██╗██████╗░██╗██████╗░
██║░██╔╝██║░░░██║██╔══██╗██╔══██╗████╗░████║██║╚█║██╔════╝  ██╔════╝╚══██╔══╝██║░░░██║██╔══██╗██║██╔══██╗
█████═╝░██║░░░██║██████╔╝██║░░██║██╔████╔██║██║░╚╝╚█████╗░  ╚█████╗░░░░██║░░░██║░░░██║██████╔╝██║██║░░██║
██╔═██╗░██║░░░██║██╔══██╗██║░░██║██║╚██╔╝██║██║░░░░╚═══██╗  ░╚═══██╗░░░██║░░░██║░░░██║██╔═══╝░██║██║░░██║
██║░╚██╗╚██████╔╝██║░░██║╚█████╔╝██║░╚═╝░██║██║░░░██████╔╝  ██████╔╝░░░██║░░░╚██████╔╝██║░░░░░██║██████╔╝
╚═╝░░╚═╝░╚═════╝░╚═╝░░╚═╝░╚════╝░╚═╝░░░░░╚═╝╚═╝░░░╚═════╝░  ╚═════╝░░░░╚═╝░░░░╚═════╝░╚═╝░░░░░╚═╝╚═════╝░

██████╗░░█████╗░████████╗
██╔══██╗██╔══██╗╚══██╔══╝
██████╦╝██║░░██║░░░██║░░░
██╔══██╗██║░░██║░░░██║░░░
██████╦╝╚█████╔╝░░░██║░░░
╚═════╝░░╚════╝░░░░╚═╝░░░""")

intents = discord.Intents.default()
intents.bans = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    await bot.tree.sync()

@bot.tree.command(name="massunb", description="Unban all banned users")
@app_commands.checks.has_permissions(administrator=True)
async def massunb(interaction: discord.Interaction):
    await interaction.response.send_message("Working...", ephemeral=True)
    guild = interaction.guild
    
    if not guild.me.guild_permissions.ban_members:
        await interaction.followup.send("Bot does not have permission to unban members.", ephemeral=True)
        return
    
    banned_users = [entry async for entry in guild.bans()]

    for entry in banned_users:
        user = entry.user
        try:
            await guild.unban(user)
            print(f'Unbanned {user.name}#{user.discriminator}')
        except discord.Forbidden:
            print(f'Failed to unban {user.name}#{user.discriminator}: Insufficient permissions')
        except discord.HTTPException as e:
            print(f'Failed to unban {user.name}#{user.discriminator}: HTTP exception {e}')

    await interaction.followup.send('Unbanning process completed.')

@bot.tree.command(name="noroles4u", description="Removes all roles from a user")
@app_commands.describe(user="The user to remove roles from")
@app_commands.checks.has_permissions(administrator=True)
async def noroles4u(interaction: discord.Interaction, user: discord.Member):
    await interaction.response.send_message("Working...", ephemeral=True)
    if user == interaction.guild.owner:
        await interaction.followup.send("You can't remove roles from the server owner.", ephemeral=True)
        return

    roles = user.roles[1:]
    if not roles:
        await interaction.followup.send(f"{user.display_name} has no roles to remove.", ephemeral=True)
        return

    try:
        for role in roles:
            await user.remove_roles(role)
        await interaction.followup.send(f"Removed all roles from {user.display_name}.", ephemeral=True)
        print(f'Removed all roles from {user.name}#{user.discriminator}')
    except discord.Forbidden:
        await interaction.followup.send("Insufficient permissions to remove some roles.", ephemeral=True)
        print(f"Failed to remove roles from {user.name}#{user.discriminator}: Insufficient permissions")
    except discord.HTTPException as e:
        await interaction.followup.send(f"An error occurred while removing roles: {e}", ephemeral=True)
        print(f"Failed to remove roles from {user.name}#{user.discriminator}: HTTP exception {e}")

@bot.tree.command(name="giveallroles", description="Gives all roles in the server to a user")
@app_commands.describe(user="The user to assign all roles to")
@app_commands.checks.has_permissions(administrator=True)
async def giveallroles(interaction: discord.Interaction, user: discord.Member):
    await interaction.response.send_message("Working...", ephemeral=True)
    guild = interaction.guild
    all_roles = guild.roles[1:]

    roles_added = []
    roles_failed = []

    for role in all_roles:
        try:
            await user.add_roles(role)
            roles_added.append(role)
            print(f"Successfully gave role {role.name} to {user.name}#{user.discriminator}")
        except discord.Forbidden:
            roles_failed.append(role)
            print(f"Failed to give role {role.name} to {user.name}#{user.discriminator}: Insufficient permissions")
        except discord.HTTPException as e:
            roles_failed.append(role)
            print(f"Failed to give role {role.name} to {user.name}#{user.discriminator}: HTTP exception {e}")

    added_count = len(roles_added)
    failed_count = len(roles_failed)

    success_message = f"Gave {added_count} roles to {user.display_name}."
    if failed_count > 0:
        success_message += f" {failed_count} roles could not be assigned due to permission issues or other errors."

    await interaction.followup.send(success_message, ephemeral=True)

@bot.tree.command(name="masskick", description="Kick all members except administrators and specified roles")
@app_commands.checks.has_permissions(administrator=True)
async def masskick(interaction: discord.Interaction):
    await interaction.response.send_message("Working...", ephemeral=True)
    guild = interaction.guild
    
    if not guild.me.guild_permissions.kick_members:
        await interaction.followup.send("Bot does not have permission to kick members.", ephemeral=True)
        return
    
    roles_to_exclude = [role.id for role in guild.roles if role.permissions.administrator]

    for member in guild.members:
        if any(role.id in roles_to_exclude for role in member.roles):
            continue
        try:
            await member.kick(reason="Mass kick")
            print(f'Kicked {member.name}#{member.discriminator}')
        except discord.Forbidden:
            print(f'Failed to kick {member.name}#{member.discriminator}: Insufficient permissions')
        except discord.HTTPException as e:
            print(f'Failed to kick {member.name}#{member.discriminator}: HTTP exception {e}')
    
    await interaction.followup.send("Mass kick process completed.")

@bot.tree.command(name="massrole", description="Assign a specific role to all members")
@app_commands.describe(role="The role to assign to all members")
@app_commands.checks.has_permissions(administrator=True)
async def massrole(interaction: discord.Interaction, role: discord.Role):
    await interaction.response.send_message("Working...", ephemeral=True)
    guild = interaction.guild
    
    if not guild.me.guild_permissions.manage_roles:
        await interaction.followup.send("Bot does not have permission to manage roles.", ephemeral=True)
        return

    members_failed = []

    for member in guild.members:
        if role in member.roles:
            continue
        try:
            await member.add_roles(role)
            print(f'Assigned role {role.name} to {member.name}#{member.discriminator}')
        except discord.Forbidden:
            members_failed.append(member)
            print(f'Failed to assign role {role.name} to {member.name}#{member.discriminator}: Insufficient permissions')
        except discord.HTTPException as e:
            members_failed.append(member)
            print(f'Failed to assign role {role.name} to {member.name}#{member.discriminator}: HTTP exception {e}')
    
    await interaction.followup.send(f"Assigned role {role.name} to all members. {len(members_failed)} failed.")

@bot.tree.command(name="massmessage", description="Send a message to all members")
@app_commands.describe(message="The message to send to all members")
@app_commands.checks.has_permissions(administrator=True)
async def massmessage(interaction: discord.Interaction, message: str):
    await interaction.response.send_message("Working...", ephemeral=True)
    guild = interaction.guild
    
    for member in guild.members:
        try:
            await member.send(message)
            print(f'Sent message to {member.name}#{member.discriminator}')
        except discord.Forbidden:
            print(f'Failed to send message to {member.name}#{member.discriminator}: Insufficient permissions')
        except discord.HTTPException as e:
            print(f'Failed to send message to {member.name}#{member.discriminator}: HTTP exception {e}')
    
    await interaction.followup.send("Mass message process completed.")

@bot.tree.command(name="massnick", description="Change the nickname of all members")
@app_commands.describe(nickname="The new nickname to set for all members")
@app_commands.checks.has_permissions(administrator=True)
async def massnick(interaction: discord.Interaction, nickname: str):
    await interaction.response.send_message("Working...", ephemeral=True)
    guild = interaction.guild
    
    if len(nickname) > 32:
        await interaction.followup.send("Nickname must be 32 characters or fewer.", ephemeral=True)
        return
    
    members_failed = []

    for member in guild.members:
        try:
            await member.edit(nick=nickname)
            print(f'Changed nickname of {member.name}#{member.discriminator} to {nickname}')
        except discord.Forbidden:
            members_failed.append(member)
            print(f'Failed to change nickname of {member.name}#{member.discriminator}: Insufficient permissions')
        except discord.HTTPException as e:
            members_failed.append(member)
            print(f'Failed to change nickname of {member.name}#{member.discriminator}: HTTP exception {e}')
    
    await interaction.followup.send(f"Changed nickname of all members. {len(members_failed)} failed.")

@bot.tree.command(name="masschannelcreate", description="Create a specified number of channels with a specified name")
@app_commands.describe(name="The name of the channels to create", count="The number of channels to create")
@app_commands.checks.has_permissions(administrator=True)
async def masschannelcreate(interaction: discord.Interaction, name: str, count: int):
    await interaction.response.send_message("Working...", ephemeral=True)
    guild = interaction.guild
    
    if count < 1 or count > 100:
        await interaction.followup.send("Please specify a number between 1 and 100.", ephemeral=True)
        return
    
    if len(name) > 100:
        await interaction.followup.send("Channel name must be 100 characters or fewer.", ephemeral=True)
        return
    
    channels_created = 0
    channels_failed = []

    for _ in range(count):
        try:
            await guild.create_text_channel(name)
            channels_created += 1
            print(f'Created channel: {name}')
        except discord.Forbidden:
            channels_failed.append(name)
            print(f'Failed to create channel {name}: Insufficient permissions')
        except discord.HTTPException as e:
            channels_failed.append(name)
            print(f'Failed to create channel {name}: HTTP exception {e}')
    
    success_message = f"Created {channels_created} channels with the name '{name}'."
    if channels_failed:
        success_message += f" Failed to create {len(channels_failed)} channels due to errors."

    await interaction.followup.send(success_message, ephemeral=True)

bot.run('nope')
