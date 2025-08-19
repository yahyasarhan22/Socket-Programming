import socket
import threading
import time

# Client configuration
TCP_PORT = 6000
UDP_PORT = 6001
SERVER = 'localhost'

name = input("Enter your name: ")
game_over = False

# TCP connection setup
tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_sock.connect((SERVER, TCP_PORT))
tcp_sock.sendall(name.encode())

# UDP connection setup
udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_sock.bind(('0.0.0.0', 0))

def listen_for_tcp_messages():
    global game_over
    buffer = ""
    while not game_over:
        data = tcp_sock.recv(1024).decode()
        if not data: 
            break
        buffer += data
        while '\n' in buffer:
            line, buffer = buffer.split('\n', 1)
            if line.startswith("GAME_START:"):
                players = line.split(":",1)[1].split(',')
                print("\n=== GAME STARTED ===")
                print("Players:", ", ".join(players))
                print(f"You have 6 guesses with 10s cooldown between guesses.")
            elif line.startswith("GUESS:"):
                print(f"\n{line.replace('GUESS:', '')}")
            elif line.startswith("PLAYER_LEFT:"):
                left_player = line.split(":", 1)[1]
                print(f"\nPlayer {left_player} left the game.")
                response = input("Do you want to play alone? (Y/N): ").upper()
                tcp_sock.sendall(response.encode())
            elif line.startswith("CONTINUE:"):
                print("\n" + line.split(":", 1)[1])
            elif line.startswith("GAME_ENDED:"):
                print("\n" + line.split(":", 1)[1])
                game_over = True
                break
            elif line.startswith("[RESULT]"):
                try:
                    result_text = line.replace("[RESULT] ", "")
                    winner_part = result_text.split(" guessed the number ")[0]
                    number_part = result_text.split(" guessed the number ")[1].split("!")[0]

                    print("\n" + "=" * 40)
                    print("===== GAME ENDED =====")
                    print(f"🎉 Winner: {winner_part} 🎉")
                    print(f"🔢 Correct Number: {number_part}")
                    print("=" * 40 + "\n")
                    game_over = True
                except IndexError:
                    print("\n[ERROR] Invalid result format received.")
                break
            elif line.startswith("TIME_UP:"):
                print("\n" + "=" * 40)
                print("===== GAME ENDED =====")
                print("⏰ Time's up! No winners.")
                print("=" * 40 + "\n")
                game_over = True
                break
            elif line.startswith("GUESSES_UP:"):
                print("\n" + "=" * 40)
                print("===== GAME ENDED =====")
                print("🔢 All guesses used! No winners.")
                print("=" * 40 + "\n")
                game_over = True
                break
            elif line.startswith("Game completed."):
                if "No winners" in line:
                    print("\n" + "=" * 40)
                    print("===== GAME ENDED =====")
                    print("⏰ Game completed. No winners.")
                    print("=" * 40 + "\n")
                else:
                    winner = line.split("Winner: ")[1].strip()
                    print("\n" + "=" * 40)
                    print("===== GAME ENDED =====")
                    print(f"🎉 Winner: {winner} 🎉")
                    print("=" * 40 + "\n")
                game_over = True
                break
            else:
                print("\nServer says:", line)

def listen_for_udp_messages():
    global game_over
    while not game_over:
        data, _ = udp_sock.recvfrom(1024)
        msg = data.decode()
        if msg in ("Higher", "Lower"):
            print(f"\nFeedback: {msg}")
        elif msg == "Correct":
            print("\n🎉 Correct! You won! 🎉")
            game_over = True
        elif msg.startswith("Error:"):
            print(f"\n{msg}")

def player_input_loop():
    global game_over
    while not game_over:
        try:
            guess = input("\nEnter your guess (1-100) or 'q' to quit: ")
            if guess.lower() == 'q':
                game_over = True
                break
                
            udp_sock.sendto(f"{name}:{guess}".encode(), (SERVER, UDP_PORT))
        except:
            break

# Start threads
threading.Thread(target=listen_for_tcp_messages, daemon=True).start()
threading.Thread(target=listen_for_udp_messages, daemon=True).start()
threading.Thread(target=player_input_loop, daemon=True).start()

print("Connected. Waiting for game to start...")
while not game_over:
    time.sleep(1)