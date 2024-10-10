import discord
from discord import app_commands
from discord import ui
from discord.ext import commands
import aiosqlite

MY_ID = ... #put your id here
TOKEN = ... #put your token here as a string
DATABASE = ... #put your .db file name here as a string

#intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='@', intents=intents)

#mission modal class. you add missions here
class Mission(ui.Modal, title='New Mission'):
  mission_name = ui.TextInput(label='Mission Name',
                              style=discord.TextStyle.short, 
                              placeholder='Mission Name', 
                              required=True, 
                              max_length=20)

  mission_desc = ui.TextInput(label='Mission Description', 
                              style=discord.TextStyle.short, 
                              placeholder='Mission Description',
                              required=True, 
                              max_length=150)

  points = ui.TextInput(label='Points', 
                        placeholder='Points',
                        required=True,
                        max_length=1)

  async def on_submit(self, interaction: discord.Interaction):
    #checking if 'points' is an int
    if not self.points.value.isnumeric() or int(self.points.value) <= 0:
      embed = discord.Embed(title='Failed', 
                            color=discord.Color.red(), 
                            description='Invalid number. Please try again.')

    else:
      await self.add_mission(interaction)
      embed = discord.Embed(title='Success!', 
                            color=discord.Colour.green(), 
                            description='Mission added.')
      
    await interaction.response.send_message(embed=embed)

  async def on_error(self, interaction: discord.Interaction, error):
    print(error)

  async def add_mission(self, interaction):
    mission_name = self.mission_name.value
    id = int(interaction.user.id)
    #checking if a mission with the same name exists with linear search. complexity doesn't matter because there
    #won't be many missions anyways.
    async with bot.db.cursor() as cur:
      await cur.execute('''SELECT mission_name FROM missions WHERE user_id = ? and mission_type = 'mission' ''', (id, ))
      missions = await cur.fetchall()
      for mission in missions: 
        if mission[0].lower() == mission_name.lower():
          embed = discord.Embed(title='Invalid Name', description='Mission name already exists.', color=discord.Color.red())
          await interaction.response.send_message(embed=embed)
          return
      
    #adding the mission to the database  
    points = int(self.points.value)
    name = str(interaction.user)
    mission_desc = self.mission_desc.value
    await init_user(name, id)
    async with bot.db.cursor() as cur:
      await cur.execute('''INSERT INTO Missions (mission_type, user_id, mission_name, points, mission_desc) VALUES (?,?,?,?,?)''', 
                        ('mission', id, mission_name, points, mission_desc))
      await bot.db.commit()

#offense modal class. you add offenses here.
class Offense(ui.Modal, title='New Offense'):
  offense_name = ui.TextInput(label='Offense Name',
                              style=discord.TextStyle.short,
                              placeholder='Offense Name',
                              required=True,
                              max_length=20)

  offense_desc = ui.TextInput(label='Offense Description',
                              style=discord.TextStyle.short,
                              placeholder='Offense Description',
                              required=True,
                              max_length=150)

  points = ui.TextInput(label='Points',
                        placeholder='Points',
                        required=True,
                        max_length=1)

  async def on_submit(self, interaction: discord.Interaction):
    if not self.points.value.isnumeric() or int(self.points.value) <= 0:
      embed = discord.Embed(title='Failed',
                            color=discord.Color.red(),
                            description='Invalid number. Please try again.')

    else:
      await self.add_offense(interaction)
      embed = discord.Embed(title='Success!',
                            color=discord.Colour.green(),
                            description='Offense added.')
    await interaction.response.send_message(embed=embed)

  async def on_error(self, interaction: discord.Interaction, error):
    print(error)

  async def add_offense(self, interaction):
    offense_name = self.offense_name.value
    id = int(interaction.user.id)
    async with bot.db.cursor() as cur:
      await cur.execute(
        '''SELECT mission_name FROM missions WHERE user_id = ? and mission_type = 'offense' ''',
        (id, ))
      offenses = await cur.fetchall()
      for offense in offenses:
        if offense[0].lower() == offense_name.lower():
          embed = discord.Embed(title='Invalid Name',
                                description='Offense name already exists.',
                                color=discord.Color.red())
          await interaction.response.send_message(embed=embed)
          return
    offense_desc = self.offense_desc.value
    points = int(self.points.value)
    name = str(interaction.user)
    id = int(interaction.user.id)
    await init_user(name, id)
    async with bot.db.cursor() as cur:
      await cur.execute(
        '''INSERT INTO Missions (mission_type, user_id, mission_name, points, mission_desc) VALUES (?,?,?,?,?)''',
        ('offense', id, offense_name, points, offense_desc))
      await bot.db.commit()

