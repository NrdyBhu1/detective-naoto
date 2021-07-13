#!/usr/bin/env python
# -*- coding: utf-8 -*-

from discord import Client, Activity, ActivityType, Embed, Permissions, PermissionOverwrite, ChannelType 
from dotenv import load_dotenv
import os

PREFIX="tr!"

class MyClient(Client):
    async def on_ready(self):
        self.the_deleted_msg_content = ""
        self.the_deleted_msg_timestamp = None
        self.the_deleted_msg_author_id = 0
        await self.change_presence(activity=Activity(type=ActivityType.listening, name="tr!help | Dm me for help"))
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

    def get_role_id_from_name(self, guild, name):
        rid = None
        for role in guild.roles:
            if role.name == name:
                rid = role.id
        return rid 


    async def on_message(self, msg):
        if msg.author == self.user:
            return

        if msg.mentions.count(self.user) > 1:
            await msg.reply(f"My Prefix is {PREFIX}")

        if msg.content.startswith(PREFIX):
            if msg.channel.type == ChannelType.private:
                await msg.reply("Pls navigate to a server to use bot commands")
            else:
                msg.content = msg.content.replace(PREFIX, "").split(" ")
                command = msg.content.pop(0)
                args = msg.content

                if command == "ping":
                    await msg.reply(f"**:ping_pong: Pong** \nLatency: {round(self.latency * 100)} ms")

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
                                await msg.mentions[0].kick()
                                await msg.channel.send(f"Kicked {msg.mentions[0].name}")
                            except:
                                await msg.channel.send("Cannot Do that sorry")
                        else:
                            if len(args) != 0:
                                try:
                                    usr = await msg.guild.fetch_member(args[0])
                                    await usr.kick()
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
                            overwrite = PermissionOverwrite().from_pair(Permissions().none(), Permissions().all())
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
                                    usr = await msg.guild.fetch_member(args[0])
                                    await usr.add_roles(role)
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
                    help_embed.add_field(name="Ban a user", value="`tr!ban *t`", inline=True)
                    help_embed.add_field(name="Kick a user", value="`tr!kick *t`", inline=True)
                    help_embed.add_field(name="Mute a user", value="`tr!mute *t`", inline=True)
                    help_embed.add_field(name="Unmute a user", value="`tr!unmute *t`", inline=True)
                    help_embed.add_field(name="Ping Latency", value="`tr!ping`", inline=True)
                    help_embed.set_footer(text=f"Requested by {msg.author}")
                    await msg.channel.send(embed=help_embed)


load_dotenv()
bot = MyClient()

bot.run(os.getenv("TOKEN"))
