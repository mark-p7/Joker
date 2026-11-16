class FirstFiveModel:
    def __init__(self, isTraining: bool):
        pass

    def get_next_move(self, state: dict) -> dict:
        num_cards = min(5, len(state["hand"]["cards"]))
        cards = list(range(num_cards))
        return {"cards" : cards}
    