#mission buttons class
class MissionButtons(discord.ui.View):
  def __init__(self, all_missions=None):
    super().__init__()
    self.value = None
    self.all_missions = all_missions
  #mission completing button  
  @discord.ui.button(label='Complete Mission', style=discord.ButtonStyle.green)
  async def menu1(self, interaction: discord.Interaction,
                  button: discord.ui.Button):
    if self.all_missions:
      await interaction.response.send_message(view=SelectViewComplete(all_missions=self.all_missions))
    
    else:
      #easter egg in the case of 0 missions  
      embed = discord.Embed(title='No missions..?', description='Seriously? I have just told you there were no missions. What are you trying to complete?', color=discord.Color.red())  
      await interaction.response.send_message(embed=embed)

  @discord.ui.button(label='Remove Mission', style=discord.ButtonStyle.red)
  async def menu2(self, interaction: discord.Interaction,
                  button: discord.ui.Button):
    if self.all_missions:
      await interaction.response.send_message(view=SelectViewRemove(all_missions=self.all_missions))
      
    else:  
      #easter egg in the case of 0 missions  
      embed = discord.Embed(title='No missions..?', description='Seriously? I have just told you there were no missions. What are you trying to remove?', color=discord.Color.red())
      await interaction.response.send_message(embed=embed)

#complete mission menu class(dropdown menu for missions)
class SelectComplete(discord.ui.Select):
  def __init__(self, all_missions=None):
    options = []
    self.all_missions = all_missions
    #all_missions: [[name,points], ...]
    #adding the missions to a dropdown list
    for mission in all_missions:
      options.append(
          discord.SelectOption(
            label=mission[0], description=f'{mission[1]} Points'))
   
    super().__init__(placeholder="Select an option",
                     max_values=1,
                     min_values=1,
                     options=options)

  async def callback(self, interaction: discord.Interaction):
    async with bot.db.cursor() as cur:
      #self.values[0]: 'name'
      mission_name = self.values[0]
      id = interaction.user.id
      #getting the user's points and the mission's points
      await cur.execute('''SELECT points FROM Missions WHERE mission_type = 'mission' AND 
                           mission_name = ? AND user_id = ?''', (mission_name, id))
      mission_points = await cur.fetchone()
      await cur.execute('SELECT points FROM Users WHERE user_id = ?', (id, ))
      user_points = await cur.fetchone()
      
      new_points = user_points[0] + mission_points[0]
      new_time = new_points * 600 #10 minutes = 600 seconds. i store time in seconds for convenience.
  
      await cur.execute(
        ''' UPDATE Users SET points = ?, completed_missions = completed_missions + 1, time = ? WHERE user_id = ?''',
        (new_points, new_time, id))
      await bot.db.commit()

      embed = discord.Embed(title='Success', description= f'Good job! You earned {mission_points[0]} point(s).',
      color=discord.Color.green())
      await interaction.response.send_message(embed=embed)

class SelectViewComplete(discord.ui.View):
  def __init__(self, *, timeout=180, all_missions=None):
    super().__init__(timeout=timeout)
    self.add_item(SelectComplete(all_missions=all_missions))

