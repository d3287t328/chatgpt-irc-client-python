import openai
import logging
import socket
import ssl
import time
import configparser

# Read configuration from file
config = configparser.ConfigParser()
config.read('chat.conf')

# Set up OpenAI API key
openai.api_key = config.get('openai', 'api_key')

# Set up IRC connection settings
server = config.get('irc', 'server')
port = config.getint('irc', 'port')
usessl = config.getboolean('irc', 'ssl')
channels = config.get('irc', 'channels').split(',')
nickname = config.get('irc', 'nickname')
ident = config.get('irc', 'ident')
realname = config.get('irc', 'realname')
password = config.get('irc', 'password')

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

def connect(server, port, usessl, password, ident, realname, nickname, channels):
    while True:
        try:
            logger.info(f"Connecting to: {server}")
            irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if usessl:
                context = ssl.create_default_context()
                irc = context.wrap_socket(irc, server_hostname=server)
            irc.connect((server, port))
            irc.send(f"NICK {nickname}\r\n".encode("UTF-8"))
            irc.send(f"USER {ident} 0 * :{realname}\r\n".encode("UTF-8"))
            if password:
                irc.send(f"PASS {password}\r\n".encode("UTF-8"))
            for channel in channels:
                irc.send(f"JOIN {channel}\r\n".encode("UTF-8"))
            return irc
        except Exception as e:
            logger.error("Connection failed: %s. Retrying in 5 seconds...", e)
            time.sleep(5)

def process_message(data):
    try:
        return data.split("PRIVMSG", 1)[1].split(":", 1)[1].strip()
    except IndexError:
        return ""

def generate_response(message):
    try:
        response = openai.ChatCompletion.create(
            model=config.get('chatcompletion', 'model'),
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": message}
            ],
            temperature=config.getfloat('chatcompletion', 'temperature'),
            max_tokens=config.getint('chatcompletion', 'max_tokens'),
            top_p=config.getfloat('chatcompletion', 'top_p'),
            frequency_penalty=config.getfloat('chatcompletion', 'frequency_penalty'),
            presence_penalty=config.getfloat('chatcompletion', 'presence_penalty'),
            timeout=config.getint('chatcompletion', 'request_timeout')
        )
        return response.choices[0].message.content.strip()
    except openai.OpenAIError as e:
        logger.error("OpenAI API error: %s", e)
        return "I apologize, but I'm currently experiencing some technical difficulties."

def send_response(irc, channel, response):
    irc.send(f"PRIVMSG {channel} :{response}\r\n".encode("UTF-8"))

# Connect to IRC server
irc = connect(server, port, usessl, password, ident, realname, nickname, channels)

# Listen for messages from users
while True:
    try:
        if data := irc.recv(4096).decode("UTF-8"):
            logger.info(data)
            if message := process_message(data):
                response = generate_response(message)
                send_response(irc, channels[0], response)  # Change the channel as per your requirement
    except UnicodeDecodeError:
        continue
    except socket.error:
        logger.error("Socket error occurred. Reconnecting...")
        time.sleep(5)
        irc = connect(server, port, usessl, password, ident, realname, nickname, channels)
    except Exception as e:
        logger.exception("An error occurred: %s", e)
        time.sleep(5)

