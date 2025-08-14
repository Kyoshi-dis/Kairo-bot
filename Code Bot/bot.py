import os
import discord
import asyncio
import datetime
import aiohttp
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from keep_alive import keep_alive

# === Load biến môi trường ===
load_dotenv()
TOKEN = os.getenv("TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", 1197904651010449530))

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

bot = commands.Bot(command_prefix="k.", intents=intents, help_command=None)

spam_running = False
# === Owo Auto Farm ===
@bot.command(name="run")
async def run_spam(ctx):
    global spam_running
    if ctx.author.id != OWNER_ID:
        await ctx.send("❌ Bạn không có quyền.")
        return
    if spam_running:
        await ctx.send("⚠️ Bot đang chạy spam rồi!")
        return

    spam_running = True
    await ctx.send("🚀 Đã bật chế độ Auto Farm OwO")

    token_other_bot = "MTE5NzkwNDY1MTAxMDQ0OTUzMA.GZlxRE.0Sl_OEOEc-Y5WZWVpgMKDA7-lX1bEtniuv7qpY"
    channel_id = "1367017459374096425"
    messages = ["oh", "ob", "owo"]

    async with aiohttp.ClientSession() as session:
        while spam_running:
            for content in messages:
                if not spam_running:
                    break
                try:
                    async with session.post(
                        f"https://hrv-api.vercel.app/api/discord?path=channels/{channel_id}/messages",
                        json={"content": content},
                        headers={
                            "Content-Type": "application/json",
                            "Authorization": token_other_bot
                        }
                    ) as resp:
                        if resp.status != 200:
                            print(f"Lỗi gửi tin: {resp.status}")
                        else:
                            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Đã gửi: {content}")
                except Exception as e:
                    print(f"Lỗi: {e}")
                await asyncio.sleep(1)  # 1 giây giữa các tin

            await asyncio.sleep(20)  # 20 giây giữa các vòng

@bot.command(name="stop")
async def stop_spam(ctx):
    global spam_running
    if ctx.author.id != OWNER_ID:
        await ctx.send("❌ Bạn không có quyền.")
        return
    if not spam_running:
        await ctx.send("⚠️ Bot chưa chạy spam.")
        return

    spam_running = False
    await ctx.send("🛑 Đã tắt chế độ Auto Farm OwO")

# === Slash: /servers ===
@bot.tree.command(name="servers", description="Xem danh sách server bot đang ở")
async def slash_servers(interaction: discord.Interaction):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("❌ Bạn không có quyền.", ephemeral=True)
        return
    msg = "\n".join([f"- {g.name} (`{g.id}`)" for g in bot.guilds])
    await interaction.response.send_message(f"📋 Server bot đang tham gia:\n{msg}", ephemeral=True)

# === Slash: /help ===
@bot.tree.command(name="help", description="Xem hướng dẫn")
async def slash_help(interaction: discord.Interaction):
    await interaction.response.send_message("📘 Dùng `k.help` để xem chi tiết các lệnh!", ephemeral=True)