#remove mission menu class
class SelectRemove(discord.ui.Select):
  def __init__(self, all_missions=None):
      options = []
      self.all_missions = all_missions
      #all_missions: [[name,points], ...]
      for mission in all_missions:
        options.append(
            discord.SelectOption(
              label=mission[0], description=f'{mission[1]} Points'))
    
      super().__init__(placeholder="Select an option",
                      max_values=1,
                      min_values=1,
                      options=options)

  async def callback(self, interaction: discord.Interaction):
    async with bot.db.cursor() as cur:
      await cur.execute(
        '''DELETE FROM Missions WHERE user_id = ? AND mission_name = ? AND mission_type = 'mission' ''',
        (interaction.user.id, self.values[0]))
      await bot.db.commit()
      embed = discord.Embed(title='Removed',
                            description='Mission removed successfully.')
      await interaction.response.send_message(embed=embed)

class SelectViewRemove(discord.ui.View):
  def __init__(self, *, timeout=180, all_missions=None):
    super().__init__(timeout=timeout)
    self.add_item(SelectRemove(all_missions=all_missions))

#shows all your missions to pick the one you want to edit
class SelectEdit(discord.ui.Select):
  def __init__(self, edit_info=None, all_missions=None):    
    options = []
    self.info = edit_info
    #all_missions: [(mission_id, type, user_id, mission_name, mission_desc, points), ...]
    for mission in all_missions:
        options.append(
        discord.SelectOption(
        label=mission[3], description=f'{mission[5]} Points'))
            
    super().__init__(placeholder="Select an option",
                     max_values=1,
                     min_values=1,
                     options=options)

  async def callback(self, interaction: discord.Interaction):
    #self.values = ['name of the mission you chose']
    mission_name = self.values[0]
    info = self.info
    user_id = interaction.user.id
    async with bot.db.cursor() as cur:
      await cur.execute(
        '''SELECT mission_id, mission_desc, points FROM Missions WHERE mission_name = ? AND user_id = ? and mission_type = 'mission' ''',
        (mission_name, user_id))
      results_list = await cur.fetchall()
      results = results_list[0]
      
      #results looks like: [(mission_id, 'desc', points)]
      #info looks like: [name, description, points]     
      
      mission_id = results[0]
      
      old_name = mission_name
      new_name = info[0]
      
      old_desc = results[1]
      new_desc = info[1]
      
      old_points = results[2]
      new_points = info[2]
      

    async with bot.db.cursor() as cur:
      # an example to explain this:
      # if new_name is not none, then set the current name to new_name. otherwise, set it as the old name
      # or in other words, don't change it.
      await cur.execute(
        '''
      UPDATE Missions
      SET mission_name = CASE WHEN ? IS NOT 'None' THEN ? ELSE ? END,
          mission_desc = CASE WHEN ? IS NOT 'None' THEN ? ELSE ? END,
          points = CASE WHEN ? IS NOT 'None' THEN ? ELSE ? END
          WHERE mission_id = ? and mission_type = 'mission';

      ''',
        (new_name, new_name, old_name, new_desc, new_desc, old_desc, new_points, new_points,
         old_points, mission_id))
      await bot.db.commit()
    embed = discord.Embed(title='Success',
                          description='Mission edited successfully.',
                          color=discord.Color.green())
    await interaction.response.send_message(embed=embed)

class SelectViewEdit(discord.ui.View):
  def __init__(self, *, timeout=180, edit_info=None, all_missions=None):
    super().__init__(timeout=timeout)
    self.add_item(SelectEdit(edit_info=edit_info, all_missions=all_missions))

