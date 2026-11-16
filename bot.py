import requests
from datetime import datetime
import logging
import random
import string
logger = logging.getLogger(__name__)

# BalatroBot API endpoint
URL = "http://127.0.0.1:12346"

def configureLogging(log_filename: str):
    logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(log_filename, encoding="utf-8"),
        logging.StreamHandler(),  # Also prints logs to the console
    ],
)

def rpc(method: str, params: dict = {}) -> dict:
    """Send a JSON-RPC 2.0 request to the BalatroBot API."""
    response = requests.post(URL, json={
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1,
    })
    data = response.json()
    # Raise if error, otherwise return result (contains game state)
    if "error" in data:
        raise Exception(data["error"]["message"])
    return data["result"]

def play_game():
    """Play a complete game of Balatro."""
    # Enable logging
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_filename = f"./logs/{timestamp}.log"
    logging.basicConfig(filename=log_filename, level=logging.INFO)
    configureLogging(log_filename=log_filename)
    logger.info('Started Game')
    
    # Return to menu and start a new game
    rpc("menu")
    
    # Init new random seed
    alphabet = string.ascii_uppercase + string.digits
    random_str = ''.join(random.choices(alphabet, k=7))
    state = rpc("start", {"deck": "CHECKERED", "stake": "WHITE", "seed": random_str})
    print(f"Started game with seed: {state['seed']}")

    # Main game loop
    while state["state"] != "GAME_OVER":
        logger.info(f"New State: {state}")
        match state["state"]:
            case "BLIND_SELECT":
                # Always select the current blind
                state = rpc("select")

            case "SELECTING_HAND":
                # Play the first 5 cards (simple strategy)
                num_cards = min(5, len(state["hand"]["cards"]))
                cards = list(range(num_cards))
                state = rpc("play", {"cards": cards})

            case "ROUND_EVAL":
                # Collect rewards and go to shop
                state = rpc("cash_out")

            case "SHOP":
                # Skip the shop and proceed to next round
                state = rpc("next_round")

            case _:
                # Handle any transitional states
                state = rpc("gamestate")

    # Game ended
    if state["won"]:
        print(f"Victory! Final ante: {state['ante_num']}")
        logger.info(f"Victory! Final ante: {state['ante_num']}")
    else:
        print(f"Game over at ante {state['ante_num']}, round {state['round_num']}")
        logger.info(f"Game over at ante {state['ante_num']}, round {state['round_num']}")

    # Final end state
    logger.info('Game End')
    return state["won"]

def train_bot(game_count: int):
    logger.info('Started training')
    
    for i in range(0, game_count):
        # Train a run here
        play_game()
        
    logger.info('Ended training')

if __name__ == "__main__":
    train_bot(100_000)