# === Slash: /addrole ===
@bot.tree.command(name="addrole", description="Thêm role cho user")
@app_commands.describe(member="Thành viên", role="Vai trò cần thêm")
async def add_role(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message("❌ Bạn không có quyền `Quản lý vai trò`.", ephemeral=True)
        return
    try:
        await member.add_roles(role)
        await interaction.response.send_message(f"✅ Đã thêm role **{role.name}** cho {member.mention}")
    except Exception as e:
        await interaction.response.send_message(f"❌ Lỗi: {e}", ephemeral=True)

# === Slash: /ban ===
@app_commands.describe(user="Người dùng (ping hoặc ID)", reason="Lý do ban")
@bot.tree.command(name="ban", description="Ban một người dùng (có thể không còn trong server)")
async def slash_ban(interaction: discord.Interaction, user: discord.User, reason: str = "Không có lý do"):
    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message("❌ Bạn không có quyền ban thành viên.", ephemeral=True)
        return
    try:
        await interaction.guild.ban(user, reason=reason)
        await interaction.response.send_message(f"⛔ `{user}` đã bị ban. Lý do: {reason}")
    except discord.Forbidden:
        await interaction.response.send_message("❌ Bot không đủ quyền để ban người này.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Lỗi: {e}", ephemeral=True)

# === Slash: /kick ===
@app_commands.describe(user="Người dùng (ping hoặc ID)", reason="Lý do kick")
@bot.tree.command(name="kick", description="Kick một thành viên khỏi server")
async def slash_kick(interaction: discord.Interaction, user: discord.User, reason: str = "Không có lý do"):
    if not interaction.user.guild_permissions.kick_members:
        await interaction.response.send_message("❌ Bạn không có quyền kick thành viên.", ephemeral=True)
        return
    member = interaction.guild.get_member(user.id)
    if member is None:
        await interaction.response.send_message("❌ Người này không còn trong server.", ephemeral=True)
        return
    try:
        await member.kick(reason=reason)
        await interaction.response.send_message(f"👢 `{user}` đã bị kick. Lý do: {reason}")
    except discord.Forbidden:
        await interaction.response.send_message("❌ Bot không đủ quyền để kick người này.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Lỗi: {e}", ephemeral=True)

# === Slash: /unban ===
@bot.tree.command(name="unban", description="Unban người dùng bằng ID")
@app_commands.describe(user_id="ID của người dùng cần unban")
async def slash_unban(interaction: discord.Interaction, user_id: str):
    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message("❌ Bạn không có quyền unban thành viên.", ephemeral=True)
        return
    try:
        uid = int(user_id)
        async for ban_entry in interaction.guild.bans():
            if ban_entry.user.id == uid:
                await interaction.guild.unban(ban_entry.user)
                await interaction.response.send_message(f"✅ Đã unban: `{ban_entry.user}`")
                return
        await interaction.response.send_message("❌ Không tìm thấy người dùng trong danh sách bị ban.", ephemeral=True)
    except ValueError:
        await interaction.response.send_message("❌ ID phải là số nguyên hợp lệ.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Lỗi: {e}", ephemeral=True)

# === Slash:/mute ===
@bot.tree.command(name="mute", description="Mute một thành viên")
@app_commands.describe(member="Thành viên cần mute", reason="Lý do mute")
async def slash_mute(interaction: discord.Interaction, member: discord.Member, reason: str = "Không có lý do"):
    if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message("❌ Bạn không có quyền `Quản lý vai trò`.", ephemeral=True)
        return
    muted_role = discord.utils.get(interaction.guild.roles, name="Muted")
    if not muted_role:
        try:
            muted_role = await interaction.guild.create_role(name="Muted", reason="Tạo role để mute")
            for channel in interaction.guild.channels:
                await channel.set_permissions(muted_role, send_messages=False, speak=False)
        except Exception as e:
            await interaction.response.send_message(f"❌ Không thể tạo role Muted: {e}", ephemeral=True)
            return
    await member.add_roles(muted_role, reason=reason)
    await interaction.response.send_message(f"🔇 `{member}` đã bị mute. Lý do: {reason}")

# === Slash:/unmute ===
@bot.tree.command(name="unmute", description="Bỏ mute một thành viên")
@app_commands.describe(member="Thành viên cần unmute")
async def slash_unmute(interaction: discord.Interaction, member: discord.Member):
    if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message("❌ Bạn không có quyền `Quản lý vai trò`.", ephemeral=True)
        return
    muted_role = discord.utils.get(interaction.guild.roles, name="Muted")
    if not muted_role:
        await interaction.response.send_message("❌ Không tìm thấy role 'Muted'.", ephemeral=True)
        return
    await member.remove_roles(muted_role)
    await interaction.response.send_message(f"🔈 `{member}` đã được unmute.")

# === Command: help ===
@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="📘 Danh sách lệnh của bot",
        description="Prefix: `k.` | Dùng `k.help` để xem hướng dẫn.",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="🛠️ Quản trị server",
        value="`k.lock`, `k.unlock`, `k.clear`, `k.ban | /ban`, `k.kick | /kick`, `/addrole`, `k.unban | /unban`",
        inline=False
    )
    embed.add_field(
        name="⚙️ Khác",
        value="`k.ping`, `k.create_invite [guild_id]`, `k.run`, `k.stop`",
        inline=False
    )
    embed.set_footer(text="Bot hỗ trợ điều hành server • Kairo Bot")
    await ctx.send(embed=embed)

# === Ping ===
@bot.command()
async def ping(ctx):
    await ctx.send(f"Pong! `{round(bot.latency*1000)}ms`")

# === Create Invite ===
@bot.command()
async def create_invite(ctx, guild_id: int):
    if ctx.author.id != OWNER_ID:
        await ctx.send("❌ Bạn không có quyền.")
        return
    guild = bot.get_guild(guild_id)
    if not guild:
        await ctx.send("❌ Bot không ở trong server này.")
        return
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).create_instant_invite:
            try:
                invite = await channel.create_invite(max_age=300)
                await ctx.send(f"📨 Link mời từ `{guild.name}`:\n{invite.url}")
                return
            except:
                continue
    await ctx.send("❌ Không thể tạo invite.")

# === Clear ===
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 10):
    deleted = await ctx.channel.purge(limit=amount+1)
    await ctx.send(f"🧹 Đã xóa {len(deleted)-1} tin nhắn.", delete_after=5)

# ===Trạng thái bot===
@bot.event
async def on_ready():
    """
    Sự kiện này sẽ chạy khi bot kết nối thành công.
    """
    print(f'Đã đăng nhập với tư cách {bot.user}')

    # Đặt trạng thái bot là "Đang stream"
    # Thay 'URL_STREAM_CỦA_BẠN' bằng một đường link stream bất kỳ, ví dụ Twitch, YouTube...
    # Nếu bạn không có, có thể dùng một URL giả như "https://www.twitch.tv/discord"
    stream_url = "https://www.twitch.tv/discord" 
    
    # Thiết lập trạng thái hoạt động của bot
    activity = discord.Streaming(name="/help | k.help", url=stream_url)
    
    # Cập nhật trạng thái cho bot
    await bot.change_presence(activity=activity)
    
    print("Trạng thái bot đã được cập nhật thành 'Đang stream'")

# === Khởi động server giữ bot chạy ===
keep_alive()

bot.run(TOKEN)