#shows all your offenses to pick the one you want to edit
class SelectEditOffense(discord.ui.Select):
  def __init__(self, edit_info=None, all_offenses=None):    
    options = []
    self.info = edit_info
    #[(mission_id, type, user_id, mission_name, mission_desc, points), ...]
    for mission in all_offenses:
        options.append(
        discord.SelectOption(
        label=mission[3], description=f'{mission[5]} Points'))
            
    super().__init__(placeholder="Select an option",
                     max_values=1,
                     min_values=1,
                     options=options)

  async def callback(self, interaction: discord.Interaction):
    #self.values = ['name of the mission you chose']
    offense_name = self.values[0]
    info = self.info
    user_id = interaction.user.id
    async with bot.db.cursor() as cur:
      await cur.execute(
        '''SELECT mission_id, mission_desc, points FROM Missions WHERE mission_name = ? AND user_id = ? and mission_type = 'offense' ''',
        (offense_name, user_id))
      results_list = await cur.fetchall()
      results = results_list[0]
      
      #results looks like: [(mission_id, 'desc', points)]
      #info looks like: [name, description, points]     
      
      mission_id = results[0]
      
      old_name = offense_name
      new_name = info[0]
      
      old_desc = results[1]
      new_desc = info[1]
      
      old_points = results[2]
      new_points = info[2]
      

    async with bot.db.cursor() as cur:
      await cur.execute(
        '''
      UPDATE Missions
      SET mission_name = CASE WHEN ? IS NOT 'None' THEN ? ELSE ? END,
          mission_desc = CASE WHEN ? IS NOT 'None' THEN ? ELSE ? END,
          points = CASE WHEN ? IS NOT 'None' THEN ? ELSE ? END
          WHERE mission_id = ? and mission_type = 'offense';

      ''',
        (new_name, new_name, old_name, new_desc, new_desc, old_desc, new_points, new_points,
         old_points, mission_id))
      await bot.db.commit()
    embed = discord.Embed(title='Success',
                          description='Offense edited successfully.',
                          color=discord.Color.green())
    await interaction.response.send_message(embed=embed)

class SelectViewEditOffense(discord.ui.View):
  def __init__(self, *, timeout=180, edit_info=None, all_offenses=None):
    super().__init__(timeout=timeout)
    self.add_item(SelectEditOffense(edit_info=edit_info, all_offenses=all_offenses))

#commit/remove offenses buttons
class OffenseButtons(discord.ui.View):
  def __init__(self, all_offenses=None):
    super().__init__()
    self.value = None
    self.all_offenses = all_offenses
  @discord.ui.button(label='Commit Offense', style=discord.ButtonStyle.green)
  async def menu1(self, interaction: discord.Interaction,
                  button: discord.ui.Button):
    if self.all_offenses:
      await interaction.response.send_message(view=SelectViewCommitOffense(all_offenses=self.all_offenses))
    else:
      embed = discord.Embed(title='No Offenses..?', description='Seriously? I have just told you there were no offenses. What are you trying to commit??', color=discord.Color.red())  
      await interaction.response.send_message(embed=embed)

  @discord.ui.button(label='Remove Offense', style=discord.ButtonStyle.red)
  async def menu2(self, interaction: discord.Interaction,
                  button: discord.ui.Button):
    if self.all_offenses:
      await interaction.response.send_message(view=SelectViewRemoveOffense(all_offenses=self.all_offenses))
    else:
      embed = discord.Embed(title='No Offenses..?', description='Seriously? I have just told you there were no offenses. What are you trying to remove??', color=discord.Color.red())
      await interaction.response.send_message(embed=embed)

#shows all your offenses to pick the one you want to commit
class SelectCommitOffense(discord.ui.Select):
  def __init__(self, all_offenses=None):
    options = []
    self.all_offenses = all_offenses
    #all_offenses: [[name,points], ...]
    for offense in all_offenses:
      options.append(
          discord.SelectOption(
            label=offense[0], description=f'{offense[1]} Points'))
   
    super().__init__(placeholder="Select an option",
                     max_values=1,
                     min_values=1,
                     options=options)

  async def callback(self, interaction: discord.Interaction):
    async with bot.db.cursor() as cur:
      #self.values[0]: 'name'
      offense_name = self.values[0]
      id = interaction.user.id
      await cur.execute('''SELECT points FROM Missions WHERE mission_type = 'offense' 
                           AND mission_name = ? AND user_id = ?''', (offense_name, id))
      offense_points = await cur.fetchone()
      await cur.execute('SELECT points FROM Users WHERE user_id = ?', (id, ))
      user_points = await cur.fetchone()
      
      new_points = user_points[0] - offense_points[0]
      new_time = new_points * 600
  
      await cur.execute(
        ''' UPDATE Users SET points = ?, commited_offenses = commited_offenses + 1, time = ? WHERE user_id = ?''',
        (new_points, new_time, id))
      await bot.db.commit()

      embed = discord.Embed(title='Done', description= f'What a disappointment. You lost {offense_points[0]} point(s).',
      color=discord.Color.red())
      await interaction.response.send_message(embed=embed)
      
