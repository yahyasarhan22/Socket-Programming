import socket
import random
import threading
import time

# Server configuration
TCP_PORT = 6000
UDP_PORT = 6001
HOST = 'localhost'
TOTAL_GAME_TIME = 60  # Game duration in seconds
GUESSES_PER_PLAYER = 6  # Each player gets 6 guesses
GUESS_COOLDOWN = 10  # 10 seconds between guesses

clients = {}  # Dictionary to store player names (keys) and their TCP sockets (values)
addresses = {}  # Dictionary to store player names (keys) and their addresses (values)
target_number = random.randint(1, 100)  # The target number players need to guess
game_started = False  # Game started flag
game_over = False  # Game over flag

# Track player guesses
player_guesses = {}  # {player_name: [list_of_guesses]}
last_guess_time = {}  # {player_name: last_guess_timestamp}

lock = threading.Lock()  # Lock for thread synchronization

def send_message_to_all_players(msg: str):
    """Send a message to all connected players and handle disconnections."""
    disconnected_players = []
    for name, conn in clients.items():
        try:
            conn.sendall(msg.encode())  # Send message to player
        except:
            disconnected_players.append(name)  # Track disconnected players

    # Handle disconnections
    for name in disconnected_players:
        handle_player_disconnect(name)

def handle_player_disconnect(name):
    """Handle player disconnections during the game."""
    global game_started, game_over
    with lock:
        if name in clients:
            print(f"[DISCONNECT] {name} disconnected mid-game.")
            del clients[name]  # Remove the player from the dictionary
            del addresses[name]  # Remove the player address
            if name in player_guesses:
                del player_guesses[name]
            if name in last_guess_time:
                del last_guess_time[name]

    # If no players remain
    if len(clients) < 1:
        game_over = True
        print("[GAME] All players disconnected. Game ended.")
        return
    
    # If only one player remains and game was started
    if len(clients) == 1 and game_started and not game_over:
        remaining_player = next(iter(clients))
        conn = clients[remaining_player]
        
        try:
            # Ask the remaining player if they want to continue alone
            conn.sendall(b"PLAYER_LEFT: " + name.encode() + b" left the game. Do you want to play alone? (Y/N)\n")
            conn.settimeout(30.0)  # Give them 30 seconds to respond
            response = conn.recv(1024).decode().strip().upper()
            
            if response == 'Y':
                print(f"[GAME] {remaining_player} chose to continue alone")
                conn.sendall(b"CONTINUE: Game continues with you alone. You have 60 seconds to guess!\n")
            else:
                print(f"[GAME] {remaining_player} chose to end the game")
                conn.sendall(b"GAME_ENDED: Game ended by your choice. No winner.\n")
                game_over = True
        except:
            print(f"[GAME] {remaining_player} didn't respond, ending game")
            game_over = True

def can_player_guess(player_name):
    """Check if player can make a guess (cooldown and guess count)."""
    if player_name not in player_guesses:
        return True  # First guess
    
    # Check guess count
    if len(player_guesses[player_name]) >= GUESSES_PER_PLAYER:
        return False
        
    # Check cooldown
    current_time = time.time()
    last_time = last_guess_time.get(player_name, 0)
    return (current_time - last_time) >= GUESS_COOLDOWN

def handle_game_round():
    """Manages the game round with cooldowns and guess limits."""
    global game_over
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((HOST, UDP_PORT))

    start_time = time.time()  # Track the game start time

    while not game_over:
        # Calculate remaining time
        elapsed_time = time.time() - start_time
        remaining_time = TOTAL_GAME_TIME - elapsed_time

        if remaining_time <= 0:
            send_message_to_all_players("TIME_UP: Time's up! No winners.\n")
            print(f"[!] Game ended. Time's up! The target number was {target_number}.")
            game_over = True
            break

        # Check if all players have used all their guesses
        all_guesses_used = True
        for player in clients:
            if player not in player_guesses or len(player_guesses[player]) < GUESSES_PER_PLAYER:
                all_guesses_used = False
                break
        
        if all_guesses_used:
            send_message_to_all_players("GUESSES_UP: All guesses used! No winners.\n")
            print(f"[!] Game ended. All guesses used! The target number was {target_number}.")
            game_over = True
            break

        # Process any incoming guesses
        try:
            udp_socket.settimeout(1)  # Short timeout to check game state frequently
            data, addr = udp_socket.recvfrom(1024)
            
            try:
                name, guess_str = data.decode().split(':')
                guess = int(guess_str)

                # Validate player can guess
                if not can_player_guess(name):
                    udp_socket.sendto(b"Error: You must wait 10 seconds between guesses", addr)
                    continue

                # Track the guess
                if name not in player_guesses:
                    player_guesses[name] = []
                player_guesses[name].append(guess)
                last_guess_time[name] = time.time()

                # Validate guess range
                if guess < 1 or guess > 100:
                    udp_socket.sendto(b"Error: Guess must be between 1-100", addr)
                    continue

                # Check guess against target
                if guess < target_number:
                    udp_socket.sendto(b"Higher", addr)
                    send_message_to_all_players(f"GUESS:{name} guessed {guess} (Higher)\n")
                elif guess > target_number:
                    udp_socket.sendto(b"Lower", addr)
                    send_message_to_all_players(f"GUESS:{name} guessed {guess} (Lower)\n")
                else:
                    # Correct guess
                    print(f"\n[!] {name} won! The target number was {target_number}.")
                    udp_socket.sendto(b"Correct", addr)
                    result_message = f"[RESULT] {name} guessed the number {target_number}! Game Over."
                    send_message_to_all_players(result_message + "\n")
                    game_over = True
                    break

            except (ValueError, IndexError):
                udp_socket.sendto(b"Error: Invalid input! Only numbers are allowed.", addr)

        except socket.timeout:
            continue  # Continue game loop if no data received

    udp_socket.close()

def handle_new_tcp_connection(conn, addr):
    """Handles new players joining via TCP."""
    global game_started, game_over
    try:
        name = conn.recv(1024).decode().strip()
    except:
        conn.close()
        return

    with lock:
        # Ensure the name is unique and valid
        if name in clients or name.strip() == "":
            conn.sendall(b"NAME_ERROR: Name already taken or invalid. Please reconnect with a different name.")
            conn.close()
            print(f"[REJECTED] Duplicate name '{name}' tried to join.")
            return
        
        if len(clients) >= 4:  # Reject players if the game is full
            conn.sendall(b"Game is full. Cannot join.")
            conn.close()
            print(f"[REJECTED] {name} tried to join (max players reached).")
            return
        
        clients[name] = conn
        addresses[name] = addr
        player_guesses[name] = []
        
    print(f"[TCP] {name} joined from {addr}")

    # Start game when minimum players (2) have joined
    with lock:
        if len(clients) >= 2 and not game_started and not game_over:
            game_started = True
            send_message_to_all_players(f"GAME_START: {','.join(clients.keys())}\n")
            send_message_to_all_players(f"Game started! You each have {GUESSES_PER_PLAYER} guesses with {GUESS_COOLDOWN}s cooldown.\n")
            threading.Thread(target=handle_game_round, daemon=True).start()

def start_server():
    """Starts the server and listens for incoming player connections."""
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcp_sock.bind((HOST, TCP_PORT))
    tcp_sock.listen(5)
    print(f"[SERVER] Listening on {HOST}:TCP {TCP_PORT},UDP {UDP_PORT}")
    print(f"[DEBUG] Target number: {target_number}")

    while True:
        conn, addr = tcp_sock.accept()
        threading.Thread(target=handle_new_tcp_connection, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    start_server()