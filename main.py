#!/usr/bin/env python
# -*- coding: utf-8 -*-

from discord import Client, Activity, ActivityType, Embed, Permissions, PermissionOverwrite, ChannelType, Intents
from dotenv import load_dotenv
from random import choice, randint
import string
import os

PREFIX="tr!"

class MyClient(Client):
    async def on_ready(self):
        self.the_deleted_msg_content = ""
        self.the_deleted_msg_timestamp = None
        self.the_deleted_msg_author_id = 0
        self.threads = {}
        await self.change_presence(activity=Activity(type=ActivityType.listening, name=f"{PREFIX}help | Dm me help for help"))
        print(f"Logged in as {self.user}")


    async def on_message_delete(self, msg):
        self.the_deleted_msg_content = msg.content
        self.the_deleted_msg_author_id = msg.author.id
        self.the_deleted_msg_timestamp = f"At {msg.created_at.hour}:{msg.created_at.minute}:{msg.created_at.second}"
        print(msg.content, msg.author)


    def check_role_in_guild(self, guild, name):
        roles = guild.roles
        present = False
        for role in roles:
            if role.name == name:
                present = True

        return present


    def arr_as_str(self, arr):
        res = ""
        for i in arr:
            res += i+" "

        return res


    def get_role_id_from_name(self, guild, name):
        rid = None
        for role in guild.roles:
            if role.name == name:
                rid = role.id
        return rid

    
    def get_seed(self):
        seed = ""
        for i in range(0, randint(4, 6)):
            seed += choice(string.ascii_letters+string.digits)

        return seed


    async def on_message(self, msg):
        if msg.author == self.user:
            return

        if msg.channel.type == ChannelType.private:
            if msg.author.id in self.threads:
                await self.threads[msg.author.id].send(f"**{msg.author.name}**: {msg.content}")
            if msg.content == "help":
                await msg.reply("Creating thread")
                await self.wait_until_ready()
                guild = await self.fetch_guild(os.getenv("GUILD"))
                overwrites = {
                    guild.default_role: PermissionOverwrite(read_messages=False)
                }
                await self.wait_until_ready()
                channel = await guild.create_text_channel(name=f"{msg.author.name}-{self.get_seed()}", overwrites=overwrites)
                await channel.send(f"@here {msg.author.name} requires help")
                self.threads[msg.author.id] = channel

        if msg.mentions.count(self.user) > 1:
            await msg.reply(f"My Prefix is {PREFIX}")


        for i in self.threads:
            if msg.channel == self.threads[i]:
                user = await self.fetch_user(i)
                await user.send(f"**{msg.author.name}**: {msg.content}")

        if msg.content.startswith(PREFIX):
            if msg.channel.type == ChannelType.private:
                await msg.reply("Pls navigate to a server to use bot commands")
            else:
                msg.content = msg.content.replace(PREFIX, "").split(" ")
                command = msg.content.pop(0)
                args = msg.content

                if command == "ping":
                    await msg.reply(f"**:ping_pong: Pong** \nLatency: {round(self.latency * 100)} ms")

                if command == "close":
                    for i in self.threads:
                        if msg.channel == self.threads[i]:
                            user = await self.fetch_user(i)
                            await user.send("Thread closed!")
                            await self.threads[i].delete()
                            self.threads.pop(i)

                if command == "snipe":
                    if self.the_deleted_msg_content == "":
                        await msg.channel.send("There is nothing to snipe!")
                    else:
                        user = await self.fetch_user(self.the_deleted_msg_author_id)
                        snipe_embed = Embed(title="Snipe", description=self.the_deleted_msg_content)
                        snipe_embed.set_author(name=str(user))
                        snipe_embed.set_footer(text=self.the_deleted_msg_timestamp)
                        await msg.channel.send(embed=snipe_embed)

                if command == "kick":
                    if msg.author.guild_permissions.kick_members:
                        if len(msg.mentions) != 0:
                            try:
                                await msg.mentions[0].kick(reason=self.arr_as_str(args))
                                await msg.channel.send(f"Kicked {msg.mentions[0].name}\nReason: {self.arr_as_str(args)}")
                            except:
                                await msg.channel.send("Cannot Do that sorry")
                        else:
                            if len(args) != 0:
                                try:
                                    usr = await msg.guild.fetch_member(args.pop(0))
                                    await usr.kick(reason=self.arr_as_str(args))
                                    await msg.channel.send(f"Kicked {usr.name}\nReason: {self.arr_as_str(args)}")
                                except:
                                    await msg.channel.send("Cannot Do that sorry")
                            else:
                                await msg.channel.send("Mention someone to kick")
                    else:
                        await msg.channel.send("I'm sorry, but you do not have that authority")

                if command == "mute":
                    if msg.author.guild_permissions.manage_roles:
                        role = None
                        if self.check_role_in_guild(msg.guild, "Muted"):
                            rid = self.get_role_id_from_name(msg.guild, "Muted")
                            role = msg.guild.get_role(rid)
                        else:
                            role = await msg.guild.create_role(name="Muted", permissions=Permissions().none(), hoist=True)
                            overwrite = PermissionOverwrite(read_messages=False)
                            for channel in msg.guild.channels:
                                await channel.set_permissions(role, overwrite=overwrite)

                        if len(msg.mentions) != 0:
                            try:
                                await msg.mentions[0].add_roles(role)
                                await msg.channel.send(f"Muted {msg.mentions[0].name}")
                            except:
                                await msg.channel.send("Cannot Do that sorry")
                        else:
                            if len(args) != 0:
                                try:
                                    usr = await msg.guild.fetch_member(args.pop(0))
                                    await usr.add_roles(role)
                                    await msg.channel.send(f"Muted {usr.name}")
                                except:
                                    await msg.channel.send("Cannot Do that sorry")
                            else:
                                await msg.channel.send("Mention someone to mute")
                    else:
                        await msg.channel.send("I'm sorry, but you do not have that authority")

                if command == "unmute":
                    if msg.author.guild_permissions.manage_roles:
                        rid = self.get_role_id_from_name(msg.guild, "Muted")
                        role = msg.guild.get_role(rid)
                        if len(msg.mentions) != 0:
                            try:
                                await msg.mentions[0].remove_roles(role)
                                await msg.channel.send(f"Unmuted {msg.mentions[0].name}")
                            except:
                                await msg.channel.send("Cannot Do that sorry")
                        else:
                            if len(args) != 0:
                                try:
                                    usr = await msg.guild.fetch_member(args[0])
                                    await usr.remove_roles(role)
                                    await msg.channel.send(f"Unmuted {usr.name}")
                                except:
                                    await msg.channel.send("Cannot Do that sorry")
                            else:
                                await msg.channel.send("Mention someone to unmute")
                    else:
                        await msg.channel.send("I'm sorry, but you do not have that authority")

                if command == "ban":
                    if msg.author.guild_permissions.ban_members:
                        if len(msg.mentions) != 0:
                            try:
                                await msg.mentions[0].ban()
                                await msg.channel.send(f"Banned {msg.mentions[0].name}")
                            except:
                                await msg.channel.send("Cannot Do that sorry")
                        else:
                            if len(args) != 0:
                                try:
                                    usr = await msg.guild.fetch_member(args[0])
                                    await usr.ban()
                                except:
                                    await msg.channel.send("Cannot Do that sorry")
                            else:
                                await msg.channel.send("Mention someone to ban")
                    else:
                        await msg.channel.send("I'm sorry, but you do not have that authority")

                if command == "help":
                    help_embed = Embed(title="Help", description="Commands list\n ***t**: User mention or User id (Required)")
                    help_embed.add_field(name="Ban a user", value=f"`{PREFIX}ban *t`", inline=True)
                    help_embed.add_field(name="Kick a user", value=f"`{PREFIX}kick *t`", inline=True)
                    help_embed.add_field(name="Mute a user", value=f"`{PREFIX}mute *t`", inline=True)
                    help_embed.add_field(name="Unmute a user", value=f"`{PREFIX}unmute *t`", inline=True)
                    help_embed.add_field(name="Ping Latency", value=f"`{PREFIX}ping`", inline=True)
                    help_embed.set_footer(text=f"Requested by {msg.author}")
                    await msg.channel.send(embed=help_embed)


load_dotenv()
intents = Intents().all()
bot = MyClient(intents=intents)
bot.run(os.getenv("TOKEN"))