class SelectViewCommitOffense(discord.ui.View):
  def __init__(self, *, timeout=180, all_offenses=None):
    super().__init__(timeout=timeout)
    self.add_item(SelectCommitOffense(all_offenses=all_offenses))

#shows all your offenses to pick the one you want to remove
class SelectRemoveOffense(discord.ui.Select):
  def __init__(self, all_offenses=None):
      options = []
      self.all_offenses= all_offenses
      #all_missions: [[name,points], ...]
      for offense in all_offenses:
        options.append(
            discord.SelectOption(
              label=offense[0], description=f'{offense[1]} Points'))
    
      super().__init__(placeholder="Select an option",
                      max_values=1,
                      min_values=1,
                      options=options)

  async def callback(self, interaction: discord.Interaction):
    async with bot.db.cursor() as cur:
      await cur.execute(
        '''DELETE FROM Missions WHERE user_id = ? AND mission_name = ? AND mission_type = 'offense' ''',
        (interaction.user.id, self.values[0]))
      await bot.db.commit()
      embed = discord.Embed(title='Removed',
                            description='Offense removed successfully.')
      await interaction.response.send_message(embed=embed)

class SelectViewRemoveOffense(discord.ui.View):
  def __init__(self, *, timeout=180, all_offenses=None):
    super().__init__(timeout=timeout)
    self.add_item(SelectRemoveOffense(all_offenses=all_offenses))
    
#onready
@bot.event
async def on_ready():
  print(f'{bot.user} has connected to Discord!')
  bot.missions = {}
  bot.db = await aiosqlite.connect(DATABASE)
  await init_db()
  try:
    synced = await bot.tree.sync()
    print(f"Synced {len(synced)} command(s)")
  except Exception as e:
    print(e)

# START #

#a debug command that removes me from the db. only i can use it (or you, if you change the constant MY_ID)
@bot.tree.command(name='angel')
async def angel(interaction: discord.Interaction):
 if interaction.user.id != MY_ID:
   await interaction.response.send_message('unauthorized')
   return

 async with bot.db.cursor() as cur:
   await cur.execute('''DELETE FROM Users WHERE user_id = ?''', (MY_ID, ))
   await bot.db.commit()
 await interaction.response.send_message('done')

@bot.tree.command(name='mission')
async def mission(interaction: discord.Interaction):
  await interaction.response.send_modal(Mission())

@bot.tree.command(name='editmission')
@app_commands.describe(n='New Name', d='New Description', p='New Points')
async def edit_mission(interaction: discord.Interaction, n: str, d: str, p: str):
  user_id = interaction.user.id
  async with bot.db.cursor() as cur:
    #getting all the missions of the user
    await cur.execute('''SELECT * FROM Missions WHERE user_id = ? AND mission_type = 'mission' ORDER BY points''', (user_id, ))
    results = await cur.fetchall()
    if not results:
        error_embed = discord.Embed(title='No Missions', 
                              description="You've got no missions to edit.",
                              color=discord.Color.red())
        await interaction.response.send_message(embed=error_embed)
        
  #checking if there's a non-integer value that's not "same".
  no = False
  if not p.isnumeric():
    if p.lower() != 'same':
      no = True
    else:
      #easter egg
      if p.lower() == d.lower() == n.lower() == 'same':
        embed = discord.Embed(title='Oh man..', description="You realize this is just a waste of time, right? Do something useful. (good job finding this ;)")
        await discord.response.send_message(embed=embed)
        return
  #checking if the user wants more points than 9
  elif int(p) > 9:
    no = True
  if no:
    int_error_embed = discord.Embed(title='Invalid Input', 
                                description="Points should be an integer between 0 and 10 or 'same'.",
                                color=discord.Color.red())
    await interaction.response.send_message(embed=int_error_embed)
    return
  info = {}
  args = {'n': n, 'd': d, 'p': p}
  info = []
  for arg in args.keys():
    if args[arg].lower() == 'same':
      info.append(None)
    else:
      info.append(args[arg])
      #info: [name, description, points] 
  await interaction.response.send_message(view=SelectViewEdit(edit_info=info, all_missions=results))

