# Lifese
Have you ever felt a guilty pleasure before? You know, just having fun in your free time, but feeling your conscience weighing on you because you are "*wasting time*". This usually leads to:
1) Not having fun during your free time
2) Working all the time instead, which will inevitably lead to **burnout**

If only there was a way to accurately convert your hardwork into free time.. 


**Oh, right! That's *exactly* why I made Lifese!**

# Brief Idea
You add some **missions**; tasks you want to do no matter what, such as reading a book, going for a walk, drinking enough water, etc..
On the other hand, you will also add some **offenses**; things you want to avoid, such as eating junk food, smoking, etc..

For each **mission** and **offense**, you will assign a number of **points**. Those points will be your life's currency. Each **point** is worth **10 minutes**. So if you assign 1 **point** to brushing your teeth twice a day, you get 10 minutes of free time when you do so. On the contrary, if you assign 5 **points** to smoking, you lose 50 minutes of your free time whenever you smoke. Pretty simple, yet pretty effective. This way, each time you spend your free time doing something fun, you will know why you totally deserve it!


# Working Details
Points can go from 1 through 9, so 10 minutes to 1.5 hours. You set the points according to how much you think a **mission**/**offense** is worth, and each has its **name** and **description**. You can delete them or edit them as needed, which offers versatility. When you have gathered some points, you use them by choosing how many hours, minutes, and seconds you want to spend. After that, just set a timer with that exact time and have some fun!

# Wow! So How Could This Possibly Go Wrong?
Well, there are a few concerns:

### Privacy
I have added no encryption to this bot, so all your **missions**, **offenses**, and **points** will be visible to the bot's host. This isn't much of an issue as long as you avoid sensitive information, and if you really had to add something private, you can name it using its acronym instead or a name only you would understand.

### Fairness
Even if this quantifies your hardwork and turns it into time, it isn't 100% accurate. You are still the one who chooses the points, so you can sometimes feel like you are giving yourself extra points, which will, again, lead to weighing on your conscience. A good way to beat this is by asking people you know how much they thing such a task could be worth. You could even ask ChatGPT! In any case, whenever you feel like you are giving yourself too many points, just give yourself 1 instead.

Just kidding :p
Don't go too hard on yourself; it's commendable that you're putting in so much effort in the first place!

### Commitment
Unfortunately, you can always just ditch the bot and spend your free time without caring about points. There is no way to combat this except with your conscience or accountability partners, both of which are pretty useful things to have.

In conclusion, they're all very valid problems, but can ultimately be fixed with the correct approach.

# Easter Eggs

I have always been an easter egg guy. Nothing more exciting than finding little secrets in any sort of software! That's why I have added many easter eggs in this bot and there are still more to come! If you want to find them, try not to read the code; as it will spoil them all :)

# Future Plans

- Allowing users to customize the value of a point.
- Well, that's it for now :p

# How to Host it

1) Visit [Discord's Developer Portal](https://discord.com/developers/applications) and create a discord account if you don't already have one.
2) Under **Applications**, create a new application.
3) Under **Bot**, click on **Reset Token** and save your new token somewhere; you will need it to run the bot.
4) While still under **Bot**, enable the intents **Message Content** and **Server Members**.
5) Under **OAuth2**, enable **Bot**, **Send Messages**, and **Send Messages in Threads**.
6) Using the link at the bottom of the page, invite the bot to a server you're in.
7) Run the code wherever you want. I suggest using **VSCode** for pc, and **Termux** for android. Whichever you choose, you will have to `pip install` all the imported libraries at the top of the code.
8) You will find three variables at the top of the page: **MY_ID**: the host's id to give them special permissions, **TOKEN**: the bot's token to run the bot, and **DATABASE**: the name of your database file. Just make a file called whatever.db in the same directory as your bot.
9) Enjoy :) You won't need to host the bot 24/7; you can simply run it when you need it and stop it when you're done.

**And finally, I hope this helps at least one person out there.**