@bot.tree.command(name='offense')
async def offense(interaction: discord.Interaction):
  await interaction.response.send_modal(Offense())


@bot.tree.command(name='editoffense')
@app_commands.describe(n='New Name', d='New Description', p='New Points')
async def edit_offense(interaction: discord.Interaction, n: str, d: str, p: str):
  user_id = interaction.user.id
  async with bot.db.cursor() as cur:
    #getting all the offenses of the user
    await cur.execute('''SELECT * FROM Missions WHERE user_id = ? AND mission_type = 'offense' ORDER BY points''', (user_id, ))
    results = await cur.fetchall()
    if not results:
        empty_error_embed = discord.Embed(title='No Offenses', 
                                description="You've got no offenses to edit.",
                                color=discord.Color.red())
        await interaction.response.send_message(embed=empty_error_embed)
        return
    
  #checking if there's a non-integer value that's not "same".
  no = False
  if not p.isnumeric():
    if p.lower() != 'same':
      no = True
    else:
      #easter egg
      if p.lower() == d.lower() == n.lower() == 'same':
        embed = discord.Embed(title='Oh man..', description="You realize this is just a waste of time, right? Do something useful. (good job finding this ;)")
        await discord.response.send_message(embed=embed)
        return
      
  #checking if the user wants more points than 9
  elif int(p) > 9:
    no = True
  if no:
    int_error_embed = discord.Embed(title='Invalid Input', 
                              description="Points should be an integer between 0 and 10 or 'same'.",
                              color=discord.Color.red())
    await interaction.response.send_message(embed=int_error_embed)
    return

  info = {}
  args = {'n': n, 'd': d, 'p': p}
  info = []
  for arg in args.keys():
    if args[arg].lower() == 'same':
      info.append(None)
    else:
      info.append(args[arg])
      #info: [name, description, points]   
  await interaction.response.send_message(view=SelectViewEditOffense(edit_info=info, all_offenses=results))

@bot.tree.command(name='missions')
async def missions(interaction: discord.Interaction):
  embed = discord.Embed()
  all_missions = []
  async with bot.db.cursor() as cur:
    id = interaction.user.id
    await cur.execute(
      '''SELECT * FROM Missions WHERE user_id = ? AND mission_type = 'mission' ORDER BY points''', (id, ))
    results = await cur.fetchall()
    if not results:
      embed = discord.Embed(title='Mission List',
                          description='You have no missions. Do /mission to add one.',
                          color=discord.Color.blue())
    else:  
      embed = discord.Embed(title='Mission List',
                            color=discord.Color.blue())
      for mission in results:
          name = mission[3]
          points = mission[5]
          desc = mission[4]
          all_missions.append([name, points])
          name += f' --- {points}P -> {points * 10} Minutes'
          embed.add_field(name=name, value=desc, inline=False)    
          
  await interaction.response.send_message(embed=embed, view=MissionButtons(all_missions=all_missions))

@bot.tree.command(name='offenses')
async def offenses(interaction: discord.Interaction):
  embed = discord.Embed()
  all_offenses = []
  async with bot.db.cursor() as cur:
    id = interaction.user.id
    await cur.execute(
      '''SELECT * FROM Missions WHERE user_id = ? AND mission_type = 'offense' ORDER BY points''',
      (id,))
    results = await cur.fetchall()
    if not results:
      embed = discord.Embed(title='Offense List', description='You have no offenses. Do /offense to add one.')
    else:  
      embed = discord.Embed(title='Offense List', color=discord.Color.blue())
      for offense in results:
          name = offense[3]
          points = offense[5]
          desc = offense[4]
          all_offenses.append([name, points])
          name += f' --- {points}P -> {points * 10} Minutes'
          embed.add_field(name=name, value=desc, inline=False)
    await interaction.response.send_message(embed=embed, view=OffenseButtons(all_offenses=all_offenses))

@bot.tree.command(name='profile')
async def profile(interaction: discord.Interaction):
  name = interaction.user
  id = name.id
  avatar = name.avatar
  title = f"{name.name}'s Profile"
  await init_user(name, id)
  async with bot.db.cursor() as cur:
    await cur.execute(
      '''SELECT points, completed_missions, commited_offenses, time FROM Users WHERE user_id = ?''',
      (id, ))
    results = await cur.fetchall()
  points = results[0][0]
  time = results[0][3]


  if time:
    if time <= 0:
      time = '-' + await format_seconds(-time)
    else:
      time = await format_seconds(time)
  offenses_commited = results[0][2]
  missions_completed = results[0][1]
  
  if points < 0:
    description = 'Your balance is in the negative. Shame on you.'
  if points == 0:
    description = 'Zero points accumulated. Start accomplishing missions.'
  if points > 0:
    description = 'Keep it up.'

  embed = discord.Embed(title=title,
                        description=description,
                        color=discord.Color.blue())
  embed.set_thumbnail(url=avatar.url)

  embed.add_field(name="Points", value=points, inline=True)

  embed.add_field(name="Missions Completed",
                  value=missions_completed,
                  inline=True)
  embed.add_field(name="Offenses Commited",
                  value=offenses_commited,
                  inline=True)
  embed.add_field(name="Time", value=time, inline=False)

  await interaction.response.send_message(embed=embed)

@bot.tree.command(name='usetime')
@app_commands.describe(h='Hours', m='Minutes', s='Seconds')
async def use_time(interaction: discord.Interaction, h: int, m: int, s: int):
  id = interaction.user.id
  await init_user(interaction.user, id)
  async with bot.db.cursor() as cur:
    await cur.execute('''SELECT time FROM users WHERE user_id = ?''', (id, ))
    time_unclean = await cur.fetchone()
    time = time_unclean[0]
    if time < 0:
      embed = discord.Embed(title='You are literally in debt', description='What are you trying to use? You have negative time.. Go do some missions.')
      await interaction.response.send_message(embed=embed)
    time2 = (h * 3600) + (m * 60) + s
    if h < 0 or m < 0 or s < 0:
      embed = discord.Embed(title='Huh?',
                            description="Negative.. time..? Are you possibly trying to lose your time? Is this masochism? Well, you do you, but I am not adding this feature.", color = discord.Colour.dark_red())
    elif time2 == 0:  
      embed = discord.Embed(title='Are you bored?', description="I can't blame you, I like checking stuff like this as well..", color = discord.Colour.dark_red())
      
    elif time2 > time:
      embed = discord.Embed(title='Not enough time', description=f'You currently have: {await format_seconds(time)}.')
      
    else:
      new_time = time - time2
      await cur.execute('''UPDATE Users SET time = ? WHERE user_id = ? ''',
                        (new_time, id))
      await bot.db.commit()
      time = await format_seconds(new_time)
      embed = discord.Embed(title='Success',
                            description=f'You currently have: {time}.',
                            color=discord.Color.green())
      embed.set_footer(
        text=
        f'Remember to set a timer on {h} hours, {m} minutes and {s} seconds.')
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='help')
async def help(interaction: discord.Interaction):
  await init_user(interaction.user, interaction.user.id)
  embed = discord.Embed(
    title="LIFESE",
    description=
    "Welcome to Lifese! This bot is designed to help you track your real-life tasks, earn points for completing them, and buy free time with your hard-earned points. Each point is worth 10 minutes. It's a great way to stay organized and motivated!",
    color=discord.Color.blue())

  embed.add_field(name="Commands", value="Here are the available commands:")

  embed.add_field(name="/mission", value="Create a new mission.")

  embed.add_field(name="/offense", value="Create a new offense.")

  embed.add_field(name="/missions",
                  value="Retrieve a list of assigned missions.")

  embed.add_field(name="/offenses", value="View a list of offenses to avoid.")

  embed.add_field(name="/profile", value="Check your user profile.")

  embed.add_field(
    name="/editmission [name] [desc] [points]",
    value="Edit a mission. Use 'same' to keep the current value.")

  embed.add_field(
    name="/editoffense [name] [desc] [points]",
    value="Edit an offense. Use 'same' to keep the current value.")

  embed.add_field(name="/usetime [hours] [minutes] [seconds]",
                  value="Use some of your deserved free time.")

  copyright = "©"
  trademark = "™"
  service_mark = "℠"
  registered_trademark = "®"
  copyleft = "ↄ"
  sound_recording_copyright = "℗"
  patent = "ⓟ"

  symbols = copyright + trademark + service_mark + registered_trademark + copyleft + sound_recording_copyright + patent
  embed.set_footer(text=f'Made by Lethargy{symbols}.')
  embed.set_thumbnail(url=bot.user.avatar)

  await interaction.response.send_message(embed=embed)
#sends a message with all the data in the database. used for debugging or fun
@bot.tree.command(name='reveal')
async def reveal(interaction: discord.Interaction):
  if interaction.user.id != MY_ID:
    await interaction.response.send_message('unauthorized')
    return
  async with bot.db.cursor() as cur:
    await cur.execute('''SELECT user_id, mission_type, mission_name, points FROM Missions''')
    missions = await cur.fetchall()
    missions = sorted(missions)

    message = ''
    last_id = None
    for id, type, name, points in missions:
      if last_id != id:
        message += '-------\n'
        last_id = id
        message += f'*{id}*\n'  
      message += f'{type} - {name} - {points}P\n'
    await interaction.response.send_message(message)

async def init_db():
  async with bot.db.cursor() as cur:
    await cur.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            user_id BIGINT PRIMARY KEY,
            username TEXT NOT NULL,
            points INT DEFAULT 0,
            time INT DEFAULT 0,
            completed_missions INT DEFAULT 0,
            commited_offenses INT DEFAULT 0
        )
        ''')

    await cur.execute('''
        CREATE TABLE IF NOT EXISTS Missions (
            mission_id INTEGER PRIMARY KEY AUTOINCREMENT,
            mission_type TEXT,
            user_id BIGINT,
            mission_name TEXT NOT NULL,
            mission_desc TEXT NOT NULL,
            points INT,
            FOREIGN KEY (user_id) REFERENCES Users(user_id)            
        ) 
        ''')

  await bot.db.commit()

async def empty_error(interaction, thing):
    embed = discord.Embed(title='Empty', description=f'There are no {thing}s.')
    interaction.response.send_message(embed=embed)
    
async def init_user(name, id):
  async with bot.db.cursor() as cur:
    await cur.execute("SELECT user_id FROM Users WHERE user_id = ?",
                      (int(id), ))
    result = await cur.fetchone()
    if result:
      return
    else:
      await cur.execute('INSERT into Users (username, user_id) VALUES(?,?)',
                        (str(name), int(id)))
      await bot.db.commit()

async def format_seconds(seconds):
  hours = seconds // 3600
  minutes = (seconds % 3600) // 60
  seconds = (seconds % 3600) % 60
  return f"{hours}h {minutes}m {seconds}s"

bot.run(TOKEN)
